import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pandas.testing import assert_frame_equal

from utils.transform import transform_data

@pytest.fixture
def raw_dataframe():
    # Data mentah tidak perlu diubah
    data = {
        'title': ['Cool T-Shirt', 'Awesome Jacket', 'Unknown Product', 'Cool T-Shirt', 'Weird Pants', None, 'Hat'],
        'price': ['$25.50', 'Price Unavailable', '$100', '$25.50', '$12.34', '$50', ''],
        'rating': ['4.5 / 5', 'Invalid Rating', '4.8 / 5', '4.5 / 5', '3 / 5', None, '5 / 5'],
        'colors': ['3 Colors', '2 Colors', '0 Colors', '3 Colors', '1 Color', '5 Colors', 'Unknown Colors'],
        'size': ['Size: L', 'Size: M', 'Size: XL', 'Size: L', 'Size: Unknown', 'Size: S', ''],
        'gender': ['Gender: Male', 'Gender: Female', 'Gender: Unisex', 'Gender: Male', 'Gender: Unknown', None, ''],
        'timestamp': ['2023-01-01 12:00:00'] * 7
    }
    df = pd.DataFrame(data)
    return df

@pytest.fixture
def expected_cleaned_dataframe():
    # Data nilai yang diharapkan sudah benar
    data = {
        'title': ['Cool T-Shirt', 'Weird Pants'],
        'price': [int(25.50 * 16000), int(12.34 * 16000)], # 408000, 197440
        'rating': [4.5, 3.0],
        'colors': [3, 1],
        'size': ['L', 'Unknown'],
        'gender': ['Male', 'Unknown'],
        'timestamp': ['2023-01-01 12:00:00'] * 2
    }
    df = pd.DataFrame(data)
    
    return df.astype({
        'title': str,     
        'price': int,     
        'rating': float,  
        'colors': int,    
        'size': str,      
        'gender': str,    
        'timestamp': str  
    })
   

def test_transform_data(raw_dataframe, expected_cleaned_dataframe):
    cleaned_df = transform_data(raw_dataframe.copy())

    # Reset index agar konsisten
    cleaned_df = cleaned_df.reset_index(drop=True)
    expected_df = expected_cleaned_dataframe.reset_index(drop=True)

    # Gunakan assert_frame_equal seperti sebelumnya
    # check_dtype=False masih relevan karena tipe object vs int/float
    assert_frame_equal(
        cleaned_df,
        expected_df,
        check_dtype=False,
        check_exact=False,
        rtol=1e-5
    )

    
    assert cleaned_df['title'].notna().all()
    assert cleaned_df['price'].notna().all()
    assert cleaned_df.duplicated().sum() == 0


def test_transform_data_empty_input():
    empty_df = pd.DataFrame(columns=['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp'])
    transformed_df = transform_data(empty_df.copy())
    assert transformed_df.empty

def test_transform_data_invalid_data():
    data = {
        'title': ['Unknown Product'],
        'price': ['Price Unavailable'],
        'rating': ['Invalid Rating'],
        'colors': ['0 Colors'],
        'size': ['Size: Unknown'],
        'gender': ['Gender: Unknown'],
        'timestamp': ['2023-01-01 12:00:00']
    }
    df = pd.DataFrame(data)
    transformed_df = transform_data(df.copy())
    assert transformed_df.empty