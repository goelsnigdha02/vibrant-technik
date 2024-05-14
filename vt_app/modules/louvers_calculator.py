import math
import pandas as pd
import modules.optimizer as optimizer
import streamlit as st
import modules.general_calculator as general_calculator

STANDARD_SLOUVER_PITCH = {
    '54.5x31.3': 43.7,
    '84.2x31.3': 57.5  # TODO
}


class SLouverCalculator:

    def __init__(self,
                 orientation,
                 width,
                 height,
                 allowed_wastage,
                 window,
                 louver_size):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.louver_size = louver_size
        self.pitch = STANDARD_SLOUVER_PITCH[self.louver_size]
        self.divisions = optimizer.calculate_divisions(
            self.height,
            self.pitch
        )
        self.window = window
        self.allowed_wastage = allowed_wastage

    def run(self):
        vars = general_calculator.run(
            'S_Louver_1' if self.louver_size == '54.5x31.3' else 'S_Louver_2',
            self.width,
            self.height,
            self.pitch,
            self.divisions,
            self.orientation,
            self.allowed_wastage,
            self.window
        )

        total_product_length = vars['total_product_length']
        total_carrier_length = vars['total_carrier_length']
        total_carrier_divisions = vars['total_carrier_divisions']
        num_carrier_pieces = round(total_carrier_length/133.7, 2)
        self_drill_screws = (
            (self.divisions * total_carrier_divisions) + (math.ceil(
                num_carrier_pieces
            )*2)
        )

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
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Self-Drilling 3/4 Inch Screws (pcs)': [
                '{} + {} extra'.format(
                    self_drill_screws,
                    math.ceil(num_carrier_pieces)
                )
            ]
        })

        return results


class CLouverCalculator:
    def __init__(self,
                 orientation,
                 width,
                 height,
                 pitch,
                 allowed_wastage,
                 window):
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

    def run(self):

        st.write('Number of total divisions: ', self.divisions)

        total_product_length = (self.width * self.divisions) / 1000

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

        no_carriers = self.divisions * no_carriers_per_piece
        total_carrier_length = no_carriers_per_piece[0] * self.height

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
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Self-Drilling 3/4 Inch Screws (pcs)': [no_carriers*2]
        })

        return results


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
