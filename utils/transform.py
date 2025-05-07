import pandas as pd
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the scraped product data."""
    try:
        if df.empty:
            logger.warning("Received empty DataFrame")
            return df

        df_clean = df.copy()

        # Step 1: Remove duplicates
        try:
            initial_count = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Removed {initial_count - len(df_clean)} duplicate rows")
        except Exception as e:
            logger.error(f"Failed to remove duplicates: {e}")
            raise

        # Step 2: Filter invalid data
        try:
            initial_count = len(df_clean)
            dirty_patterns = {
                "Title": ["Unknown Product"],
                "Rating": ["Invalid Rating", "Not Rated"],
                "Price": ["Price Unavailable", None, np.nan],
            }

            for col, patterns in dirty_patterns.items():
                if col in df_clean.columns:
                    df_clean = df_clean[~df_clean[col].isin(patterns)]

            logger.info(f"Removed {initial_count - len(df_clean)} rows with invalid entries")
        except Exception as e:
            logger.error(f"Failed filtering invalid entries: {e}")
            raise

        # Step 3: Remove nulls
        try:
            initial_count = len(df_clean)
            df_clean = df_clean.dropna()
            logger.info(f"Removed {initial_count - len(df_clean)} rows with null values")
        except Exception as e:
            logger.error(f"Failed to drop nulls: {e}")
            raise

        # Step 4: Type conversions
        try:
            if 'Price' in df_clean.columns:
                df_clean['Price'] = pd.to_numeric(df_clean['Price'], errors='coerce') * 16000  # Convert USD to IDR

            if 'Rating' in df_clean.columns:
                df_clean['Rating'] = df_clean['Rating'].astype(str).str.extract(r'(\d+\.?\d*)', expand=False)
                df_clean['Rating'] = pd.to_numeric(df_clean['Rating'], errors='coerce')

            if 'Colors' in df_clean.columns:
                df_clean['Colors'] = df_clean['Colors'].astype(str).str.extract(r'(\d+)', expand=False)
                df_clean['Colors'] = pd.to_numeric(df_clean['Colors'], errors='coerce')

            for col in ['Size', 'Gender']:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].astype(str)

        except Exception as e:
            logger.error(f"Error during data type conversion: {e}")
            raise

        # Step 5: Final null check
        if df_clean.isnull().values.any():
            logger.warning("Data still contains nulls after processing. Dropping remaining nulls.")
            df_clean = df_clean.dropna()

        df_clean.reset_index(drop=True, inplace=True)
        logger.info(f"Data cleaning completed. Final row count: {len(df_clean)}")
        return df_clean

    except Exception as e:
        logger.error(f"Unexpected error in clean_data: {e}")
        raise
