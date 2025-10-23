import os
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import yfinance as yf

# === Setup ===
FRED_API_KEY = 'be0e147be18716db5ef460415b62aaec'
fred = Fred(api_key=FRED_API_KEY)

# === Output path ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_DIR, 'fred_data.csv')

# === Date range (fetch past 90 days to get monthly data) ===
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# === Define indicators (FRED) ===
indicators = {
    'CPI': 'CPIAUCSL',
    'PPI': 'PPIACO',
    'Unemployment Rate': 'UNRATE',
    'Jobless Claims': 'ICSA',
    'PCE': 'PCEPI',
    'Fed Funds Rate': 'FEDFUNDS',
    '10Y-2Y Spread': 'T10Y2Y',
    '10Y-3M Spread': 'T10Y3M',
    'Oil Price (WTI)': 'DCOILWTICO',
    'USD to EUR': 'DEXUSEU',
}

# === Fetch FRED indicators ===
data_frames = []

for name, code in indicators.items():
    try:
        print(f"📥 Fetching {name} ({code})...")
        series = fred.get_series(code, observation_start=start_date, observation_end=end_date)
        df = series.rename(name).to_frame()
        df.index.name = 'date'
        df.index = pd.to_datetime(df.index)
        data_frames.append(df)
    except Exception as e:
        print(f"⚠️ Failed to fetch {name}: {e}")

# === Merge and clean FRED series ===
if data_frames:
    fred_df = pd.concat(data_frames, axis=1)
    fred_df = fred_df.sort_index()
    fred_df.index = pd.to_datetime(fred_df.index)
    fred_df = fred_df.resample('D').ffill().bfill()
else:
    print("❌ No FRED data fetched.")
    fred_df = pd.DataFrame()

# === Add S&P 500 from Yahoo Finance ===
try:
    print("📥 Fetching S&P 500 (Yahoo Finance)...")
    sp500 = yf.download("^GSPC", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    if isinstance(sp500.columns, pd.MultiIndex):
        sp500.columns = sp500.columns.get_level_values(0)

    sp500 = sp500[['Close']].rename(columns={'Close': 'S&P 500'})
    sp500.index.name = 'date'
    sp500.index = pd.to_datetime(sp500.index)
    sp500 = sp500.resample('D').ffill().bfill()

    full_df = pd.merge(fred_df, sp500, left_index=True, right_index=True, how='outer')
except Exception as e:
    print(f"⚠️ Failed to fetch S&P 500: {e}")
    full_df = fred_df

# === Final filter: last 30 days only ===
final_df = full_df.loc[end_date - timedelta(days=30):end_date]
final_df.to_csv(OUTPUT_FILE)
print(f"✅ Saved full FRED + market dataset (last 30 days) to: {OUTPUT_FILE}")
