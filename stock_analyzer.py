import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI


# ============================
#   GPT STOCK ANALYSIS
# ============================
def analyze_stock(api_key, ticker):
    """
    Analyse une action avec GPT :
    - Résumé de l'entreprise
    - Analyse financière
    - Risques clés
    - Vision long terme
    """

    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are a senior equity analyst.
    Provide a clear and structured analysis of the stock {ticker}.

    Include:
    1) Business overview
    2) Moat & competitive advantages
    3) Key financial trends (growth, margins)
    4) Risks
    5) Long-term outlook
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response.choices[0].message.content

    # ======= Financials from Yahoo =======
    stock = yf.Ticker(ticker)
    financials = stock.financials

    if financials is None or financials.empty:
        raise ValueError("No financial data available for this stock.")

    # Extract Revenue
    revenue = financials.loc["Total Revenue"].T
    revenue.index = revenue.index.year

    return {
        "summary": summary,
        "financials": revenue
    }


# ============================
#   REVENUE CHART
# ============================
def chart_revenues(revenue_series):
    """
    Transforme la série de revenus en graphique Plotly.
    """

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=revenue_series.index,
        y=revenue_series.values,
        name="Revenue"
    ))

    fig.update_layout(
        title="Total Revenue (10 years)",
        xaxis_title="Year",
        yaxis_title="Revenue (USD)",
        template="plotly_white"
    )

    return fig

