import pandas as pd
import pytest

from algoquant import Backtester


class ConstantStrategy:
    def __init__(self, signal: float):
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        return pd.Series(self.signal, index=data.index, dtype=float)


def test_signal_is_applied_with_one_bar_lag():
    market = pd.DataFrame({"Close": [100.0, 110.0, 121.0]})
    result = Backtester(data=market, strategy=ConstantStrategy(1.0)).run()
    assert result.loc[0, "Position"] == 0.0
    assert result.loc[1, "Position"] == 1.0
    assert result.loc[0, "Net_Returns"] == 0.0
    assert result.loc[1, "Net_Returns"] == pytest.approx(0.10)


def test_turnover_costs_are_charged_as_return_rates():
    market = pd.DataFrame({"Close": [100.0, 100.0, 100.0]})
    result = Backtester(
        data=market,
        strategy=ConstantStrategy(1.0),
        commission=0.001,
        slippage=0.002,
    ).run()
    assert result.loc[1, "Turnover"] == 1.0
    assert result.loc[1, "Transaction_Cost"] == pytest.approx(0.003)
    assert result.loc[1, "Net_Returns"] == pytest.approx(-0.003)


def test_input_dataframe_is_not_mutated():
    market = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})
    original = market.copy(deep=True)
    Backtester(data=market, strategy=ConstantStrategy(0.0)).run()
    pd.testing.assert_frame_equal(market, original)


def test_close_column_is_required():
    with pytest.raises(ValueError, match="Close"):
        Backtester(data=pd.DataFrame({"Open": [1.0]}), strategy=ConstantStrategy(0.0)).run()


def test_exactly_one_data_source_is_required(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("Close\n100\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one"):
        Backtester(
            data=pd.DataFrame({"Close": [100.0]}),
            data_path=csv_path,
            strategy=ConstantStrategy(0.0),
        )
