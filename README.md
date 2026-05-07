# AI Bubble Contagion Dashboard

## Thesis

AI stock valuations are increasingly driven by synchronized institutional flows, ETF concentration, and thematic market contagion rather than isolated firm fundamentals.

---

# Project Overview

This project analyzes whether AI-related equities exhibit synchronized market behaviour associated with speculative momentum and sector-wide contagion.

The dashboard investigates:

- AI stock correlations
- NVIDIA-driven market contagion
- Semiconductor ETF synchronization
- Rolling correlation dynamics
- Bubble risk scoring

The goal is not to predict stock prices, but to identify whether AI-linked assets display bubble-like synchronization patterns.

---

# Features

## Market Data Pipeline
- Historical AI stock data collection
- ETF tracking
- Daily returns generation

## Correlation Analysis
- Correlation heatmaps
- Rolling correlation detection
- AI sector synchronization analysis

## Contagion Detection
- NVIDIA shock-event analysis
- ETF contagion monitoring
- Cross-asset synchronization tracking

## Bubble Risk Engine
- Bubble score calculation
- Momentum analysis
- Rolling synchronization scoring

## Interactive Dashboard
- Bubble risk gauge
- Correlation visualization
- ETF synchronization charts
- Rolling contagion analysis

---

# AI Stocks & ETFs Tracked

## AI & Semiconductor Stocks
- NVDA
- AMD
- AVGO
- TSM
- ARM
- PLTR
- MSFT

## ETFs
- SMH
- SOXX
- QQQ
- SPY

---

# Tech Stack

## Languages & Libraries
- Python
- pandas
- numpy

## Financial Data
- yFinance

## Visualization
- Streamlit
- Plotly
- Matplotlib
- Seaborn

## Machine Learning & Analytics
- scikit-learn

---

# Project Structure

```text
ai-bubble-contagion-dashboard/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data_collection.py
│   ├── correlation_engine.py
│   ├── heatmap_analysis.py
│   ├── rolling_correlation.py
│   ├── event_analysis.py
│   └── bubble_score.py
│
├── dashboard/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore

