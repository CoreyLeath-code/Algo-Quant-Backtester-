from __future__ import annotations

import pandas as pd


def _validate_window(name: str, value: int) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be positive.")
    return int(value)


class SMAStrategy:
    """Simple moving-average crossover strategy."""

    def __init__(self, short_window: int = 20, long_window: int = 50, allow_short: bool = False) -> None:
        self.short_window = _validate_window("short_window", short_window)
        self.long_window = _validate_window("long_window", long_window)
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be smaller than long_window.")
        self.allow_short = bool(allow_short)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["Close"].astype(float)
        fast = close.rolling(self.short_window, min_periods=self.short_window).mean()
        slow = close.rolling(self.long_window, min_periods=self.long_window).mean()
        ready = fast.notna() & slow.notna()
        signal = pd.Series(0.0, index=data.index)
        signal.loc[ready & (fast > slow)] = 1.0
        if self.allow_short:
            signal.loc[ready & (fast < slow)] = -1.0
        return signal


class RSIStrategy:
    """RSI threshold strategy using rolling mean gains/losses."""

    def __init__(
        self,
        window: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        allow_short: bool = False,
    ) -> None:
        self.window = _validate_window("window", window)
        if not 0 <= oversold < overbought <= 100:
            raise ValueError("Require 0 <= oversold < overbought <= 100.")
        self.oversold = float(oversold)
        self.overbought = float(overbought)
        self.allow_short = bool(allow_short)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["Close"].astype(float)
        delta = close.diff()
        gain = delta.clip(lower=0.0).rolling(self.window, min_periods=self.window).mean()
        loss = (-delta.clip(upper=0.0)).rolling(self.window, min_periods=self.window).mean()
        rs = gain / loss.replace(0.0, float("nan"))
        rsi = 100.0 - 100.0 / (1.0 + rs)
        rsi = rsi.where(loss != 0.0, 100.0)
        signal = pd.Series(0.0, index=data.index)
        signal.loc[rsi <= self.oversold] = 1.0
        if self.allow_short:
            signal.loc[rsi >= self.overbought] = -1.0
        return signal


class MACDStrategy:
    """MACD line/signal-line crossover strategy."""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, allow_short: bool = False) -> None:
        self.fast = _validate_window("fast", fast)
        self.slow = _validate_window("slow", slow)
        self.signal = _validate_window("signal", signal)
        if self.fast >= self.slow:
            raise ValueError("fast must be smaller than slow.")
        self.allow_short = bool(allow_short)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["Close"].astype(float)
        fast_ema = close.ewm(span=self.fast, adjust=False).mean()
        slow_ema = close.ewm(span=self.slow, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=self.signal, adjust=False).mean()
        result = pd.Series(0.0, index=data.index)
        result.loc[macd_line > signal_line] = 1.0
        if self.allow_short:
            result.loc[macd_line < signal_line] = -1.0
        return result
