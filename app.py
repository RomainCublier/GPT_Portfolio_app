import streamlit as st
import pandas as pd
import yfinance as yf

from portfolio_engine import run_backtest
from gpt_allocation import generate_portfolio_allocation
from stock_analyzer import run_stock_analyzer


# ============================================
# 🎨 GENERAL PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="GPT Portfolio Assistant — AI Investment App",
    layout="wide",
)


# ============================================
# 🧭 SIDEBAR NAVIGATION
# ============================================
st.sidebar.title("📌 Navigation")
page = st.sidebar.selectbox(
    "Menu",
    ["Portfolio Generator", "Portfolio Backtest", "Stock Analyzer"],
)


# ============================================
# 📌 PAGE 1 — PORTFOLIO GENERATOR
# ============================================
if page == "Portfolio Generator":
    st.title("🤖 AI Portfolio Generator (No API Needed)")

    st.subheader("Investor Profile")

    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input("Capital to invest (€)", min_value=100, value=10000)

    with col2:
        risk = st.selectbox("Risk Level", ["Low", "Moderate", "High"])

    horizon = st.selectbox(
        "Investment Horizon",
        ["Short (<3 years)", "Medium (3-5 years)", "Long (>5 years)"]
    )

    esg = st.checkbox("Include ESG constraints?")

    if st.button("Generate Portfolio"):
        try:
            df_alloc = generate_portfolio_allocation(capital, risk, horizon, esg)

            st.success("Portfolio generated successfully!")
            st.subheader("📊 Allocation Results")
            st.dataframe(df_alloc)

            # Compute invested € column
            df_alloc["Invested (€)"] = df_alloc["Allocation (%)"] * capital / 100
            st.dataframe(df_alloc)

            st.subheader("📈 Backtest of Generated Portfolio")
            fig, stats = run_backtest(df_alloc)
            st.plotly_chart(fig, use_container_width=True)
            st.write(stats)

        except Exception as e:
            st.error(f"❌ Error during calculation: {e}")


# ============================================
# 📌 PAGE 2 — PORTFOLIO BACKTEST (UPLOAD)
# ============================================
elif page == "Portfolio Backtest":
    st.title("📈 Portfolio Backtest (Upload Your Own Allocation)")

    st.write("Upload a CSV with columns **Ticker** and **Allocation (%)**.")

    uploaded_file = st.file_uploader("Upload Portfolio CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df_user = pd.read_csv(uploaded_file)

            # Clean column names
            df_user.columns = [c.strip().capitalize() for c in df_user.columns]

            st.subheader("Uploaded Portfolio")
            st.dataframe(df_user)

            fig, stats = run_backtest(df_user)

            st.subheader("Backtest Results")
            st.plotly_chart(fig, use_container_width=True)
            st.write(stats)

        except Exception as e:
            st.error(f"❌ Error during backtest: {e}")


# ============================================
# 📌 PAGE 3 — STOCK ANALYZER (NO API)
# ============================================
elif page == "Stock Analyzer":
    st.title("🔍 Stock Analyzer (no API, Yahoo Finance only)")
    run_stock_analyzer()

