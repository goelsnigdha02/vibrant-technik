import streamlit as st
import pandas as pd
import math


def get_window_info():
    data = {}
    data['orientation'] = st.radio('Select orientation:', ('Horizontal', 'Vertical'))
    data['width'] = st.number_input('Width:', min_value=150, value=6000)
    data['height'] = st.number_input('Height:', min_value=0, value=3250)

    if data['orientation'] == 'Vertical':
            temp = data['width']
            data['width'] = data['height']
            data['height'] = temp

    data['pitch'] = st.number_input('Pitch:', min_value=0, max_value=data['height'], value=50)
    data['num_pieces'] = data['width']//data['pitch']

    return data


def run_fixed_fringe(data):
     output_df = pd.DataFrame([
          ['Aerofoil Type', data['af_type']],
          ['Width (mm)', data['width'] if data['orientation'] == 'Horizontal' else data['height']],
          ['Height (mm)', data['height'] if data['orientation'] == 'Horizontal' else data['width']],
          ['Pitch (mm)', data['pitch']],
          ['Orientation', data['orientation']],
          ['Total Pieces (pcs)', data['num_pieces']],
          ['{} Fringe End Caps (pcs)'.format(data['af_type']), data['num_pieces']*2],
          ['Black Gypsum Screws (pcs)', data['num_pieces']*4],
          ['Full Threaded Screws (pcs)', data['num_pieces']*4],
          ['PVC Gitty (pcs)', data['num_pieces']*4],
     ])

     st.dataframe(output_df)


def run_fixed_c_channel(data):
    if data['af_type'] == 'AF 60':
        plate_width = st.selectbox('Select C-Plate Width (mm):', [50])
    elif data['af_type'] == 'AF 100':
        plate_width = st.selectbox('Select C-Plate Width (mm):', [50, 75])
    else:
        plate_width = st.selectbox('Select C-Plate Width (mm):', [75, 112])

    plate_length = data['width'] * 2


def run_fixed(data):
    fixing_method = st.selectbox('Fixing Method:', [
        'Fringe End Caps',
        'C-Channel',
        'MS Rod/Slot Cut Pipe',
        'D-Wall Bracket'
    ])

    if fixing_method == 'Fringe End Caps':
        run_fixed_fringe(data)
    elif fixing_method == 'C-Channel':
        run_fixed_c_channel(data)
    

def run():

    installation = st.selectbox('Installation method:', [
          'Fixed',
          'Moveable (Manual)',
          'Moveable (Motorized)'
        ])
    af_type = st.selectbox('Aerofoil type:', [
          'AF 60',
          'AF 100',
          'AF 150',
          'AF 200',
          'AF 2500',
          'AF 300',
          'AF 400',
    ])

    data = get_window_info()
    data['af_type'] = af_type

    if installation == 'Fixed':
         run_fixed(data)


# c-plate aerofoil
# sizes of plate x10
# number of pieces
# length of plate = width*2
# no of 19mm black gypsum screw pieces = num pieces * 4
# full threaded screw = plate length /300
# pvc gitty = full threaded
         

# 
