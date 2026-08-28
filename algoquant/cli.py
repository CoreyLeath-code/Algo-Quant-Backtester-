from __future__ import annotations

import argparse
import json

from .backtester import Backtester
from .benchmark import synthetic_market
from .strategies import SMAStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic AlgoQuant backtest demo.")
    parser.add_argument("--rows", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=20260828)
    parser.add_argument("--commission", type=float, default=0.0005)
    parser.add_argument("--slippage", type=float, default=0.0002)
    args = parser.parse_args()

    market = synthetic_market(args.rows, args.seed)
    engine = Backtester(
        data=market,
        strategy=SMAStrategy(20, 50),
        commission=args.commission,
        slippage=args.slippage,
    )
    engine.run()
    print(json.dumps(engine.get_metrics(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
