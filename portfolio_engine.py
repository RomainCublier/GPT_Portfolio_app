# ==========================================
# 📁 portfolio_engine.py
# GPT Portfolio Assistant – Backtest Engine
# ==========================================

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def run_backtest(allocation):
    """
    Backtest simplifié : télécharge les données des tickers fournis par GPT,
    calcule l’évolution d’un portefeuille pondéré.
    """

    try:
        tickers = [item["Ticker"] for item in allocation if item["Ticker"] != "ERROR"]
        weights = [float(item["Poids"]) for item in allocation if item["Ticker"] != "ERROR"]

        if not tickers or len(tickers) != len(weights):
            raise ValueError("Aucun ticker valide reçu pour le backtest.")

        # Normaliser les poids pour que la somme = 1
        weights = [w / sum(weights) for w in weights]

        # Télécharger les données de prix (3 dernières années)
        data = yf.download(tickers, start="2021-01-01")["Adj Close"]

        # Calcul du rendement normalisé
        returns = data.pct_change().dropna()
        portfolio_returns = (returns * weights).sum(axis=1)

        # Valeur cumulée du portefeuille
        portfolio_value = (1 + portfolio_returns).cumprod()

        # 📈 Tracer avec Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value.values,
            mode="lines",
            name="Portefeuille IA",
            line=dict(color="blue", width=2)
        ))

        fig.update_layout(
            title="📊 Backtest du portefeuille GPT",
            xaxis_title="Date",
            yaxis_title="Valeur (base 1.0)",
            template="plotly_white"
        )

        return fig

    except Exception as e:
        import streamlit as st
        st.error(f"❌ Erreur dans le backtest : {e}")
        return go.Figure()
