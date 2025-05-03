import pandas as pd

def clean_data(df):
    """Clean and transform the scraped data."""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Filter out invalid products
    dirty_patterns = {
        "Title": ["Unknown Product"],
        "Rating": ["Invalid Rating", "Not Rated"],
        "Price": ["Price Unavailable", None]
    }
    
    # Filter rows with invalid data
    df = df[~df['Title'].isin(dirty_patterns['Title'])]
    df = df[~df['Rating'].isin(dirty_patterns['Rating'])]
    df = df[~df['Price'].isin(dirty_patterns['Price'])]
    
    # Drop rows with any remaining null values
    df = df.dropna()
    
    # Convert price to float and then to IDR (exchange rate 16000)
    df['Price'] = df['Price'].astype(float) * 16000
    
    # Clean rating - extract numeric value
    df['Rating'] = df['Rating'].str.extract(r'(\d+\.?\d*)').astype(float)
    
    # Clean colors - extract numeric value
    df['Colors'] = df['Colors'].str.extract(r'(\d+)').astype(int)
    
    # Clean size - already cleaned during extraction
    
    # Clean gender - already cleaned during extraction
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df