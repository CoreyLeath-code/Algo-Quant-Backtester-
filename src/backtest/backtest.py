"""Compatibility shim for the pre-v0.1 backtester import path.

New code should import :class:`algoquant.Backtester`.
"""

from algoquant.backtester import Backtester

__all__ = ["Backtester"]
