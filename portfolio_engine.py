import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def backtest_portfolio(df_allocation):
    """
    Backtest robuste : gère tous les cas (colonnes manquantes, tickers invalides, formats variables).
    """
    tickers = df_allocation['Ticker'].tolist()
    weights = df_allocation['Poids'].tolist()

    # Télécharger les prix
    data = yf.download(tickers, start="2015-01-01", end="2025-01-01", progress=False)

    # Cas 1 : MultiIndex (plusieurs tickers)
    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.levels[0]:
            data = data["Adj Close"]
        else:
            # On prend la première couche valide (ex: 'Close')
            first_layer = data.columns.levels[0][0]
            data = data[first_layer]

    # Cas 2 : une seule colonne (un seul ticker)
    elif "Adj Close" in data.columns:
        data = pd.DataFrame(data["Adj Close"])
    elif "Close" in data.columns:
        data = pd.DataFrame(data["Close"])
    else:
        # Dernier recours : prendre la dernière colonne
        data = pd.DataFrame(data.iloc[:, -1])
        data.columns = tickers[:1]

    # Nettoyage
    data = data.dropna(axis=1, how="all")

    # Vérifier les tickers valides
    valid_tickers = [t for t in tickers if t in data.columns]
    if not valid_tickers:
        raise ValueError(f"Aucun ticker valide trouvé parmi : {tickers}")

    # Ajuster les poids
    weights = [w for t, w in zip(tickers, weights) if t in valid_tickers]
    weights = [w / sum(weights) for w in weights]
    data = data[valid_tickers]

    # Normaliser les prix
    normalized = data / data.iloc[0]
    portfolio = (normalized * weights).sum(axis=1)

    # Calculs de performance
    returns = portfolio.pct_change().dropna()
    cumulative_return = (portfolio.iloc[-1] / portfolio.iloc[0]) - 1
    annualized_return = (1 + cumulative_return) ** (1 / 10) - 1
    volatility = returns.std() * (252 ** 0.5)
    sharpe = annualized_return / volatility if volatility != 0 else 0

    metrics = {
        "Cumulative Return": f"{cumulative_return:.2%}",
        "Annualized Return": f"{annualized_return:.2%}",
        "Volatility (ann.)": f"{volatility:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}"
    }

    # Graphique Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio.index, y=portfolio, mode='lines', name='Portefeuille'))
    fig.update_layout(title="📈 Performance du portefeuille (2015–2025)",
                      xaxis_title="Date", yaxis_title="Valeur normalisée",
                      template="plotly_white")

    return fig, metrics
