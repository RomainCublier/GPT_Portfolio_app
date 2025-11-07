# ==========================================
# 📁 portfolio_engine.py
# GPT Portfolio Assistant – Backtest Engine (v4 robust)
# ==========================================

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def run_backtest(allocation):
    """
    Backtest d'un portefeuille GPT à partir des tickers fournis.
    Gère tous les formats yfinance (Adj Close ou Close).
    """
    try:
        # Extraction des tickers et poids
        tickers = [item["Ticker"] for item in allocation if item["Ticker"] != "ERROR"]
        weights = [float(item["Poids"]) for item in allocation if item["Ticker"] != "ERROR"]

        if not tickers or len(tickers) != len(weights):
            raise ValueError("Aucun ticker valide reçu pour le backtest.")

        # Normaliser les poids
        weights = [w / sum(weights) for w in weights]

        # Télécharger les données depuis Yahoo Finance
        data = yf.download(tickers, start="2021-01-01")

        # ✅ Sélectionne Adj Close si dispo, sinon Close
        if "Adj Close" in data.columns:
            data = data["Adj Close"]
        elif "Close" in data.columns:
            data = data["Close"]
        else:
            raise KeyError("Aucune colonne de prix ('Adj Close' ou 'Close') trouvée.")

        # Aplatir les colonnes si MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Si un seul ticker → forcer DataFrame
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])

        # Calcul des rendements
        returns = data.pct_change().dropna()

        # Alignement des colonnes
        returns = returns[tickers]

        # Poids sous forme de Series
        weights_df = pd.Series(weights, index=tickers)

        # Calcul rendement global du portefeuille
        portfolio_returns = (returns * weights_df).sum(axis=1)

        # Valeur cumulée
        portfolio_value = (1 + portfolio_returns).cumprod()

        # 📈 Graphique Plotly
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
            yaxis_title="Valeur du portefeuille (base 1.0)",
            template="plotly_white"
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erreur dans le backtest : {e}")
        return go.Figure()
