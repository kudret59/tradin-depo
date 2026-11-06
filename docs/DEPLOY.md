# KUDRET AI — Running and deploying (paper only)

## Local Windows / macOS / Linux
Requires Python 3.11+.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python server.py
```

Open http://127.0.0.1:8765. Use the dashboard's **scan** and **research** controls. Neither requires an API key. This currently uses Binance Global USDT spot public data, **not** Binance TR TRY pairs.

## Optional background simulation
Set environment variables before running:

- `KUDRET_AUTO_SCAN=1` starts a periodic market scan.
- `KUDRET_SCAN_INTERVAL=300` sets scan interval in seconds (minimum 60).
- `KUDRET_AUTO_PAPER=1` enables paper entries after scans; **requires** auto-scan enabled.
- `KUDRET_OLLAMA_MODEL=qwen2.5:3b` selects an optional local model.

The default is **manual research with no automatic entries**. Simulation uses closed 4-hour candles, estimated fees/slippage and a 1% position risk budget; it does not model exchange order books or guarantee executable prices. The broker checks stop/target only when a fresh scan supplies a quote, so real stop execution is not guaranteed. Paper portfolio and jobs persist in local SQLite. Initial paper cash is 10,000 simulated USDT units.

## Deployment warning
The server binds to `127.0.0.1` intentionally. This Dockerfile is for local/isolated evaluation; it does **not** expose a publicly accessible web service without an authenticated reverse proxy, HTTPS, and a durable database volume. Do not change the bind address to `0.0.0.0` on an untrusted network. Public hosting has **not** been deployed.

## LLM research
`llm_local.py` supports an optional local Ollama server, but it is not yet scheduled as an autonomous agent and does not trade. `integrations/tradingagents_bridge.py` requires the separately reviewed TradingAgents framework and a configured LLM provider. It has not been integrated into the automatic paper broker.

## Validation checklist
- Confirm all offline tests pass in GitHub Actions.
- Check whether Binance API access is available in the target region; never fabricate fallback prices.
- Compare simulated fills to real orderbook conditions before trusting profitability.
- Verify SQLite persistence, task errors, and agent job lifecycle.
- Validate Binance TR symbols, precision, filters, rate limits and API data contract separately.
- Deploy only behind authenticated HTTPS and persistent storage.

**No real trading functionality is included.**
