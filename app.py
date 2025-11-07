import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import backtest_portfolio

# =========================
#⚙️ CONFIGURATION DE L’APP
# =========================
st.set_page_config(page_title="GPT Portfolio Assistant", layout="wide")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.title("🤖 GPT Portfolio Assistant")
st.write("Une IA qui construit et analyse ton portefeuille d’investissement à partir de ton profil investisseur.")

# =========================
# 🧭 SAISIE DU PROFIL CLIENT
# =========================
st.sidebar.header("🎯 Profil investisseur")

capital = st.sidebar.number_input("💰 Capital à investir (€)", min_value=1000, max_value=1_000_000, value=10_000, step=1000)
horizon = st.sidebar.selectbox("⏳ Horizon d’investissement", ["Court terme (<3 ans)", "Moyen terme (3-7 ans)", "Long terme (>7 ans)"])
risque = st.sidebar.selectbox("⚡ Tolérance au risque", ["Prudent", "Équilibré", "Dynamique", "Audacieux"])
esg = st.sidebar.selectbox("🌱 Préférence ESG", ["Indifférent", "Modéré", "Forte préférence"])

generate_button = st.sidebar.button("🚀 Générer mon portefeuille IA")

# =========================
# 📊 GÉNÉRATION DU PORTEFEUILLE
# =========================
if generate_button:
    with st.spinner("🤖 Génération du portefeuille par GPT..."):
        try:
            allocation, justification = generate_portfolio_allocation(
                api_key=api_key,
                capital=capital,
                horizon=horizon,
                risque=risque,
                esg=esg
            )

            df_allocation = pd.DataFrame(allocation)
            st.subheader("📊 Allocation proposée par l'IA")
            st.dataframe(df_allocation, use_container_width=True)

            st.markdown("### 🧠 Justification de l'allocation")
            st.info(justification)

            # =========================
            # 📈 BACKTEST AUTOMATIQUE
            # =========================
            st.subheader("📈 Backtest du portefeuille (2015–2025)")
            fig, metrics = backtest_portfolio(df_allocation)
            st.plotly_chart(fig, use_container_width=True)

            st.write("### 📊 Indicateurs de performance")
            st.json(metrics)

        except Exception as e:
            st.error(f"❌ Erreur lors de la génération ou du backtest : {e}")

# =========================
# 🧩 INFO APP
# =========================
st.markdown("---")
st.caption("Projet créé par **Romain Cublier** — Assistant IA pour l’allocation et le backtest d’un portefeuille d’investissement.")
