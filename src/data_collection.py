import yfinance as yf
import pandas as pd
from pathlib import Path

TICKERS = [
    "NVDA", "AMD", "AVGO", "TSM", "ARM",
    "PLTR", "MSFT", "SMH", "SOXX", "QQQ", "SPY"
]

START_DATE = "2020-01-01"
OUTPUT_PATH = Path("data/raw/stock_prices.csv")


def download_stock_data():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = yf.download(
        TICKERS,
        start=START_DATE,
        auto_adjust=True,
        progress=False
    )

    prices = data["Close"].dropna(axis=1, how="all").dropna()
    if prices.empty or prices.shape[1] < 2:
        raise RuntimeError("Download did not return complete prices for at least two assets. Try again later.")
    prices.index.name = "Date"
    prices.to_csv(OUTPUT_PATH)

    print(f"Saved stock price data to {OUTPUT_PATH}")


if __name__ == "__main__":
    download_stock_data()
