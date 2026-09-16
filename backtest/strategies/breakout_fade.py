"""Breakout-fade candidate strategy (Phase 5).

Fade upside breakouts (SELL when price breaks above the channel) and follow
downside breakouts (BUY when price breaks below the channel).  Based on
MARKET_RESEARCH_REPORT.md §2C — in this dataset upside breakouts tend to
fail (negative forward returns) while downside breakouts tend to continue
(positive forward returns).

Rules (simple, defensible, NOT optimised):
  BUY  when low < lowest low of prior CHANNEL bars  (downside break -> follow)
  SELL when high > highest high of prior CHANNEL bars (upside break -> fade)

Additional: require the break to be at least BREAK_ATR * ATR beyond the
channel level to filter noise.

SL/TP are handled by the backtester engine (ATR-based, same as V1).
No look-ahead: only bars <= signal candle used for channel computation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategy import BUY, SELL
from ..config import StrategyConfig

CHANNEL = 160
BREAK_ATR = 0.25
MIN_BARS = CHANNEL + 5


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add breakout helper columns if not already present."""
    if "bf_chan_high" not in df.columns:
        df = df.copy()
        # Prior N-bar channel (shift so the signal candle itself is excluded)
        df["bf_chan_high"] = df["high"].rolling(CHANNEL).max().shift(1)
        df["bf_chan_low"] = df["low"].rolling(CHANNEL).min().shift(1)
    return df


def signal_at(df: pd.DataFrame, i: int, cfg: StrategyConfig) -> str | None:
    """Breakout-fade signal at closed candle *i*."""
    if i < MIN_BARS:
        return None

    atr = float(df["atr"].iat[i]) if "atr" in df.columns else np.nan
    if pd.isna(atr) or atr <= 0:
        return None

    chan_hi = df["bf_chan_high"].iat[i] if "bf_chan_high" in df.columns else np.nan
    chan_lo = df["bf_chan_low"].iat[i] if "bf_chan_low" in df.columns else np.nan
    if pd.isna(chan_hi) or pd.isna(chan_lo):
        return None

    high = float(df["high"].iat[i])
    low = float(df["low"].iat[i])

    # Downside break -> follow (BUY)
    if low < chan_lo - BREAK_ATR * atr:
        return BUY

    # Upside break -> fade (SELL)
    if high > chan_hi + BREAK_ATR * atr:
        return SELL

    return None
