import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px


def run_stock_analyzer():

    st.header("📈 Stock Analyzer (no API, Yahoo Finance only)")
    st.write(
        "Analyze stocks, ETFs, or cryptos using free Yahoo Finance data — "
        "no API key required."
    )

    # --- USER INPUTS ---
    ticker = st.text_input("Ticker (e.g., AAPL, MSFT, SPY, BTC-USD)", "AAPL")

    period_label = st.selectbox(
        "History period",
        ["1 year", "5 years", "10 years", "Max history"],
        index=1
    )

    # Convert label to yfinance format
    period_map = {
        "1 year": "1y",
        "5 years": "5y",
        "10 years": "10y",
        "Max history": "max"
    }
    yf_period = period_map[period_label]

    # --- ANALYZE BUTTON ---
    if st.button("Analyze"):

        try:
            # Download data
            df = yf.download(ticker, period=yf_period)

            if df.empty:
                st.error("❌ Invalid ticker or no data available.")
                return

            df["Date"] = df.index

            # --- PRICE CHART ---
            st.subheader(f"{ticker} Price History")
            fig = px.line(
                df,
                x="Date",
                y="Adj Close",
                title=f"{ticker} Price Chart"
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- PERFORMANCE METRICS ---
            st.subheader("📊 Performance Metrics")

            df["Daily Return"] = df["Adj Close"].pct_change()
            df = df.dropna()

            # CAGR
            start_price = df["Adj Close"].iloc[0]
            end_price = df["Adj Close"].iloc[-1]
            years = len(df) / 252
            cagr = (end_price / start_price) ** (1 / years) - 1

            # Annualized Volatility
            vol = df["Daily Return"].std() * (252 ** 0.5)

            # Sharpe Ratio (rf = 0)
            sharpe = cagr / vol if vol != 0 else 0

            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("CAGR", f"{cagr * 100:.2f}%")
            col2.metric("Volatility (ann.)", f"{vol * 100:.2f}%")
            col3.metric("Sharpe Ratio", f"{sharpe:.2f}")

        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")
