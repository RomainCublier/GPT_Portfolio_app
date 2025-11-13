{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "eb58c70f-0370-403d-afd7-8c1d510876dd",
   "metadata": {},
   "outputs": [],
   "source": [
    "import yfinance as yf\n",
    "import pandas as pd\n",
    "import plotly.graph_objects as go\n",
    "from openai import OpenAI\n",
    "\n",
    "\n",
    "def analyze_stock(api_key, ticker):\n",
    "    client = OpenAI(api_key=api_key)\n",
    "\n",
    "    # Récupération des données financières\n",
    "    stock = yf.Ticker(ticker)\n",
    "\n",
    "    info = stock.info\n",
    "    financials = stock.financials\n",
    "    balance_sheet = stock.balance_sheet\n",
    "    cashflow = stock.cashflow\n",
    "\n",
    "    # --- GPT Résumé stratégique ---\n",
    "    prompt = f\"\"\"\n",
    "    You are an equity research analyst. Provide a clear, professional analysis of the stock {ticker}.\n",
    "    Structure your answer in 5 bullet points:\n",
    "\n",
    "    1) Business overview\n",
    "    2) Growth drivers\n",
    "    3) Profitability and margins\n",
    "    4) Balance sheet strength (debt, liquidity)\n",
    "    5) Key risks\n",
    "\n",
    "    Keep the style like a real asset-management analyst.\n",
    "    \"\"\"\n",
    "\n",
    "    response = client.chat.completions.create(\n",
    "        model=\"gpt-4o-mini\",\n",
    "        messages=[{\"role\": \"user\", \"content\": prompt}],\n",
    "        temperature=0.3\n",
    "    )\n",
    "\n",
    "    summary = response.choices[0].message.content\n",
    "\n",
    "    return {\n",
    "        \"info\": info,\n",
    "        \"financials\": financials,\n",
    "        \"balance_sheet\": balance_sheet,\n",
    "        \"cashflow\": cashflow,\n",
    "        \"summary\": summary\n",
    "    }\n",
    "\n",
    "\n",
    "def chart_revenues(financials):\n",
    "    fig = go.Figure()\n",
    "    rev = financials.loc[\"Total Revenue\"]\n",
    "    fig.add_trace(go.Bar(x=rev.index, y=rev.values))\n",
    "    fig.update_layout(title=\"Revenue\", template=\"plotly_white\")\n",
    "    return fig\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "15eb6a62-ac46-43dd-8db7-c27314d3ae4c",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
