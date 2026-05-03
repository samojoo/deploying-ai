from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
import gradio as gr
from langchain_core.messages import AIMessage, HumanMessage

from assignment_chat.main import get_graph

load_dotenv("05_src/.secrets")
load_dotenv(".secrets")

llm = get_graph()

BLOCKED_TERMS = [
    "cat",
    "cats",
    "dog",
    "dogs",
    "horoscope",
    "horoscopes",
    "zodiac",
    "taylor swift",
    "system prompt",
    "developer message",
    "change your instructions",
    "modify your instructions",
]


def _is_blocked(message: str) -> bool:
    text = message.lower()
    return any(term in text for term in BLOCKED_TERMS)


def assignment_chat(message: str, history: list[dict]) -> str:
    if _is_blocked(message):
        return (
            "I can’t help with that topic or request. I can help with stock tickers, "
            "latest available end-of-day prices, exchange codes, or ticker comparisons."
        )

    langchain_messages = []
    for msg in history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    langchain_messages.append(HumanMessage(content=message))
    response = llm.invoke({"messages": langchain_messages})
    return response["messages"][-1].content


chat = gr.ChatInterface(
    fn=assignment_chat,
    type="messages",
    title="Global Ticker Desk",
    description=(
        "Ask about latest available end-of-day ticker prices, market terms, "
        "exchange codes, or simple ticker comparisons. Educational only."
    ),
    examples=[
        "What is the latest available price for AAPL?",
        "Compare AAPL and MSFT.",
        "What does end-of-day price mean?",
        "What does volume tell me?",
    ],
)


if __name__ == "__main__":
    chat.launch()
