import streamlit as st
import pandas as pd
from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import backtest_portfolio
from stock_analyzer import analyze_stock

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="GPT Portfolio Assistant",
    page_icon="📈",
    layout="wide"
)

st.title("🤖 GPT Portfolio Assistant — AI Investment App")

# =============================
# 1️⃣  PORTFOLIO GENERATOR
# =============================
st.header("📊 AI Portfolio Generator")

with st.container():
    st.subheader("Investor Profile")

    capital = st.number_input("Capital (€)", min_value=1000, max_value=10_000_000, value=10000)

    risk_level = st.selectbox("Risk Level", ["Low", "Moderate", "High"])
    horizon_value = st.selectbox("Investment Horizon", ["Short", "Medium", "Long"])
    esg_flag = st.checkbox("Include ESG constraints")

    api_key = st.text_input("🔑 Enter your OpenAI API Key (never stored)", type="password")

    if st.button("Generate Portfolio"):
        if api_key.strip() == "":
            st.error("❌ Please enter an API key.")
        else:
            try:
                df_allocation = generate_portfolio_allocation(
                    api_key=api_key,
                    capital=capital,
                    horizon=horizon_value,
                    risque=risk_level,
                    esg=esg_flag
                )

                st.success("Portfolio generated successfully!")

                st.subheader("📈 Allocation Results")
                st.dataframe(df_allocation)

            except Exception as e:
                st.error(f"❌ Error during calculation : {e}")

# =============================
# 2️⃣  STOCK ANALYZER (GPT)
# =============================

st.header("🔎 Stock Analyzer — GPT Investment Trainer")

ticker = st.text_input("Enter a stock/ETF ticker (ex: AAPL, MSFT, SPY)")

if st.button("Analyze Stock"):
    if api_key.strip() == "":
        st.error("❌ Please enter an API key above.")
    else:
        try:
            result = analyze_stock(api_key, ticker)
            st.subheader(f"📌 Analysis for {ticker.upper()}")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Error analyzing stock : {e}")

# =============================
# 3️⃣  PORTFOLIO BACKTEST
# =============================

st.header("📉 Portfolio Backtest")

uploaded_file = st.file_uploader(
    "Upload a CSV with columns: Ticker, Allocation",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("📄 Uploaded Portfolio:")
        st.dataframe(df)

        st.subheader("📊 Backtest Results")
        results = run_backtest(df)

        st.line_chart(results)

    except Exception as e:
        st.error(f"❌ Error in backtest : {e}")

st.markdown("---")
st.markdown("Created with ❤️ — GPT Portfolio App 2025")
