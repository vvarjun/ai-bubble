"""Benchmark-conditioned downside study with a moving-block bootstrap."""
import numpy as np
import pandas as pd


def downside_study(returns: pd.DataFrame, benchmark: str, assets: list,
                   quantile: float = .10, block: int = 10, iterations: int = 1000,
                   seed: int = 42) -> dict:
    """Compare equal-weight basket and benchmark on full-sample worst benchmark days.

    Bootstrap resamples contiguous blocks of paired returns; the benchmark threshold
    is recalculated per sample. This is descriptive, not an out-of-sample forecast.
    """
    if benchmark not in returns or not assets or benchmark in assets:
        raise ValueError("Choose a benchmark and at least one different basket asset.")
    if not 0 < quantile < 1 or block < 1 or iterations < 1:
        raise ValueError("Invalid quantile, block length, or bootstrap iterations.")
    data = returns[[benchmark] + assets].dropna()
    if len(data) < 30:
        raise ValueError("At least 30 complete return observations are required.")
    market = data[benchmark].to_numpy()
    basket = data[assets].mean(axis=1).to_numpy()

    def statistic(m, b):
        cutoff = np.quantile(m, quantile)
        mask = m <= cutoff
        return float(np.mean((b - m)[mask]))

    threshold = float(np.quantile(market, quantile))
    mask = market <= threshold
    excess = statistic(market, basket)
    rng = np.random.default_rng(seed)
    n = len(data)
    length = min(block, n)
    samples = np.empty(iterations)
    for i in range(iterations):
        starts = rng.integers(0, n - length + 1, size=int(np.ceil(n / length)))
        indices = (starts[:, None] + np.arange(length)).ravel()[:n]
        samples[i] = statistic(market[indices], basket[indices])
    days = pd.DataFrame({"Benchmark return": market[mask], "Basket return": basket[mask],
                         "Excess return": (basket - market)[mask]}, index=data.index[mask])
    return {"threshold": threshold, "stress_days": int(mask.sum()), "observations": n,
            "benchmark_mean": float(market[mask].mean()), "basket_mean": float(basket[mask].mean()),
            "excess": excess, "ci_low": float(np.quantile(samples, .025)),
            "ci_high": float(np.quantile(samples, .975)), "days": days}


def factor_adjusted_comovement(returns: pd.DataFrame, factors: list, assets: list,
                               train_fraction: float = .7) -> dict:
    """Fit intercept and factor loadings chronologically; correlate test residuals."""
    if len(set(factors)) != len(factors) or not factors or len(assets) < 2:
        raise ValueError("Select distinct factors and at least two assets.")
    if set(factors) & set(assets) or len(set(assets)) != len(assets):
        raise ValueError("Factors and assets must be distinct.")
    if not 0 < train_fraction < 1:
        raise ValueError("Training fraction must be between zero and one.")
    data = returns[factors + assets].dropna().sort_index()
    split = int(len(data) * train_fraction)
    train, test = data.iloc[:split], data.iloc[split:]
    if len(train) < max(30, len(factors) + 2) or len(test) < 20:
        raise ValueError("Need at least 30 training and 20 test return observations.")
    x_train = np.column_stack([np.ones(len(train)), train[factors].to_numpy()])
    if np.linalg.matrix_rank(x_train) < x_train.shape[1]:
        raise ValueError("Factor returns are linearly dependent or constant in training.")
    x_test = np.column_stack([np.ones(len(test)), test[factors].to_numpy()])
    coefficients = np.linalg.lstsq(x_train, train[assets].to_numpy(), rcond=None)[0]
    residuals = pd.DataFrame(test[assets].to_numpy() - x_test @ coefficients,
                             index=test.index, columns=assets)
    def mean_pair(corr):
        matrix = corr.to_numpy()
        pairs = matrix[np.triu_indices_from(matrix, 1)]
        return float(np.nanmean(pairs)) if np.isfinite(pairs).any() else float('nan')
    return {"raw": test[assets].corr(), "residual": residuals.corr(),
            "raw_mean": mean_pair(test[assets].corr()),
            "residual_mean": mean_pair(residuals.corr()),
            "train_start": train.index[0], "train_end": train.index[-1],
            "test_start": test.index[0], "test_end": test.index[-1],
            "train_n": len(train), "test_n": len(test),
            "coefficients": pd.DataFrame(coefficients, index=["Intercept"] + factors, columns=assets)}


def revenue_shock(customer_cut: float, exposed_share: float, supplier_share: float) -> dict:
    """Illustrative two-link revenue shock, with user-specified shares only."""
    if not all(0 <= value <= 1 for value in (customer_cut, exposed_share, supplier_share)):
        raise ValueError("All scenario inputs must be between 0 and 1.")
    first = customer_cut * exposed_share
    return {"first_loss": first, "second_loss": first * supplier_share}


def token_price_stress(monthly_million_tokens: float, price_per_million: float,
                       price_increase: float, planned_usage_cut: float,
                       budget_change: float) -> dict:
    """Illustrative monthly spend with an optional binding customer budget.

    Inputs describe a single blended token product and one representative customer.
    Fractions are expressed as decimals. A budget_change of 0 fixes baseline spend.
    """
    values = (monthly_million_tokens, price_per_million, price_increase,
              planned_usage_cut, budget_change)
    if not np.isfinite(values).all():
        raise ValueError("Scenario inputs must be finite.")
    if monthly_million_tokens <= 0 or price_per_million <= 0:
        raise ValueError("Baseline usage and price must be positive.")
    if price_increase < 0 or not 0 <= planned_usage_cut <= 1 or budget_change < -1:
        raise ValueError("Invalid price increase, usage reduction, or budget change.")
    baseline_spend = monthly_million_tokens * price_per_million
    new_price = price_per_million * (1 + price_increase)
    budget = baseline_spend * (1 + budget_change)
    planned_tokens = monthly_million_tokens * (1 - planned_usage_cut)
    actual_tokens = min(planned_tokens, budget / new_price)
    spend = actual_tokens * new_price
    return {"baseline_spend": baseline_spend, "new_price": new_price,
            "budget": budget, "planned_tokens": planned_tokens,
            "actual_tokens": actual_tokens, "spend": spend,
            "usage_change": actual_tokens / monthly_million_tokens - 1,
            "spend_change": spend / baseline_spend - 1,
            "budget_binding": actual_tokens < planned_tokens - 1e-9}
