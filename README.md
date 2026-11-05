# AI Equity Contagion Monitor

An interactive research dashboard for exploring co-movement and drawdowns across a basket of assets. Compare normalized prices, inspect rolling pairwise correlations, and explore the relationships between individual assets. The default dataset is **synthetic**, so the dashboard can be explored immediately without an API key or network connection.

> This is a descriptive research project, not a bubble detector or investment advice. Correlation does not establish contagion or causation.

## Get started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

Choose **Practice data** in the sidebar, or upload your own CSV using **Upload CSV**. The app processes uploads locally in the running Streamlit process.

### CSV format

The first column must contain unique dates; subsequent columns must contain complete, strictly positive numeric prices. Include at least two assets and five rows. Prices should be consistently adjusted for corporate actions where appropriate.

```csv
Date,Asset A,Asset B
2024-01-02,100.0,80.0
2024-01-03,101.0,79.5
2024-01-04,102.0,81.0
2024-01-05,100.5,82.0
2024-01-08,103.0,83.0
```

Optionally, download adjusted historical closes for a predefined AI equity and ETF basket using Yahoo Finance:

```bash
python src/data_collection.py
```

Upload the resulting `data/raw/stock_prices.csv` to the dashboard. The download requires internet access, depends on a third-party service, and keeps only dates with complete data for all available tickers; assets with later listing dates can shorten the history. Verify the data before using it.

## Methodology

- **Returns:** percentage changes between consecutive observations.
- **Rolling co-movement:** mean absolute Pearson correlation across unique asset pairs over a trailing window of returns. Strong negative correlations also increase this score; pairs with undefined correlations are excluded. This is not a calibrated contagion measure.
- **Drawdown:** price relative to its running maximum within the supplied history.
- **Correlation matrix:** signed Pearson correlations across the full return history.

The dashboard does not measure sentiment, institutional flows, fundamentals, or bubble probabilities. The selected assets, time period, window, and data quality affect every result.

## Project structure

- `dashboard/app.py` — Streamlit interface
- `src/analytics.py` — validation and analytical functions
- `src/data_collection.py` — optional Yahoo Finance download
- `tests/` — unit tests

Run tests with `python -m unittest discover -s tests`.

## Downside-risk research study

**Research question:** Do selected AI-linked equities underperform the broad US market on the market's worst days? In the **Bad market days** tab, SPY is the default benchmark and the selected non-ETF stocks form an equal-weight basket, rebalanced each observation. Stress days are defined retrospectively as the worst 10% of benchmark daily returns in the complete sample. The effect is the mean basket return minus the mean benchmark return on those days. A 95% moving-block bootstrap interval resamples paired 10-day blocks 1,000 times (seed 42), recalculating the stress threshold each time. This is a descriptive in-sample comparison—not a prediction, a causal test, or evidence of a bubble.

### Reproducible snapshot

On a Yahoo Finance download performed 5 November 2026, the complete panel covered **14 September 2023–4 November 2026** (788 returns). For NVDA, AMD, AVGO, TSM, ARM, PLTR and MSFT versus SPY, 79 stress days had a mean SPY return of **−1.67%** and a mean basket return of **−3.41%**. The difference was **−1.74 percentage points** per stress day, with a bootstrap interval of **−2.11 to −1.30 percentage points**. This snapshot may change with provider revisions and data refreshes; rerun the download and study to reproduce it. The data file is not committed.

The basket was selected with hindsight; ARM's recent listing truncates the common sample, creating selection and survivorship biases. A high-beta technology basket can underperform simply due to market exposure; no beta adjustment, causal identification, multiple-testing correction, transaction costs, or out-of-sample validation is included. A negative difference is **not evidence of contagion**. The percentile threshold is computed using the entire sample and must not be used as a real-time signal. The bootstrap interval is approximate and depends on block length and stationarity assumptions.

### Data sources and freshness

- [Yahoo Finance historical data](https://help.yahoo.com/kb/SLN2311.html), accessed via the unofficial [yfinance library](https://github.com/ranaroussi/yfinance), provides adjusted daily prices. Availability, licensing and rate limits may change. Refresh with `python3 src/data_collection.py`; the app displays the actual last observation. No data is silently substituted if a download fails.
- [FRED VIXCLS](https://fred.stlouisfed.org/series/VIXCLS) is an alternative source for daily Cboe VIX volatility context. FRED listed an observation through 30 October 2026 when checked on 5 November 2026. It is **not currently included in the analysis**; review the series' copyright terms before redistribution.

## Factor-adjusted co-movement and exposure scenarios

The **Market influence** fits an intercept and selected factor returns (by default SPY and SMH when available) to each selected non-ETF asset using ordinary least squares on the first 70% of observations. It compares mean signed pairwise correlations of raw returns with correlations of residuals on the final 30%. The model uses same-day test factor returns, so the held-out split tests stability of the decomposition, **not forecasting performance**. ETF holdings overlap with some basket stocks, and omitted factors, changing exposures and selection effects can influence residual correlations. Neither residual correlation nor the absence of it demonstrates a causal business dependency. No significance test is provided.

For the download described above, the default held-out sample produced mean raw correlation **0.39** and mean residual correlation **0.11**. This is an illustrative snapshot, not a universal result; factor selection and future data revisions can change it.

The **Business links** tab links to NVIDIA's fiscal 2026 10-K and TSMC's 2025 20-F for customer concentration disclosures. These disclosures do not identify a closed loop. The adjacent calculator is a purely hypothetical, one-way two-link shock: first-firm revenue loss = customer spending cut × exposed revenue share; second-firm revenue loss = first-firm loss × second-firm exposure share. Its inputs are user assumptions, not values inferred from the filings. It assumes proportional purchasing and ignores feedback, valuation, leverage, contractual protections and substitution. It cannot establish systemic risk or a housing-crisis analogy.

### Relationship evidence inventory

`data/research/relationships.csv` contains a small, manually curated, primary-source inventory of Anthropic investment and compute relationships. View and download it in **Business links**. Its [data dictionary](data/research/README.md) explains direction, statuses, overlapping disclosures and limitations. It does not establish current ownership percentages or constitute a comprehensive ownership network. The recorded Microsoft–Anthropic mixed-type loop is not reciprocal share ownership or proof of cash recycling.

## Token-price stress scenario

The **Token price scenario** tab models one hypothetical customer's monthly token usage and spending under a higher blended token price, a manually assumed usage cut, and a hard budget. Stressed volume is the lower of planned volume and budget divided by stressed price; spending is stressed volume times stressed price. With no fixed fees, this customer's spend equals the provider's revenue from this transaction only. Inputs are illustrative—not actual prices or empirically estimated demand elasticity. The model does not predict total revenue, profit, stock prices, or contagion; it excludes tiered input/output pricing, contracts, minimums, alternative providers, supply costs, and feedback effects.
