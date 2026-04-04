import requests
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import yfinance as yf

API_KEY = "d772739r01qtg3nfc4ngd772739r01qtg3nfc4o0"

def get_company_info(symbol):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={API_KEY}"

    response = requests.get(url)
    data = response.json()

    return data

@lru_cache(maxsize=20)
def get_stock_data(symbol):
    try:
        df = yf.download(symbol, period="1y")

        if df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.reset_index(inplace=True)
        return df

    except Exception as e:
        print("YFINANCE ERROR:", e)
        return pd.DataFrame()