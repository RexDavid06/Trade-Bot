"""Indicator calculation.

Uses the same `ta` library and the same indicator definitions as bot.py
(EMA via close, RSI via close, ATR via high/low/close) so the backtest
reproduces the live strategy exactly. The `ta` rolling indicators only use
data up to and including the current row, so there is no look-ahead bias: the
value at row i is a pure function of rows [0, i].
"""

from __future__ import annotations

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange

from .config import StrategyConfig


def add_indicators(df: pd.DataFrame, cfg: StrategyConfig) -> pd.DataFrame:
    """Return a copy of `df` with EMA/RSI/ATR columns appended."""
    out = df.copy()
    out["ema_fast"] = EMAIndicator(out["close"], cfg.ema_fast).ema_indicator()
    out["ema_slow"] = EMAIndicator(out["close"], cfg.ema_slow).ema_indicator()
    out["rsi"] = RSIIndicator(out["close"], cfg.rsi_period).rsi()
    out["atr"] = AverageTrueRange(out["high"], out["low"], out["close"], cfg.atr_period).average_true_range()
    return out
