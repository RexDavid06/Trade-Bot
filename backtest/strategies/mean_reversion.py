"""Mean-reversion candidate strategy (Phase 5).

Fade-the-extreme: trade AGAINST the direction of recent over-extension from
the trailing mean.  Based on MARKET_RESEARCH_REPORT.md §2B — bars far below
the mean (< -1 sigma) tend to show positive forward returns; bars far above
(> +1 sigma) tend to show negative forward returns.

Rules (simple, defensible, NOT optimised):
  BUY  when close < SMA(10) - 1.0 * rolling_std(10)   (oversold)
  SELL when close > SMA(10) + 1.0 * rolling_std(10)   (overbought)

Additional filter: require at least MIN_BARS warmup so the SMA/std is stable.

SL/TP are handled by the backtester engine (ATR-based, same as V1).
No look-ahead: all values use only data up to and including the signal candle.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategy import BUY, SELL
from ..config import StrategyConfig

SMA_WINDOW = 10
SIGMA_MULT = 1.0
MIN_BARS = SMA_WINDOW + 5


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add mean-reversion helper columns if not already present."""
    if "mr_sma" not in df.columns:
        df = df.copy()
        df["mr_sma"] = df["close"].rolling(SMA_WINDOW).mean()
        df["mr_std"] = df["close"].rolling(SMA_WINDOW).std()
    return df


def signal_at(df: pd.DataFrame, i: int, cfg: StrategyConfig) -> str | None:
    """Mean-reversion signal at closed candle *i*."""
    if i < MIN_BARS:
        return None

    close = float(df["close"].iat[i])
    sma = df["mr_sma"].iat[i] if "mr_sma" in df.columns else np.nan
    std = df["mr_std"].iat[i] if "mr_std" in df.columns else np.nan

    if pd.isna(sma) or pd.isna(std) or std <= 0:
        return None

    lower = sma - SIGMA_MULT * std
    upper = sma + SIGMA_MULT * std

    if close < lower:
        return BUY   # oversold -> expect bounce
    if close > upper:
        return SELL  # overbought -> expect drop
    return None
