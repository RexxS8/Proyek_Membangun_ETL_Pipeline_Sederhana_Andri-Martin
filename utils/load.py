import pandas as pd
from sqlalchemy import create_engine
import os

def save_to_csv(df, filename='products.csv'):
    """Save DataFrame to CSV file."""
    try:
        df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def save_to_postgresql(df, db_url, table_name='products'):
    """Save DataFrame to PostgreSQL database."""
    try:
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Data successfully saved to PostgreSQL table {table_name}")
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")

def save_to_google_sheets(df, spreadsheet_id, credentials_file):
    """Save DataFrame to Google Sheets."""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        service = build('sheets', 'v4', credentials=creds)
        
        # Convert DataFrame to list of lists
        values = [df.columns.tolist()] + df.values.tolist()
        
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Data successfully saved to Google Sheets: {result.get('updatedCells')} cells updated.")
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")