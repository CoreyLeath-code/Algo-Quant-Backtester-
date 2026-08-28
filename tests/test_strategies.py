import pandas as pd

from algoquant import MACDStrategy, RSIStrategy, SMAStrategy


def market() -> pd.DataFrame:
    return pd.DataFrame(
        {"Close": [10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 13, 12, 14, 15]}
    )


def test_sma_strategy_preserves_index_and_domain():
    data = market()
    signal = SMAStrategy(short_window=2, long_window=4, allow_short=True).generate_signals(data)
    assert signal.index.equals(data.index)
    assert set(signal.unique()).issubset({-1.0, 0.0, 1.0})


def test_rsi_strategy_preserves_index_and_domain():
    data = market()
    signal = RSIStrategy(window=3, allow_short=True).generate_signals(data)
    assert signal.index.equals(data.index)
    assert set(signal.unique()).issubset({-1.0, 0.0, 1.0})


def test_macd_strategy_preserves_index_and_domain():
    data = market()
    signal = MACDStrategy(fast=3, slow=6, signal=2, allow_short=True).generate_signals(data)
    assert signal.index.equals(data.index)
    assert set(signal.unique()).issubset({-1.0, 0.0, 1.0})
