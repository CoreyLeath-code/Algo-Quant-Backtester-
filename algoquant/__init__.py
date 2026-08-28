"""Evidence-oriented quantitative backtesting primitives."""

from .backtester import Backtester
from .metrics import Metrics
from .strategies import MACDStrategy, RSIStrategy, SMAStrategy

__all__ = ["Backtester", "Metrics", "SMAStrategy", "RSIStrategy", "MACDStrategy"]
__version__ = "0.1.0"
