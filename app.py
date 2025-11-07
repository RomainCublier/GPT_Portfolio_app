# app.py

import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# Import des fonctions du projet
from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import backtest_portfolio

# ===============================
# ⚙️ CONFIGURATION DE L'APPLICATION
# ===============================
st.set_page_config(page_title="GPT Portfolio Assistant", layout="wide")
st.title("🤖 GPT Portfolio Assistant")
st.markdown("**Crée ton portefeuille optimal avec l’aide de l’IA !**")

# Chargement de la clé OpenAI
load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    st.success("🔑 Clé API chargée avec succès")
else:
    st.error("❌ Aucune clé API trouvée dans ton fichier .env")

# ===============================
# 🧭 SECTION : PROFIL UTILISATEUR
# ===============================
st.sidebar.header("🧭 Profil Investisseur")

capital = st.sidebar.number_input("💰 Capital à investir (€)", min_value=1000, value=10000, step=1000)
horizon = st.sidebar.selectbox("⏳ Horizon d’investissement", ["Court terme (<2 ans)", "Moyen terme (2-5 ans)", "Long terme (>5 ans)"])
risk = st.sidebar.select_slider("⚖️ Niveau de risque", options=["Faible", "Modéré", "Élevé"], value="Modéré")
esg = st.sidebar.checkbox("🌱 Intégrer des critères ESG ?", value=True)

profile = {
    "capital": capital,
    "horizon": horizon,
    "risk": risk,
    "esg": esg
}

# ===============================
# 🔮 GÉNÉRATION DU PORTEFEUILLE
# ===============================
st.header("🎯 Allocation proposée par GPT")

if st.button("🚀 Générer mon portefeuille IA"):
    with st.spinner("Analyse en cours..."):
        try:
            allocation_df = generate_portfolio_allocation(profile)
            st.subheader("📊 Résultat de l’allocation proposée :")
            st.dataframe(allocation_df, use_container_width=True)

            # ===============================
            # 📈 BACKTEST DU PORTEFEUILLE
            # ===============================
            st.header("📈 Backtest du portefeuille")

            fig, metrics = backtest_portfolio(allocation_df)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📉 Indicateurs de performance :")
            for key, value in metrics.items():
                st.write(f"**{key}** : {value}")

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")

else:
    st.info("👉 Remplis ton profil à gauche et clique sur *Générer mon portefeuille IA* pour commencer.")

# ===============================
# 🔍 FOOTER
# ===============================
st.markdown("---")
st.caption("Créé avec ❤️ par Romain Cublier — Projet GPT Portfolio 2025")
