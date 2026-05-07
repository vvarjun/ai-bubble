import yfinance as yf
import pandas as pd
from pathlib import Path
import time

TICKERS = [
    "NVDA", "AMD", "AVGO", "TSM", "ARM",
    "PLTR", "MSFT", "SMH", "SOXX", "QQQ", "SPY"
]

START_DATE = "2020-01-01"
OUTPUT_PATH = Path("data/raw/stock_prices.csv")


def download_single_ticker(ticker):
    for attempt in range(3):
        try:
            data = yf.download(
                ticker,
                start=START_DATE,
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if not data.empty:
                close = data["Close"]

                # Convert DataFrame to Series if needed
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close.name = ticker
                return close

        except Exception as e:
            print(f"{ticker} failed on attempt {attempt + 1}: {e}")
            time.sleep(2)

    print(f"Failed to download {ticker}")
    return None


def download_stock_data():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_prices = []

    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        prices = download_single_ticker(ticker)

        if prices is not None:
            all_prices.append(prices)

    final_df = pd.concat(all_prices, axis=1)
    final_df.to_csv(OUTPUT_PATH)

    print(f"Saved stock price data to {OUTPUT_PATH}")
    print(final_df.tail())


if __name__ == "__main__":
    download_stock_data()