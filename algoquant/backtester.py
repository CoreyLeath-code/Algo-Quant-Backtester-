from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd

from .metrics import Metrics


class Strategy(Protocol):
    """Strategy contract consumed by :class:`Backtester`."""

    def generate_signals(self, data: pd.DataFrame) -> pd.Series: ...


class Backtester:
    """Deterministic vectorized backtester for bar-based research.

    Signals generated from information available at bar ``t`` are applied as
    positions on bar ``t + 1``. Commission and slippage are decimal return costs
    per unit of turnover (for example ``0.001`` = 10 bps).

    This is a research simulator, not an exchange/order-management system.
    """

    def __init__(
        self,
        *,
        strategy: Strategy,
        data: pd.DataFrame | None = None,
        data_path: str | Path | None = None,
        initial_capital: float = 100_000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        trading_days: int = 252,
    ) -> None:
        if (data is None) == (data_path is None):
            raise ValueError("Provide exactly one of data or data_path.")
        if initial_capital <= 0:
            raise ValueError("initial_capital must be positive.")
        if commission < 0 or slippage < 0:
            raise ValueError("commission and slippage must be non-negative rates.")
        if trading_days <= 0:
            raise ValueError("trading_days must be positive.")

        self.strategy = strategy
        self._input_data = data.copy(deep=True) if data is not None else None
        self.data_path = Path(data_path) if data_path is not None else None
        self.initial_capital = float(initial_capital)
        self.commission = float(commission)
        self.slippage = float(slippage)
        self.trading_days = int(trading_days)
        self.data: pd.DataFrame | None = None
        self.results: pd.DataFrame | None = None

    def load_data(self) -> pd.DataFrame:
        """Load and validate market data without mutating caller-owned frames."""
        if self._input_data is not None:
            frame = self._input_data.copy(deep=True)
        else:
            assert self.data_path is not None
            frame = pd.read_csv(self.data_path)

        if "Close" not in frame.columns:
            raise ValueError("Market data must contain a 'Close' column.")
        if frame.empty:
            raise ValueError("Market data must contain at least one row.")

        close = pd.to_numeric(frame["Close"], errors="coerce")
        if close.isna().any() or not np.isfinite(close.to_numpy(dtype=float)).all():
            raise ValueError("'Close' must contain only finite numeric values.")
        if (close <= 0).any():
            raise ValueError("'Close' prices must be strictly positive.")
        frame["Close"] = close.astype(float)

        if "Date" in frame.columns:
            parsed = pd.to_datetime(frame["Date"], errors="coerce", utc=True)
            if parsed.isna().any():
                raise ValueError("'Date' contains unparseable timestamps.")
            frame = frame.assign(Date=parsed).sort_values("Date", kind="stable")

        frame = frame.reset_index(drop=True)
        self.data = frame
        return frame

    def run(self) -> pd.DataFrame:
        """Execute the strategy with one-bar signal lag and turnover-based costs."""
        frame = self.load_data() if self.data is None else self.data.copy(deep=True)

        raw_signals = self.strategy.generate_signals(frame.copy(deep=True))
        if not isinstance(raw_signals, pd.Series):
            raw_signals = pd.Series(raw_signals, index=frame.index, dtype=float)
        else:
            raw_signals = raw_signals.reindex(frame.index)

        signals = pd.to_numeric(raw_signals, errors="coerce").fillna(0.0).astype(float)
        if not np.isfinite(signals.to_numpy()).all():
            raise ValueError("Strategy signals must be finite.")
        signals = signals.clip(-1.0, 1.0)

        returns = frame["Close"].pct_change(fill_method=None).fillna(0.0)
        positions = signals.shift(1).fillna(0.0)
        turnover = positions.diff().abs().fillna(positions.abs())
        gross_returns = positions * returns
        transaction_cost = turnover * (self.commission + self.slippage)
        net_returns = gross_returns - transaction_cost

        frame["Returns"] = returns
        frame["Signal"] = signals
        frame["Position"] = positions
        frame["Gross_Returns"] = gross_returns
        frame["Turnover"] = turnover
        frame["Transaction_Cost"] = transaction_cost
        frame["Net_Returns"] = net_returns
        frame["Equity"] = self.initial_capital * (1.0 + net_returns).cumprod()

        self.results = frame
        return frame.copy(deep=True)

    def get_metrics(self) -> dict[str, float]:
        """Return research metrics for the completed backtest."""
        if self.results is None:
            raise RuntimeError("Run the backtest before requesting metrics.")
        metrics = Metrics(
            self.results["Net_Returns"],
            self.results["Equity"],
            trading_days=self.trading_days,
        )
        return metrics.compute_all()

    def save_results(self, out_path: str | Path = "backtest_results.csv") -> None:
        """Persist the completed result frame as CSV."""
        if self.results is None:
            raise RuntimeError("Run the backtest before saving results.")
        self.results.to_csv(out_path, index=False)
