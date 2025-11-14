import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta

# --------------------------------------------------
#  CONFIG GÉNÉRALE
# --------------------------------------------------
st.set_page_config(
    page_title="GPT Portfolio Assistant",
    layout="wide",
)

# --------------------------------------------------
# 1. LOGIQUE D’ALLOCATION RULE-BASED (SANS GPT)
# --------------------------------------------------

def build_rule_based_allocation(risk_level: str, horizon: str, esg: bool) -> pd.DataFrame:
    """
    Génère une allocation simple mais propre, en fonction :
    - du niveau de risque (Low / Moderate / High)
    - de l’horizon d’investissement (Short / Medium / Long)
    - du choix ESG ou non
    Retourne un DataFrame avec colonnes: Ticker, Weight, Classe
    """

    # ETF disponibles
    # Pas d’immobilier, comme demandé
    etf = {
        "SPY":  "US Equities",
        "VTI":  "US Total Market",
        "QQQ":  "US Tech Growth",
        "SPYG": "US ESG Growth",
        "ESGV": "US ESG Large Cap",
        "SUSB": "ESG Bonds",
        "AGG":  "US Bonds",
        "BND":  "Global Bonds",
        "GLDM": "Gold",
        "BTC-USD": "Crypto",
    }

    # On initialise une liste de dicts (un par ligne)
    alloc = []

    # Pour plus de lisibilité on normalise le texte
    risk_level = risk_level.lower()
    horizon = horizon.lower()

    # -----------------------------
    # PROFIL FAIBLE RISQUE
    # -----------------------------
    if risk_level == "low":
        if horizon == "short":
            # Portefeuille très défensif : obligations + or
            base = [
                ("AGG", 0.45),
                ("BND", 0.35),
                ("GLDM", 0.20),
            ]
        elif horizon == "medium":
            base = [
                ("AGG", 0.40),
                ("BND", 0.30),
                ("GLDM", 0.20),
                ("SPY", 0.10),
            ]
        else:  # long
            base = [
                ("AGG", 0.35),
                ("BND", 0.25),
                ("GLDM", 0.20),
                ("SPY", 0.20),
            ]

    # -----------------------------
    # PROFIL MODÉRÉ
    # -----------------------------
    elif risk_level == "moderate":
        if horizon == "short":
            base = [
                ("SPY", 0.30),
                ("VTI", 0.20),
                ("AGG", 0.30),
                ("GLDM", 0.20),
            ]
        elif horizon == "medium":
            base = [
                ("SPY", 0.35),
                ("VTI", 0.25),
                ("AGG", 0.25),
                ("GLDM", 0.10),
                ("BTC-USD", 0.05),
            ]
        else:  # long
            base = [
                ("SPY", 0.35),
                ("QQQ", 0.20),
                ("VTI", 0.20),
                ("AGG", 0.15),
                ("GLDM", 0.05),
                ("BTC-USD", 0.05),
            ]

    # -----------------------------
    # PROFIL DYNAMIQUE
    # -----------------------------
    else:  # "high"
        if horizon == "short":
            base = [
                ("SPY", 0.35),
                ("QQQ", 0.30),
                ("GLDM", 0.15),
                ("BTC-USD", 0.20),
            ]
        elif horizon == "medium":
            base = [
                ("QQQ", 0.35),
                ("SPYG", 0.20),
                ("VTI", 0.20),
                ("GLDM", 0.10),
                ("BTC-USD", 0.15),
            ]
        else:  # long
            base = [
                ("QQQ", 0.40),
                ("SPYG", 0.20),
                ("VTI", 0.15),
                ("GLDM", 0.10),
                ("BTC-USD", 0.15),
            ]

    # Adaptation ESG : on remplace certaines lignes par leurs équivalents ESG
    if esg:
        esg_replacements = {
            "SPY": "ESGV",
            "VTI": "ESGV",
            "AGG": "SUSB",
            "BND": "SUSB",
        }
        new_base = []
        for ticker, w in base:
            if ticker in esg_replacements:
                new_base.append((esg_replacements[ticker], w))
            else:
                new_base.append((ticker, w))
        base = new_base

    # On regroupe les poids si plusieurs lignes pour un même ticker
    weights = {}
    for t, w in base:
        weights[t] = weights.get(t, 0) + w

    # Normalisation sécurité
    total_w = sum(weights.values())
    if total_w <= 0:
        raise ValueError("Total weight is zero, allocation rule error.")
    for t in weights:
        weights[t] /= total_w

    for t, w in weights.items():
        alloc.append({
            "Ticker": t,
            "Weight": round(w, 4),
            "Classe": etf.get(t, "Unknown"),
        })

    df_alloc = pd.DataFrame(alloc)
    return df_alloc


# --------------------------------------------------
# 2. FONCTIONS DE BACKTEST
# --------------------------------------------------

def download_prices(tickers, start_date="2018-01-01"):
    """Télécharge les prix ajustés depuis Yahoo Finance et renvoie un DataFrame de prix."""
    data = yf.download(tickers, start=start_date, progress=False)

    if data.empty:
        raise ValueError("Aucune donnée téléchargée. Vérifie les tickers.")

    # Si multi-index (colonnes Niveau 0: 'Adj Close', Niveau 1: tickers)
    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            prices = data["Adj Close"].copy()
        else:
            # fallback sur Close
            prices = data["Close"].copy()
    else:
        # Un seul ticker
        if "Adj Close" in data.columns:
            prices = data["Adj Close"].to_frame(name=tickers if isinstance(tickers, str) else tickers[0])
        else:
            prices = data["Close"].to_frame(name=tickers if isinstance(tickers, str) else tickers[0])

    prices = prices.dropna(how="all")
    return prices


def run_backtest(allocation_df: pd.DataFrame, start_date="2018-01-01", benchmark="SPY"):
    """
    Backtest simple : portefeuille vs benchmark.
    allocation_df doit avoir 'Ticker' et 'Weight' (somme ≈ 1).
    """

    tickers = allocation_df["Ticker"].tolist()
    weights = allocation_df["Weight"].values.astype(float)

    all_tickers = list(set(tickers + [benchmark]))
    prices = download_prices(all_tickers, start_date=start_date)

    # On garde uniquement les colonnes nécessaires
    port_prices = prices[tickers].dropna(how="all")
    bm_prices = prices[benchmark].dropna()

    # On aligne les dates
    common_index = port_prices.index.intersection(bm_prices.index)
    port_prices = port_prices.loc[common_index]
    bm_prices = bm_prices.loc[common_index]

    daily_returns = port_prices.pct_change().dropna()
    bm_returns = bm_prices.pct_change().dropna()

    # Alignement final
    common_index = daily_returns.index.intersection(bm_returns.index)
    daily_returns = daily_returns.loc[common_index]
    bm_returns = bm_returns.loc[common_index]

    # Rendement du portefeuille
    port_ret = (daily_returns * weights).sum(axis=1)

    # Valeur cumulée (base 1)
    port_cum = (1 + port_ret).cumprod()
    bm_cum = (1 + bm_returns).cumprod()

    # --------- métriques ---------
    nb_days = len(port_ret)
    if nb_days == 0:
        raise ValueError("Pas assez de données pour le backtest.")

    cagr = port_cum.iloc[-1] ** (252 / nb_days) - 1
    vol = port_ret.std() * np.sqrt(252)
    sharpe = cagr / vol if vol > 0 else np.nan

    running_max = port_cum.cummax()
    drawdown = port_cum / running_max - 1
    max_dd = drawdown.min()

    metrics = {
        "CAGR": cagr,
        "Volatilité": vol,
        "Sharpe": sharpe,
        "Max Drawdown": max_dd,
    }

    # --------- Graphique ---------
    df_plot = pd.DataFrame({
        "Portfolio": port_cum,
        benchmark: bm_cum,
    })

    fig = px.line(
        df_plot,
        labels={"value": "Growth of 1 €", "index": "Date"},
        title="Portfolio vs Benchmark",
    )
    fig.update_layout(legend_title_text="")

    return fig, metrics


# --------------------------------------------------
# 3. STOCK ANALYZER (ANALYSE D’UN TICKER)
# --------------------------------------------------

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px


def stock_analyzer_page():

    st.header("📈 Stock Analyzer (no API, Yahoo Finance only)")
    st.write("Analyze any stock, crypto, or ETF using free price data from Yahoo Finance.")

    ticker = st.text_input("Ticker (e.g., AAPL, MSFT, SPY, BTC-USD)", "AAPL")

    period = st.selectbox(
        "History period",
        ["1y", "5y", "10y", "max"],
        index=1
    )

    if st.button("Analyze"):
        try:
            df = yf.download(ticker, period=period)

            if df.empty:
                st.error("Invalid ticker or unavailable data.")
                return

            df["Date"] = df.index

            # ---- PRICE CHART ----
            st.subheader(f"{ticker} Price History")

            fig = px.line(df, x="Date", y="Adj Close", title=f"{ticker} Price")
            st.plotly_chart(fig, use_container_width=True)

            # ---- METRICS ----
            st.subheader("Performance Metrics")

            df["Daily Return"] = df["Adj Close"].pct_change()
            df = df.dropna()

            # CAGR
            start_price = df["Adj Close"].iloc[0]
            end_price = df["Adj Close"].iloc[-1]
            years = len(df) / 252
            cagr = (end_price / start_price) ** (1 / years) - 1

            # Volatility
            vol = df["Daily Return"].std() * (252 ** 0.5)

            # Sharpe (risk-free = 0)
            sharpe = cagr / vol if vol != 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("CAGR", f"{cagr*100:.2f}%")
            col2.metric("Volatility (ann.)", f"{vol*100:.2f}%")
            col3.metric("Sharpe Ratio", f"{sharpe:.2f}")

        except Exception as e:
            st.error(f"Error during analysis: {e}")

# --------------------------------------------------
# 4. UI : DEUX SECTIONS (PORTFOLIO / STOCK ANALYZER)
# --------------------------------------------------

st.title("GPT Portfolio Assistant — AI Investment App")

page = st.sidebar.radio(
    "Navigation",
    ["AI Portfolio Generator", "Stock Analyzer"],
)

# --------------------------------------------------
# PAGE 1 : AI PORTFOLIO GENERATOR + BACKTEST
# --------------------------------------------------
if page == "AI Portfolio Generator":
    st.header("AI Portfolio Generator")

    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.subheader("Investor Profile")

        capital = st.number_input("Capital to invest (€)", min_value=1000, max_value=1_000_000, value=10_000, step=500)

        risk_level = st.selectbox(
            "Risk Level",
            ["Low", "Moderate", "High"],
            index=1,
        )

        horizon = st.selectbox(
            "Investment Horizon",
            ["Short (<2 years)", "Medium (2–5 years)", "Long (>5 years)"],
            index=2,
        )

        esg = st.checkbox("Include ESG constraints?", value=False)

        generate_btn = st.button("Generate Portfolio")

    with col_right:
        st.subheader("Allocation Results")

        if generate_btn:
            try:
                # On mappe le texte long vers short codes
                if horizon.startswith("Short"):
                    hz_code = "short"
                elif horizon.startswith("Medium"):
                    hz_code = "medium"
                else:
                    hz_code = "long"

                df_alloc = build_rule_based_allocation(
                    risk_level=risk_level,
                    horizon=hz_code,
                    esg=esg,
                )

                df_display = df_alloc.copy()
                df_display["Allocation (%)"] = (df_display["Weight"] * 100).round(1)
                df_display["Invested (€)"] = (df_display["Weight"] * capital).round(0).astype(int)

                st.success("Portfolio generated successfully!")
                st.dataframe(df_display[["Ticker", "Classe", "Allocation (%)", "Invested (€)"]],
                             use_container_width=True)

                st.markdown("### Backtest of Generated Portfolio")
                fig_bt, metrics = run_backtest(df_alloc[["Ticker", "Weight"]])
                st.plotly_chart(fig_bt, use_container_width=True)

                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("CAGR", f"{metrics['CAGR']*100:.2f} %")
                col_m2.metric("Volatility (ann.)", f"{metrics['Volatilité']*100:.2f} %")
                col_m3.metric("Sharpe", f"{metrics['Sharpe']:.2f}")
                col_m4.metric("Max Drawdown", f"{metrics['Max Drawdown']*100:.2f} %")

            except Exception as e:
                st.error(f"Error during calculation/backtest: {e}")

    st.markdown("---")
    st.header("Portfolio Backtest (Upload Your Own Allocation)")

    st.write("Upload a CSV with columns **Ticker** and **Allocation (%)** (or **Weight** between 0 and 1).")

    uploaded_file = st.file_uploader("Upload Portfolio CSV", type="csv")

    if uploaded_file is not None:
        try:
            df_user = pd.read_csv(uploaded_file)

            if "Ticker" not in df_user.columns:
                raise ValueError("CSV must contain a 'Ticker' column.")

            if "Allocation (%)" in df_user.columns:
                df_user["Weight"] = df_user["Allocation (%)"] / 100.0
            elif "Weight" not in df_user.columns:
                raise ValueError("CSV must contain either 'Allocation (%)' or 'Weight' column.")

            df_user["Weight"] = df_user["Weight"].astype(float)
            # Normalisation
            total_w = df_user["Weight"].sum()
            if total_w <= 0:
                raise ValueError("Sum of weights <= 0.")
            df_user["Weight"] /= total_w

            st.write("📊 Normalized allocation used for backtest:")
            st.dataframe(df_user[["Ticker", "Weight"]], use_container_width=True)

            fig_user, metrics_user = run_backtest(df_user[["Ticker", "Weight"]])
            st.plotly_chart(fig_user, use_container_width=True)

            col_u1, col_u2, col_u3, col_u4 = st.columns(4)
            col_u1.metric("CAGR", f"{metrics_user['CAGR']*100:.2f} %")
            col_u2.metric("Volatility (ann.)", f"{metrics_user['Volatilité']*100:.2f} %")
            col_u3.metric("Sharpe", f"{metrics_user['Sharpe']:.2f}")
            col_u4.metric("Max Drawdown", f"{metrics_user['Max Drawdown']*100:.2f} %")

        except Exception as e:
            st.error(f"Error in backtest: {e}")

# --------------------------------------------------
# PAGE 2 : STOCK ANALYZER
# --------------------------------------------------
else:
    st.header("Stock Analyzer (no API, Yahoo Finance only)")

    col_a, col_b = st.columns([1, 2])

    with col_a:
        ticker = st.text_input("Ticker (e.g. AAPL, MSFT, SPY, BTC-USD)", value="AAPL")
        period_choice = st.selectbox(
            "History period",
            ["1 year", "3 years", "5 years"],
            index=1,
        )
        if period_choice.startswith("1"):
            years = 1
        elif period_choice.startswith("3"):
            years = 3
        else:
            years = 5

        analyze_btn = st.button("Analyze")

    with col_b:
        if analyze_btn:
            try:
                fig_sa, metrics_sa = analyze_ticker(ticker, period_years=years)
                st.plotly_chart(fig_sa, use_container_width=True)

                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("Last Price", f"{metrics_sa['Last Price']:.2f}")
                col_s2.metric("Total Return", f"{metrics_sa['Total Return']*100:.2f} %")
                col_s3.metric("Ann. Volatility", f"{metrics_sa['Annualized Volatility']*100:.2f} %")
                col_s4.metric("Max Drawdown", f"{metrics_sa['Max Drawdown']*100:.2f} %")

                st.info(
                    "This module is fully rule-based (no GPT) and uses Yahoo Finance "
                    "data to help you train your investment analysis skills."
                )

            except Exception as e:
                st.error(f"Error during analysis: {e}")
