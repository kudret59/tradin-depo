# KUDRET AI — Expert Agent Team & Engineering Plan

## Mission
Seek **risk-adjusted positive expectancy**, not guaranteed profit. Every agent's incentive is measured by honest out-of-sample contribution, drawdown control, and reproducibility; no agent is rewarded for simply producing BUY signals.

## Chain of command
Chief Assistant (orchestrator) -> research, market, altcoin, technical, on-chain, quant, ML, execution and engineering desks. Independent Risk Officer has an absolute veto.

## 12 desks
1. **Chief Assistant** — assigns tasks, reconciles disagreement, publishes sourced decisions.
2. **Market Regime Expert** — BTC/ETH trend, dominance, volatility, correlation.
3. **Altcoin Hunter** — universe discovery, liquidity, spreads, pump/dump filters.
4. **Technical Expert** — dip/top structures, EMA, RSI, multi-timeframe confirmation.
5. **On-chain Expert** — supply, unlocks, exchange flows, token fundamentals.
6. **Quant Researcher** — hypotheses, leakage-free backtests, walk-forward and Monte Carlo.
7. **Risk Officer** — max 1% equity risk per paper trade, max 3 simultaneous positions, hard veto.
8. **Paper Execution Expert** — orderbook-aware slippage, fees, partial fills, rejects.
9. **ML Engineer** — feature store, temporal splits, calibration, drift and champion/challenger.
10. **Data Engineer** — API ingestion, timestamps, deduplication, stale feed alarms.
11. **Security Engineer** — sandbox, auth, secrets, untrusted-web prompt injection defense.
12. **AI Research Librarian** — approved RSS/official docs, provenance and experiment briefs.

## Internet learning pipeline
Approved sources -> fetch -> store source/time/URL -> classify claims as UNVERIFIED -> human/automated source cross-check -> propose falsifiable hypothesis -> time-split backtest -> paper forward test -> review. Never fine-tune directly on scraped headlines, execute web-supplied code, or promote a strategy based only on in-sample returns.

`research_agents.py` provides a **real but limited** RSS ingestion module and a machine-readable agent roster. It does **not** run autonomous LLMs. Actual model-backed agents require credentials, model integration, orchestration, logging, evaluation and operating budget.

## Acceptance criteria
- Genuine Binance TR TRY discovery, timestamped OHLCV, retries and rate limits; no fabricated prices.
- Agent desks reflect actual queued/running/completed/failed jobs, not cosmetic activity.
- Deterministic, reproducible strategy tests; commissions, spread and slippage.
- Temporal train/validation/test split with no lookahead.
- Paper trades persisted, P&L reconciled; 1% risk, 3-position ceiling.
- Circuit breakers on stale data, disconnect, drawdown and abnormal volatility.
- Audit every recommendation: data snapshot, source, strategy version, dissent, veto, confidence calibration.
- No live orders until a separate explicit future authorization and safety review.

## Build order
1. Tests and local server hardening; CI.
2. Reliable Binance TR adapter and streaming pipeline.
3. Job queue, agent lifecycle and dashboard visualization.
4. Paper broker and trade accounting.
5. Research feeds and human-reviewed experiment registry.
6. LLM orchestration, source-grounded tools and offline evaluations.
7. Auth, HTTPS, deploy and operations.
