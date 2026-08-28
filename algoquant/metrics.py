from __future__ import annotations

import math

import numpy as np
import pandas as pd


class Metrics:
    """Small, explicit metric set for bar-return research."""

    def __init__(self, returns: pd.Series, equity: pd.Series, trading_days: int = 252) -> None:
        if trading_days <= 0:
            raise ValueError("trading_days must be positive.")
        self.returns = pd.Series(returns, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
        self.equity = pd.Series(equity, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
        if self.returns.empty or self.equity.empty:
            raise ValueError("returns and equity must contain finite observations.")
        self.trading_days = int(trading_days)

    def total_return(self) -> float:
        return float((1.0 + self.returns).prod() - 1.0)

    def cagr(self) -> float:
        years = len(self.returns) / self.trading_days
        growth = 1.0 + self.total_return()
        if years <= 0 or growth <= 0:
            return -1.0
        return float(growth ** (1.0 / years) - 1.0)

    def volatility(self) -> float:
        if len(self.returns) < 2:
            return 0.0
        return float(self.returns.std(ddof=1) * math.sqrt(self.trading_days))

    def sharpe(self, risk_free_rate: float = 0.0) -> float:
        if len(self.returns) < 2:
            return 0.0
        daily_rf = (1.0 + risk_free_rate) ** (1.0 / self.trading_days) - 1.0
        excess = self.returns - daily_rf
        std = float(excess.std(ddof=1))
        if std == 0.0 or not math.isfinite(std):
            return 0.0
        return float(excess.mean() / std * math.sqrt(self.trading_days))

    def sortino(self, risk_free_rate: float = 0.0) -> float:
        daily_rf = (1.0 + risk_free_rate) ** (1.0 / self.trading_days) - 1.0
        excess = self.returns - daily_rf
        downside = np.minimum(excess.to_numpy(dtype=float), 0.0)
        downside_deviation = float(np.sqrt(np.mean(np.square(downside))))
        if downside_deviation == 0.0 or not math.isfinite(downside_deviation):
            return 0.0
        return float(excess.mean() / downside_deviation * math.sqrt(self.trading_days))

    def max_drawdown(self) -> float:
        running_max = self.equity.cummax()
        drawdown = self.equity / running_max - 1.0
        return float(drawdown.min())

    def calmar(self) -> float:
        drawdown = abs(self.max_drawdown())
        return float(self.cagr() / drawdown) if drawdown > 0 else 0.0

    def win_rate(self) -> float:
        non_zero = self.returns[self.returns != 0]
        return float((non_zero > 0).mean()) if not non_zero.empty else 0.0

    def profit_factor(self) -> float:
        gross_profit = float(self.returns[self.returns > 0].sum())
        gross_loss = abs(float(self.returns[self.returns < 0].sum()))
        if gross_loss == 0.0:
            return 0.0 if gross_profit == 0.0 else float("inf")
        return gross_profit / gross_loss

    def expectancy(self) -> float:
        return float(self.returns.mean())

    def compute_all(self) -> dict[str, float]:
        values = {
            "total_return": self.total_return(),
            "cagr": self.cagr(),
            "annualized_volatility": self.volatility(),
            "sharpe_ratio": self.sharpe(),
            "sortino_ratio": self.sortino(),
            "max_drawdown": self.max_drawdown(),
            "calmar_ratio": self.calmar(),
            "win_rate": self.win_rate(),
            "profit_factor": self.profit_factor(),
            "expectancy": self.expectancy(),
        }
        return {
            key: round(value, 8) if math.isfinite(value) else value
            for key, value in values.items()
        }
