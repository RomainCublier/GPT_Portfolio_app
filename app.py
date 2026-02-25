import streamlit as st

from config.assumptions import APP_NAME

st.set_page_config(page_title=f"{APP_NAME} — AI Investment App", layout="wide")

navigation = st.navigation(
    [
        st.Page("pages/portfolio_generator.py", title="Portfolio Generator", icon="🤖"),
        st.Page("pages/etf_due_diligence.py", title="ETF Due Diligence", icon="🧾"),
        st.Page("pages/asset_analysis.py", title="Asset Analysis", icon="📈"),
        st.Page("pages/risk_lab.py", title="Risk Lab", icon="🧮"),
    ],
    position="sidebar",
)

navigation.run()
