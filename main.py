from utils.extract import scrape_products
from utils.transform import clean_data
from utils.load import save_to_csv, save_to_postgresql, save_to_google_sheets
import pandas as pd

def main():
    # Extract data
    print("Starting data extraction...")
    base_url = "https://fashion-studio.dicoding.dev"
    products = scrape_products(base_url)
    
    if not products:
        print("No products were scraped. Exiting.")
        return
    
    # Transform data
    print("Transforming data...")
    df = pd.DataFrame(products)
    cleaned_df = clean_data(df)
    
    print(f"Data cleaning complete. {len(cleaned_df)} valid products found.")
    print(cleaned_df.info())
    
    # Load data
    print("Loading data to various repositories...")
    
    # Save to CSV
    save_to_csv(cleaned_df)
    
    # Save to PostgreSQL (optional - uncomment and configure if needed)
    # db_url = "postgresql://username:password@localhost:5432/database_name"
    # save_to_postgresql(cleaned_df, db_url)
    
    # Save to Google Sheets (optional - uncomment and configure if needed)
    # spreadsheet_id = "your-spreadsheet-id"
    # credentials_file = "google-sheets-api.json"
    # save_to_google_sheets(cleaned_df, spreadsheet_id, credentials_file)
    
    print("ETL process completed successfully!")

if __name__ == "__main__":
    main()