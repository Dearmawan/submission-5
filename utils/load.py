import pandas as pd
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import gspread
from google.oauth2.service_account import Credentials

def load_to_csv(df, filename):
    """Save DataFrame to a CSV file."""
    if df.empty:
        logging.warning("DataFrame is empty. Skipping CSV load.")
        return False

    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Successfully saved data to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error writing to CSV file {filename}: {str(e)}")
        return False

def load_to_postgres(df, db_conn_str=None, table_name="products", if_exists='append'):
    """Load DataFrame to PostgreSQL database."""
    if df.empty:
        logging.warning("DataFrame is empty. Skipping PostgreSQL load.")
        return False

    if not db_conn_str:
        logging.error("Database connection string is not provided.")
        return False

    try:
        engine = create_engine(db_conn_str)
        with engine.connect():
            df.to_sql(table_name, con=engine, if_exists=if_exists, index=False, chunksize=1000)
        logging.info(f"Successfully loaded data to PostgreSQL table {table_name}")
        return True
    except ImportError as e:
        logging.error(f"SQLAlchemy or psycopg2 not installed correctly: {str(e)}")
        return False
    except SQLAlchemyError as e:
        logging.error(f"An error occurred during PostgreSQL load: {str(e)}")
        return False

def load_to_gsheets(df, spreadsheet_id=None, creds_path="google-sheets-api.json", worksheet_name="Sheet1"):
    """Load DataFrame to Google Sheets."""
    if df.empty:
        logging.warning("DataFrame is empty. Skipping Google Sheets load.")
        return False

    if not all([spreadsheet_id, creds_path, worksheet_name]):
        logging.error("Google Sheets ID, credentials path, or worksheet name not provided.")
        return False

    if not os.path.exists(creds_path):
        logging.error(f"Credentials file not found at {creds_path}")
        return False

    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        worksheet.clear()

        df_for_upload = df.copy()
        if 'timestamp' in df_for_upload.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_for_upload['timestamp']):
                df_for_upload['timestamp'] = pd.to_datetime(df_for_upload['timestamp'], errors='coerce')

            df_for_upload['timestamp'] = df_for_upload['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        df_for_upload = df_for_upload.fillna('')

        data_to_upload = [df_for_upload.columns.tolist()] + df_for_upload.values.tolist()
        worksheet.update(data_to_upload, 'A1')

        logging.info(f"Successfully loaded data to Google Sheets: {spreadsheet_id}, worksheet: {worksheet_name}")
        return True
    except gspread.exceptions.APIError as e:
        error_details = e.response.text if hasattr(e.response, 'text') else str(e)
        logging.error(f"Google Sheets API error: Status {e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'}, Details: {error_details}")
        return False
    except Exception as e:
        logging.error(f"An error occurred during Google Sheets load: {str(e)}")
        return False