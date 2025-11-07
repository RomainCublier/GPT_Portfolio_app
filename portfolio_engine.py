# portfolio_engine.py

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ===============================
# 📥 Téléchargement des données
# ===============================
def download_data(tickers, start="2015-01-01"):
    """
    Télécharge les prix ajustés des actifs depuis Yahoo Finance.
    """
    data = yf.download(tickers, start=start, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"] if "Close" in data.columns.levels[0] else data.iloc[:, 0]
    data = data.dropna()
    return data


# ===============================
# 💰 Calcul de la valeur du portefeuille
# ===============================
def compute_portfolio_value(prices, weights):
    """
    Calcule la valeur quotidienne du portefeuille en fonction des poids.
    """
    returns = prices.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    portfolio_value = (1 + portfolio_returns).cumprod()
    return portfolio_value


# ===============================
# 📊 Calcul des indicateurs de performance
# ===============================
def calculate_performance_metrics(portfolio_value):
    """
    Calcule CAGR, volatilité, Sharpe et drawdown max.
    """
    returns = portfolio_value.pct_change().dropna()
    if len(returns) == 0:
        return {"Erreur": "Aucune donnée de performance disponible."}

    cagr = ((portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (252 / len(returns))) - 1
    vol = returns.std() * np.sqrt(252)
    sharpe = cagr / vol if vol != 0 else np.nan

    cum_returns = (1 + returns).cumprod()
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_dd = drawdown.min()

    return {
        "CAGR": f"{cagr * 100:.2f}%",
        "Volatilité": f"{vol * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_dd * 100:.2f}%"
    }


# ===============================
# 🧠 Backtest principal
# ===============================
def backtest_portfolio(allocation_df, start="2015-01-01"):
    """
    Exécute un backtest complet à partir de l'allocation donnée.
    """
    tickers = allocation_df["Ticker"].tolist()
    weights = allocation_df.set_index("Ticker")["Allocation (%)"] / 100

    prices = download_data(tickers, start=start)
    portfolio_value = compute_portfolio_value(prices, weights)

    # Benchmark : S&P 500 (SPY)
    benchmark = download_data(["SPY"], start=start)
    benchmark_value = benchmark / benchmark.iloc[0]

    # Indicateurs
    metrics = calculate_performance_metrics(portfolio_value)

    # ===============================
    # 📈 Création du graphique
    # ===============================
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_value.index,
        y=portfolio_value.values,
        mode="lines",
        name="Portefeuille IA",
        line=dict(color="blue", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=benchmark_value.index,
        y=benchmark_value.values,
        mode="lines",
        name="S&P 500",
        line=dict(color="gray", dash="dot")
    ))

    fig.update_layout(
        title="Évolution du portefeuille vs Benchmark",
        xaxis_title="Date",
        yaxis_title="Valeur cumulée (base 1)",
        hovermode="x unified",
        legend=dict(x=0.02, y=0.98)
    )

    return fig, metrics


# ===============================
# 🧪 Test local
# ===============================
if __name__ == "__main__":
    allocation_df = pd.DataFrame({
        "Ticker": ["URTH", "BND"],
        "Allocation (%)": [60, 40]
    })
    fig, metrics = backtest_portfolio(allocation_df)
    fig.show()
    print(metrics)
