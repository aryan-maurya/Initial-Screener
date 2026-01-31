import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO
import time

# Page Config
st.set_page_config(page_title="Nifty 50 OHLC Tracker", layout="wide")

st.title("📈 Nifty 50 Real-Time OHLC Dashboard")
st.write("Fetch latest 15-minute interval data and export to formatted Excel.")

# 1. Manual Ticker List
nifty50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LTIM.NS", "AXISBANK.NS"
]

# Sidebar for controls
st.sidebar.header("Settings")
selected_stocks = st.sidebar.multiselect("Select Stocks to Fetch", nifty50, default=nifty50[:5])
fetch_btn = st.sidebar.button("Fetch Market Data")

if fetch_btn:
    all_data = {}
    progress_bar = st.progress(0)

    # We use a BytesIO object to store the Excel in memory so it can be downloaded
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i, symbol in enumerate(selected_stocks):
            try:
                # Update progress
                progress_bar.progress((i + 1) / len(selected_stocks))

                # Fetch Data
                df = yf.download(symbol, period="5d", interval="15m", auto_adjust=True, progress=False)

                if df.empty:
                    st.warning(f"No data found for {symbol}")
                    continue

                # Clean & Format
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df.index = df.index.tz_convert('Asia/Kolkata')
                df_ist = df.between_time('09:15', '15:30').copy()
                df_ist = df_ist.round(2).reset_index()
                df_ist['Datetime'] = df_ist['Datetime'].dt.strftime('%Y-%m-%d %H:%M')

                # Store for display
                all_data[symbol] = df_ist

                # Write to Excel Sheet
                sheet_name = symbol.replace(".NS", "")
                df_ist.to_excel(writer, sheet_name=sheet_name, index=False)

                # Auto-resize columns in the Excel
                worksheet = writer.sheets[sheet_name]
                for col in worksheet.columns:
                    max_len = max([len(str(cell.value)) for cell in col])
                    worksheet.column_dimensions[col[0].column_letter].width = max_len + 2

            except Exception as e:
                st.error(f"Error fetching {symbol}: {e}")

    st.success("Data Fetched Successfully!")

    # --- DISPLAY DATA ON WEB ---
    st.divider()
    cols = st.columns(len(all_data))

    # Display each stock in a clean expander/tab
    tabs = st.tabs(list(all_data.keys()))
    for i, symbol in enumerate(all_data.keys()):
        with tabs[i]:
            st.subheader(f"{symbol} Latest Candles")
            st.dataframe(all_data[symbol], use_container_width=True)

    # --- DOWNLOAD BUTTON ---
    st.sidebar.divider()
    st.sidebar.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name="Nifty50_Market_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Click 'Fetch Market Data' in the sidebar to begin.")