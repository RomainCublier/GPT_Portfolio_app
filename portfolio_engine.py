# ==========================================
# 📁 portfolio_engine.py
# GPT Portfolio Assistant – Backtest Engine (v2 stable)
# ==========================================

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def run_backtest(allocation):
    """
    Backtest simple d'un portefeuille GPT à partir des tickers renvoyés.
    """
    try:
        tickers = [item["Ticker"] for item in allocation if item["Ticker"] != "ERROR"]
        weights = [float(item["Poids"]) for item in allocation if item["Ticker"] != "ERROR"]

        if not tickers or len(tickers) != len(weights):
            raise ValueError("Aucun ticker valide reçu pour le backtest.")

        # Normaliser les poids pour que la somme fasse bien 1
        weights = [w / sum(weights) for w in weights]

        # Télécharger les données de prix ajustés (sur 3 ans)
        data = yf.download(tickers, start="2021-01-01")["Adj Close"]

        # Vérifier si un seul ticker → convertir en DataFrame
        if isinstance(data, pd.Series):
            data = data.to_frame(tickers[0])

        # Calcul des rendements journaliers
        returns = data.pct_change().dropna()

        # ✅ Alignement des dimensions
        weights_df = pd.Series(weights, index=data.columns)
        portfolio_returns = (returns * weights_df).sum(axis=1)

        # Valeur cumulée du portefeuille (base 1)
        portfolio_value = (1 + portfolio_returns).cumprod()

        # 📈 Graphique interactif Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value.values,
            mode="lines",
            name="Portefeuille IA",
            line=dict(color="blue", width=2)
        ))

        fig.update_layout(
            title="📊 Backtest du portefeuille GPT (3 ans)",
            xaxis_title="Date",
            yaxis_title="Valeur (base 1.0)",
            template="plotly_white"
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erreur dans le backtest : {e}")
        return go.Figure()
