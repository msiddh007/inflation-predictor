import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'merged_data_clean.csv')

# === Load data ===
df = pd.read_csv(DATA_FILE, parse_dates=['date'])
df = df.sort_values('date')

# === Targets ===
targets = {
    'Inflation': 'CPI',
    'Unemployment': 'Unemployment Rate'
}

# === Features: Exclude dates, targets ===
exclude_cols = ['date'] + list(targets.values())
feature_cols = [col for col in df.columns if col not in exclude_cols]

# === Scale features ===
scaler = StandardScaler()
X = scaler.fit_transform(df[feature_cols])

def run_model(df, target_col, feature_names, label):
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.3)

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))

    # Feature importances
    coef_importance = pd.Series(model.coef_, index=feature_names).sort_values(ascending=False)

    print(f"\n📊 {label} Prediction:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  RMSE: {rmse:.4f}\n")
    print(f"🔍 Top Features:\n{coef_importance.head(10)}")

    # === Plotting Predicted vs. Current (Last Year) ===
    test_dates = df['date'].iloc[-len(y_test):].reset_index(drop=True)
    last_date = test_dates.max()
    mask = test_dates >= (last_date - timedelta(days=365))
    recent_dates = test_dates[mask]
    recent_actual = y_test.reset_index(drop=True)[mask]
    recent_preds = pd.Series(preds).reset_index(drop=True)[mask]

    plt.figure(figsize=(10, 6))
    plt.plot(recent_dates, recent_preds, label="Predicted", marker='x')
    plt.plot(recent_dates, recent_actual, label="Current", marker='o')
    plt.title(f"{label} - Predicted vs. Current (Last Year)")
    plt.xlabel('Date')
    plt.ylabel(label)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # === Save Plot ===
    save_dir = os.path.join(BASE_DIR, 'Predicted_vs_Current')
    os.makedirs(save_dir, exist_ok=True)

    file_name = f"{label.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path, dpi=300)
    print(f"✅ Plot saved to: {file_path}")

    plt.close()

# === Run Model ===
run_model(df, targets['Inflation'], feature_cols, label="CPI")
