import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from menu import display_menu

display_menu()


@st.cache_resource
def init_connection():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn


conn = init_connection()

URL = "https://docs.google.com/spreadsheets/d/1ESz9y13cuZBo8UvgvhauYirrklvU7QG7Do-I5slY5Hs/edit#gid=0"
DATA = conn.read(
        spreadsheet=URL, usecols=list(range(6)), ttl=0
    ).dropna(how="all")


@st.cache_data()
def get_inv():
    data = conn.read(spreadsheet=URL, usecols=list(range(6)), ttl=0)
    data = data.dropna(how="all")
    return data


def update_data():
    global DATA
    DATA = conn.read(
        spreadsheet=URL, usecols=list(range(6)), ttl=0
        ).dropna(how="all")


def display_inv(product):
    data = get_inv()
    return st.dataframe(data[data["Product Code"] == product])


def string_to_set(s):
    if type(s) is not str:
        s = str(s)
    elements = s.strip("{}").split(",")

    result_set = set()

    for element in elements:
        element = element.strip()
        if element.lower() == "nan":
            continue
        result_set.add(int(float(element)))
    return result_set


def select_product():
    return st.selectbox(
        "Product Code",
        sorted(list(DATA["Product Code"].unique()))
    )


def select_num_pieces():
    return st.number_input(
            label="Number of pieces",
            min_value=0,
            step=1
        )


def run_view():
    product = select_product()
    st.dataframe(DATA[DATA["Product Code"] == product])


def run_add():
    with st.form(key="add_form"):
        product = select_product()
        product_length = st.number_input(
            label="Product Length",
            min_value=0,
            step=1
        )
        num_pieces_new = int(float(select_num_pieces()))

        rack_no = int(st.number_input(
            label="Material Location (Rack No.)",
            min_value=0,
            step=1
        ))
        rack_no = int(float(rack_no))

        submit_button = st.form_submit_button(label="ADD")

        df = DATA[DATA["Product Code"] == product]

        if submit_button:
            if not product_length or not num_pieces_new:
                st.warning("Ensure all fields are filled.")
            elif product_length in list(
                    df[df["Piece Length"] == product_length]["Piece Length"]
            ):

                old_num_pieces = df[
                        df["Piece Length"] == product_length
                    ]["Units Available"].values[0]
                updated_num_pieces = old_num_pieces + num_pieces_new

                old_rack = df.loc[
                      df["Piece Length"] == product_length,
                      "Material Location (Rack No.)"
                ].values[0]

                updated_rack_nos = set()
                if pd.notna(old_rack):
                    old_rack = string_to_set(old_rack)
                    updated_rack_nos.update(old_rack)
                updated_rack_nos.add(rack_no)

                # Removing old entry
                data_new = DATA.copy()
                data_new.drop(
                    df[
                        df["Piece Length"] == product_length
                    ].index,
                    inplace=True,
                )

                # Creating updated data entry
                updated_product_inv = pd.DataFrame(
                    [
                        {
                            "Product Code": product,
                            "Units Available": updated_num_pieces,
                            "Piece Length": product_length,
                            "Total Product Length": (
                                updated_num_pieces*product_length
                            )/1000,
                            "Total Product Weight": 100000,
                            "Material Location (Rack No.)": updated_rack_nos,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [data_new, updated_product_inv], ignore_index=True
                )
                conn.update(spreadsheet=URL, data=updated_df)
                st.success("Inventory successfully updated!")
                update_data()
                st.dataframe(DATA[DATA["Product Code"] == product])
            else:
                updated_rack_nos = set()
                updated_rack_nos.add(rack_no)

                # Creating updated data entry
                updated_product_inv = pd.DataFrame(
                    [
                        {
                            "Product Code": product,
                            "Units Available": num_pieces_new,
                            "Piece Length": product_length,
                            "Total Product Length": (
                                num_pieces_new*product_length
                            )/1000,
                            "Total Product Weight": 100000,
                            "Material Location (Rack No.)": updated_rack_nos,
                        }
                    ]
                )

                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [DATA, updated_product_inv], ignore_index=True
                )
                conn.update(spreadsheet=URL, data=updated_df)
                st.success("Inventory successfully updated!")
                update_data()
                st.dataframe(DATA[DATA["Product Code"] == product])


def run_issue():
    product = select_product()
    df = DATA[DATA["Product Code"] == product]
    product_lengths = df["Piece Length"].unique()
    product_length = st.selectbox("Product Length", product_lengths)
    avail = float(
        df[df["Piece Length"] == product_length]["Units Available"].values[0]
    )
    st.write('Available Pieces: {}'.format(avail))

    with st.form(key="add_form"):

        num_pieces_issue = select_num_pieces()
        num_pieces_issue = int(float(num_pieces_issue))

        submit_button = st.form_submit_button(label="Update")

        if submit_button:
            if not product_length or not num_pieces_issue:
                st.warning("Ensure all fields are filled.")
            elif num_pieces_issue > avail:
                st.error("Cannot issue more than {} units.".format(
                    avail
                ))
            else:
                old_rack = df.loc[
                        df["Piece Length"] == product_length,
                        "Material Location (Rack No.)"
                ].values[0]

                # Removing old entry
                data_new = DATA.copy()
                data_new.drop(
                    df[
                        df["Piece Length"] == product_length
                    ].index,
                    inplace=True,
                )

                new_avail = avail-num_pieces_issue

                # Creating updated data entry
                updated_product_inv = pd.DataFrame(
                    [
                        {
                            "Product Code": product,
                            "Units Available": new_avail,
                            "Piece Length": product_length,
                            "Total Product Length": new_avail/1000,
                            "Total Product Weight": 100000,
                            "Material Location (Rack No.)": old_rack,
                        }
                    ]
                )

                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [data_new, updated_product_inv], ignore_index=True
                )
                conn.update(spreadsheet=URL, data=updated_df)
                st.success("Inventory successfully updated!")
                update_data()
                st.dataframe(DATA[DATA["Product Code"] == product])


action = st.selectbox(
    "Choose an Action",
    [
        "View Inventory",
        "Add to Inventory",
        "Issue from Inventory"
    ]
)

if action == "View Inventory":
    run_view()
elif action == "Add to Inventory":
    run_add()
elif action == "Issue from Inventory":
    run_issue()