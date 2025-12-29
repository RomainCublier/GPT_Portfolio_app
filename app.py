import streamlit as st

from config.assumptions import APP_NAME

st.set_page_config(page_title=f"{APP_NAME} — AI Investment App", layout="wide")

st.title("🤖 GPT Portfolio Assistant")
st.write(
    """
    Bienvenue ! Utilisez le menu latéral (pages Streamlit) pour :

    * Générer automatiquement un portefeuille ETF en fonction de votre profil.
    * Backtester une allocation personnelle uploadée en CSV.
    * Analyser un actif (action, ETF, crypto) avec les données Yahoo Finance.
    """
)

st.success("Sélectionnez une page dans la barre latérale pour commencer.")
