"""Portfolio backtesting utilities using Yahoo Finance data."""

import pandas as pd
import plotly.graph_objects as go

from config.assumptions import DEFAULT_END_DATE, DEFAULT_START_DATE
from utils.data_loader import download_price_data, ensure_valid_tickers
from utils.metrics import compute_portfolio_metrics
from utils.streamlit_helpers import allocation_percent_to_weights


def backtest_portfolio(df_allocation: pd.DataFrame):
    """Backtest a portfolio allocation dataframe.

    The input dataframe must contain at least ``Ticker`` and ``Allocation (%)`` columns.
    A ``Poids`` column will be created automatically from the percentage weights.
    """

    df_alloc = allocation_percent_to_weights(df_allocation)
    df_alloc = df_alloc[df_alloc["Poids"] > 0].copy()

    if df_alloc.empty:
        raise ValueError("Portfolio has no positive weights to backtest.")

    tickers = df_alloc["Ticker"].tolist()
    weights = df_alloc["Poids"].tolist()

    data = download_price_data(tickers, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE)
    valid_tickers = ensure_valid_tickers(data, tickers)

    weights = [w for t, w in zip(tickers, weights) if t in valid_tickers]
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("No positive weights remain after filtering unavailable tickers.")
    weights = [w / total_weight for w in weights]
    data = data[valid_tickers]

    normalized = data / data.iloc[0]
    portfolio = (normalized * weights).sum(axis=1)

    metrics = compute_portfolio_metrics(portfolio)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio.index, y=portfolio, mode="lines", name="Portefeuille"))
    fig.update_layout(
        title="📈 Performance du portefeuille",
        xaxis_title="Date",
        yaxis_title="Valeur normalisée",
        template="plotly_white",
    )

    return fig, metrics
