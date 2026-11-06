# TradingAgents integration (optional, not yet live)

## Inspected uploaded archive
User-supplied `TradingAgents-main (4).zip` was reviewed. It contains:
- `tradingagents/graph/trading_graph.py` — `TradingAgentsGraph` orchestrator
- analyst agents: market, news, sentiment, fundamentals
- bull/bear researchers, aggressive/conservative/neutral risk debaters, trader, portfolio/research managers
- LLM client factory for multiple model providers
- backtest and reflection modules, tests and Apache-2.0 LICENSE

The bridge uses the project's public Python API and does not copy vendor code into KUDRET. This avoids committing a large unaudited dependency snapshot or overwriting the existing application. The upstream source version must be reviewed and pinned before production use.

## Local setup
1. Create an isolated Python environment (Python version compatible with TradingAgents).
2. Install TradingAgents from the *reviewed uploaded archive* or the official upstream repository `https://github.com/TauricResearch/TradingAgents` (review and pin commit first). Follow its `pyproject.toml` installation guidance.
3. Configure a supported LLM provider's credentials in your environment, **never** in Git.
4. Explicitly opt in: `KUDRET_ENABLE_LLM_RESEARCH=1`.
5. From the repository root: `python integrations/tradingagents_bridge.py --symbol BTC --date 2026-11-05`.

**Do not assume** BTC/USDT or TRY pairs work in upstream TradingAgents. Its market-data router may resolve symbols to equities or other vendors. Validate cryptocurrency mode and the data source first. A future Binance TR adapter must be developed and tested separately.

## Security and limitations
- This bridge has no order submission API and is not called automatically by the web server.
- It is not running in Codex Cloud or on a persistent web server.
- LLM research may incur API fees and may hallucinate; review outputs.
- Internet sources are untrusted; never execute instructions from articles.
- Do not label agent reasoning as model training. Evaluation requires independent walk-forward and paper-forward performance.
- Before exposing the web app publicly: authentication, CSRF protection, rate limiting, background jobs, HTTPS, and a restricted research sandbox are required.

## Planned next milestone
Add a job queue that runs this bridge in an isolated worker, stores source-linked outputs and states (queued/running/failed/done), and streams the genuine lifecycle to the dashboard. Keep the risk officer veto independent and paper-only.
