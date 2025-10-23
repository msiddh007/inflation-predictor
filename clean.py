import os
import pandas as pd

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

INPUT_FILE = os.path.join(RAW_DIR, 'merged_data.csv')
OUTPUT_FILE = os.path.join(PROCESSED_DIR, 'merged_data_clean.csv')

# === Load data ===
df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
df = df.sort_values('date')

# === Separate sentiment columns (no forward-fill) ===
sentiment_cols = [col for col in df.columns if 'sentiment' in col.lower()]
macro_cols = [col for col in df.columns if col not in sentiment_cols and col != 'date']

# Forward-fill macro/economic indicators
df[macro_cols] = df[macro_cols].ffill().bfill()

# Sentiment columns: missing -> 0
for col in sentiment_cols:
    df[col] = df[col].fillna(0)

# === Save cleaned ===
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Cleaned merged dataset saved to: {OUTPUT_FILE}")
