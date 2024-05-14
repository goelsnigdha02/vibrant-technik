import streamlit as st
import pandas as pd
import modules.optimizer as optimizer
import modules.general_calculator as general_calculator


class GrilleCalculator:
    def __init__(
            self, orientation, width, height, pitch, allowed_wastage, window
    ):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.pitch = pitch
        self.allowed_wastage = allowed_wastage
        self.window = window
        self.inventory = pd.read_csv('modules/inventory.csv')
        self.divisions = optimizer.calculate_divisions(
            self.height,
            self.pitch
        )

    def add_to_data(self, df, rows):
        for row in rows:
            # param, val = row
            df.loc[len(df)] = row
        return df

    def run(self):
        vars = general_calculator.run(
            'Grille',
            self.width,
            self.height,
            self.pitch,
            self.divisions,
            self.orientation,
            self.allowed_wastage,
            self.window
        )

        length_combination = vars['length_combination']
        total_product_length = vars['total_product_length']
        total_carrier_length = vars['total_carrier_length']
        total_carrier_divisions = vars['total_carrier_divisions']

        nuts_bolts_cnt = self.divisions * total_carrier_divisions

        st.subheader("Nuts & Bolts")
        st.write('Nuts & Bolts needed: {}'.format(nuts_bolts_cnt))
        st.write('Self-drilling screw: {}'.format(total_carrier_length/300))

        joining_pieces = (len(length_combination)-1) * self.divisions
        st.subheader("Joining Pieces")
        st.write("Total Joining Pieces: {}".format(joining_pieces))

        st.subheader("End Caps")
        caps = ["L", "Inverse L"]

        if self.orientation == 'Horizontal':
            left_key = f'left_{self.window}'
            left = st.radio(
                "Left end caps required?",
                ("Yes", "No"),
                key=left_key
            )
            st.write("Total left end caps: {}".format(
                self.divisions if left == "Yes" else 0
            ))

            right_key = f'right_{self.window}'
            right = st.radio(
                "Right end caps required?",
                ("Yes", "No"),
                key=right_key
                )
            st.write("Total right end caps: {}".format(
                self.divisions if right == "Yes" else 0
            ))

            top = False
            bottom = False
        elif self.orientation == 'Vertical':
            top_key = f'top_{self.window}'
            top = st.radio(
                "Top end caps required?",
                ("Yes", "No"),
                key=top_key
            )
            top_orientation = st.radio(
                "Top end cap orientation?",
                caps,
                key=self.window+3
            )

            st.write('Total {} top end caps required: {}'.format(
                top_orientation,
                self.divisions if top == "Yes" else 0
            ))

            bottom_key = f'bottom_{self.window}'
            bottom = st.radio(
                "Bottom end caps required?",
                ("Yes", "No"),
                key=bottom_key
            )

            st.write('Total {} bottom end caps required: {}'.format(
                caps[caps.index(top_orientation)-1],
                self.divisions if bottom == "Yes" else 0
            ))
            left = False
            right = False

        results = pd.DataFrame({
            'Width (mm)': [
                self.width if self.orientation == "Horizontal"
                else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == "Horizontal"
                else self.width
            ],
            'Orientation': [self.orientation],
            'Pitch (mm)': [self.pitch],
            'Area (ft2)': [((self.width * self.height) / (304.8 * 304.8))],
            'Divisions': [self.divisions],
            'Total Product Length (m)': [total_product_length],
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Total Covering Plate Length (m)': [total_carrier_length / 1000],
            'Product Weight (kg)': [total_product_length * 0.412],
            'Carrier+Covering Plate Weight (kg)': [
                total_carrier_length * 0.427
            ],
            'Nuts/Bolts Weight (kg)': [nuts_bolts_cnt * 0.02],
            'Nuts/Bolts/Washers (pcs)': [nuts_bolts_cnt],
            'Self-drilling screws (pcs)': [total_carrier_length / 300],
            'Joining Pieces (pcs)': [joining_pieces],
            'Right End Cap (pcs)': [self.divisions if right else 0],
            'Left End Cap (pcs)': [self.divisions if left else 0],
            'Top End Cap (pcs)': [self.divisions if top else 0],
            'Top End Cap Orientation': [top_orientation if top else pd.NA],
            'Bottom End Cap (pcs)': [self.divisions if bottom else 0],
            'Bottom End Cap Orientation': [
                caps[caps.index(top_orientation) - 1] if top else pd.NA
            ]
        })

        return results
