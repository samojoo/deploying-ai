from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Iterable

import chromadb
from langchain.tools import tool

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "market_knowledge.md"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "market_knowledge"


class HashEmbeddingFunction:
    """Small deterministic embedding fallback that keeps Chroma file-persistent."""

    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions

    @staticmethod
    def name() -> str:
        return "global_ticker_hash_embedding"

    @staticmethod
    def build_from_config(config: dict) -> "HashEmbeddingFunction":
        return HashEmbeddingFunction(dimensions=config.get("dimensions", 128))

    def get_config(self) -> dict:
        return {"dimensions": self.dimensions}

    def __call__(self, input: Iterable[str]) -> list[list[float]]:
        return [self._embed(text) for text in input]

    def embed_query(self, input: Iterable[str]) -> list[list[float]]:
        return self.__call__(input)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % self.dimensions
            vector[idx] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def _chunks_from_markdown(text: str) -> list[str]:
    chunks = []
    current = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if chunk and not chunk.startswith("# Market Knowledge")]


def _get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=HashEmbeddingFunction(),
    )

    if collection.count() == 0:
        chunks = _chunks_from_markdown(DATA_PATH.read_text(encoding="utf-8"))
        collection.add(
            ids=[f"market-note-{i}" for i in range(len(chunks))],
            documents=chunks,
        )
    return collection


@tool
def search_market_knowledge(query: str, n_results: int = 2) -> str:
    """
    Search the local market knowledge base for explanations of tickers, exchanges,
    end-of-day prices, adjusted close, volume, and global listings.
    """
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=max(1, min(n_results, 4)))
    documents = results.get("documents", [[]])[0]
    if not documents:
        return "I could not find a relevant note in the local market knowledge base."
    return "\n\n".join(documents)
