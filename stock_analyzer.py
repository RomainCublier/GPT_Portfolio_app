"""Streamlit module for single-asset analysis."""

import streamlit as st
import plotly.express as px
import pandas as pd

from config import assumptions
from utils.data_loader import download_price_data, fetch_asset_profile
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

    period_offset_map = {
        "1 year": "365D",
        "5 years": "5Y",
        "10 years": "10Y",
        "Max history": None,
    }

    def _format_large_number(value: float) -> str:
        """Human readable large-number formatter (e.g., market cap)."""

        try:
            value = float(value)
        except (TypeError, ValueError):
            return "N/A"

        for suffix in ["", "K", "M", "B", "T"]:
            if abs(value) < 1000:
                return f"{value:,.0f}{suffix}"
            value /= 1000
        return f"{value:,.0f}P"

    if st.button("Analyze"):
        try:
            period_offset = period_offset_map[period_label]

            df = download_price_data(
                [ticker],
                start=assumptions.DEFAULT_START_DATE if period_offset is None else None,
                end=None,
            )

            if period_offset:
                df = df.last(period_offset)

            if df.empty:
                st.error("❌ Invalid ticker or no data available.")
                return

            profile = None
            try:
                profile = fetch_asset_profile(ticker)
            except Exception as profile_err:  # noqa: BLE001
                st.warning(f"ℹ️ Impossible de récupérer la description de l'actif: {profile_err}")

            if profile:
                st.subheader("🧾 Aperçu détaillé de l'actif")
                st.markdown(
                    f"**{profile.get('name', ticker)}** — {profile.get('instrument_type', 'Instrument')}\n"
                    f"Cotation: {profile.get('exchange', 'N/A')} | Devise: {profile.get('currency', 'N/A')}"
                )

                cols = st.columns(3)
                cols[0].metric("Secteur", profile.get("sector", "N/A"))
                cols[1].metric("Industrie", profile.get("industry", "N/A"))
                cols[2].metric("Pays", profile.get("country", "N/A"))

                cols = st.columns(3)
                cols[0].metric("Effectifs", _format_large_number(profile.get("fullTimeEmployees")))
                cols[1].metric("Market Cap", _format_large_number(profile.get("marketCap")))
                cols[2].metric("Site web", profile.get("website", "N/A"))

                inception_date = profile.get("first_trade_date")
                if inception_date:
                    inception_date = pd.to_datetime(inception_date, unit="s").date()
                    st.info(f"🗓️ Première cotation: {inception_date}")

                summary = profile.get("summary")
                if summary:
                    st.write(summary)

                st.markdown(
                    """
                    **Ce que représente cet actif**  \
                    • Nature de l'instrument (action, ETF, crypto) et place de cotation.  \
                    • Couverture sectorielle et zone géographique.  \
                    • Objectif économique : comment l'entreprise/indice génère de la valeur.  \
                    • Risques clés potentiels (volatilité de marché, exposition devises, cycle économique).
                    """
                )

            df["Date"] = df.index
            st.subheader(f"{ticker} — Historique des prix")
            fig = px.line(df, x="Date", y=ticker, title=f"{ticker} Price Chart")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📊 Performance et diagnostics")
            metrics = compute_asset_metrics(df[ticker])
            col1, col2, col3 = st.columns(3)
            col1.metric("CAGR", f"{metrics['CAGR'] * 100:.2f}%")
            col2.metric("Volatilité (ann.)", f"{metrics['Volatility (ann.)'] * 100:.2f}%")
            col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Max Drawdown", f"{metrics['Max Drawdown'] * 100:.2f}%")
            col2.metric("Best Day", f"{metrics['Best Day'] * 100:.2f}%")
            col3.metric("Worst Day", f"{metrics['Worst Day'] * 100:.2f}%")

            st.markdown(
                """
                **Lecture rapide des métriques**  \
                • CAGR & Sharpe = rendement annualisé et ajusté du risque.  \
                • Max Drawdown = perte maximale en cours de route, utile pour mesurer la tolérance au stress.  \
                • Best/Worst Day = amplitude des chocs journaliers, indicateur de la nervosité du titre.
                """
            )

        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Error during analysis: {handle_network_error(exc)}")
