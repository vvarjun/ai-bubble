import pandas as pd
from pathlib import Path

INPUT_PATH = Path("data/processed/daily_returns.csv")
OUTPUT_PATH = Path("data/processed/bubble_scores.csv")


def calculate_bubble_score():
    returns = pd.read_csv(INPUT_PATH, index_col="Date", parse_dates=True)

    rolling_corr_nvda_amd = returns["NVDA"].rolling(30).corr(returns["AMD"])
    rolling_corr_smh_soxx = returns["SMH"].rolling(30).corr(returns["SOXX"])

    nvda_momentum = returns["NVDA"].rolling(5).mean()
    ai_etf_momentum = returns[["SMH", "SOXX"]].mean(axis=1).rolling(5).mean()

    score = (
                    rolling_corr_nvda_amd.rank(pct=True)
                    + rolling_corr_smh_soxx.rank(pct=True)
                    + nvda_momentum.rank(pct=True)
                    + ai_etf_momentum.rank(pct=True)
            ) / 4 * 100

    bubble_df = pd.DataFrame({
        "nvda_amd_rolling_corr": rolling_corr_nvda_amd,
        "smh_soxx_rolling_corr": rolling_corr_smh_soxx,
        "nvda_momentum": nvda_momentum,
        "ai_etf_momentum": ai_etf_momentum,
        "bubble_score": score
    }).dropna()

    bubble_df.to_csv(OUTPUT_PATH)

    print(f"Saved bubble scores to {OUTPUT_PATH}")
    print(bubble_df.tail())


if __name__ == "__main__":
    calculate_bubble_score()