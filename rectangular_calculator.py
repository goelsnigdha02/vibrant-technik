import pandas as pd
import optimizer
import streamlit as st


class RectangularCalculator:

    def __init__(self,
                 orientation,
                 width,
                 height,
                 pitch,
                 allowed_wastage,
                 window,
                 louver_size):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.pitch = pitch
        self.divisions = optimizer.calculate_divisions(
            self.height,
            self.pitch
        )
        self.window = window
        self.allowed_wastage = allowed_wastage
        self.louver_size = louver_size

    def run(self):

        st.write('Number of total divisions: ', self.divisions)

        total_product_length = (self.width * self.divisions) / 1000
        total_carrier_length = total_product_length

        carrier_lengths = 0
        no_carriers_per_piece = []

        centre_gaps_per_piece, no_carriers_per_piece = optimizer.carrier_calculation(
            [self.width],
            carrier_lengths,
            no_carriers_per_piece
        )

        carrier_distances_per_piece = optimizer.calculate_carrier_distances(
            centre_gaps_per_piece,
            no_carriers_per_piece
        )
        print(carrier_distances_per_piece)
        rivet_df = pd.DataFrame()
        rivet_df['Rivet Distance'] = [carrier_distances_per_piece[0]]
        rivet_pcs = len(carrier_distances_per_piece[0])*self.divisions
        rivet_df['Total Rivets Required'] = rivet_pcs
        st.subheader('Rivet Calculations')
        st.write(rivet_df.T.rename_axis('Item'))

        top_key = f'top_{self.window}'
        top = st.radio(
            "Top end caps required?",
            ("Yes", "No"),
            key=top_key
        )

        bottom_key = f'bottom_{self.window}'
        bottom = st.radio(
            "Bottom end caps required?",
            ("Yes", "No"),
            key=bottom_key
        )

        endcaps = 0
        if top == "Yes":
            endcaps += self.divisions
        if bottom == "Yes":
            endcaps += self.divisions

        results = pd.DataFrame({
            'Width (mm)': [
                self.width if self.orientation == "Horizontal" else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == "Horizontal" else self.width
            ],
            'Orientation': [self.orientation],
            'Area (ft2)': [
                round(((self.width * self.height) / (304.8 ** 2)), 2)
            ],
            'Product Divisions': [self.divisions],
            'Total Product Length (m)': [total_product_length],
            'Total Carrier Length (m)': [total_carrier_length],
            'Rivet Screws (pcs)': [rivet_pcs],
            'Endcaps (pcs)': [endcaps]
        })

        return results
