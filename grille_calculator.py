import math
import streamlit as st
import pandas as pd
import optimizer

CARRIER_LENGTH = 3000


class GrilleCalculator:
    def __init__(self, orientation, width, height, pitch, allowed_wastage, window):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.pitch = pitch
        self.allowed_wastage = allowed_wastage
        self.window = window
        self.inventory = pd.read_csv('inventory.csv')
        self.divisions = optimizer.calculate_divisions(
            self.width,
            self.height,
            self.pitch,
            self.orientation
        )


    def add_to_data(self, df, rows):
        for row in rows:
            # param, val = row
            df.loc[len(df)] = row
        return df


    def run(self):
        curr_inv = optimizer.filter_inv(
            self.inventory,
            'Grille'
        )#, self.divisions)
        cnts = optimizer.find_counts(curr_inv)
        possible_lengths = optimizer.find_combinations(
            self.width,
            curr_inv['length'].unique().tolist(),
            cnts,
            self.divisions,
            self.allowed_wastage
        )

        # wastages = [sum(opt)-width for opt in possible_lengths]

        strs = [
            'Option {num}: {option}'.format(num=opt+1, option=possible_lengths[opt])
            for opt in range(len(possible_lengths))
        ]

        st.write('Number of total divisions: ', self.divisions)

        for opt in range(len(possible_lengths)):

            st.write(strs[opt])
            st.write('Wastage: {}'.format(sum(possible_lengths[opt])-self.width))
            st.write('total: {}\n'.format(sum(possible_lengths[opt])))

        st.subheader('Choose desired Grille breakdown:')
        option_key = f'option_{self.window}'
        selected_option = st.selectbox('Select an option', strs, key=option_key)
        length_combination = possible_lengths[strs.index(selected_option)]

        st.write('Number of pieces required for each length:')
        total_grille_pieces = []
        for l in set(length_combination):
            length_cnt_per_division = length_combination.count(l)
            grille_cnt_per_length = self.divisions*(length_cnt_per_division)
            total_grille_pieces.append(grille_cnt_per_length)
            st.write(
                '{len} mm --> {length_cnt_per_division} piece(s) per division * {divisions} divisions = {number} pieces'.format(
                    len = l,
                    length_cnt_per_division = length_cnt_per_division,
                    divisions = self.divisions,
                    number = grille_cnt_per_length
                )
            )

        total_grille_length = (self.width*self.divisions)/1000 # in metres

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
                piece_length = length_combination[i],
                breakdown = carrier_distances_per_piece[i]
            ))

        for item in set(lsts):
            st.write(item)

        total_carrier_divisions = sum(no_carriers_per_piece)
        total_carrier_length = total_carrier_divisions*self.height

        st.write('Total carrier divisions = {}'.format(total_carrier_divisions))
        st.write('Total length of carrier required: {divs} * {height} = {tcl} mm'.format(
            divs = total_carrier_divisions,
            height = self.height,
            tcl = total_carrier_length
            ))
        st.write('Number of 3000mm carriers required = {}'.format(total_carrier_length/CARRIER_LENGTH))
        st.write('Total covering plate required: {} mm'.format(total_carrier_length))

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
            left = st.radio("Left end caps required?", ("Yes", "No"), key=left_key)
            st.write("Total left end caps: {}".format(self.divisions if left=="Yes" else 0))

            right_key = f'right_{self.window}'
            right = st.radio("Right end caps required?", ("Yes", "No"), key=right_key)
            st.write("Total right end caps: {}".format(self.divisions if right=="Yes" else 0))

            top = False
            bottom = False
        elif self.orientation == 'Vertical':
            top_key = f'top_{self.window}'
            top = st.radio("Top end caps required?", ("Yes", "No"), key=self.window+3)

            top_orientation_key = f'top_orientation_{self.window}'
            top_orientation = st.radio("Top end cap orientation?", caps, key=top_key)

            st.write('Total {} top end caps required: {}'.format(
                top_orientation,
                self.divisions if top == "Yes" else 0
            ))

            bottom_key = f'bottom_{self.window}'
            bottom = st.radio("Bottom end caps required?", ("Yes", "No"), key=bottom_key)

            st.write('Total {} bottom end caps required: {}'.format(
                caps[caps.index(top_orientation)-1],
                self.divisions if bottom == "Yes" else 0
            ))
            left = False
            right = False

        results = pd.DataFrame({
            'Width (mm)': [self.width if self.orientation == "Horizontal" else self.height],
            'Height (mm)': [self.height if self.orientation == "Horizontal" else self.width],
            'Orientation': [self.orientation],
            'Pitch (mm)': [self.pitch],
            'Area (ft2)': [((self.width * self.height) / (304.8 * 304.8))],
            'Divisions': [self.divisions],
            'Total Product Length (m)': [total_grille_length],
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Total Covering Plate Length (m)': [total_carrier_length / 1000],
            'Product Weight (kg)': [total_grille_length * 0.412],
            'Carrier+Covering Plate Weight (kg)': [total_carrier_length * 0.427],
            'Nuts/Bolts Weight (kg)': [nuts_bolts_cnt * 0.02],
            'Nuts/Bolts/Washers (pcs)': [nuts_bolts_cnt],
            'Self-drilling screws (pcs)': [total_carrier_length / 300],
            'Joining Pieces (pcs)': [joining_pieces],
            'Right End Cap (pcs)': [self.divisions if right else 0],
            'Left End Cap (pcs)': [self.divisions if left else 0],
            'Top End Cap (pcs)': [self.divisions if top else 0],
            'Top End Cap Orientation': [top_orientation if top else pd.NA],
            'Bottom End Cap (pcs)': [self.divisions if bottom else 0],
            'Bottom End Cap Orientation': [caps[caps.index(top_orientation) - 1] if top else pd.NA]
        })

        return results