from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd

from .backtester import Backtester
from .strategies import SMAStrategy

DEFAULT_SEED = 20260828


def synthetic_market(rows: int, seed: int) -> pd.DataFrame:
    if rows < 100:
        raise ValueError("rows must be at least 100 for the benchmark protocol.")
    rng = np.random.default_rng(seed)
    log_returns = rng.normal(loc=0.0002, scale=0.01, size=rows)
    close = 100.0 * np.exp(np.cumsum(log_returns))
    return pd.DataFrame({"Close": close})


def run_benchmark(*, rows: int, iterations: int, warmups: int, seed: int) -> dict[str, object]:
    if iterations <= 0 or warmups < 0:
        raise ValueError("iterations must be positive and warmups must be non-negative.")

    market = synthetic_market(rows, seed)
    strategy = SMAStrategy(short_window=20, long_window=50)

    for _ in range(warmups):
        Backtester(data=market, strategy=strategy, commission=0.0005, slippage=0.0002).run()

    durations_ms: list[float] = []
    tracemalloc.start()
    started = time.perf_counter()
    last_engine: Backtester | None = None
    for _ in range(iterations):
        engine = Backtester(data=market, strategy=strategy, commission=0.0005, slippage=0.0002)
        t0 = time.perf_counter_ns()
        engine.run()
        durations_ms.append((time.perf_counter_ns() - t0) / 1_000_000.0)
        last_engine = engine
    elapsed = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert last_engine is not None
    metrics = last_engine.get_metrics()
    durations = np.asarray(durations_ms, dtype=float)

    return {
        "protocol": {
            "seed": seed,
            "rows_per_backtest": rows,
            "warmups": warmups,
            "measured_iterations": iterations,
            "strategy": "SMA(20,50), long-only",
            "commission_rate": 0.0005,
            "slippage_rate": 0.0002,
            "scope": "in-process synthetic-data backtest; excludes network, market-data I/O, dashboards, and live execution",
        },
        "environment": {
            "git_sha": os.getenv("GITHUB_SHA", "local-unpinned"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "performance": {
            "mean_ms": round(float(statistics.fmean(durations_ms)), 6),
            "median_ms": round(float(np.median(durations)), 6),
            "p95_ms": round(float(np.percentile(durations, 95)), 6),
            "p99_ms": round(float(np.percentile(durations, 99)), 6),
            "backtests_per_second": round(iterations / elapsed, 6),
            "rows_per_second": round((rows * iterations) / elapsed, 3),
            "peak_traced_memory_mib": round(peak_bytes / (1024 * 1024), 6),
        },
        "deterministic_result_snapshot": metrics,
        "interpretation": "Performance is a development benchmark of deterministic synthetic research execution, not evidence of trading profitability or production/live-market latency.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible AlgoQuant development benchmark.")
    parser.add_argument("--rows", type=int, default=5_000)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run_benchmark(rows=args.rows, iterations=args.iterations, warmups=args.warmups, seed=args.seed)
    rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
