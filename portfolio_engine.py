import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def backtest_portfolio(df_allocation):
    """
    Backtest robuste du portefeuille proposé.
    Gère les tickers manquants et les formats variables de Yahoo Finance.
    """

    tickers = df_allocation['Ticker'].tolist()
    weights = df_allocation['Poids'].tolist()

    # Télécharger les données (multi-tickers ou single)
    data = yf.download(tickers, start="2015-01-01", end="2025-01-01", progress=False)

    # Si un seul ticker → le DataFrame n’a pas de multi-index
    if 'Adj Close' in data.columns:
        data = pd.DataFrame(data['Adj Close'])
    elif isinstance(data.columns, pd.MultiIndex):
        data = data['Adj Close']
    else:
        raise ValueError("Impossible de trouver la colonne 'Adj Close' dans les données Yahoo Finance.")

    # Nettoyage : supprimer les colonnes vides
    data = data.dropna(axis=1, how='all')

    # Vérifie que les tickers téléchargés existent bien
    valid_tickers = [t for t in tickers if t in data.columns]
    if not valid_tickers:
        raise ValueError(f"Aucun ticker valide téléchargé parmi : {tickers}")

    # Ajuster les poids si certains manquent
    weights = [w for t, w in zip(tickers, weights) if t in valid_tickers]
    weights = [w / sum(weights) for w in weights]

    data = data[valid_tickers]
    normalized = data / data.iloc[0]
    portfolio = (normalized * weights).sum(axis=1)

    # Calcul des métriques
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
    fig.update_layout(title="Performance du portefeuille (2015–2025)",
                      xaxis_title="Date", yaxis_title="Valeur normalisée",
                      template="plotly_white")

    return fig, metrics
