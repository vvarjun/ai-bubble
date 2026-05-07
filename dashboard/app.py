import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Bubble Dashboard",
    layout="wide"
)

st.title("AI Equity Contagion & Bubble Dashboard")

st.markdown("""
### Thesis

AI stock valuations are increasingly driven by synchronized institutional flows,
ETF concentration, and thematic market contagion rather than isolated firm fundamentals.
""")

bubble_df = pd.read_csv("data/processed/bubble_scores.csv")
returns_df = pd.read_csv("data/processed/daily_returns.csv")

latest_score = bubble_df["bubble_score"].iloc[-1]
latest_nvda_amd_corr = bubble_df["nvda_amd_rolling_corr"].iloc[-1]
latest_smh_soxx_corr = bubble_df["smh_soxx_rolling_corr"].iloc[-1]

# ------------------------
# Top Metrics
# ------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Latest Bubble Score",
    round(latest_score, 2)
)

col2.metric(
    "NVDA-AMD Rolling Corr",
    round(latest_nvda_amd_corr, 2)
)

col3.metric(
    "SMH-SOXX Rolling Corr",
    round(latest_smh_soxx_corr, 2)
)

# ------------------------
# Bubble Gauge
# ------------------------

st.header("AI Bubble Risk Gauge")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=latest_score,
    title={"text": "AI Bubble Risk"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "black"},
        "steps": [
            {"range": [0, 30], "color": "lightgreen"},
            {"range": [30, 60], "color": "yellow"},
            {"range": [60, 100], "color": "red"}
        ],
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("""
**Risk Interpretation**

- **0–30:** Normal market conditions  
- **30–60:** Elevated synchronization  
- **60–80:** Speculative momentum  
- **80–100:** High bubble risk  
""")

# ------------------------
# Bubble Score Over Time
# ------------------------

st.header("AI Bubble Index Over Time")

fig_bubble = px.line(
    bubble_df,
    x="Date",
    y="bubble_score",
    title="Bubble Risk Score Over Time"
)

fig_bubble.add_hline(y=30, line_dash="dash")
fig_bubble.add_hline(y=60, line_dash="dash")
fig_bubble.add_hline(y=80, line_dash="dash")

st.plotly_chart(fig_bubble, use_container_width=True)

# ------------------------
# Correlation Heatmap
# ------------------------

st.header("AI Stock Correlation Heatmap")

corr = returns_df.drop(columns=["Date"]).corr()

fig_heatmap = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdBu_r",
    title="Correlation Matrix of AI Stocks and ETFs"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ------------------------
# NVDA vs AMD Daily Returns
# ------------------------

st.header("NVDA vs AMD Daily Returns")

fig_nvda_amd = px.line(
    returns_df,
    x="Date",
    y=["NVDA", "AMD"],
    title="NVDA vs AMD Daily Returns"
)

st.plotly_chart(fig_nvda_amd, use_container_width=True)

# ------------------------
# ETF Synchronization
# ------------------------

st.header("ETF Synchronization: SMH vs SOXX")

fig_etf = px.line(
    returns_df,
    x="Date",
    y=["SMH", "SOXX"],
    title="Semiconductor ETF Daily Returns"
)

st.plotly_chart(fig_etf, use_container_width=True)

# ------------------------
# Rolling Correlations
# ------------------------

st.header("Rolling Correlation Signals")

fig_corr = px.line(
    bubble_df,
    x="Date",
    y=[
        "nvda_amd_rolling_corr",
        "smh_soxx_rolling_corr"
    ],
    title="Rolling Correlation: NVDA-AMD vs SMH-SOXX"
)

st.plotly_chart(fig_corr, use_container_width=True)

# ------------------------
# Latest Interpretation
# ------------------------

st.header("Latest Market Interpretation")

if latest_score < 30:
    status = "Normal"
    explanation = "AI assets are not showing strong synchronized speculative behaviour."
elif latest_score < 60:
    status = "Elevated Synchronization"
    explanation = "AI assets are showing increased co-movement, suggesting rising thematic market concentration."
elif latest_score < 80:
    status = "Speculative Momentum"
    explanation = "AI stocks and semiconductor ETFs are moving together strongly, indicating possible contagion behaviour."
else:
    status = "High Bubble Risk"
    explanation = "AI-related equities show very high synchronization and momentum, suggesting elevated bubble-like behaviour."

st.subheader(f"Current Status: {status}")
st.write(explanation)

# ------------------------
# Project Summary
# ------------------------

st.header("Project Summary")

st.markdown("""
This dashboard investigates whether AI-related equities move as a synchronized market theme.

The analysis focuses on:

1. **NVIDIA shock events**
2. **AMD and semiconductor stock reactions**
3. **ETF synchronization through SMH and SOXX**
4. **Rolling correlation patterns**
5. **Bubble risk scoring**

The goal is not to predict stock prices, but to identify whether AI-linked equities display
contagion-like behaviour associated with speculative market concentration.
""")