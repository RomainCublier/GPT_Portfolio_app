"""Streamlit module for single-asset analysis."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from core.metrics import drawdown_curve
from core.returns import compute_returns
from config import assumptions
from utils.data_loader import download_price_data, fetch_asset_profile
from utils.metrics import compute_asset_metrics
from utils.streamlit_helpers import handle_network_error

PERIOD_MAPPING = {
    "1 month": "1mo",
    "3 months": "3mo",
    "6 months": "6mo",
    "1 year": "1y",
    "2 years": "2y",
    "5 years": "5y",
    "10 years": "10y",
    "Max": "max",
}

EXPECTED_DAYS = {
    "1 month": 30,
    "3 months": 90,
    "6 months": 180,
    "1 year": 365,
    "2 years": 365 * 2,
    "5 years": 365 * 5,
    "10 years": 365 * 10,
}


def run_stock_analyzer():
    st.header("📈 Stock Analyzer (Yahoo Finance)")
    st.write(
        "Analyze stocks, ETFs, or cryptos using free Yahoo Finance data — no API key required."
    )

    ticker = st.text_input("Ticker (e.g., AAPL, MSFT, SPY, BTC-USD)", "AAPL")
    period_options = list(PERIOD_MAPPING.keys())
    default_index = period_options.index("5 years") if "5 years" in period_options else 0
    period_label = st.selectbox("History period", period_options, index=default_index)

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

    def _period_return(prices: pd.Series, days: int) -> float | None:
        if len(prices) <= days:
            return None
        return prices.iloc[-1] / prices.iloc[-(days + 1)] - 1

    def _ytd_return(prices: pd.Series) -> float | None:
        if prices.empty:
            return None
        year_start = pd.Timestamp(prices.index[-1].year, 1, 1)
        subset = prices[prices.index >= year_start]
        if subset.shape[0] < 2:
            return None
        return subset.iloc[-1] / subset.iloc[0] - 1

    def _beta_and_correlation(asset_ret: pd.Series, bench_ret: pd.Series) -> tuple[float | None, float | None]:
        if asset_ret.empty or bench_ret.empty:
            return None, None
        covariance = asset_ret.cov(bench_ret)
        variance = bench_ret.var()
        beta = covariance / variance if variance and not pd.isna(variance) else None
        correlation = asset_ret.corr(bench_ret)
        return beta, correlation

    if st.button("Analyze"):
        try:
            yf_period = PERIOD_MAPPING.get(period_label, "5y") or "5y"

            df = download_price_data(
                [ticker],
                start=None if yf_period else assumptions.DEFAULT_START_DATE,
                end=None,
                period=yf_period,
            )

            if df.empty:
                st.error("❌ Invalid ticker or no data available.")
                return

            coverage_days = (df.index.max() - df.index.min()).days if len(df.index) else 0
            expected_days = EXPECTED_DAYS.get(period_label)
            if expected_days and coverage_days < expected_days * 0.6:
                st.warning(
                    "Price history looks shorter than requested. Showing the longest available window."
                )

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

            df = df.sort_index()
            price_series = df[ticker].dropna()
            if price_series.empty:
                st.error("No price history available after cleaning.")
                return
            if price_series.shape[0] < 2:
                st.error("Not enough observations to compute metrics for this asset.")
                return

            df["Date"] = df.index
            st.subheader(f"{ticker} — Historique des prix")
            fig = px.line(df, x="Date", y=ticker, title=f"{ticker} Price Chart")
            st.plotly_chart(fig, use_container_width=True)

            returns_series = price_series.pct_change().dropna()
            st.subheader("📊 Performance Snapshot")

            period_returns = {
                "1W": _period_return(price_series, 5),
                "1M": _period_return(price_series, 21),
                "3M": _period_return(price_series, 63),
                "YTD": _ytd_return(price_series),
                "1Y": _period_return(price_series, 252),
                "3Y": _period_return(price_series, 252 * 3),
                "5Y": _period_return(price_series, 252 * 5),
            }

            snapshot_rows = []
            for label, value in period_returns.items():
                if value is None:
                    continue
                snapshot_rows.append({"Metric": f"Return {label}", "Value": f"{value * 100:.2f}%"})

            metrics = compute_asset_metrics(price_series)
            snapshot_rows.extend(
                [
                    {"Metric": "CAGR", "Value": f"{metrics['CAGR'] * 100:.2f}%"},
                    {
                        "Metric": "Annualized Volatility",
                        "Value": f"{metrics['Volatility (ann.)'] * 100:.2f}%",
                    },
                    {"Metric": "Max Drawdown", "Value": f"{metrics['Max Drawdown'] * 100:.2f}%"},
                ]
            )

            if snapshot_rows:
                st.dataframe(pd.DataFrame(snapshot_rows), hide_index=True)
            else:
                st.info("Not enough data to compute performance metrics.")

            st.subheader("📌 Risk vs Benchmark (SPY)")
            benchmark_series = None
            try:
                bench_df = download_price_data(
                    [ticker, "SPY"],
                    start=None if yf_period else assumptions.DEFAULT_START_DATE,
                    end=None,
                    period=yf_period,
                )
                if "SPY" in bench_df.columns:
                    benchmark_series = bench_df["SPY"].dropna()
            except Exception as bench_exc:  # noqa: BLE001
                st.warning(f"Unable to load benchmark data: {handle_network_error(bench_exc)}")

            if benchmark_series is not None and not benchmark_series.empty:
                combined_prices = pd.concat([price_series, benchmark_series], axis=1, join="inner").dropna()
                if combined_prices.shape[0] < 10:
                    st.warning("Not enough overlapping data with SPY for risk comparison.")
                else:
                    combined_prices.columns = [ticker, "SPY"]
                    paired_returns = compute_returns(combined_prices)
                    beta, correlation = _beta_and_correlation(
                        paired_returns[ticker], paired_returns["SPY"]
                    )
                    col1, col2 = st.columns(2)
                    col1.metric("Beta vs SPY", f"{beta:.2f}" if beta is not None else "N/A")
                    col2.metric(
                        "Correlation vs SPY",
                        f"{correlation:.2f}" if correlation is not None else "N/A",
                    )
            else:
                st.info("Benchmark data unavailable for SPY with the selected window.")

            st.subheader("📉 Drawdown profile")
            if returns_series.empty:
                st.info("Not enough returns history to compute drawdowns.")
            else:
                drawdown_series = drawdown_curve(returns_series)
                draw_fig = go.Figure()
                draw_fig.add_trace(
                    go.Scatter(
                        x=drawdown_series.index,
                        y=drawdown_series.values,
                        fill="tozeroy",
                        mode="lines",
                        name="Drawdown",
                        line_color="#EF553B",
                    )
                )
                draw_fig.update_layout(
                    template="plotly_white",
                    yaxis_title="Drawdown",
                    xaxis_title="Date",
                )
                st.plotly_chart(draw_fig, use_container_width=True)

        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Error during analysis: {handle_network_error(exc)}")
