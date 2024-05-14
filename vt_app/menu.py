import streamlit as st

def display_menu():
    st.set_option("client.showSidebarNavigation", False)
    st.sidebar.page_link("pages/inventory.py", label="Inventory Manager")
    st.sidebar.page_link("pages/main.py", label="Material Calculator")