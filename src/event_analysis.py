import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_PATH = Path("data/processed/daily_returns.csv")


def detect_contagion_events():
    returns = pd.read_csv(INPUT_PATH, index_col="Date", parse_dates=True)

    nvda_moves = returns["NVDA"]

    # Detect large NVDA daily jumps
    threshold = 0.05

    major_events = nvda_moves[nvda_moves > threshold]

    print("\nMajor NVDA Positive Shock Events:\n")
    print(major_events)

    contagion_results = []

    for date in major_events.index:
        row = returns.loc[date]

        contagion_results.append({
            "Date": date,
            "NVDA": row["NVDA"],
            "AMD": row["AMD"],
            "SMH": row["SMH"],
            "SOXX": row["SOXX"],
            "QQQ": row["QQQ"]
        })

    contagion_df = pd.DataFrame(contagion_results)

    print("\nContagion Analysis:\n")
    print(contagion_df)

    contagion_df.set_index("Date")[[
        "NVDA", "AMD", "SMH", "SOXX", "QQQ"
    ]].plot(
        kind="bar",
        figsize=(14, 7)
    )

    plt.title("Market Reaction to Major NVIDIA Shock Events")
    plt.ylabel("Daily Return")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    detect_contagion_events()