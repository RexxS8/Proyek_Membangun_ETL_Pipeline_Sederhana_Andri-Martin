import pytest
import pandas as pd
import os
from unittest.mock import patch, Mock
from utils.load import save_to_csv, save_to_postgresql, save_to_google_sheets

def test_save_to_csv(tmp_path):
    df = pd.DataFrame({
        'Title': ['Product A', 'Product B'],
        'Price': [1600000.0, 2400000.0],
        'Rating': [4.5, 3.8],
        'Colors': [3, 2],
        'Size': ['M', 'L'],
        'Gender': ['Men', 'Women'],
        'Timestamp': ['2024-01-01'] * 2
    })
    filepath = tmp_path / "fashion_products.csv"
    
    save_to_csv(df, filepath)
    
    assert filepath.exists()
    loaded = pd.read_csv(filepath)
    assert len(loaded) == 2
    assert loaded['Title'].tolist() == ['Product A', 'Product B']

@patch('sqlalchemy.create_engine')
def test_save_to_postgresql(mock_engine):
    mock_conn = Mock()
    mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
    
    df = pd.DataFrame({
        'Title': ['Product A'],
        'Price': [1600000.0],
        'Rating': [4.5],
        'Colors': [3],
        'Size': ['M'],
        'Gender': ['Men'],
        'Timestamp': ['2024-01-01']
    })
    
    save_to_postgresql(df, "postgresql://user:pass@localhost/db")
    
    # Verify that to_sql was called with correct parameters
    mock_conn.__enter__().to_sql.assert_called_once_with(
        'products',  # table name
        mock_conn.__enter__(),
        if_exists='replace',
        index=False
    )

@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.build')
def test_save_to_google_sheets(mock_build, mock_creds):
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    df = pd.DataFrame({
        'Title': ['Product A'],
        'Price': [1600000.0],
        'Rating': [4.5],
        'Colors': [3],
        'Size': ['M'],
        'Gender': ['Men'],
        'Timestamp': ['2024-01-01']
    })
    
    save_to_google_sheets(df, "spreadsheet_id", "credentials.json")
    
    # Verify the update was called
    mock_service.spreadsheets().values().update.assert_called_once()