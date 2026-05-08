from __future__ import annotations

from pathlib import Path

import pandas as pd
from langchain.tools import tool

DATA_PATH = Path(__file__).parent / "data" / "watchlist.csv"


def _load_watchlist() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    data["symbol"] = data["symbol"].str.upper()
    return data


@tool
def compare_tickers(symbol_1: str, symbol_2: str) -> str:
    """
    Compare two stock tickers using local watchlist metadata.
    Useful when users ask to compare companies, exchanges, sectors, countries, or currencies.
    """
    watchlist = _load_watchlist()
    s1 = symbol_1.strip().upper()
    s2 = symbol_2.strip().upper()

    matches = watchlist[watchlist["symbol"].isin([s1, s2])]
    found = set(matches["symbol"].tolist())
    missing = [symbol for symbol in [s1, s2] if symbol not in found]
    if missing:
        return (
            f"I do not have {', '.join(missing)} in the local comparison watchlist. "
            "Try AAPL, MSFT, TSLA, IBM, RY, SHOP, TD, BP, VOD, or SAP."
        )

    rows = {row["symbol"]: row for _, row in matches.iterrows()}
    left = rows[s1]
    right = rows[s2]

    shared_sector = (
        "They are in the same sector."
        if left["sector"] == right["sector"]
        else "They are in different sectors."
    )
    shared_currency = (
        "They trade in the same currency."
        if left["currency"] == right["currency"]
        else "They trade in different currencies, so direct price comparisons need care."
    )

    return (
        f"{s1} is {left['name']}, a {left['sector']} company listed on "
        f"{left['exchange']} in {left['country']} and quoted in {left['currency']}.\n"
        f"{s2} is {right['name']}, a {right['sector']} company listed on "
        f"{right['exchange']} in {right['country']} and quoted in {right['currency']}.\n"
        f"{shared_sector} {shared_currency}"
    )

