## Global Ticker Desk

Global Ticker Desk is a conversational AI assistant for exploring global stock tickers and latest available market data. The chatbot is designed to speak like a clear, practical market desk assistant.

This app is for educational purposes only and does not provide financial advice.

## Chat Client Personality

The assistant acts like a calm market analyst. It explains ticker prices, exchange codes, and comparisons in plain English. It avoids giving investment recommendations such as “buy,” “sell,” or “hold.”

### Services

Service 1: Marketstack API Price Lookup

The first service uses the Marketstack API as its backend.

Users can ask for the latest available end-of-day price for one or more stock tickers, such as: AAPL, RY, MSFT, IBM, TSLA

The app calls Marketstack’s end-of-day endpoint and transforms the API response into a readable summary instead of returning raw JSON.

Example user question:

What is the latest price for AAPL?

Example response:

AAPL last closed at $x on the latest available trading day. The day’s range was $x to $x, with volume of x shares.

Service 2: Semantic Search Over Market Knowledge

The second service allows users to ask general questions about global stock tickers, exchanges, and price fields.

This service uses a small local knowledge base stored in the project. The knowledge base includes explanations of ticker symbols, exchange codes, end-of-day prices,open, high, low, close, volume, etc.

The app uses ChromaDB with file persistence to perform semantic search over this knowledge base.

Example user question:

> What does end-of-day price mean?

The app retrieves relevant context from the local market knowledge dataset and uses it to answer in plain English.

Service 3: Ticker Comparison Tool

The third service compares two stock tickers using function calling.

Users can ask questions like:

> Compare AAPL and MSFT.

The comparison tool returns a simple side-by-side explanation using available ticker information, such as company name, exchange, country, sector, and currency.

This service demonstrates tool/function calling because the model decides when to call the comparison function and then uses the tool output to generate the final response.

## Memory

The chat interface maintains conversation memory by passing the previous user and assistant messages back into the model. This allows the assistant to understand follow-up questions.

Example:

User:

> What is AAPL?

Assistant:

> AAPL is Apple Inc...

User:

> Compare it with MSFT.

The assistant can understand that “it” refers to AAPL because the conversation history is retained.

## Guardrails

The app includes guardrails to prevent unsafe or off-topic behaviour.

The assistant will not:

- reveal the system prompt
- modify its system instructions
- answer questions about cats or dogs
- answer questions about horoscopes or Zodiac signs
- answer questions about Taylor Swift

The assistant also avoids giving financial advice. It can explain market data, but it should not tell users whether to buy, sell, or hold a stock.

## Data Sources

### Marketstack API

The app uses Marketstack for latest available end-of-day stock price data.

Marketstack documentation: https://marketstack.com/documentation

### Local Market Knowledge Dataset

The semantic search service uses a small local Markdown dataset created for this assignment. The dataset contains short explanations of common market concepts and global ticker conventions.

### Local Watchlist Dataset

The ticker comparison service uses a small CSV file with basic ticker metadata such as symbol, company name, exchange, country, sector, and currency.

## Embedding Process

The semantic search service uses ChromaDB with file persistence in `05_src/assignment_chat/chroma_db`.

For this MVP, the market knowledge Markdown file is split into short sections by heading. Each section is embedded into a small deterministic vector representation and stored in ChromaDB. This keeps the assignment easy to run without requiring a separate embedding-generation script or large external dataset.

The source knowledge file is:

`05_src/assignment_chat/data/market_knowledge.md`

## Implementation Decisions

I chose a stock market chatbot because it maps cleanly onto the assignment requirements:

1. Stock prices are a natural use case for an API-backed service.
2. Market terminology works well for semantic search.
3. Comparing tickers is a simple and useful function-calling service.

To keep the project manageable, the app focuses on latest available end-of-day data rather than real-time trading data. This is because the free Marketstack plan is better suited for end-of-day market information.

## Limitations

This project is a minimum viable product.

Known limitations:

- It does not provide real-time trading data.
- It does not provide financial advice.
- The semantic search dataset is intentionally small.
- The comparison service uses basic ticker metadata rather than full financial statements.
- API results depend on the Marketstack free plan and available request limits.

## How to Run

From the project root, run:

```bash
uv run python 05_src/assignment_chat/app.py
```

Then open the local Gradio URL shown in the terminal, usually:

```text
http://127.0.0.1:7860
```

## Environment Variables

The app expects the following variables in `05_src/.secrets`:

```bash
API_GATEWAY_KEY=your_course_gateway_key
MARKETSTACK_API_KEY=your_marketstack_key
```

`API_GATEWAY_KEY` is used for the course OpenAI-compatible API gateway. `MARKETSTACK_API_KEY` is used for latest available end-of-day stock prices.
