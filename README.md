# 📈 Inflation Predictor (CPI Forecasting)

The orange line shows the latest released CPI values, while the blue line represents the model’s predicted CPI for the next release period — forecasting ahead of each official update.
Model has an R^2 score of 0.99 and RMSE of less than 0.63


## 🔧 Tools & Libraries
- Python
- pandas & NumPy
- scikit-learn (Linear Regression, StandardScaler)
- matplotlib (for visualization)

## 🧪 Model Summary
- **Model**: Linear Regression
- **Target**: Consumer Price Index (CPI)
- **R² Score**: 0.99
- **RMSE**: 0.63

## 📊 Sample Output

![cpi_predictions](visuals/cpi_predictions.png)

## 🗂️ Features Used
- Oil Price (WTI)
- Fed Funds Rate
- Jobless Claims
- Nonfarm Payrolls
- Yield Spreads (10Y-3M, 10Y-2Y)
- USD to EUR
- Inflation-related sentiment scores

## 🛠 How to Run
1. Clone the repo
2. Install requirements: `pip install -r requirements.txt`
3. Run the model: `python scripts/inflation_predictor.py`

## 📂 Data
Data was preprocessed from multiple sources, including macroeconomic indicators and sentiment metrics.
