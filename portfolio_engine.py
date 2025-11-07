# ==========================================
# 📁 portfolio_engine.py
# GPT Portfolio Assistant – Backtest Engine (v5 final & universal)
# ==========================================

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def run_backtest(allocation):
    """
    Backtest robuste d’un portefeuille GPT à partir des tickers Yahoo Finance.
    Gère tous les formats de colonnes et les éventuels tickers manquants.
    """
    try:
        # --- Extraction tickers et poids
        tickers = [item["Ticker"] for item in allocation if item["Ticker"] != "ERROR"]
        weights = [float(item["Poids"]) for item in allocation if item["Ticker"] != "ERROR"]

        if not tickers or len(tickers) != len(weights):
            raise ValueError("Aucun ticker valide reçu pour le backtest.")

        # Normaliser les poids
        weights = [w / sum(weights) for w in weights]

        # --- Télécharger les données Yahoo Finance
        data = yf.download(tickers, start="2021-01-01", progress=False)

        # ✅ Identifier la colonne correcte (Adj Close ou Close)
        price_cols = [col for col in data.columns if "Adj Close" in str(col) or "Close" in str(col)]
        if not price_cols:
            raise KeyError("Aucune colonne de prix trouvée dans les données Yahoo Finance.")

        prices = data[price_cols]

        # ✅ Nettoyage automatique des noms de colonnes (pour n'avoir que les tickers)
        clean_cols = []
        for c in prices.columns:
            if isinstance(c, tuple):
                clean_cols.append(c[-1])  # si MultiIndex
            else:
                name = str(c).replace("Adj Close", "").replace("Close", "").strip()
                clean_cols.append(name)
        prices.columns = clean_cols

        # ✅ Supprimer les colonnes vides / manquantes
        prices = prices.dropna(axis=1, how="all")

        # ✅ Filtrer uniquement les tickers présents
        existing_tickers = [t for t in tickers if t in prices.columns]
        if not existing_tickers:
            raise KeyError(f"Aucun ticker valide trouvé dans les données. Colonnes reçues : {list(prices.columns)}")

        # Adapter les poids aux tickers réellement disponibles
        valid_weights = [weights[tickers.index(t)] for t in existing_tickers]
        valid_weights = [w / sum(valid_weights) for w in valid_weights]

        # --- Calcul des rendements
        returns = prices[existing_tickers].pct_change().dropna()
        weights_series = pd.Series(valid_weights, index=existing_tickers)
        portfolio_returns = (returns * weights_series).sum(axis=1)
        portfolio_value = (1 + portfolio_returns).cumprod()

        # --- Graphique Plotly
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
