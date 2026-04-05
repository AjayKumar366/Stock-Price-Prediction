import requests
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache

API_KEY = "d772739r01qtg3nfc4ngd772739r01qtg3nfc4o0"

# ================= COMPANY INFO =================
def get_company_info(symbol):
    try:
        symbol = symbol.upper().strip()

        # Remove .NS for Finnhub
        if symbol.endswith(".NS"):
            symbol = symbol.replace(".NS", "")

        url = "https://finnhub.io/api/v1/stock/profile2"

        params = {
            "symbol": symbol,
            "token": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if not data or "name" not in data:
            return {
                "name": symbol,
                "finnhubIndustry": "No data available"
            }

        return data

    except Exception as e:
        print("Company info error:", e)
        return {
            "name": symbol,
            "finnhubIndustry": "Error fetching data"
        }


# ================= FINNHUB (US STOCKS) =================
def get_us_stock_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

        params = {
            "range": "1y",
            "interval": "1d"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, params=params, headers=headers)
        data = res.json()

        result = data["chart"]["result"][0]

        timestamps = result["timestamp"]
        quotes = result["indicators"]["quote"][0]

        df = pd.DataFrame({
            "Date": pd.to_datetime(timestamps, unit="s"),
            "Open": quotes["open"],
            "High": quotes["high"],
            "Low": quotes["low"],
            "Close": quotes["close"],
            "Volume": quotes["volume"]
        })

        return df

    except Exception as e:
        print("Yahoo API error:", e)
        return pd.DataFrame()


# ================= NSE (INDIAN STOCKS) =================
def get_nse_data(ticker):
    try:
        ticker = ticker.replace(".NS", "").upper()

        url = f"https://www.nseindia.com/api/chart-databyindex?index={ticker}EQN"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()
        session.headers.update(headers)

        res = session.get(url)
        data = res.json()

        prices = data.get("grapthData", [])

        if not prices:
            return pd.DataFrame()

        df = pd.DataFrame(prices, columns=["timestamp", "Close"])
        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")

        # NSE gives only Close → create OHLC
        df["Open"] = df["Close"]
        df["High"] = df["Close"]
        df["Low"] = df["Close"]
        df["Volume"] = 0

        return df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    except Exception as e:
        print("NSE error:", e)
        return pd.DataFrame()


# ================= MAIN FUNCTION =================
@lru_cache(maxsize=20)
def get_stock_data(ticker):
    ticker = ticker.upper().strip()

    # 🇮🇳 Indian stocks
    if ticker.endswith(".NS"):
        return get_nse_data(ticker)

    # 🇺🇸 US stocks
    else:
        return get_us_stock_data(ticker)