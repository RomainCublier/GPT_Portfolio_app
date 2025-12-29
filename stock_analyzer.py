"""Streamlit module for single-asset analysis."""

import streamlit as st
import plotly.express as px
import pandas as pd

from config import assumptions
from utils.data_loader import download_price_data, fetch_asset_profile
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
        "1 year": 1,
        "5 years": 5,
        "10 years": 10,
        "1 year": "365D",
        "5 years": "5Y",
        "10 years": "10Y",
        "Max history": None,
    }

    if st.button("Analyze"):
        try:
            years = period_map[period_label]
            if years:
                start_date = (pd.Timestamp.today() - pd.DateOffset(years=years)).date().isoformat()
            else:
                start_date = assumptions.DEFAULT_START_DATE

            df = download_price_data([ticker], start=start_date, end=None)
            if period_map[period_label]:
                df = download_price_data([ticker], start=None, end=None)
                df = df.last(period_map[period_label])
            else:
                df = download_price_data([ticker], start=assumptions.DEFAULT_START_DATE, end=None)

            if df.empty:
                st.error("❌ Invalid ticker or no data available.")
                return

            profile = None
            try:
                profile = fetch_asset_profile(ticker)
            except Exception as profile_err:  # noqa: BLE001
                st.warning(f"ℹ️ Impossible de récupérer la description de l'actif: {profile_err}")

            if profile:
                st.subheader("🧾 Aperçu de l'actif")
                st.markdown(
                    f"**{profile.get('name', ticker)}** — {profile.get('instrument_type', 'Instrument')} \n"
                    f"Cote: {profile.get('exchange', 'N/A')} | Devise: {profile.get('currency', 'N/A')}"
                )
                inception_date = profile.get("first_trade_date")
                if inception_date:
                    inception_date = pd.to_datetime(inception_date, unit="s").date()
                    st.write(f"🗓️ Première cotation: {inception_date}")
                summary = profile.get("summary")
                if summary:
                    st.write(summary)

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
