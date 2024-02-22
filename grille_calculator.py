import streamlit as st
import pandas as pd
import math

CARRIER_MAX_GAP = 1000
CARRIER_END_GAP = 150
CARRIER_LENGTH = 3000


class GrilleCalculator:
    def __init__(self, orientation, width, height, pitch, allowed_wastage, window):
        self.orientation = orientation
        self.width = width
        self.height = height
        self.pitch = pitch
        self.allowed_wastage = allowed_wastage
        self.window = window

    
    def calculate_divisions(self, width, height, pitch, orientation):

        divisions = math.ceil(height / pitch)

        if orientation == 'Vertical':
            temp = width
            width = height
            height = temp

        return divisions


    def filter_inv(self, df, product):#, divisions):
        inv = df[(df['name'] == product)]# & (df['stock'] >= divisions)]
        return inv


    def find_counts(self, df):
        counts = {}
        for _, row in df.iterrows():
            if int(row['length']) not in counts:
                counts[row['length']] = 0
            counts[row['length']] += row['stock']
        
        return counts


    def find_combinations_grille(self, target, lengths, counts, req_pieces, wastage):
        output = set()
        
        def dfs(total, arr, i):
            if target <= total <= target + wastage:
                stock_avail = True
                for l in set(arr):
                    req = arr.count(l) * req_pieces
                    if counts[l] < req:
                        stock_avail = False
                        break
                if stock_avail:
                    output.add(tuple(sorted(arr)))
                return
            
            if (total > target + wastage) or (i >= len(lengths)):
                return
            
            arr.append(lengths[i])
            dfs(total + lengths[i], arr, i)
            arr.pop()
            dfs(total, arr, i + 1)
        
        dfs(0, [], 0)
        return [list(x) for x in output]


    def carrier_calculation(
        self,
        carrier_max_gap,
        carrier_end_gap,
        length_combination,
        carrier_lengths,
        no_carriers_per_piece
    ):
        centre_gaps_per_piece = []

        for l in length_combination:
            carrier_lengths = 1 # for end piece
            centre_width = l - (2 * carrier_end_gap)
            if centre_width >= 900:
                carrier_lengths += math.ceil(centre_width / carrier_max_gap)
                centre_gap = centre_width / (carrier_lengths - 1)
            else:
                carrier_lengths += 1
                centre_gap = centre_width

            centre_gaps_per_piece.append(centre_gap)
            no_carriers_per_piece.append(carrier_lengths)

        return centre_gaps_per_piece, no_carriers_per_piece


    def calculate_carrier_distances(self,
                                    carrier_end_gap,
                                    centre_gaps_per_piece,
                                    no_carriers_per_piece
                                    ):
        carrier_distances = []
        
        for j in range(len(no_carriers_per_piece)):
            curr = 0
            curr_distances = []
            for i in range(no_carriers_per_piece[j]):
                if i == 0:
                    curr += carrier_end_gap
                else:
                    curr += centre_gaps_per_piece[j]
                curr_distances.append(curr)
            carrier_distances.append(curr_distances)

        return carrier_distances


    def add_to_data(self, df, rows):
        for row in rows:
            # param, val = row
            df.loc[len(df)] = row
        return df


    def run(self):

        # orientation = st.radio('Select orientation:', ('Horizontal', 'Vertical'))
        # width = st.number_input('Width:', min_value=150, value=6000)
        # height = st.number_input('Height:', min_value=0, value=3250)

        # if orientation == 'Vertical':
        #         temp = width
        #         width = height
        #         height = temp

        # pitch = st.number_input('Pitch:', min_value=0, max_value=height, value=50)
        # allowed_wastage = st.number_input('Buffer Wastage:', min_value=0, value=100)

        output_csv = pd.DataFrame([
            'Width (mm)',
            'Height (mm)',
            'Orientation',
            'Pitch (mm)',
            'Area (ft2)',
            'Divisions',
            'Total Product Length (m)',
            'Total Carrier Length (m)',
            'Total Covering Plate Length (m)',
            'Product Weight (kg)',
            'Carrier+Covering Plate Weight (kg)',
            'Nuts/Bolts Weight (kg)',
            'Nuts/Bolts/Washers (pcs)',
            'Self-drilling screws (pcs)',
            'Joining Pieces (pcs)',
            'Right End Cap (pcs)',
            'Left End Cap (pcs)',
            'Top End Cap (pcs)',
            'Top End Cap Orientation',
            'Bottom End Cap (pcs)',
            'Bottom End Cap Orientation'
        ])

        inventory = pd.read_csv('inventory.csv')

        divisions = self.calculate_divisions(
            self.width,
            self.height,
            self.pitch,
            self.orientation
        )
        curr_inv = self.filter_inv(
            inventory,
            'Grille'
        )#, divisions)
        cnts = self.find_counts(curr_inv)
        possible_lengths = self.find_combinations_grille(
            self.width,
            curr_inv['length'].unique().tolist(),
            cnts,
            divisions,
            self.allowed_wastage
        )

        # wastages = [sum(opt)-width for opt in possible_lengths]

        strs = [
            'Option {num}: {option}'.format(num=opt+1, option=possible_lengths[opt])
            for opt in range(len(possible_lengths))
        ]

        st.write('Number of total divisions: ', divisions)

        for opt in range(len(possible_lengths)):

            st.write(strs[opt])
            st.write('Wastage: {}'.format(sum(possible_lengths[opt])-self.width))
            st.write('total: {}\n'.format(sum(possible_lengths[opt])))

        st.subheader('Choose desired Grille combination:')
        option_key = f'option_{self.window}'
        selected_option = st.selectbox('Select an option', strs, key=option_key)
        length_combination = possible_lengths[strs.index(selected_option)]

        st.write('Number of pieces required for each length:')
        total_grille_pieces = []
        for l in set(length_combination):
            length_cnt_per_division = length_combination.count(l)
            grille_cnt_per_length = divisions*(length_cnt_per_division)
            total_grille_pieces.append(grille_cnt_per_length)
            st.write(
                '{len} mm --> {length_cnt_per_division} piece(s) per division * {divisions} divisions = {number} pieces'.format(
                    len = l,
                    length_cnt_per_division = length_cnt_per_division,
                    divisions = divisions,
                    number = grille_cnt_per_length
                )
            )

        total_grille_length = (self.width*divisions)/1000 # in metres

        st.subheader('Carrier Calculations')
        
        carrier_lengths = 0
        no_carriers_per_piece = []
        
        centre_gaps_per_piece, no_carriers_per_piece = self.carrier_calculation(
            CARRIER_MAX_GAP,
            CARRIER_END_GAP,
            length_combination,
            carrier_lengths,
            no_carriers_per_piece
        )

        carrier_distances_per_piece = self.calculate_carrier_distances(
            CARRIER_END_GAP,
            centre_gaps_per_piece, 
            no_carriers_per_piece
        )
        # carrier divisions: sum(no_carriers_per_piece)
        # total carrier height: height * divisions
        # number of 3000mm carrier pieces required: total carrier height / carrier divisions

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

        nuts_bolts_cnt = divisions * total_carrier_divisions

        st.subheader("Nuts & Bolts")
        st.write('Nuts & Bolts needed: {}'.format(nuts_bolts_cnt))
        st.write('Self-drilling screw: {}'.format(total_carrier_length/300))

        joining_pieces = (len(length_combination)-1) * divisions
        st.subheader("Joining Pieces")
        st.write("Total Joining Pieces: {}".format(joining_pieces))

        st.subheader("End Caps")
        caps = ["L", "Inverse L"]

        if self.orientation == 'Horizontal':
            left_key = f'left_{self.window}'
            left = st.radio("Left end caps required?", ("Yes", "No"), key=left_key)
            st.write("Total left end caps: {}".format(divisions if left=="Yes" else 0))

            right_key = f'right_{self.window}'
            right = st.radio("Right end caps required?", ("Yes", "No"), key=right_key)
            st.write("Total right end caps: {}".format(divisions if right=="Yes" else 0))

            top = False
            bottom = False
        elif self.orientation == 'Vertical':
            top_key = f'top_{self.window}'
            top = st.radio("Top end caps required?", ("Yes", "No"), key=self.window+3)

            top_orientation_key = f'top_orientation_{self.window}'
            top_orientation = st.radio("Top end cap orientation?", caps, key=top_key)

            st.write('Total {} top end caps required: {}'.format(
                top_orientation,
                divisions if top == "Yes" else 0
            ))

            bottom_key = f'bottom_{self.window}'
            bottom = st.radio("Bottom end caps required?", ("Yes", "No"), key=bottom_key)

            st.write('Total {} bottom end caps required: {}'.format(
                caps[caps.index(top_orientation)-1],
                divisions if bottom == "Yes" else 0
            ))
            left = False
            right = False

        # output_csv = add_to_data(output_csv, rows=[
        #     ['Width (mm)', width if orientation=="Horizontal" else height],
        #     ['Height (mm)', height if orientation=="Horizontal" else width],
        #     ['Orientation', orientation],
        #     ['Pitch (mm)', pitch],
        #     ['Area (ft2)', ((width*height)/(304.8 * 304.8))], # 304.8 * 304.8 --> convert to ft2
        #     ['Divisions', divisions],
        #     ['Total Product Length (m)', total_grille_length],
        #     ['Total Carrier Length (m)', total_carrier_length/1000],
        #     ['Total Covering Plate Length (m)', total_carrier_length/1000],
        #     ['Product Weight (kg)', total_grille_length*0.412],
        #     ['Carrier+Covering Plate Weight (kg)', total_carrier_length*0.427],
        #     ['Nuts/Bolts Weight (kg)', nuts_bolts_cnt*0.02],
        #     ['Nuts/Bolts/Washers (pcs)', nuts_bolts_cnt],
        #     ['Self-drilling screws (pcs)', total_carrier_length/300],
        #     ['Joining Pieces (pcs)', joining_pieces],
        #     ['Right End Cap (pcs)', divisions if right else 0],
        #     ['Left End Cap (pcs)', divisions if left else 0],
        #     ['Top End Cap (pcs)', divisions if top else 0],
        #     ['Top End Cap Orientation', top_orientation if top else pd.NA],
        #     ['Bottom End Cap (pcs)', divisions if bottom else 0],
        #     ['Bottom End Cap Orientation', caps[caps.index(top_orientation)-1] if top else pd.NA]
        # ])

        results = pd.DataFrame({
            'Width (mm)': [self.width if self.orientation == "Horizontal" else self.height],
            'Height (mm)': [self.height if self.orientation == "Horizontal" else self.width],
            'Orientation': [self.orientation],
            'Pitch (mm)': [self.pitch],
            'Area (ft2)': [((self.width * self.height) / (304.8 * 304.8))],
            'Divisions': [divisions],
            'Total Product Length (m)': [total_grille_length],
            'Total Carrier Length (m)': [total_carrier_length / 1000],
            'Total Covering Plate Length (m)': [total_carrier_length / 1000],
            'Product Weight (kg)': [total_grille_length * 0.412],
            'Carrier+Covering Plate Weight (kg)': [total_carrier_length * 0.427],
            'Nuts/Bolts Weight (kg)': [nuts_bolts_cnt * 0.02],
            'Nuts/Bolts/Washers (pcs)': [nuts_bolts_cnt],
            'Self-drilling screws (pcs)': [total_carrier_length / 300],
            'Joining Pieces (pcs)': [joining_pieces],
            'Right End Cap (pcs)': [divisions if right else 0],
            'Left End Cap (pcs)': [divisions if left else 0],
            'Top End Cap (pcs)': [divisions if top else 0],
            'Top End Cap Orientation': [top_orientation if top else pd.NA],
            'Bottom End Cap (pcs)': [divisions if bottom else 0],
            'Bottom End Cap Orientation': [caps[caps.index(top_orientation) - 1] if top else pd.NA]
        })

        # st.subheader('Final Calculations:')
        # st.dataframe(output_csv)

        # # Add a download button
        # csv_file = output_csv.to_csv(index=False)
        # st.download_button(label='Download CSV', data=csv_file, file_name='sample_data.csv', mime='text/csv')

        return results