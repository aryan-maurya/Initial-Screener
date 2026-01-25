import yfinance as yf
import pandas as pd

# 1. Fetch data (Using a buffer of 5 days to ensure we have enough candles)
df = yf.download("RELIANCE.NS", period="10d", interval="15m", auto_adjust=True, progress=False)

# 2. Convert Timezone & Filter Market Hours
df.index = df.index.tz_convert('Asia/Kolkata')
df_ist = df.between_time('09:15', '15:30')

# 3. Print the last 15 rows
print("\n--- Last 15 Rows (IST) ---")
print(df_ist.tail(30))