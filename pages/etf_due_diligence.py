diff --git a/pages/etf_due_diligence.py b/pages/02_etf_due_diligence.py
similarity index 91%
rename from pages/etf_due_diligence.py
rename to pages/02_etf_due_diligence.py
index 2ed6562e4e6ca98f670c8a1beae0c7a61d9f2dc8..75d7337d49b3199262b14bc098b7066889afb0a1 100644
--- a/pages/etf_due_diligence.py
+++ b/pages/02_etf_due_diligence.py
@@ -1,87 +1,90 @@
 """ETF & Fund Due Diligence page."""
 
 from __future__ import annotations
 
 from datetime import datetime, timedelta
 from typing import Dict, Tuple
 
 import numpy as np
 import pandas as pd
 import plotly.graph_objects as go
 import streamlit as st
 import yfinance as yf
 
 from core.data import download_adjusted_prices
 from core.etf_analysis import (
     compute_tracking_metrics,
     get_etf_identity,
     liquidity_proxies,
     portfolio_fit_summary,
     stress_metrics,
 )
 from core.metrics import drawdown_curve, performance_metrics
 from core.returns import compute_returns
+from utils.streamlit_helpers import handle_network_error
 
 
 def _date_range(lookback: str) -> Tuple[datetime | None, datetime]:
     end = datetime.today()
     if lookback == "3y":
         start = end - timedelta(days=365 * 3)
     elif lookback == "5y":
         start = end - timedelta(days=365 * 5)
     else:
         start = None
     return start, end
 
 
 def _fetch_volume(ticker: str, start: datetime | None, end: datetime) -> pd.Series:
-    data = yf.download(ticker, start=start, end=end, progress=False)
+    """Fetch a normalized volume series for the given ticker."""
+
+    try:
+        data = yf.download(ticker, start=start, end=end, progress=False)
+    except Exception:
+        return pd.Series(dtype=float)
+
     if data.empty:
         return pd.Series(dtype=float)
 
     volume_col = None
     if isinstance(data.columns, pd.MultiIndex):
         for col in data.columns:
             if any(str(part).lower() == "volume" for part in col):
                 volume_col = col
                 break
-    else:
-        if "Volume" in data:
-            volume_col = "Volume"
+    elif "Volume" in data.columns:
+        volume_col = "Volume"
 
     if volume_col is None:
         return pd.Series(dtype=float)
 
     volume = data[volume_col]
     if isinstance(volume, pd.DataFrame):
         volume = volume.iloc[:, 0]
-    volume = volume.astype(float).ffill()
-    volume.name = "Volume"
-    if data.empty or "Volume" not in data:
-        return pd.Series(dtype=float)
-    volume = data["Volume"].rename("Volume").ffill()
+
+    volume = pd.to_numeric(volume, errors="coerce").rename("Volume").ffill().dropna()
     volume.index = pd.to_datetime(volume.index)
     return volume
 
 
 def _stress_windows(data_start: pd.Timestamp, data_end: pd.Timestamp) -> Dict[str, Tuple[datetime, datetime]]:
     scenarios = {
         "COVID-19 Shock (2020)": (datetime(2020, 2, 15), datetime(2020, 3, 31)),
         "Inflation Spike (2022)": (datetime(2022, 1, 1), datetime(2022, 6, 30)),
         "Rate Pivot (2023)": (datetime(2023, 9, 1), datetime(2023, 12, 31)),
     }
     return {
         name: window
         for name, window in scenarios.items()
         if (data_start is None or window[1] >= data_start) and window[0] <= data_end
     }
 
 
 def _format_pct(value: float) -> str:
     if value is None or np.isnan(value):
         return "N/A"
     return f"{value:.2%}"
 
 
 def _format_number(value: float) -> str:
     if value is None or np.isnan(value):
@@ -118,82 +121,87 @@ def _render_price_charts(prices: pd.DataFrame, ticker: str, benchmark: str | Non
     )
     draw_fig.update_layout(template="plotly_white", yaxis_title="Drawdown", xaxis_title="Date")
     st.plotly_chart(draw_fig, use_container_width=True)
 
 
 def main():
     st.title("ETF & Fund Due Diligence")
     st.caption("Quick audit of ETF quality, liquidity and behaviour under stress.")
 
     default_benchmarks = {"Equity": "SPY", "Fixed Income": "AGG", "Commodity": "GLD"}
 
     with st.sidebar:
         ticker = st.text_input("ETF Ticker", value="SPY").strip().upper()
         asset_class = st.selectbox("Asset class", ["Equity", "Fixed Income", "Commodity"])
         benchmark_default = default_benchmarks.get(asset_class, "SPY")
         benchmark = st.text_input("Benchmark ticker", value=benchmark_default).strip().upper()
         lookback = st.selectbox("Lookback", ["3y", "5y", "max"], index=0)
         run_analysis = st.button("Run due diligence")
 
     if not run_analysis:
         st.info("Enter a ticker and click **Run due diligence** to see the framework in action.")
         st.stop()
 
     start, end = _date_range(lookback)
 
+    benchmark = benchmark if benchmark and benchmark != ticker else None
+
     try:
-        prices = download_adjusted_prices([ticker, benchmark], start=start, end=end)
+        requested_tickers = [ticker] + ([benchmark] if benchmark else [])
+        prices = download_adjusted_prices(requested_tickers, start=start, end=end)
     except Exception as exc:  # noqa: BLE001
-        st.error(f"Data error: {exc}")
+        st.error(f"Data error: {handle_network_error(exc)}")
         st.stop()
 
     if ticker not in prices.columns:
         st.error("ETF price series unavailable. Please try a different ticker or lookback.")
         st.stop()
 
     benchmark_returns = None
     if benchmark in prices.columns:
         benchmark_returns = compute_returns(prices[[benchmark]])[benchmark]
     else:
         st.warning("Benchmark data missing. Tracking metrics will be limited.")
 
     etf_returns = compute_returns(prices[[ticker]])[ticker]
     if etf_returns.empty:
         st.error("No returns available for the selected parameters.")
         st.stop()
 
     annual_factor = 252
     perf = performance_metrics(etf_returns, periods_per_year=annual_factor)
     tracking = (
         compute_tracking_metrics(etf_returns, benchmark_returns)
         if benchmark_returns is not None and not benchmark_returns.empty
         else {"tracking_difference": np.nan, "tracking_error": np.nan}
     )
 
     volume_series = _fetch_volume(ticker, start, end)
     liquidity_input = prices[[ticker]].copy()
-    if not volume_series.empty:
+    if volume_series.empty:
+        st.info("Volume data unavailable for this ticker; liquidity metrics are partially estimated.")
+    else:
         liquidity_input["Volume"] = volume_series.reindex(liquidity_input.index)
     liquidity = liquidity_proxies(liquidity_input)
 
     stress_periods = _stress_windows(etf_returns.index.min(), etf_returns.index.max())
     stress_df = stress_metrics(etf_returns, stress_periods)
 
     identity = get_etf_identity(ticker)
 
     st.subheader("ETF Identity")
     st.dataframe(pd.DataFrame(identity, index=[0]).set_index("ticker"))
 
     _render_price_charts(prices, ticker, benchmark if benchmark in prices.columns else None)
 
     st.subheader("Key Metrics")
     metrics_table = pd.DataFrame(
         {
             "Metric": [
                 "CAGR",
                 "Annual Volatility",
                 "Sharpe",
                 "Sortino",
                 "Max Drawdown",
                 "Tracking Difference",
                 "Tracking Error",
             ],
