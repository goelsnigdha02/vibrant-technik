import math
import pandas as pd
import optimizer
import general_calculator

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
