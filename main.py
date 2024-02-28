import streamlit as st
import pandas as pd
import importlib

from grille_calculator import GrilleCalculator
from aerofoil_calculator import AerofoilCalculator

st.title("Vibrant Technik Material Calculator")

PRODUCT = st.selectbox('Select a product:', ['Grille', 'Aerofoil', 'S-Louver', 'C-Louver', 'Cottal'])
GRILLE_COLUMNS = [
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
    ]
CALCULATOR_MAPPING = {
        'Grille': GrilleCalculator,
        'Aerofoil': AerofoilCalculator
    }


def get_num_windows():
    num_windows = st.number_input('Enter number of windows:', min_value=1, value=1, step=1)
    return num_windows


def run(product, num_windows, **kwargs):
    output = pd.DataFrame()

    for window in range(num_windows):
        window_expander = st.expander(f'Window {window + 1}', expanded=False)

        with window_expander:
            orientation_key = f'orientation_{window}'
            orientation = st.radio(f'Select orientation for Window {window + 1}:', ('Horizontal', 'Vertical'), key=orientation_key)

            width_key = f'width_{window}'
            width = st.number_input(f'Width for Window {window + 1}:', min_value=150, value=6000, key=width_key)

            height_key = f'height_{window}'
            height = st.number_input(f'Height for Window {window + 1}:', min_value=0, value=3250, key=height_key)

            if orientation == 'Vertical':
                width, height = height, width

            pitch_key = f'pitch_{window}'
            pitch = st.number_input(f'Pitch for Window {window + 1}:', min_value=0, max_value=height, value=50, key=pitch_key)

            wastage_key = f'wastage_{window}'
            allowed_wastage = st.number_input(f'Buffer Wastage for Window {window + 1}:', min_value=0, value=100, key=wastage_key)

            calculator_class = CALCULATOR_MAPPING[product]
            
            if calculator_class == GrilleCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    pitch,
                    allowed_wastage,
                    window
                )
            elif calculator_class == AerofoilCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    pitch,
                    allowed_wastage,
                    window,
                    kwargs['af_type'],
                    kwargs['installation'],
                    fixing_method=kwargs.get('fixing_method')
                )
            df = calculator.run()
            output = pd.concat([output, df], axis=0)
            st.subheader(f'Results for Window {window + 1}:')
            st.write(df)

    st.write(output)


if PRODUCT == 'Grille':
    num_windows = st.number_input('Number of areas:', min_value=1, value=1, step=1)
    run(PRODUCT, num_windows)
elif PRODUCT == 'Aerofoil':
    af_type = st.selectbox('Aerofoil type:', [
          'AF 60',
          'AF 100',
          'AF 150',
          'AF 200',
          'AF 250',
          'AF 300',
          'AF 400',
    ])
    installation = st.selectbox('Installation method:', [
          'Fixed',
          'Moveable (Manual)',
          'Moveable (Motorized)'
        ])
    if installation == 'Fixed':
        fixing_method = st.selectbox('Fixing Method:', [
            'Fringe End Caps',
            'C-Channel',
            'MS Rod/Slot Cut Pipe',
            'D-Wall Bracket'
        ])
        num_windows = get_num_windows()
        run(PRODUCT,
            num_windows,
            af_type=af_type,
            installation=installation,
            fixing_method=fixing_method
        )
    else:
        num_windows = get_num_windows()
        run(PRODUCT,
            num_windows,
            af_type=af_type,
            installation=installation
        )
