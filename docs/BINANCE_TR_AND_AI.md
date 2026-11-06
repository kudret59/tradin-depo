# Binance TR + local AI — integration status

- `binance_tr.py` uses Binance TR public symbol and kline endpoints, without a personal API key. These were derived from Binance TR developer documentation, but **live network connectivity has not been verified**.
- `server.py` now scans TRY markets (not Binance Global USDT). If the public API is inaccessible or malformed, scanning fails closed and does not fabricate candles.
- Enable periodic scanning: `KUDRET_AUTO_SCAN=1`.
- Enable automatic paper-only entries: `KUDRET_AUTO_PAPER=1` (requires auto scan).
- Enable local LLM research: install and run Ollama, download a compatible model, then set `KUDRET_AUTO_LLM=1` and `KUDRET_OLLAMA_MODEL=qwen2.5:3b`. This does not require a cloud API key but **does require a running local model server**.
- `GET /api/llm` shows the latest model research output or error. Local model output does not authorize paper trades.
- TradingAgents crypto support: the optional bridge calls `graph.propagate(symbol,date,asset_type="crypto")`, as confirmed from the user-supplied TradingAgents archive. The TradingAgents dependency is not installed automatically; its crypto data providers may not match Binance TR TRY markets.
- All balances are virtual; the broker uses an illustrative fee/slippage model, not a live order book.
- The repository is **not deployed** as a public website. The server intentionally binds to localhost.
- CI tests, live Binance TR response parsing, Ollama startup, and the upstream TradingAgents graph still need end-to-end verification before describing the system as fully operational.
