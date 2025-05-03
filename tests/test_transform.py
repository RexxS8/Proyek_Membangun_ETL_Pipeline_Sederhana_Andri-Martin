import pytest
import pandas as pd
from utils.transform import clean_data

def test_clean_data():
    # Create test data with various issues
    data = {
        'Title': ['Good Product', 'Unknown Product', 'Another Product', None, 'Product with Invalid Rating'],
        'Price': ['100.00', None, '50.00', 'Price Unavailable', '75.00'],
        'Rating': ['4.5 / 5', 'Invalid Rating', '3.8 / 5', None, 'Invalid Rating / 5'],
        'Colors': ['3 Colors', '2 Colors', '1 Color', None, '4 Colors'],
        'Size': ['M', 'L', 'XL', None, 'S'],
        'Gender': ['Men', 'Women', 'Unisex', None, 'Women'],
        'Timestamp': ['2024-01-01'] * 5
    }
    df = pd.DataFrame(data)
    
    cleaned = clean_data(df)
    
    # Check that invalid rows were removed (hanya 2 yang valid)
    assert len(cleaned) == 2
    
    # Check data types and transformations
    assert cleaned['Price'].dtype == float
    assert cleaned['Rating'].dtype == float
    assert cleaned['Colors'].dtype == int
    assert cleaned['Size'].dtype == object
    assert cleaned['Gender'].dtype == object
    
    # Check price conversion (100 * 16000 = 1600000)
    assert cleaned.loc[cleaned['Title'] == 'Good Product', 'Price'].values[0] == 1600000.0
    
    # Test untuk product dengan rating valid
    assert cleaned.loc[cleaned['Title'] == 'Another Product', 'Rating'].values[0] == 3.8

def test_clean_data_empty():
    # Test dengan DataFrame kosong
    df = pd.DataFrame(columns=['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'Timestamp'])
    cleaned = clean_data(df)
    assert len(cleaned) == 0