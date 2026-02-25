import streamlit as st

from config.assumptions import APP_NAME

st.set_page_config(page_title=f"{APP_NAME} — AI Investment App", layout="wide")

if hasattr(st, "navigation") and hasattr(st, "Page"):
    pages = [
        st.Page("pages/portfolio_generator.py", title="Portfolio Generator", icon="🤖"),
        st.Page("pages/etf_due_diligence.py", title="ETF & Fund Due Diligence", icon="🧾"),
        st.Page("pages/asset_analysis.py", title="Asset Analysis", icon="📈"),
        st.Page("pages/risk_lab.py", title="Risk Lab", icon="🧮"),
    ]
    navigation = st.navigation(pages, position="sidebar")
    navigation.run()
else:
    st.title("🤖 GPT Portfolio Assistant")
    st.write(
        """
        Bienvenue ! Utilisez le menu latéral (pages Streamlit) pour :

        * Générer automatiquement un portefeuille ETF en fonction de votre profil.
        * Accéder au Risk Lab pour analyser le risque et la performance de votre portefeuille.
        * Analyser un actif (action, ETF, crypto) avec les données Yahoo Finance.
        """
    )
    st.warning(
        "Votre version Streamlit est ancienne : navigation avancée indisponible. "
        "Le site reste accessible via le menu multipage standard."
    )
