import streamlit as st
import pandas as pd
import modules.optimizer as optimizer

AEROFOIL_WIDTH = {
    'AF 60': 60,
    'AF 100': 100,
    'AF 150': 150,
    'AF 200': 200,
    'AF 250': 250,
    'AF 300': 300,
    'AF 400': 400,
}
L_ANGLE_LENGTH = 3250


class AerofoilCalculator:

    def __init__(self,
                 orientation,
                 width,
                 height,
                 pitch,
                 allowed_wastage,
                 window,
                 af_type,
                 installation,
                 **kwargs):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.pitch = pitch
        self.allowed_wastage = allowed_wastage
        self.window = window
        self.af_type = af_type
        self.installation = installation
        self.inventory = pd.read_csv('modules/inventory.csv')
        self.divisions = optimizer.calculate_divisions(
            self.height,
            self.pitch
        )

        if 'fixing_method' in kwargs:
            self.fixing_method = kwargs['fixing_method']

    def run_fringe(self):
        output_df = pd.DataFrame({
            'Aerofoil Type': [self.af_type],
            'Width (mm)': [
                self.width if self.orientation == 'Horizontal' else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == 'Horizontal' else self.width
            ],
            'Pitch (mm)': [self.pitch],
            'Orientation': [self.orientation],
            'Total Pieces (pcs)': [self.divisions],
            '{} Fringe End Caps (pcs)'.format(
                self.af_type
            ): [self.divisions*2],
            '19mm Black Gypsum Screws (pcs)': [self.divisions*4],
            'Full Threaded Screws (pcs)': [self.divisions*4],
            'PVC Gitty (pcs)': [self.divisions*4],
        })

        return output_df

    def run_c_channel(self):

        plate_key = f'option_{self.window}'
        if self.af_type == 'AF 60':
            plate_width = st.selectbox(
                'Select C-Plate Width (mm):',
                [50],
                key=plate_key
            )
        elif self.af_type == 'AF 100':
            plate_width = st.selectbox(
                'Select C-Plate Width (mm):',
                [50, 75],
                key=plate_key
            )
        else:
            plate_width = st.selectbox(
                'Select C-Plate Width (mm):',
                [75, 112],
                key=plate_key
            )
        plate_length = self.width * 2

        output_df = pd.DataFrame({
            'Aerofoil Type': [self.af_type],
            'Width (mm)': [
                self.width if self.orientation == 'Horizontal' else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == 'Horizontal' else self.width
            ],
            'Pitch (mm)': [self.pitch],
            'Orientation': [self.orientation],
            'Total Pieces (pcs)': [self.divisions],
            'Length of {}mm x 10mm C-Plate'.format(
                str(plate_width)
            ): [plate_length],
            '19mm Black Gypsum Screws (pcs)': [self.divisions*4],
            'Full Threaded Screws (pcs)': [plate_length/300],
            'PVC Gitty (pcs)': [plate_length/300],
        })

        return output_df

    def run_ms_rod(self):
        top_key = f'top_{self.window}'
        top_suspension = st.number_input(
            'Top Air Suspension (mm):',
            min_value=0,
            value=100,
            key=top_key
        )
        bottom_key = f'bottom_{self.window}'
        bottom_suspension = st.number_input(
            'Bottom Air Suspension (mm):',
            min_value=0,
            value=100,
            key=bottom_key
        )
        piece_length = self.height - (top_suspension + bottom_suspension)

        output_df = pd.DataFrame({
            'Aerofoil Type': [self.af_type],
            'Width (mm)': [
                self.width if self.orientation == 'Horizontal' else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == 'Horizontal' else self.width
            ],
            'Piece Length (mm)': [piece_length],
            'Pitch (mm)': [self.pitch],
            'Orientation': [self.orientation],
            'Total Pieces (pcs)': [self.divisions],
            'Number of {} End Caps (with centre hole) (pcs)'.format
            (self.af_type): [self.divisions*2],
            'Total MS Rods (pcs)': [self.divisions*2],
            '19mm Black Gypsum Screws (pcs)': [self.divisions*4]
        })

        return output_df

    def run_d_wall(self):
        divisions = optimizer.calculate_divisions(
            self.height,
            self.pitch
        )
        inventory = pd.read_csv('modules/inventory.csv')
        curr_inv = optimizer.filter_inv(
            inventory,
            'Grille'
        )  # , divisions)
        cnts = optimizer.find_counts(curr_inv)
        possible_lengths = optimizer.find_combinations(
            self.width,
            curr_inv['length'].unique().tolist(),
            cnts,
            divisions,
            self.allowed_wastage
        )

        # wastages = [sum(opt)-width for opt in possible_lengths]

        strs = [
            'Option {num}: {option}'.format(
                num=opt+1, option=possible_lengths[opt]
            ) for opt in range(len(possible_lengths))
        ]

        st.write('Number of total divisions: ', divisions)

        for opt in range(len(possible_lengths)):

            st.write(strs[opt])
            st.write(
                'Wastage: {}'.format(sum(possible_lengths[opt])-self.width)
            )
            st.write('total: {}\n'.format(sum(possible_lengths[opt])))

        st.subheader('Choose desired Aerofoil breakdown:')
        option_key = f'option_{self.window}'
        selected_option = st.selectbox(
            'Select an option',
            strs,
            key=option_key
        )
        length_combination = possible_lengths[strs.index(selected_option)]

        st.write('Number of pieces required for each length:')
        total_grille_pieces = []
        for combo in set(length_combination):
            length_cnt_per_division = length_combination.count(combo)
            grille_cnt_per_length = divisions*(length_cnt_per_division)
            total_grille_pieces.append(grille_cnt_per_length)
            st.write(
                '{len} mm --> {length_cnt_per_division} piece(s) per \
                    division * {divisions} divisions = {number} pieces'.format(
                    len=combo,
                    length_cnt_per_division=length_cnt_per_division,
                    divisions=divisions,
                    number=grille_cnt_per_length
                )
            )

        total_grille_length = (self.width*divisions)/1000  # in metres

        st.subheader('Carrier Calculations')

        carrier_lengths = 0
        no_carriers_per_piece = []

        centre_gaps_per_piece, no_carriers_per_piece = optimizer.carrier_calculation(
            length_combination,
            carrier_lengths,
            no_carriers_per_piece
        )

        carrier_distances_per_piece = optimizer.calculate_carrier_distances(
            centre_gaps_per_piece,
            no_carriers_per_piece
        )

        st.write("Chosen length option: {}".format(length_combination))
        st.write("Carrier divisions for each piece in the chosen option:")

        lsts = []
        for i in range(len(length_combination)):
            lsts.append('{piece_length} mm: {breakdown}'.format(
                piece_length=length_combination[i],
                breakdown=carrier_distances_per_piece[i]
            ))

        for item in set(lsts):
            st.write(item)

        total_carrier_divisions = sum(no_carriers_per_piece)
        total_carrier_length = total_carrier_divisions*self.height

        st.write('Total carrier divisions = {}'.format(
            total_carrier_divisions
        ))
        st.write('Number of D Brackets required: {} aerofoil divisions \
                 * {} carrier divisions = {} brackets'.format(
            divisions,
            total_carrier_divisions,
            divisions * total_carrier_divisions
        ))
        st.write('Total length of D-Bracket required: {} brackets * 55 \
                 mm per bracket = {} mm'.format(
            divisions * total_carrier_divisions,
            divisions * total_carrier_divisions * 55
        ))

        results = pd.DataFrame({
            'Width (mm)': [
                self.width if self.orientation == "Horizontal" else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == "Horizontal" else self.width
            ],
            'Orientation': [self.orientation],
            'Pitch (mm)': [self.pitch],
            'Area (ft2)': [((self.width * self.height) / (304.8 * 304.8))],
            'Divisions': [self.divisions],
            'Total Product Length (m)': [total_grille_length],
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Total D-Brackets (pcs)': [divisions * total_carrier_divisions],
            'Length of D-Bracket (mm)': [
                divisions * total_carrier_divisions * 55
            ],
            # 'Nuts/Bolts Weight (kg)': [nuts_bolts_cnt * 0.02],
            # 'Nuts/Bolts/Washers (pcs)': [nuts_bolts_cnt],
            'Self-drilling screws (pcs)': [total_carrier_length / 300],
            # 'Joining Pieces (pcs)': [joining_pieces]
        })

        return results

    def run_manual_moveable(self):

        total_carrier_length = (self.height * 2)

        l_angle_pcs = (self.height//L_ANGLE_LENGTH)
        length_per_l_angle = self.height / l_angle_pcs

        results = pd.DataFrame({
            'Width (mm)': [
                self.width if self.orientation == "Horizontal" else self.height
            ],
            'Height (mm)': [
                self.height if self.orientation == "Horizontal" else self.width
            ],
            'Orientation': [self.orientation],
            'Pitch (mm)': [self.pitch],
            'Total Aerofoil (pcs)': [self.divisions],
            'Total Aerofoil Length (m)': [self.divisions * self.width],
            'Total Carrier Length (m)': [total_carrier_length/1000],
            'Carrier Hole Gap (pcs)': [self.pitch],
            'Top Endcap (pcs)': [self.divisions],
            'Bottom Endcap (pcs)': [self.divisions],
            'Pivot (pcs)': [self.divisions*2],
            'Total Length of L-Angle (m)': [self.height/1000],
            'Number of {} mm L-Angles (pcs)'.format(
                L_ANGLE_LENGTH
            ): [l_angle_pcs],
            'Length per L-Angle': [length_per_l_angle],
            'Knobs (pcs)': [l_angle_pcs * 2],
            'Black Gypsum Screws (pcs)': ['{} + {} buffer screws'.format(
                self.divisions*4,
                self.divisions)
            ],
            '3/4 Inch SS Screws': [self.divisions*1],
            '75mm Full Threaded Screws (pcs)': ['{} + {} buffer pieces'.format(
                round(total_carrier_length/300, 2),
                1)],
            'PVC Gitty (pcs)': ['{} + {} buffer pieces'.format(
                round(total_carrier_length/300, 2),
                1)],
            '6mm Interlocking Screws (pcs)': [self.divisions]
        })

        return results

    def run_motorized_moveable(self):

        return

    def run_fixed(self):
        if self.fixing_method == 'Fringe End Caps':
            return self.run_fringe()
        elif self.fixing_method == 'C-Channel':
            return self.run_c_channel()
        elif self.fixing_method == 'MS Rod/Slot Cut Pipe':
            return self.run_ms_rod()
        elif self.fixing_method == 'D-Wall Bracket':
            return self.run_d_wall()

    def run(self):
        if self.installation == 'Fixed':
            return self.run_fixed()
        elif self.installation == 'Moveable (Manual)':
            return self.run_manual_moveable()
        elif self.installation == 'Moveable (Motorized)':
            return self.run_motorized_moveable()
