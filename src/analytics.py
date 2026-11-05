"""Transparent, descriptive cross-asset risk calculations."""
import numpy as np
import pandas as pd


def prepare_prices(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate a wide price table whose first column contains dates."""
    if frame.shape[1] < 3:
        raise ValueError("Provide a date column and at least two asset columns.")
    dates = pd.to_datetime(frame.iloc[:, 0], errors="coerce", utc=True)
    if dates.isna().any():
        raise ValueError("The first column must contain valid dates on every row.")
    if dates.duplicated().any():
        raise ValueError("Dates must be unique; remove duplicate rows.")
    prices = frame.iloc[:, 1:].copy()
    if prices.columns.duplicated().any():
        raise ValueError("Asset names must be unique.")
    prices = prices.apply(pd.to_numeric, errors="coerce")
    if prices.isna().any().any() or not np.isfinite(prices.to_numpy()).all():
        raise ValueError("All asset prices must be finite numbers with no missing values.")
    prices.index = pd.DatetimeIndex(dates.dt.tz_convert(None), name="Date")
    prices = prices.sort_index()
    if len(prices) < 5 or (prices <= 0).any().any():
        raise ValueError("Provide at least five rows of strictly positive prices.")
    return prices


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty or (prices <= 0).any().any():
        raise ValueError("Prices must be nonempty and positive")
    return prices.sort_index().pct_change(fill_method=None).dropna(how="all")


def rolling_contagion(returns: pd.DataFrame, window: int = 30) -> pd.Series:
    if window < 3:
        raise ValueError("window must be >= 3")
    values = []
    for i in range(len(returns)):
        if i + 1 < window:
            values.append(np.nan)
            continue
        corr = returns.iloc[i + 1 - window:i + 1].corr().to_numpy(dtype=float)
        pairs = corr[np.triu_indices_from(corr, 1)]
        values.append(float(np.nanmean(np.abs(pairs))) if np.isfinite(pairs).any() else np.nan)
    return pd.Series(values, index=returns.index, name="mean_absolute_pairwise_correlation")


def drawdown(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.div(prices.cummax()).sub(1)


def demo_prices() -> pd.DataFrame:
    """Deterministic synthetic prices for exploring the interface, not market data."""
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2022-01-03", periods=750)
    common = rng.normal(0.0004, 0.012, len(dates))
    assets = {name: 100 * np.exp(np.cumsum(beta * common + rng.normal(0.0001, volatility, len(dates))))
              for name, beta, volatility in [("ATLAS", 1.3, .015), ("NOVA", 1.1, .012),
                                              ("ORBIT", .9, .014), ("PULSE", .8, .010),
                                              ("MARKET", .7, .005)]}
    return pd.DataFrame(assets, index=dates).rename_axis("Date")
