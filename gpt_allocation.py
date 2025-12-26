"""Portfolio allocation generator using static assumptions."""

import pandas as pd

from config import assumptions


def generate_portfolio_allocation(capital, risk, horizon, esg):
    """Generate ETF allocation based on risk tolerance and horizon."""

    alloc = assumptions.BASE_ALLOCATIONS[risk].copy()

    if "Short" in horizon:  # <2 years
        alloc["AGG"] += 15
        alloc["SPY"] -= 5
        alloc["QQQ"] = max(0, alloc.get("QQQ", 0) - 10)
        alloc["BTC-USD"] = 0
    elif "Medium" in horizon:  # 2–5 years
        alloc["AGG"] += 5
        alloc["SPY"] -= 5
    elif "Long" in horizon:  # 5–10 years
        alloc["QQQ"] += 5
    elif "Very Long" in horizon:  # >10 years
        alloc["QQQ"] += 10
        alloc["BTC-USD"] = alloc.get("BTC-USD", 0) + 5

    if esg and "BTC-USD" in alloc:
        alloc.pop("BTC-USD")

    total = sum(alloc.values())
    alloc = {k: round(v / total * 100, 2) for k, v in alloc.items()}

    df = pd.DataFrame(
        {
            "Ticker": list(alloc.keys()),
            "Classe": [assumptions.ETF_DATABASE[k] for k in alloc.keys()],
            "Allocation (%)": list(alloc.values()),
            "Invested (€)": [round(capital * v / 100, 2) for v in alloc.values()],
        }
    )

    return df
