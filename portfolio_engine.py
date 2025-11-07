import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def backtest_portfolio(df_allocation):
    """
    Effectue un backtest simple du portefeuille proposé.
    Prend un DataFrame avec colonnes : ['Ticker', 'Poids']
    Retourne : figure Plotly + métriques de performance
    """

    tickers = df_allocation['Ticker'].tolist()
    weights = df_allocation['Poids'].tolist()

    # Télécharger les prix ajustés
    data = yf.download(tickers, start="2015-01-01", end="2025-01-01")['Adj Close']

    # Normaliser les rendements
    normalized = data / data.iloc[0]
    portfolio = (normalized * weights).sum(axis=1)

    # Calcul des métriques
    returns = portfolio.pct_change().dropna()
    cumulative_return = (portfolio[-1] / portfolio[0]) - 1
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
