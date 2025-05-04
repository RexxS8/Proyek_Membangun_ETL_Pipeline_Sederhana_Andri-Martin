from utils.load import save_to_google_sheets
import pandas as pd

df = pd.DataFrame({'Test': [1,2,3]})
save_to_google_sheets(df, '1Exleh2grb0y5WwKs9lNcKo4ICigrauYKKTScCwYf0aA', 'google-sheets-api.json')