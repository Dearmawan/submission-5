import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, call
import os
from datetime import datetime
import gspread.exceptions
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging

from utils.load import load_to_csv, load_to_postgres, load_to_gsheets

@pytest.fixture
def sample_clean_dataframe():
    data = {
        'title': ['Test Product 1', 'Test Product 2'],
        'price': [160000, 320000],
        'rating': [4.5, 4.8],
        'colors': [3, 2],
        'size': ['L', 'M'],
        'gender': ['Male', 'Female'],
        'timestamp': [datetime(2023, 1, 1, 10, 0, 0), datetime(2023, 1, 1, 11, 0, 0)]
    }
    df = pd.DataFrame(data)
    return df.astype({
        'title': 'string',
        'price': 'int',
        'rating': 'float',
        'colors': 'int',
        'size': 'string',
        'gender': 'string',
        'timestamp': 'datetime64[ns]'
    })

@patch('utils.load.pd.DataFrame.to_csv')
def test_load_to_csv_success(mock_to_csv, sample_clean_dataframe):
    filename = "test_output.csv"
    result = load_to_csv(sample_clean_dataframe, filename)

    assert result is True
    mock_to_csv.assert_called_once_with(filename, index=False, encoding='utf-8')

def test_load_to_csv_actual_file(tmp_path, sample_clean_dataframe):
    filename = tmp_path / "test_output.csv"
    result = load_to_csv(sample_clean_dataframe, str(filename))

    assert result is True
    assert filename.exists()
    df_read = pd.read_csv(filename)
    assert list(df_read.columns) == list(sample_clean_dataframe.columns)
    assert len(df_read) == len(sample_clean_dataframe)

@patch('utils.load.pd.DataFrame.to_csv', side_effect=IOError("Disk full"))
def test_load_to_csv_io_error(mock_to_csv, sample_clean_dataframe, caplog):
    filename = "test_output.csv"
    with caplog.at_level(logging.ERROR):
        result = load_to_csv(sample_clean_dataframe, filename)

    assert result is False
    assert "Error writing to CSV file" in caplog.text
    assert "Disk full" in caplog.text

def test_load_to_csv_empty_df(caplog):
    empty_df = pd.DataFrame(columns=['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp'])
    with caplog.at_level(logging.WARNING):
        result = load_to_csv(empty_df, "empty.csv")
    assert result is False
    assert "DataFrame is empty. Skipping CSV load." in caplog.text

@patch('utils.load.create_engine')
def test_load_to_postgres_success(mock_create_engine, sample_clean_dataframe):
    mock_engine = MagicMock()
    mock_connection = mock_engine
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
        db_conn_str = "postgresql://user:pass@host:port/db"
        table_name = "test_products"
        if_exists = 'append'

        result = load_to_postgres(sample_clean_dataframe, db_conn_str, table_name, if_exists=if_exists)

        assert result is True
        mock_create_engine.assert_called_once_with(db_conn_str)
        mock_engine.connect.assert_called_once()
        mock_to_sql.assert_called_once_with(
            table_name,
            con=mock_engine,  # Ubah ke mock_engine karena engine langsung digunakan
            if_exists=if_exists,
            index=False,
            chunksize=1000
        )

@patch('utils.load.create_engine', side_effect=ImportError("No module named psycopg2"))
def test_load_to_postgres_import_error(mock_create_engine, sample_clean_dataframe, caplog):
    db_conn_str = "postgresql://user:pass@host:port/db"
    table_name = "test_products"
    if_exists = 'append'
    with caplog.at_level(logging.ERROR):
        result = load_to_postgres(sample_clean_dataframe, db_conn_str, table_name, if_exists=if_exists)
    assert result is False
    assert "SQLAlchemy or psycopg2 not installed correctly" in caplog.text

@patch('utils.load.create_engine')
def test_load_to_postgres_db_error(mock_create_engine, sample_clean_dataframe, caplog):
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = OperationalError("connection failed", {}, None)
    mock_create_engine.return_value = mock_engine

    db_conn_str = "postgresql://user:pass@host:port/db"
    table_name = "test_products"
    if_exists = 'append'

    with caplog.at_level(logging.ERROR):
        result = load_to_postgres(sample_clean_dataframe, db_conn_str, table_name, if_exists=if_exists)

    assert result is False
    assert "An error occurred during PostgreSQL load" in caplog.text
    assert "connection failed" in caplog.text

def test_load_to_postgres_no_conn_string(sample_clean_dataframe, caplog):
    table_name = "test_products"
    if_exists = 'append'
    with caplog.at_level(logging.ERROR):
        result = load_to_postgres(sample_clean_dataframe, None, table_name, if_exists=if_exists)
    assert result is False
    assert "Database connection string is not provided" in caplog.text

def test_load_to_postgres_empty_df(caplog):
    empty_df = pd.DataFrame(columns=['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp'])
    with caplog.at_level(logging.WARNING):
        result = load_to_postgres(empty_df, "dummy_conn", "test_table")
    assert result is False
    assert "DataFrame is empty. Skipping PostgreSQL load." in caplog.text

@patch('utils.load.gspread.authorize')
@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.os.path.exists')
def test_load_to_gsheets_success(mock_exists, mock_creds_from_file, mock_authorize, sample_clean_dataframe):
    mock_exists.return_value = True

    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()

    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    spreadsheet_id = "dummy_sheet_id"
    creds_path = "dummy_creds.json"
    worksheet_name = "TestSheet"

    result = load_to_gsheets(sample_clean_dataframe, spreadsheet_id, creds_path, worksheet_name=worksheet_name)

    assert result is True
    mock_exists.assert_called_once_with(creds_path)
    mock_creds_from_file.assert_called_once_with(creds_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    mock_authorize.assert_called_once_with(mock_creds_from_file.return_value)
    mock_client.open_by_key.assert_called_once_with(spreadsheet_id)
    mock_spreadsheet.worksheet.assert_called_once_with(worksheet_name)
    mock_worksheet.clear.assert_called_once()

    df_for_upload = sample_clean_dataframe.copy()
    if 'timestamp' in df_for_upload.columns:
        df_for_upload['timestamp'] = df_for_upload['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df_for_upload = df_for_upload.fillna('')
    expected_data = [df_for_upload.columns.tolist()] + df_for_upload.values.tolist()

    mock_worksheet.update.assert_called_once_with(expected_data, 'A1')

@patch('utils.load.os.path.exists', return_value=False)
@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.gspread.authorize')
def test_load_to_gsheets_no_creds_file(mock_authorize, mock_creds_from_file, mock_exists, sample_clean_dataframe, caplog):
    spreadsheet_id = "dummy_id"
    creds_path = "nonexistent.json"
    worksheet_name = "TestSheet"
    with caplog.at_level(logging.ERROR):
        result = load_to_gsheets(sample_clean_dataframe, spreadsheet_id, creds_path, worksheet_name=worksheet_name)
    assert result is False
    assert f"Credentials file not found at {creds_path}" in caplog.text
    mock_exists.assert_called_once_with(creds_path)
    mock_creds_from_file.assert_not_called()
    mock_authorize.assert_not_called()

@patch('utils.load.gspread.authorize')
@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.os.path.exists', return_value=True)
def test_load_to_gsheets_api_error(mock_exists, mock_creds_from_file, mock_authorize, sample_clean_dataframe, caplog):
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = '{"error": {"message": "Permission denied"}}'
    mock_spreadsheet.worksheet.side_effect = gspread.exceptions.APIError(mock_response)

    spreadsheet_id = "dummy_id"
    creds_path = "creds.json"
    worksheet_name = "TestSheet"
    with caplog.at_level(logging.ERROR):
        result = load_to_gsheets(sample_clean_dataframe, spreadsheet_id, creds_path, worksheet_name=worksheet_name)
    assert result is False

    assert "Google Sheets API error: Status 403, Details: " in caplog.text
    assert "Permission denied" in caplog.text

def test_load_to_gsheets_empty_df(caplog):
    empty_df = pd.DataFrame(columns=['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp'])
    with caplog.at_level(logging.WARNING):
        result = load_to_gsheets(empty_df, "dummy_id", "creds.json", "TestSheet")
    assert result is False
    assert "DataFrame is empty. Skipping Google Sheets load." in caplog.text

def test_load_to_gsheets_missing_args(sample_clean_dataframe, caplog):
    with caplog.at_level(logging.ERROR):
        result = load_to_gsheets(sample_clean_dataframe, None, "creds.json", "TestSheet")
    assert result is False
    assert "Google Sheets ID, credentials path, or worksheet name not provided." in caplog.text

    caplog.clear()
    with caplog.at_level(logging.ERROR):
        result = load_to_gsheets(sample_clean_dataframe, "dummy_id", None, "TestSheet")
    assert result is False
    assert "Google Sheets ID, credentials path, or worksheet name not provided." in caplog.text

    caplog.clear()
    with caplog.at_level(logging.ERROR):
        result = load_to_gsheets(sample_clean_dataframe, "dummy_id", "creds.json", None)
    assert result is False
    assert "Google Sheets ID, credentials path, or worksheet name not provided." in caplog.text