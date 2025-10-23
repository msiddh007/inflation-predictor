import os
import pandas as pd

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')

macro_file = os.path.join(DATA_DIR, 'historical_macro_features.csv')
news_file = os.path.join(DATA_DIR, 'daily_news.csv')
sentiment_file = os.path.join(DATA_DIR, 'daily_news_sentiment.csv')

# Load data
macro = pd.read_csv(macro_file, parse_dates=['date'])
news_sentiment = pd.read_csv(sentiment_file, parse_dates=['date'])

# Merge macro with news sentiment
df = pd.merge(macro, news_sentiment, on='date', how='left')

# Save output
OUTPUT_FILE = os.path.join(DATA_DIR, 'merged_data.csv')
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Merged dataset saved to: {OUTPUT_FILE}")
