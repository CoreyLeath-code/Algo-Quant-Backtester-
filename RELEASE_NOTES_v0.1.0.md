# AlgoQuant Backtester v0.1.0

This is the first evidence-backed release of the repository's canonical Python backtesting package.

## Included

- deterministic bar-based backtester with one-bar signal lag to prevent same-bar look-ahead execution;
- explicit turnover-based commission and slippage rates;
- SMA, RSI, and MACD reference strategies;
- descriptive return/risk metrics with corrected Sharpe annualization;
- reproducible synthetic benchmark protocol with seed, sample count, runtime versions, commit SHA, latency percentiles, throughput, and traced memory;
- fail-closed Python 3.10/3.11/3.12 CI, wheel/sdist build-and-install verification, container smoke testing, CodeQL, and release artifacts;
- versioned GHCR container package.

## Evidence boundary

The benchmark uses deterministic synthetic prices and an in-process research backtest. It excludes live market data, broker/exchange connectivity, network latency, order-book simulation, market impact, concurrency, and production deployment. Strategy return metrics from that synthetic workload are reproducibility snapshots, not evidence of alpha, expected profitability, or investment suitability.

The legacy `agents/` directory contains experimental orchestration concepts, including a mocked LLM analyst path. v0.1.0 does **not** claim a live Claude integration, an institutional-grade trading platform, a hard real-time risk SLA, or automated live liquidation.
