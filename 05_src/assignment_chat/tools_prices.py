from __future__ import annotations

import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv("05_src/.secrets")
load_dotenv(".secrets")


def _fmt_money(value) -> str:
    if value is None:
        return "not available"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


@tool
def get_latest_prices(symbols: str) -> str:
    """
    Fetch latest available end-of-day prices for one or more stock tickers.
    Symbols should be comma-separated, for example: AAPL,MSFT,TSLA.
    """
    api_key = os.getenv("MARKETSTACK_API_KEY")
    if not api_key:
        return "Marketstack is not configured. Add MARKETSTACK_API_KEY to 05_src/.secrets."

    cleaned_symbols = ",".join(
        symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()
    )
    if not cleaned_symbols:
        return "Please provide at least one ticker symbol, such as AAPL or MSFT."

    url = "http://api.marketstack.com/v1/eod/latest"
    params = {
        "access_key": api_key,
        "symbols": cleaned_symbols,
        "limit": 10,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
    except requests.RequestException as exc:
        return f"I could not reach Marketstack right now: {exc.__class__.__name__}."
    except ValueError:
        return "Marketstack returned a response that was not valid JSON."

    if "error" in data:
        message = data["error"].get("message", "Unknown Marketstack error.")
        return f"Marketstack could not return the requested price data: {message}"

    rows = data.get("data", [])
    if not rows:
        return f"I could not find latest end-of-day data for {cleaned_symbols}."

    summaries = []
    for row in rows:
        date_raw = row.get("date", "")
        try:
            date = datetime.fromisoformat(date_raw.replace("Z", "+00:00")).date()
        except ValueError:
            date = date_raw or "the latest available session"

        summaries.append(
            f"{row.get('symbol', 'Unknown')} on {row.get('exchange', 'an exchange')} "
            f"last closed at {_fmt_money(row.get('close'))} on {date}. "
            f"The session range was {_fmt_money(row.get('low'))} to "
            f"{_fmt_money(row.get('high'))}, with volume "
            f"{int(row.get('volume', 0)):,} shares."
        )

    return "\n".join(summaries)
