import pandas as pd
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_data(df):
    """Clean and transform the scraped data with comprehensive error handling."""
    try:
        if df.empty:
            logger.warning("Empty DataFrame received")
            return df
            
        # Create a copy to avoid SettingWithCopyWarning
        df_clean = df.copy()
        
        # Remove duplicates
        try:
            initial_count = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            removed = initial_count - len(df_clean)
            logger.info(f"Removed {removed} duplicate rows")
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            raise
        
        # Filter out invalid products
        dirty_patterns = {
            "Title": ["Unknown Product"],
            "Rating": ["Invalid Rating", "Not Rated"],
            "Price": ["Price Unavailable", None, np.nan]
        }
        
        try:
            initial_count = len(df_clean)
            for col, patterns in dirty_patterns.items():
                if col in df_clean.columns:
                    df_clean = df_clean[~df_clean[col].isin(patterns)]
            removed = initial_count - len(df_clean)
            logger.info(f"Removed {removed} rows with invalid data")
        except Exception as e:
            logger.error(f"Error filtering invalid data: {e}")
            raise
        
        # Drop rows with any remaining null values
        try:
            initial_count = len(df_clean)
            df_clean = df_clean.dropna()
            removed = initial_count - len(df_clean)
            logger.info(f"Removed {removed} rows with null values")
        except Exception as e:
            logger.error(f"Error removing null values: {e}")
            raise
        
        # Data type conversions with error handling
        try:
            # Price conversion
            df_clean['Price'] = pd.to_numeric(df_clean['Price'], errors='coerce')
            df_clean['Price'] = df_clean['Price'] * 16000  # Convert to IDR
            
            # Rating conversion
            df_clean['Rating'] = df_clean['Rating'].str.extract(r'(\d+\.?\d*)', expand=False)
            df_clean['Rating'] = pd.to_numeric(df_clean['Rating'], errors='coerce')
            
            # Colors conversion
            df_clean['Colors'] = df_clean['Colors'].str.extract(r'(\d+)', expand=False)
            df_clean['Colors'] = pd.to_numeric(df_clean['Colors'], errors='coerce')
            
            # Ensure Size and Gender are strings
            df_clean['Size'] = df_clean['Size'].astype(str)
            df_clean['Gender'] = df_clean['Gender'].astype(str)
            
        except Exception as e:
            logger.error(f"Error during data conversion: {e}")
            raise
        
        # Final validation
        try:
            if df_clean.isnull().values.any():
                logger.warning("Data still contains null values after cleaning")
                df_clean = df_clean.dropna()
        except Exception as e:
            logger.error(f"Error in final validation: {e}")
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Data cleaning complete. Final count: {len(df_clean)} rows")
        return df_clean
        
    except Exception as e:
        logger.error(f"Fatal error in clean_data: {e}")
        raise  # Re-raise to allow handling in calling function