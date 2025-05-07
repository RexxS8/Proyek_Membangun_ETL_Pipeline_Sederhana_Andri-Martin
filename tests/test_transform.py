import pytest
import pandas as pd
import numpy as np
from utils.transform import clean_data
import logging

def test_clean_data_normal_case():
    data = {
        'Title': ['Good', 'Unknown Product', 'Another', None],
        'Price': ['10.00', None, '20.00', 'Price Unavailable'],
        'Rating': ['4.5 / 5', 'Invalid Rating', '3.8 / 5', None],
        'Colors': ['3 Colors', '2 Colors', '1 Color', '1 Color'],
        'Size': ['M', 'L', 'XL', None],
        'Gender': ['Men', 'Women', 'Unisex', 'Unisex'],
        'Timestamp': ['2024-01-01']*4
    }
    df = pd.DataFrame(data)
    
    cleaned = clean_data(df)
    
    # Check that invalid rows were removed (hanya 2 yang valid)
    assert len(cleaned) == 2
    
    # Check data types and transformations
    assert cleaned['Price'].dtype == float
    assert cleaned['Rating'].dtype == float
    assert cleaned['Colors'].dtype == np.int64
    assert cleaned['Size'].dtype == object
    assert cleaned['Gender'].dtype == object
    
    # Check price conversion (10.00 * 16000 = 160000.0)
    assert cleaned.loc[cleaned['Title'] == 'Good', 'Price'].values[0] == 160000.0
    
    # Test untuk product dengan rating valid
    assert cleaned.loc[cleaned['Title'] == 'Another', 'Rating'].values[0] == 3.8

def test_clean_data_empty_input():
    df = pd.DataFrame(columns=['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender'])
    cleaned = clean_data(df)
    assert len(cleaned) == 0

def test_clean_data_currency_conversion():
    df = pd.DataFrame({
        'Title': ['Test'],
        'Price': ['100.00'],
        'Rating': ['5.0 / 5'],
        'Colors': ['2 Colors'],
        'Size': ['M'],
        'Gender': ['Men'],
        'Timestamp': ['2024-01-01']
    })
    cleaned = clean_data(df)
    assert cleaned.loc[0, 'Price'] == 1600000.0  # 100 * 16000

def test_clean_data_rating_extraction():
    df = pd.DataFrame({
        'Title': ['Test'],
        'Price': ['10.00'],
        'Rating': ['4.8 / 5'],
        'Colors': ['1 Color'],
        'Size': ['S'],
        'Gender': ['Women'],
        'Timestamp': ['2024-01-01']
    })
    cleaned = clean_data(df)
    assert cleaned.loc[0, 'Rating'] == 4.8

def test_clean_data_error_handling(caplog):
    with pytest.raises(Exception):
        clean_data("invalid input")
    assert "Unexpected error in clean_data" in caplog.text