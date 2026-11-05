"""Interactive, descriptive monitor of cross-asset co-movement."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import daily_returns, demo_prices, drawdown, prepare_prices, rolling_contagion
from src.research import downside_study, factor_adjusted_comovement, revenue_shock, token_price_stress

st.set_page_config(page_title="AI Equity Contagion Monitor", page_icon="◈", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1380px; padding-top: 2.5rem; padding-bottom: 3rem;}
[data-testid="stMetric"] {background: rgba(120, 145, 175, .09); border: 1px solid rgba(120, 145, 175, .2); padding: 20px; border-radius: 14px;}
[data-testid="stMetricLabel"] {font-size: .88rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(120, 145, 175, .18);}
.stTabs [data-baseweb="tab-list"] {gap: 8px; flex-wrap: wrap;}
.stTabs [data-baseweb="tab"] {border-radius: 8px 8px 0 0; padding: 10px 14px;}
h1, h2, h3 {letter-spacing: -0.035em;}
.intro {font-size: 1.08rem; opacity: .8; max-width: 780px; line-height: 1.6;}
</style>""", unsafe_allow_html=True)

st.caption("A SIMPLE GUIDE TO AI MARKET RISK")
st.title("AI market risk explorer")
st.markdown('<p class="intro">A clear look at how AI-related stocks move together—and what might happen if AI becomes more expensive to use.</p>', unsafe_allow_html=True)
st.info("Start with **Your results** for the big picture, then explore the charts or try the **Token price scenario**. A token is a small piece of text an AI system processes.")

with st.sidebar:
    st.header("Choose your data")
    source = st.radio("Where should the data come from?", ["Practice data", "Downloaded stock data", "Upload CSV"], help="The demo is generated data, not historical market prices.")
    if source == "Upload CSV":
        upload = st.file_uploader("Price history CSV", type="csv", help="First column: dates. Remaining columns: positive numeric prices.")
        if upload is None:
            st.info("Upload a CSV to begin. Every asset must have a price on every date.")
            st.stop()
        try:
            prices = prepare_prices(pd.read_csv(upload))
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            st.error(f"Could not read price data: {exc}")
            st.stop()
    elif source == "Downloaded stock data":
        path = Path(__file__).resolve().parents[1] / "data/raw/stock_prices.csv"
        if not path.exists():
            st.info("Run `python3 src/data_collection.py` from the project root to download market data.")
            st.stop()
        try:
            prices = prepare_prices(pd.read_csv(path))
        except (ValueError, pd.errors.ParserError) as exc:
            st.error(f"Could not read downloaded data: {exc}")
            st.stop()
    else:
        prices = demo_prices()
    st.divider()
    selected = st.multiselect("Assets", prices.columns.tolist(), default=prices.columns.tolist())
    if len(selected) < 2:
        st.warning("Select at least two assets.")
        st.stop()
    prices = prices[selected]
    window = st.slider("Rolling window · observations", 3, min(120, len(prices) - 1), min(30, len(prices) - 1))
    st.caption("The window is measured in return observations, not calendar days.")
    st.divider()
    st.caption("Built for exploration, not investment decisions.")

if source == "Practice data":
    st.info("DEMO MODE · These prices are synthetic and do not represent real companies or market history. Upload your own data to analyze actual assets.")
elif source == "Downloaded stock data":
    st.success(f"DOWNLOADED DATA · Yahoo Finance adjusted closes via yfinance; latest observation: {prices.index.max():%d %b %Y}. Refresh using the collection script.")
else:
    st.success("YOUR DATA · Analysis is calculated from the uploaded price history.")

returns = daily_returns(prices)
contagion = rolling_contagion(returns, window)
drawdowns = drawdown(prices)
correlation = returns.corr()
latest = contagion.dropna()
worst = drawdowns.min().min()
metrics = st.columns(4)
metrics[0].metric("Stocks and funds", len(selected))
metrics[1].metric("Days of price data", f"{len(prices):,}", help="Number of price rows in the selected dataset.")
metrics[2].metric("How closely prices move", f"{latest.iloc[-1]:.2f}" if not latest.empty else "N/A", help="Mean absolute pairwise return correlation in the latest rolling window. Higher means stronger relationships, regardless of direction.")
metrics[3].metric("Biggest fall from a high", f"{worst:.1%}", help="Largest peak-to-trough decline observed for any selected asset.")
st.caption(f"PERIOD  {prices.index.min():%d %b %Y} — {prices.index.max():%d %b %Y}  ·  {window}-OBSERVATION WINDOW")

chart_config = dict(displayModeBar=False)
tab0, tab1, tab2, tab4, tab5, tab6, tab7, tab3 = st.tabs(["Your results", "Stock overview", "Stock connections", "Bad market days", "Market influence", "Business links", "Token price scenario", "How it works"])
with tab1:
    st.subheader("If you started with $100")
    st.caption("Each line starts at 100 so you can compare how the investments changed over time. It does not show an actual investment.")
    normalized = prices.div(prices.iloc[0]).mul(100)
    fig = px.line(normalized, labels={"value": "Indexed price", "Date": "", "variable": "Asset"}, color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(legend_title_text="", hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True, config=chart_config)
    left, right = st.columns(2)
    with left:
        st.subheader("How closely stocks move over time")
        st.caption("A higher score means the stocks have a stronger relationship over the chosen period. Stocks moving in opposite directions can also raise the score.")
        fig = px.line(contagion, labels={"value": "Mean absolute correlation", "Date": ""})
        fig.update_traces(line_color="#3478c0")
        fig.update_layout(showlegend=False, yaxis_range=[0, 1], margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
    with right:
        st.subheader("Falls from previous highs")
        st.caption("Shows how far each investment fell from its highest price so far in the selected data.")
        fig = px.line(drawdowns, labels={"value": "Drawdown", "Date": "", "variable": "Asset"}, color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(yaxis_tickformat=".0%", legend_title_text="", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
with tab2:
    st.subheader("How stock returns move together")
    st.caption("Numbers near 1 mean two investments often moved in the same direction; numbers near -1 mean they often moved in opposite directions. This does not show why.")
    fig = px.imshow(correlation, zmin=-1, zmax=1, color_continuous_scale="RdBu", text_auto=".2f", aspect="auto", labels={"color": "Correlation"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True, config=chart_config)
    st.dataframe(correlation.style.format("{:.2f}"), use_container_width=True)
with tab4:
    st.subheader("What happened on the market’s worst days?")
    st.caption("Compare a group of stocks with a market benchmark on its worst days. Each stock has the same weight. This describes the past; it does not predict the future or prove one company caused another to fall.")
    benchmark = st.selectbox("Benchmark", selected, index=selected.index("SPY") if "SPY" in selected else 0)
    choices = [asset for asset in selected if asset != benchmark]
    defaults = [asset for asset in choices if asset not in ("QQQ", "SMH", "SOXX", "SPY")] or choices
    basket = st.multiselect("Basket assets", choices, default=defaults)
    if not basket:
        st.info("Select at least one basket asset.")
    else:
        try:
            result = downside_study(returns, benchmark, basket)
            cols = st.columns(4)
            cols[0].metric("Worst market days", f"{result['stress_days']} / {result['observations']}")
            cols[1].metric("Market average", f"{result['benchmark_mean']:.2%}")
            cols[2].metric("Stock group average", f"{result['basket_mean']:.2%}")
            cols[3].metric("Group vs market", f"{result['excess']:+.2%}")
            st.write(f"Worst market days are the worst 10% of benchmark returns in the selected sample (threshold ≤ {result['threshold']:.2%}). The estimated mean difference is **{result['excess']:+.2%}**, with a 95% moving-block bootstrap interval of **[{result['ci_low']:+.2%}, {result['ci_high']:+.2%}]**.")
            st.caption("Bootstrap: 1,000 resamples of paired 10-observation blocks, fixed seed 42, threshold recomputed per resample. This interval is approximate and sensitive to serial dependence, sample period and basket selection; it does not correct for trying multiple baskets.")
            st.dataframe(result["days"].sort_index(ascending=False).style.format("{:.2%}"), use_container_width=True)
        except ValueError as exc:
            st.info(str(exc))
with tab5:
    st.subheader("Do the stocks still move together after accounting for the market?")
    st.caption("We use the first 70% of the history to estimate how each stock responds to market and industry funds. We then check the remaining 30% for movement those funds do not explain.")
    factor_defaults = [x for x in ("SPY", "SMH") if x in selected]
    if not factor_defaults:
        factor_defaults = selected[:1]
    factors = st.multiselect("Market and sector factor proxies", selected, default=factor_defaults)
    factor_assets = [x for x in selected if x not in factors and x not in ("SPY", "SMH", "SOXX", "QQQ")]
    if len(factor_assets) < 2:
        st.info("Select factors and at least two other non-ETF assets in the sidebar.")
    elif factors:
        try:
            adjusted = factor_adjusted_comovement(returns, factors, factor_assets)
            a, b = st.columns(2)
            a.metric("Average connection before adjustment", f"{adjusted['raw_mean']:.2f}")
            b.metric("Average connection after adjustment", f"{adjusted['residual_mean']:.2f}")
            st.caption(f"Train: {adjusted['train_start']:%Y-%m-%d} to {adjusted['train_end']:%Y-%m-%d} ({adjusted['train_n']} days). Test: {adjusted['test_start']:%Y-%m-%d} to {adjusted['test_end']:%Y-%m-%d} ({adjusted['test_n']} days).")
            st.write("Held-out residual correlation")
            st.dataframe(adjusted["residual"].style.format("{:.2f}"), use_container_width=True)
            with st.expander("Training factor coefficients"):
                st.dataframe(adjusted["coefficients"].style.format("{:.3f}"), use_container_width=True)
            st.caption("Signed pairwise means exclude undefined correlations. Residuals are actual test returns minus the training-fitted intercept and factor predictions using same-day test factor returns. This is an explanatory decomposition, not a forecast. ETF factors can include basket stocks, creating mechanical overlap; residual association does not establish a commercial dependency, causality, or statistical significance.")
        except ValueError as exc:
            st.info(str(exc))
    else:
        st.info("Select at least one factor.")
with tab6:
    st.subheader("Business links: what do we actually know?")
    st.markdown("""
    - **NVIDIA:** its [fiscal 2026 10-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm) reports two direct customers at **22% and 14%** of revenue. These figures do not identify the customers or establish a feedback loop.
    - **TSMC:** its [2025 20-F](https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm) reports its top ten customers at approximately **78%** of revenue; its two largest accounted for **19% and 17%**. These are concentration disclosures, not a verified company-to-company network.

    These disclosures describe different firms and periods. They cannot be multiplied together as though they represented the same relationship. A circular exposure would require documented directional links forming a closed loop, with monetary amounts and dates.
    """)
    st.subheader("Business links backed by sources")
    st.caption("A small manually curated evidence inventory—not an exhaustive ownership network. Arrows represent the direction of investment or the buyer's purchase commitment, not necessarily cash paid. Historical commitments can be amended and must not be added to overlapping investment records.")
    relationship_path = Path(__file__).resolve().parents[1] / "data/research/relationships.csv"
    if relationship_path.exists():
        relationships = pd.read_csv(relationship_path)
        st.dataframe(relationships, use_container_width=True, hide_index=True)
        st.download_button("Download the source data", relationship_path.read_bytes(), "relationships.csv", "text/csv")
        st.info("Microsoft → Anthropic (investment) and Anthropic → Microsoft (compute commitment) form a mixed-type relationship loop. This is not mutual share ownership, proof of cash recycling, or evidence of systemic risk.")
    else:
        st.warning("Relationship evidence file is missing.")
    st.subheader("Example: how lower spending might spread")
    st.warning("Illustration only: all inputs are assumptions, not estimates from the disclosures above. This is not a stock-price prediction or evidence of a feedback loop.")
    cut = st.slider("Customer spending reduction (%)", 0, 100, 25)
    exposure = st.slider("Share of first firm's revenue exposed to that customer (%)", 0, 100, 20)
    supplier = st.slider("Share of second firm's revenue exposed to first firm (%)", 0, 100, 15)
    scenario = revenue_shock(cut / 100, exposure / 100, supplier / 100)
    c1, c2 = st.columns(2)
    c1.metric("First firm's illustrative revenue decline", f"{scenario['first_loss']:.2%}")
    c2.metric("Second firm's illustrative revenue decline", f"{scenario['second_loss']:.2%}")
    st.caption("Assumes the spending cut applies uniformly to exposed revenue and the first firm cuts purchases from the second proportionally to its own revenue loss. Static one-way transmission; no margins, substitution, contracts, timing, leverage, valuation, market reaction or feedback effects are modeled.")
with tab7:
    st.subheader("What if AI becomes more expensive to use?")
    st.warning("Try a made-up example for one customer. The starting numbers are not real prices and the result is not a prediction.")
    left, right = st.columns(2)
    with left:
        tokens = st.number_input("Tokens used each month today · millions", min_value=0.01, value=1000.0, step=100.0)
        price = st.number_input("Average price today · dollars per million tokens", min_value=0.01, value=5.0, step=1.0)
        increase = st.slider("How much could the price increase? (%)", 0, 500, 100)
    with right:
        cut = st.slider("How much usage would the customer plan to cut? (%)", 0, 100, 20)
        budget_delta = st.slider("How much could their monthly budget change? (%)", -100, 500, 0)
        st.caption("The customer cannot spend more than this budget. If necessary, they use fewer tokens than planned.")
    outcome = token_price_stress(tokens, price, increase / 100, cut / 100, budget_delta / 100)
    a, b, c, d = st.columns(4)
    a.metric("New price per million tokens", f"${outcome['new_price']:,.2f}")
    b.metric("New monthly usage · millions", f"{outcome['actual_tokens']:,.2f}", f"{outcome['usage_change']:+.1%}")
    c.metric("New monthly spending", f"${outcome['spend']:,.2f}", f"{outcome['spend_change']:+.1%}")
    d.metric("Budget limit", "Limits usage" if outcome['budget_binding'] else "Does not limit usage")
    st.write(f"Baseline spend: **${outcome['baseline_spend']:,.2f}/month**. Scenario budget: **${outcome['budget']:,.2f}/month**. Planned usage before the budget cap: **{outcome['planned_tokens']:,.2f} million tokens/month**.")
    st.caption("This example assumes every token costs the same and there are no fixed fees or minimum payments. The customer's spending is the provider's revenue from this one customer—not the provider's total revenue or profit. Real pricing and contracts are more complicated. This does not predict stock prices or a wider market crash.")
with tab0:
    st.subheader("The big picture")
    if source == "Practice data":
        st.warning("These stock results use made-up practice data. Choose Downloaded stock data in the sidebar to see market history.")
    elif source == "Downloaded stock data":
        st.caption(f"Based on downloaded stock prices from {prices.index.min():%d %b %Y} to {prices.index.max():%d %b %Y}. These are historical observations, not predictions.")
    else:
        st.caption(f"Based on your uploaded prices from {prices.index.min():%d %b %Y} to {prices.index.max():%d %b %Y}. These are historical observations, not predictions.")
    st.markdown("#### 1 · What happened on bad market days?")
    result_assets = [x for x in selected if x not in ("SPY", "QQQ", "SMH", "SOXX")]
    summary = None
    if "SPY" in selected and result_assets:
        try:
            summary = downside_study(returns, "SPY", result_assets)
            st.write(f"On the {summary['stress_days']} worst SPY days in this dataset, SPY changed **{summary['benchmark_mean']:+.2%} on average** and the selected stock group changed **{summary['basket_mean']:+.2%} on average**. The difference was **{summary['excess']:+.2%}** per day.")
            st.caption("The worst days are the bottom 10% of SPY returns. The group has equal weights and excludes SPY, QQQ, SMH and SOXX. Past losses do not prove one company caused another to fall.")
        except ValueError as exc:
            st.info(f"Not enough data to show this result: {exc}")
    else:
        st.info("Select SPY and at least one other stock in the sidebar to compare the group with the market.")
    st.markdown("#### 2 · Are business links proof of a bubble?")
    st.write("No. The sources document investments and business commitments between some AI companies. Those links may create shared risks, but they do not by themselves prove a bubble or a chain reaction. Open **Business links** to inspect the sources.")
    st.markdown("#### 3 · What does your token-price example show?")
    st.write(f"With the assumptions in **Token price scenario**, monthly usage changes by **{outcome['usage_change']:+.1%}**, and this customer's spending changes by **{outcome['spend_change']:+.1%}**. The budget {'limits' if outcome['budget_binding'] else 'does not limit'} usage in this example.")
    st.caption("This is a made-up scenario for one customer, not a prediction of what companies will do or how markets will react.")
    st.markdown("#### Conclusion at a glance")
    bad_days_conclusion = "Select SPY and at least one stock to calculate this comparison."
    if summary is not None:
        bad_days_conclusion = (f"On the worst 10% of SPY days, the stock group averaged "
                               f"{summary['basket_mean']:+.2%} versus {summary['benchmark_mean']:+.2%} for SPY.")
    elif "SPY" in selected and result_assets:
        bad_days_conclusion = "Not enough data to calculate the comparison."
    conclusions = pd.DataFrame([
        {"Question": "What happened on bad market days?", "Result": bad_days_conclusion,
         "What it cannot tell us": "Whether one company caused another to fall, or what will happen next."},
        {"Question": "Are AI businesses connected?", "Result": "Some investments and business commitments are documented in the source data.",
         "What it cannot tell us": "Whether the full network forms a dangerous feedback loop or proves a bubble."},
        {"Question": "What if tokens cost more?", "Result": f"In this example, usage changes {outcome['usage_change']:+.1%} and spending changes {outcome['spend_change']:+.1%}.",
         "What it cannot tell us": "How real customers, AI companies, or stock prices will respond."},
    ])
    st.dataframe(conclusions, hide_index=True, use_container_width=True)
    st.caption("The first row uses the selected price data; the second summarizes sourced disclosures; the third is a hypothetical scenario. None is investment advice.")
with tab3:
    st.subheader("What the numbers mean")
    st.markdown("""
    - **Returns** are the percentage change between consecutive observations.
    - **Co-movement** is the average absolute Pearson correlation of every unique pair of returns within a trailing window. It ranges from 0 to 1; it measures association, not causation or a probability of contagion. Constant-return pairs are excluded.
    - **Drawdown** is the percentage change from each asset’s highest price so far in the supplied history. It does not account for peaks before that history.
    - **Correlation matrix** uses the full selected history and retains positive and negative signs.

    These descriptive indicators do not establish a bubble, institutional flows, sentiment, or a trading signal. Results depend on the chosen assets, period, data quality, and window. This is not investment advice.
    """)
    st.subheader("Price data")
    st.dataframe(prices.sort_index(ascending=False), use_container_width=True)
    st.download_button("Download displayed prices", prices.to_csv().encode("utf-8"), "prices.csv", "text/csv")

st.divider()
st.caption("AI EQUITY CONTAGION MONITOR  ·  An exploratory research project  ·  Not financial advice")
