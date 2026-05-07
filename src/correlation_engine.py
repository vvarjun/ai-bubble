import pandas as pd
from pathlib import Path

INPUT_PATH = Path("data/raw/stock_prices.csv")
OUTPUT_PATH = Path("data/processed/daily_returns.csv")


def calculate_returns():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    prices = pd.read_csv(INPUT_PATH, index_col="Date", parse_dates=True)
    returns = prices.pct_change().dropna()

    returns.to_csv(OUTPUT_PATH)

    print(f"Saved daily returns to {OUTPUT_PATH}")
    print(returns.tail())


if __name__ == "__main__":
    calculate_returns()