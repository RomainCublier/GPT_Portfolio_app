import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf

# === IMPORT DE TES MODULES ===
from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import run_backtest
from stock_analyzer import analyze_stock, chart_revenues


# ============================
#   CONFIGURATION GÉNÉRALE
# ============================
st.set_page_config(
    page_title="GPT Portfolio Assistant",
    layout="wide",
    page_icon="📈"
)

st.title("📈 GPT Portfolio Assistant — AI Investment App")


# ============================
#       MENU LATERAL
# ============================
menu = st.sidebar.selectbox(
    "Navigation",
    ["Portfolio IA", "Backtest", "Stock Analyzer"]
)


# ==========================================================
#  1️⃣ PAGE ALLOCATION IA : GPT génère l'allocation ETF
# ==========================================================
if menu == "Portfolio IA":

    st.header("🤖 AI Portfolio Generator")

    capital = st.number_input("Capital (€)", min_value=1000, value=10000)
    risk = st.selectbox("Risk Level", ["Low", "Medium", "High"])
    horizon = st.selectbox("Investment Horizon", ["Short", "Medium", "Long"])
    esg = st.checkbox("Include ESG constraints")

    api_key = st.secrets["OPENAI_API_KEY"]

    if st.button("Generate Portfolio"):
        try:
            with st.spinner("GPT is generating your optimized portfolio..."):
                df, explanation = generate_portfolio_allocation(
                    api_key=api_key,
                    capital=capital,
                    risk=risk,
                    horizon=horizon,
                    esg=esg
                )

            st.subheader("📊 Suggested Portfolio Allocation")
            st.dataframe(df)

            st.subheader("🧠 GPT Explanation")
            st.info(explanation)

        except Exception as e:
            st.error(f"❌ Erreur lors du calcul : {e}")


# ==========================================================
#   2️⃣ PAGE BACKTEST : calcul historique du portefeuille
# ==========================================================
elif menu == "Backtest":

    st.header("📉 Portfolio Backtest")

    st.write("Upload an allocation file or paste a table.")

    file = st.file_uploader("Upload CSV with columns: Ticker, Allocation (%)")

    if file:
        try:
            df_alloc = pd.read_csv(file)
            st.dataframe(df_alloc)

            with st.spinner("Running backtest..."):
                fig, metrics = run_backtest(df_alloc)

            st.subheader("📈 Portfolio Performance")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📊 Performance Metrics")
            st.write(metrics)

        except Exception as e:
            st.error(f"❌ Error during backtest : {e}")


# ==========================================================
#   3️⃣ PAGE STOCK ANALYZER — GPT Investment Trainer
# ==========================================================
elif menu == "Stock Analyzer":

    st.header("🔎 Stock Analyzer — GPT Investment Trainer")

    api_key = st.secrets["OPENAI_API_KEY"]
    ticker = st.text_input("Enter stock ticker (AAPL, MSFT, NVDA, LVMH.PA)", "")

    if st.button("Analyze Stock"):
        if ticker == "":
            st.error("Please enter a ticker.")
        else:
            try:
                with st.spinner("GPT analyzing the stock fundamentals..."):
                    res = analyze_stock(api_key, ticker)

                st.subheader("📘 GPT Summary")
                st.info(res["summary"])

                st.subheader("📊 10-Year Revenue Chart")
                fig = chart_revenues(res["financials"])
                st.plotly_chart(fig)

            except Exception as e:
                st.error(f"❌ Cannot analyze stock : {e}")
