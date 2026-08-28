import math

import pandas as pd
import pytest

from algoquant.metrics import Metrics


def test_total_return_and_drawdown():
    returns = pd.Series([0.0, 0.10, -0.10])
    equity = 100.0 * (1.0 + returns).cumprod()
    metrics = Metrics(returns, equity, trading_days=252)
    assert metrics.total_return() == pytest.approx(-0.01)
    assert metrics.max_drawdown() == pytest.approx(-0.10)


def test_sharpe_is_annualized_once():
    returns = pd.Series([0.01, 0.02, -0.01, 0.00])
    equity = 100.0 * (1.0 + returns).cumprod()
    metrics = Metrics(returns, equity, trading_days=252)
    expected = returns.mean() / returns.std(ddof=1) * math.sqrt(252)
    assert metrics.sharpe() == pytest.approx(expected)


def test_compute_all_has_finite_core_values():
    returns = pd.Series([0.0, 0.01, -0.005, 0.002])
    equity = 100.0 * (1.0 + returns).cumprod()
    report = Metrics(returns, equity).compute_all()
    for key in ["total_return", "cagr", "annualized_volatility", "sharpe_ratio", "max_drawdown"]:
        assert math.isfinite(report[key])
