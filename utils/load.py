import pandas as pd
from sqlalchemy import create_engine
import os
import logging
from typing import Optional
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_to_csv(df: pd.DataFrame, filename: str = 'products.csv') -> bool:
    """Save DataFrame to CSV file in project root directory."""
    try:
        if df.empty:
            logger.warning("Empty DataFrame provided for CSV export")
            return False
            
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        try:
            # Save directly to project root
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Successfully saved {len(df)} rows to {os.path.abspath(filename)}")
            return True
            
        except PermissionError:
            logger.error(f"Permission denied when writing to {filename}")
            return False
        except OSError as os_err:
            logger.error(f"OS error when writing to {filename}: {os_err}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error saving to CSV: {e}")
        return False

def save_to_postgresql(df: pd.DataFrame, db_url: str, table_name: str = 'products') -> bool:
    """Save DataFrame to PostgreSQL database with comprehensive error handling."""
    try:
        if df.empty:
            logger.warning("Empty DataFrame provided for PostgreSQL export")
            return False
            
        try:
            engine = create_engine(db_url)
            with engine.connect() as connection:
                df.to_sql(
                    table_name,
                    con=connection,
                    if_exists='replace',
                    index=False,
                    method='multi'
                )
            logger.info(f"Successfully saved {len(df)} rows to PostgreSQL table {table_name}")
            return True
            
        except ImportError as import_err:
            logger.error(f"Database driver error: {import_err}")
            return False
        except Exception as db_err:
            logger.error(f"Database error: {db_err}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error saving to PostgreSQL: {e}")
        return False

def save_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str, credentials_file: str = 'google-sheets-api.json') -> bool:
    """Save DataFrame to Google Sheets."""
    try:
        # Validate input
        if not os.path.exists(credentials_file):
            logger.error(f"Credentials file not found: {credentials_file}")
            return False

        # Authenticate with Google Sheets API
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(
            credentials_file, 
            scopes=scopes
        )
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        # Convert dataframe to list of lists
        values = [df.columns.tolist()]
        values.extend(df.values.tolist())

        # Clear existing data first
        sheet.values().clear(
            spreadsheetId=spreadsheet_id,
            range='A:Z'  # Clear all columns
        ).execute()

        # Update spreadsheet
        result = sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()

        logger.info(f"Data saved to Google Sheets. Updated cells: {result.get('updatedCells')}")
        return True

    except HttpError as e:
        logger.error(f"Google Sheets API error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}")
        return False