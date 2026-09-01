"""Signal generation.

Replicates the exact BUY/SELL rules from bot.py:

    BUY  : ema_fast > ema_slow AND rsi_buy_min < rsi < rsi_buy_max
    SELL : ema_fast < ema_slow AND rsi_sell_min < rsi < rsi_sell_max

Strict (non-inclusive) inequalities are used, matching bot.py's `40 < rsi < 55`
and `45 < rsi < 60`. Signals are evaluated only on a fully closed candle.
"""

from __future__ import annotations

import pandas as pd

from .config import StrategyConfig

BUY = "BUY"
SELL = "SELL"


def _valid(df: pd.DataFrame, i: int) -> bool:
    """Indicators are valid only once the slow EMA has warmed up."""
    return not (
        pd.isna(df["ema_fast"].iat[i])
        or pd.isna(df["ema_slow"].iat[i])
        or pd.isna(df["rsi"].iat[i])
        or pd.isna(df["atr"].iat[i])
    )


def signal_at(df: pd.DataFrame, i: int, cfg: StrategyConfig) -> str | None:
    """Return BUY/SELL for closed candle `i`, or None if no signal.

    The direction conditions match bot.py. When `cfg.ema_sep_min` > 0, an
    additional filter requires the normalized EMA separation
    ``abs(EMA50 - EMA200) / ATR`` to exceed that value (stronger trend), which
    is a controlled-experiment refinement of the baseline rules.
    """
    if not _valid(df, i):
        return None

    ema_fast = df["ema_fast"].iat[i]
    ema_slow = df["ema_slow"].iat[i]
    rsi = df["rsi"].iat[i]
    atr = df["atr"].iat[i]

    if cfg.ema_sep_min > 0 and atr > 0:
        separation = abs(ema_fast - ema_slow) / atr
        if separation <= cfg.ema_sep_min:
            return None

    if ema_fast > ema_slow and cfg.rsi_buy_min < rsi < cfg.rsi_buy_max:
        return BUY
    if ema_fast < ema_slow and cfg.rsi_sell_min < rsi < cfg.rsi_sell_max:
        return SELL
    return None
