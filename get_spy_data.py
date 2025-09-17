import yfinance as yf
import pandas as pd

# Get SPY data - max period gets all available historical data
spy = yf.Ticker("SPY")
data = spy.history(period="max")

# Display basic info
print(f"Data range: {data.index[0].date()} to {data.index[-1].date()}")
print(f"Total records: {len(data)}")
print(f"Columns: {list(data.columns)}")
print("\nFirst 5 rows:")
print(data.head())
print("\nLast 5 rows:")
print(data.tail())

# Optional: save to CSV
data.to_csv('spy_historical_data.csv')
print("\nData saved to 'spy_historical_data.csv'")