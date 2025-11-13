import streamlit as st
import pandas as pd
import yfinance as yf
from openai import OpenAI
from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import backtest_portfolio
from stock_analyzer import analyze_stock

# Load API key from Streamlit Secrets
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="GPT Portfolio Assistant", layout="wide")

st.title("📈 GPT Portfolio Assistant — AI Investment App")


# ----------------------------
# TAB NAVIGATION
# ----------------------------
tab1, tab2, tab3 = st.tabs([
    "🚀 AI Portfolio Generator",
    "📊 Portfolio Backtest",
    "🔎 Stock Analyzer (GPT Trainer)"
])


# ============================================================
# 🚀 1. PORTFOLIO GENERATOR
# ============================================================
with tab1:
    st.header("🤖 AI Portfolio Generator")

    capital = st.number_input("Capital (€)", min_value=100, value=10000, step=100)

    risk = st.selectbox("Risk Level", ["Low", "Moderate", "High"])
    horizon = st.selectbox("Investment Horizon", ["Short", "Medium", "Long"])
    esg = st.checkbox("Include ESG constraints")

    if st.button("Generate Portfolio"):
        try:
            # ⬅️ Assure-toi d'avoir ces variables avant :
# capital  -> float ou int
# risk_level -> "Low" / "Medium" / "High"  (par ex.)
# horizon_value -> "Short" / "Medium" / "Long"
# esg_flag -> booléen True/False
# api_key -> ta clé OpenAI (depuis st.secrets ou un text_input)

df_allocation = generate_portfolio_allocation(
    api_key=api_key,          # 1. ta clé OpenAI
    capital=capital,          # 2. le capital saisi en €
    horizon=horizon_value,    # 3. ton horizon d’investissement
    risque=risk_level,        # 4. le niveau de risque (nom du param = "risque")
    esg=esg_flag,             # 5. True/False selon la case ESG
)

            st.success("Allocation generated!")
            st.dataframe(df_alloc)

        except Exception as e:
            st.error(f"❌ Error during calculation : {e}")


# ============================================================
# 📊 2. PORTFOLIO BACKTEST
# ============================================================
with tab2:
    st.header("📊 Portfolio Backtest")

    st.write("Upload a CSV with columns: **Ticker, Allocation**")

    uploaded = st.file_uploader("Upload Portfolio CSV", type=["csv"])

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.dataframe(df)

            tickers = df["Ticker"].tolist()
            weights = df["Allocation"].tolist()

            st.info("Running backtest...")

            fig = run_backtest(tickers, weights)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error during backtest: {e}")


# ============================================================
# 🔎 3. STOCK ANALYZER
# ============================================================
with tab3:
    st.header("🔎 Stock Analyzer — GPT Investment Trainer")

    ticker = st.text_input("Enter stock ticker (ex: AAPL, TSLA, NVDA):")

    if st.button("Analyze stock"):
        try:
            result = analyze_stock(ticker, client)
            st.success("Analysis complete!")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Error : {e}")
