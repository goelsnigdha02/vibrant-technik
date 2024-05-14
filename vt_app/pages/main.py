import streamlit as st
import pandas as pd

from modules.grille_calculator import GrilleCalculator
from modules.aerofoil_calculator import AerofoilCalculator
from modules.cottal_calculator import CottalCalculator
from modules.fluted_calculator import FlutedCalculator
from modules.louvers_calculator import SLouverCalculator, CLouverCalculator, RectangularCalculator
from menu import display_menu

display_menu()

st.title("Vibrant Technik Material Calculator")

PRODUCTS = [
    'Grille',
    'Aerofoil',
    'Cottal',
    'Fluted',
    'S-Louvers',
    'C-Louvers',
    'Rectangular Louvers'
    ]
PRODUCT = st.selectbox('Select a product:', PRODUCTS)
CALCULATOR_MAPPING = {
        'Grille': GrilleCalculator,
        'Aerofoil': AerofoilCalculator,
        'Cottal': CottalCalculator,
        'Fluted': FlutedCalculator,
        'S-Louvers': SLouverCalculator,
        'C-Louvers': CLouverCalculator,
        'Rectangular Louvers': RectangularCalculator
    }
MIN_MAX_PITCH = {
    'Rectangular Louvers': (50, 200),
    'C-Louvers': (80, 100)
}


def get_num_windows():
    num_windows = st.number_input(
        'Enter number of windows:', min_value=1, value=1, step=1
    )
    return num_windows


def run(product, num_windows, **kwargs):
    output = pd.DataFrame()

    for window in range(num_windows):
        window_expander = st.expander(
            f'Window {window + 1}', expanded=False
        )

        with window_expander:
            orientation_key = f'orientation_{window}'
            orientation = st.radio(
                f'Select orientation for Window {window + 1}:',
                ('Horizontal', 'Vertical'),
                key=orientation_key
            )

            width_key = f'width_{window}'
            width = st.number_input(
                f'Width for Window {window + 1}:',
                min_value=150,
                value=6000,
                key=width_key
            )

            height_key = f'height_{window}'
            height = st.number_input(
                f'Height for Window {window + 1}:',
                min_value=0,
                value=3250,
                key=height_key
            )

            if orientation == 'Vertical':
                width, height = height, width

            if product in ['Rectangular Louvers', 'C-Louvers']:
                pitch_key = f'pitch_{window}'
                pitch = st.number_input(
                    f'Pitch for Window {window + 1}:',
                    min_value=MIN_MAX_PITCH[product][0],
                    max_value=MIN_MAX_PITCH[product][1],
                    value=100,
                    key=pitch_key
                )
            elif product not in ['Cottal', 'S-Louvers']:
                pitch_key = f'pitch_{window}'
                pitch = st.number_input(
                    f'Pitch for Window {window + 1}:',
                    min_value=0,
                    max_value=height,
                    value=50,
                    key=pitch_key
                )

            wastage_key = f'wastage_{window}'
            allowed_wastage = st.number_input(
                f'Buffer Wastage for Window {window + 1}:',
                min_value=0,
                value=100,
                key=wastage_key
            )

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
            elif calculator_class == CottalCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    allowed_wastage,
                    window,
                    kwargs['pipe_grade']
                )
            elif calculator_class == FlutedCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    pitch,
                    allowed_wastage,
                    window
                )
            elif calculator_class == SLouverCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    allowed_wastage,
                    window,
                    kwargs['louver_size']
                )
            elif calculator_class == CLouverCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    pitch,
                    allowed_wastage,
                    window
                )
            elif calculator_class == RectangularCalculator:
                calculator = calculator_class(
                    orientation,
                    width,
                    height,
                    pitch,
                    allowed_wastage,
                    window,
                    kwargs['louver_size']
                )
            df = calculator.run()
            output = pd.concat([output, df], axis=0)
            st.subheader(f'Results for Window {window + 1}:')
            st.write(df)

    st.write(output)


if PRODUCT == 'Grille':
    num_windows = st.number_input(
        'Number of areas:', min_value=1, value=1, step=1
    )
    run(PRODUCT, num_windows)
elif PRODUCT == 'Aerofoil':
    af_type = st.selectbox('Aerofoil type:', [
          'AF 60',
          'AF 100',
          'AF 150',
          'AF 200',
          'AF 250',
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
elif PRODUCT == 'Cottal':
    pipe_grade = st.selectbox('Pipe Grade:', [
            '2550 Grade',
            '2538 Grade'
        ])
    num_windows = get_num_windows()
    run(PRODUCT, num_windows, pipe_grade=pipe_grade)
elif PRODUCT == 'Fluted':
    num_windows = get_num_windows()
    run(PRODUCT, num_windows)
elif PRODUCT == 'S-Louvers':
    louver_size = st.selectbox('S-Louvers Size:', [
            '54.5x31.3',
            '84.2x31.3'
        ])
    num_windows = get_num_windows()
    run(PRODUCT, num_windows, louver_size=louver_size)
elif PRODUCT == 'C-Louvers':
    num_windows = get_num_windows()
    run(PRODUCT, num_windows)
elif PRODUCT == 'Rectangular Louvers':
    louver_size = st.selectbox('Rectangular Louvers Size:', [
            '50x75',
            '50x100',
            '50x125'
        ])
    num_windows = get_num_windows()
    run(PRODUCT, num_windows, louver_size=louver_size)
