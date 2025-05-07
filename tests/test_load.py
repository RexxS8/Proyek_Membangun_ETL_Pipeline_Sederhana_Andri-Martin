import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from utils.load import save_to_csv, save_to_postgresql, save_to_google_sheets
import os
import logging

# Test save_to_csv
def test_save_to_csv_success(tmp_path):
    df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})
    filepath = tmp_path / "test.csv"

    result = save_to_csv(df, filepath)
    assert result is True
    assert filepath.exists()

from unittest.mock import patch

def test_save_to_csv_failure(tmp_path):
    df = pd.DataFrame({'A': [1, 2]})
    invalid_path = tmp_path / "invalid_dir" / "test.csv"

    with patch("pathlib.Path.mkdir", side_effect=PermissionError("Mocked permission error")):
        result = save_to_csv(df, invalid_path)
        assert result is False

# Test save_to_postgresql
@patch('pandas.DataFrame.to_sql')
@patch('sqlalchemy.create_engine')
def test_save_to_postgresql_success(mock_create_engine, mock_to_sql):
    df = pd.DataFrame({'A': [1], 'B': ['x']})

    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    result = save_to_postgresql(df, "postgresql://developer:48694404@localhost/productsdb")

    assert result is True
    mock_to_sql.assert_called_once()


@patch('sqlalchemy.create_engine')
def test_save_to_postgresql_failure(mock_create_engine, caplog):
    mock_create_engine.side_effect = Exception("DB error")
    df = pd.DataFrame({'A': [1]})
    result = save_to_postgresql(df, "invalid_connection_string")
    assert result is False
    assert "Database error" in caplog.text

# Test save_to_google_sheets
@patch('utils.load.build')
@patch('utils.load.Credentials.from_service_account_file')
def test_save_to_google_sheets_success(mock_creds, mock_build):
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Simulasi update berhasil
    mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {'updatedCells': 10}

    df = pd.DataFrame({'A': [1], 'B': ['x']})
    result = save_to_google_sheets(df, "spreadsheet_id")

    assert result is True
    mock_service.spreadsheets.return_value.values.return_value.update.assert_called_once()

@patch('utils.load.Credentials.from_service_account_file')
def test_save_to_google_sheets_failure(mock_creds, caplog):
    mock_creds.side_effect = Exception("Auth error")
    df = pd.DataFrame({'A': [1]})
    result = save_to_google_sheets(df, "spreadsheet_id")
    assert result is False
    assert "Error saving to Google Sheets" in caplog.text

def test_save_to_google_sheets_missing_creds(tmp_path, caplog):
    df = pd.DataFrame({'A': [1]})
    result = save_to_google_sheets(df, "spreadsheet_id", "nonexistent.json")
    assert result is False
    assert "Credentials file not found" in caplog.text
