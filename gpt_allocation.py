import pandas as pd

# ============================================================
#   ETF DATABASE
# ============================================================

ETF_DATABASE = {
    "SPY": "US Equities",
    "QQQ": "US Tech Growth",
    "VTI": "US Total Market",
    "AGG": "US Bonds",
    "GLDM": "Gold",
    "BTC-USD": "Crypto"
}


# ============================================================
#   FIXED ROBUST ALLOCATION SYSTEM (5 RISKS × 4 HORIZONS)
# ============================================================

BASE_ALLOCATIONS = {
    "Very Low":   {"SPY": 10, "QQQ": 0,  "VTI": 10, "AGG": 65, "GLDM": 15},
    "Low":        {"SPY": 20, "QQQ": 5,  "VTI": 20, "AGG": 45, "GLDM": 10},
    "Moderate":   {"SPY": 35, "QQQ": 15, "VTI": 20, "AGG": 20, "GLDM": 5, "BTC-USD": 5},
    "High":       {"SPY": 35, "QQQ": 25, "VTI": 15, "AGG": 10, "GLDM": 5, "BTC-USD": 10},
    "Very High":  {"SPY": 30, "QQQ": 35, "VTI": 10, "AGG": 5,  "GLDM": 5, "BTC-USD": 15},
}


def generate_portfolio_allocation(capital, risk, horizon, esg):
    """
    Generate a realistic ETF allocation based on risk tolerance,
    investment horizon, and ESG preference. Fully offline.
    """

    # 1) Start from base allocation
    alloc = BASE_ALLOCATIONS[risk].copy()

    # ============================================================
    #   HORIZON ADJUSTMENTS
    # ============================================================

    if "Short" in horizon:                 # <2 years
        alloc["AGG"] += 15
        alloc["SPY"] -= 5
        alloc["QQQ"] = max(0, alloc.get("QQQ", 0) - 10)
        alloc["BTC-USD"] = 0

    elif "Medium" in horizon:             # 2–5 years
        alloc["AGG"] += 5
        alloc["SPY"] -= 5

    elif "Long" in horizon:               # 5–10 years
        alloc["QQQ"] += 5

    elif "Very Long" in horizon:          # >10 years
        alloc["QQQ"] += 10
        alloc["BTC-USD"] = alloc.get("BTC-USD", 0) + 5

    # ============================================================
    #   ESG FILTER (remove BTC)
    # ============================================================

    if esg and "BTC-USD" in alloc:
        alloc.pop("BTC-USD")

    # ============================================================
    #   NORMALIZE TO 100%
    # ============================================================

    total = sum(alloc.values())
    alloc = {k: round(v / total * 100, 2) for k, v in alloc.items()}

    # ============================================================
    #   BUILD DATAFRAME
    # ============================================================

    df = pd.DataFrame({
        "Ticker": list(alloc.keys()),
        "Classe": [ETF_DATABASE[k] for k in alloc.keys()],
        "Allocation (%)": list(alloc.values()),
        "Invested (€)": [round(capital * v / 100, 2) for v in alloc.values()]
    })

    return df

