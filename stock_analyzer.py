"""Streamlit module for single-asset analysis."""

import streamlit as st
import plotly.express as px

from config import assumptions
from utils.data_loader import download_price_data
from utils.metrics import compute_asset_metrics
from utils.streamlit_helpers import handle_network_error


def run_stock_analyzer():
    st.header("📈 Stock Analyzer (Yahoo Finance)")
    st.write(
        "Analyze stocks, ETFs, or cryptos using free Yahoo Finance data — no API key required."
    )

    ticker = st.text_input("Ticker (e.g., AAPL, MSFT, SPY, BTC-USD)", "AAPL")
    period_label = st.selectbox(
        "History period",
        ["1 year", "5 years", "10 years", "Max history"],
        index=1,
    )

    period_map = {
        "1 year": "365D",
        "5 years": "5Y",
        "10 years": "10Y",
        "Max history": None,
    }

    if st.button("Analyze"):
        try:
            if period_map[period_label]:
                df = download_price_data([ticker], start=None, end=None)
                df = df.last(period_map[period_label])
            else:
                df = download_price_data([ticker], start=assumptions.DEFAULT_START_DATE, end=None)

            if df.empty:
                st.error("❌ Invalid ticker or no data available.")
                return

            df["Date"] = df.index
            st.subheader(f"{ticker} Price History")
            fig = px.line(df, x="Date", y=ticker, title=f"{ticker} Price Chart")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📊 Performance Metrics")
            metrics = compute_asset_metrics(df[ticker])
            col1, col2, col3 = st.columns(3)
            col1.metric("CAGR", f"{metrics['CAGR'] * 100:.2f}%")
            col2.metric("Volatility (ann.)", f"{metrics['Volatility (ann.)'] * 100:.2f}%")
            col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")

        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Error during analysis: {handle_network_error(exc)}")
