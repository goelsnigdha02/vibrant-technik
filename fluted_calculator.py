import pandas as pd
import optimizer
import general_calculator


class FlutedCalculator:

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
        vars = general_calculator.run(
            'Fluted',
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
            'Start Piece (29-3002-00)': ['{}mm: 1 piece'.format(
                self.width
            )],
            'End Pieces (29-4001-00)': ['{}mm: 2 pieces'.format(
                self.width
            )],
            'EPDM Gasket': ['{}mm'.format(total_product_length+self.width)],
            'Self-Drilling 3/4 Inch Screws (pcs)': [
                self.divisions * total_carrier_divisions
            ],
            'Full Threaded 75mm Screws (pcs)': [total_carrier_length/500],
            'PVC Gitty': [total_carrier_length/500]
        })

        return results
