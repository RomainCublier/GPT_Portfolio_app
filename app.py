import streamlit as st
from gpt_allocation import generate_portfolio_allocation
from portfolio_engine import run_backtest

st.set_page_config(page_title="GPT Portfolio Assistant", layout="wide")

st.title("🤖 GPT Portfolio Assistant")
st.markdown("Crée ton portefeuille optimal avec l’aide de l’IA !")

st.success("🔑 Clé API chargée avec succès")

# ------------------------------
# 🎯 Sidebar — Profil investisseur
# ------------------------------
st.sidebar.header("🧭 Profil Investisseur")

capital = st.sidebar.number_input("💰 Capital à investir (€)", min_value=1000, value=10000, step=500)
horizon = st.sidebar.selectbox("⏳ Horizon d’investissement", ["Court terme (<2 ans)", "Moyen terme (2–5 ans)", "Long terme (>5 ans)"])
risque = st.sidebar.slider("⚖️ Niveau de risque", 0, 10, 5)
esg = st.sidebar.checkbox("🌱 Intégrer des critères ESG ?", value=True)

# ------------------------------
# 🚀 Génération de portefeuille
# ------------------------------
st.subheader("🎯 Allocation proposée par GPT")

if st.button("🚀 Générer mon portefeuille IA"):
    try:
        allocation = generate_portfolio_allocation(capital, horizon, risque, esg)
        st.write("🔍 Allocation GPT :", allocation)

        if allocation and isinstance(allocation, list) and "Ticker" in allocation[0]:
            st.success("✅ Allocation générée avec succès !")
            st.dataframe(allocation)

            st.subheader("📊 Backtest du portefeuille")
            fig = run_backtest(allocation)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("⚠️ Erreur : format d’allocation inattendu.")
            st.json(allocation)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")

else:
    st.info("👉 Remplis ton profil à gauche et clique sur **Générer mon portefeuille IA** pour commencer.")

st.markdown("Créé avec 💗 par Romain Cublier — Projet GPT Portfolio 2025")
