import pandas as pd
import streamlit as st
import modules.optimizer as optimizer
import sys

STANDARD_PRODUCT_LENGTHS = [3050, 3650, 4550]
CARRIER_TYPES = {
    'Grille': 'Carrier',
    'Aerofoil': 'Carrier',
    'Cottal': 'Aluminum Pipe',
    'Fluted': 'Carrier',
    'S_Louver_1': 'Carrier',
    'S_Louver_2': 'Carrier',
    'C-Louvers': 'Carrier',
    'Rectangular Louvers': 'Carrier'
    }
CARRIER_LENGTHS = {
        'Grille': 3000,
        'Aerofoil': 3000,
        'Cottal': 3000,
        'Fluted': 3000,
        'S_Louver_1': 133.7,
        'S_Louver_2': 115.3,
        'C-Louvers': 3000,
        'Rectangular Louvers': 3000
    }


def run(
        product,
        width,
        height,
        pitch,
        divisions,
        orientation,
        wastage,
        window,
    ):

    # inventory = pd.read_csv('modules/inventory.csv')
    # curr_inv = optimizer.filter_inv(
    #     inventory,
    #     product
    # ), divisions)
    # cnts = optimizer.find_counts(curr_inv)

    cnts = {}
    for i in STANDARD_PRODUCT_LENGTHS:
        cnts[i] = sys.maxsize
    possible_lengths = optimizer.find_combinations(
        width,
        STANDARD_PRODUCT_LENGTHS,
        cnts,
        divisions,
        wastage
    )

    strs = [
        'Option {num}: {option}'.format(
            num=opt+1,
            option=possible_lengths[opt]
        )
        for opt in range(len(possible_lengths))
    ]
    wastages = [
        (sum(possible_lengths[opt])-width)
        for opt in range(len(possible_lengths))
    ]

    st.write('Number of total divisions: ', divisions)

    for opt in range(len(possible_lengths)):

        st.write(strs[opt])
        st.write('Wastage: {}'.format(wastages[opt]))
        st.write('total: {}\n'.format(sum(possible_lengths[opt])))

    strs.append('Add Custom')
    st.subheader('Product Breakdown')
    option_key = f'option_{window}'
    selected_option = st.selectbox('Select an option', strs, key=option_key)

    if selected_option == 'Add Custom':
        num_pieces_key = f'num_pieces_key_{window}'
        num_pieces_custom = st.number_input(
            'Enter number of product lengths in this combination:',
            key=num_pieces_key,
            step=1
        )
        combination = []
        for i in range(int(num_pieces_custom)):
            custom_piece_key = f'custom_piece_key_{window}_{i}'
            piece_length = st.number_input(
                'Enter length for piece {} in mm'.format(i+1),
                key=custom_piece_key
            )
            combination.append(piece_length)
        st.write(combination)
    else:
        combination = possible_lengths[strs.index(selected_option)]
        wastage = wastages[strs.index(selected_option)]

    length_combination = []

    for i in range(len(combination)):
        comb_key = f'comb_key_{i}_{window}'
        num = st.number_input('Usable length from the {}mm piece:'.format(
            combination[i]),
            min_value=combination[i]-wastage,
            max_value=combination[i],
            key=comb_key
        )
        length_combination.append(num)

    if sum(length_combination) != width:
        st.error(f"Error: Lengths should total {width}")

    st.subheader('Number of pieces required for each length:')
    total_product_pieces = []
    for combo in set(length_combination):
        length_cnt_per_division = length_combination.count(combo)
        product_cnt_per_length = divisions*(length_cnt_per_division)
        total_product_pieces.append(product_cnt_per_length)
        st.write(
            '{len} mm --> {length_cnt_per_division} piece(s) \
            per division * {divisions} divisions = {number} pieces'.format(
                len=combo,
                length_cnt_per_division=length_cnt_per_division,
                divisions=divisions,
                number=product_cnt_per_length
            )
        )

    total_product_length = (width*divisions)/1000

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

    carrier_distances_per_piece = [
        [round(num, 2) for num in sublist]
        for sublist in carrier_distances_per_piece
    ]

    st.write('Length option chosen: {}'.format(length_combination))

    st.write("{} divisions for each piece in the chosen option:".format(
        CARRIER_TYPES[product]
    ))

    carrier_combinations = {}
    for i in range(len(length_combination)):
        carrier_combinations['{}mm'.format(
            length_combination[i]
        )] = [carrier_distances_per_piece[i]]

    carrier_table = pd.DataFrame.from_dict(carrier_combinations)

    total_carrier_divisions = sum(no_carriers_per_piece)
    total_carrier_length = total_carrier_divisions*width

    carrier_table['Total {} divisions'.format(
        CARRIER_TYPES[product]
    )] = total_carrier_divisions

    carrier_table['Total length of {x} required'.format(
        x=CARRIER_TYPES[product].lower()
    )] = '{divs} * {l} = {tcl} mm'.format(
        divs=total_carrier_divisions,
        l=height,
        tcl=total_carrier_length
    )

    carrier_table[
        'Number of {}mm {} required'.format(
            CARRIER_LENGTHS[product],
            CARRIER_TYPES[product].lower()+'s'
        )
    ] = round(total_carrier_length/CARRIER_LENGTHS[product], 2)

    # st.write(carrier_table.T.rename_axis('Item'))
    st.write(carrier_table)

    vars = {
        'length_combination': length_combination,
        'total_product_length': total_product_length,
        'total_carrier_length': total_carrier_length,
        'total_carrier_divisions': total_carrier_divisions
    }

    return vars
