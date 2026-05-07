import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

INPUT_PATH = Path("data/processed/daily_returns.csv")
OUTPUT_PATH = Path("data/processed/correlation_matrix.csv")


def generate_correlation_heatmap():
    returns = pd.read_csv(INPUT_PATH, index_col="Date", parse_dates=True)

    correlation_matrix = returns.corr()

    correlation_matrix.to_csv(OUTPUT_PATH)

    plt.figure(figsize=(12, 8))

    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f"
    )

    plt.title("AI Stock Correlation Heatmap")
    plt.tight_layout()

    plt.show()

    print("\nCorrelation Matrix:\n")
    print(correlation_matrix)


if __name__ == "__main__":
    generate_correlation_heatmap()