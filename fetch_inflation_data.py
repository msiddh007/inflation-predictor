import os
import pandas as pd
from datetime import datetime
from fredapi import Fred
import yfinance as yf
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, 'historical_macro_features.csv')

start_date = '2015-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# === FRED Indicators ===
indicators = {
    'CPI': 'CPIAUCSL',
    'PPI': 'PPIACO',
    'Unemployment Rate': 'UNRATE',
    'Jobless Claims': 'ICSA',
    'Nonfarm Payrolls': 'PAYEMS',
    'PCE': 'PCEPI',
    'Fed Funds Rate': 'FEDFUNDS',
    '10Y-2Y Spread': 'T10Y2Y',
    '10Y-3M Spread': 'T10Y3M',
    'Oil Price (WTI)': 'DCOILWTICO',
    'USD to EUR': 'DEXUSEU',
}

frames = []

for name, code in indicators.items():
    print(f"Fetching {name}...")
    data = fred.get_series(code, observation_start=start_date, observation_end=end_date)
    df = data.rename(name).to_frame()
    df.index.name = 'date'
    df.index = pd.to_datetime(df.index)
    frames.append(df)

fred_df = pd.concat(frames, axis=1)
fred_df = fred_df.sort_index().reindex(date_range).ffill()

# === Yahoo Finance Daily Indicators ===
tickers = {
    'S&P 500': '^GSPC',
    'VIX': '^VIX'
}

yahoo_frames = []

for label, symbol in tickers.items():
    data = yf.download(symbol, start=start_date, end=end_date)
    if 'Close' in data.columns:
        data.rename(columns={'Close': label}, inplace=True)
        yahoo_frames.append(data[[label]])
    else:
        print(f"⚠ No data for {label}")


yahoo_df = pd.concat(yahoo_frames, axis=1).reindex(date_range).ffill()

# === Final Dataset ===
df = pd.concat([fred_df, yahoo_df], axis=1)
df.index.name = 'date'
df.to_csv(OUTPUT_FILE)

print(f"✅ Saved historical data to {OUTPUT_FILE}")
