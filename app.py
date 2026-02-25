import streamlit as st

from config.assumptions import APP_NAME
from pages import etf_due_diligence

st.set_page_config(page_title=f"{APP_NAME} — AI Investment App", layout="wide")


PAGES = [
    st.Page("pages/portfolio_generator.py", title="Portfolio Generator", icon="🤖"),
    st.Page("pages/etf_due_diligence.py", title="ETF & Fund Due Diligence", icon="🧾"),
    st.Page("pages/asset_analysis.py", title="Asset Analysis", icon="📈"),
    st.Page("pages/risk_lab.py", title="Risk Lab", icon="🧮"),
]


if hasattr(st, "navigation"):
    navigation = st.navigation(PAGES, position="sidebar")
    navigation.run()
else:
    st.title("🤖 GPT Portfolio Assistant")
    st.warning(
        "Your Streamlit version is too old for programmatic navigation. "
        "Please upgrade Streamlit (>=1.36) or use the sidebar multipage menu."
    )
navigation = st.navigation(
    [
        st.Page("pages/portfolio_generator.py", title="Portfolio Generator", icon="🤖"),
        st.Page(etf_due_diligence.main, title="ETF & Fund Due Diligence", icon="🧾"),
        st.Page("pages/etf_due_diligence.py", title="ETF & Fund Due Diligence", icon="🧾"),
        st.Page("pages/asset_analysis.py", title="Asset Analysis", icon="📈"),
        st.Page("pages/risk_lab.py", title="Risk Lab", icon="🧮"),
    ],
    position="sidebar",
)

navigation.run()
