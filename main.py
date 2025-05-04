from utils.extract import scrape_products
from utils.transform import clean_data
from utils.load import save_to_csv, save_to_postgresql, save_to_google_sheets
import pandas as pd
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Extract data
        logger.info("Starting data extraction...")
        base_url = "https://fashion-studio.dicoding.dev"
        
        try:
            products = scrape_products(base_url)
            if not products:
                logger.error("No products were scraped. Exiting.")
                return 1
        except Exception as e:
            logger.error(f"Fatal error during extraction: {e}")
            return 1
        
        # Transform data
        logger.info("Transforming data...")
        try:
            df = pd.DataFrame(products)
            cleaned_df = clean_data(df)
            
            if cleaned_df.empty:
                logger.error("No valid data after transformation. Exiting.")
                return 1
                
            logger.info(f"Data cleaning complete. {len(cleaned_df)} valid products found.")
            logger.debug("\n" + str(cleaned_df.info()))
            
        except Exception as e:
            logger.error(f"Fatal error during transformation: {e}")
            return 1
        
        # Load data
        logger.info("Loading data to various repositories...")
        
        # Save to CSV
        if not save_to_csv(cleaned_df, 'products.csv'):
            logger.error("Failed to save to CSV")
            return 1
        
        # Optional: Save to PostgreSQL
        try:
            # db_url = "postgresql://username:password@localhost:5432/database_name"
            # if not save_to_postgresql(cleaned_df, db_url):
            #     logger.error("Failed to save to PostgreSQL")
            #     return 1
            pass
        except Exception as e:
            logger.error(f"Error saving to PostgreSQL: {e}")
        
        # Optional: Save to Google Sheets
        try:
            # spreadsheet_id = "your-spreadsheet-id"
            # credentials_file = "google-sheets-api.json"
            # if not save_to_google_sheets(cleaned_df, spreadsheet_id, credentials_file):
            #     logger.error("Failed to save to Google Sheets")
            #     return 1
            pass
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")
        
        logger.info("ETL process completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())