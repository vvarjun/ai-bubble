import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_PATH = Path("data/processed/daily_returns.csv")


def rolling_correlation():
    returns = pd.read_csv(INPUT_PATH, index_col="Date", parse_dates=True)

    rolling_corr = (
        returns["NVDA"]
        .rolling(window=30)
        .corr(returns["AMD"])
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        rolling_corr.index,
        rolling_corr,
        label="NVDA vs AMD Rolling Correlation"
    )

    plt.axhline(
        rolling_corr.mean(),
        linestyle="--",
        label="Average Correlation"
    )

    plt.title("30-Day Rolling Correlation: NVDA vs AMD")
    plt.xlabel("Date")
    plt.ylabel("Correlation")

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    print("\nAverage Rolling Correlation:")
    print(rolling_corr.mean())


if __name__ == "__main__":
    rolling_correlation()