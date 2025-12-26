import pandas as pd
import streamlit as st

from portfolio_engine import backtest_portfolio
from utils.streamlit_helpers import handle_network_error

st.title("📈 Portfolio Backtest (Upload Your Own Allocation)")
st.write("Upload a CSV with columns **Ticker** and **Allocation (%)**.")

uploaded_file = st.file_uploader("Upload Portfolio CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df_user = pd.read_csv(uploaded_file)
        df_user.columns = [c.strip().capitalize() for c in df_user.columns]

        st.subheader("Uploaded Portfolio")
        st.dataframe(df_user)

        fig, stats = backtest_portfolio(df_user)
        st.subheader("Backtest Results")
        st.plotly_chart(fig, use_container_width=True)
        st.write(stats)

    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Error during backtest: {handle_network_error(exc)}")
