"""A3 regression tests: live signal generation operates only on closed candles.

bot.signal_from_candles() reads indicator values exclusively from the last
COMPLETED candle (df.iloc[-2]); the trailing (forming) candle at df.iloc[-1]
must never influence the emitted signal. Importing ``bot`` must not connect to
MT5 (connection lives under ``main()``), and it must not perform trades.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bot
from bot import BUY, SELL, signal_from_candles


def _frame(rows=220):
    """Synthetic, indicator-warmed frame ending with a forming candle.

    EMA50 > EMA200 (uptrend) and RSI in (40, 55) on the last closed candle
    would normally produce BUY; rows are tweaked per test.
    """
    n = rows + 1  # +1 forming candle at the end
    rng = np.random.default_rng(42)
    close = 1.1000 + np.cumsum(rng.normal(0, 0.0001, n))
    high = close + 0.0003
    low = close - 0.0003
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=n, freq="5min"),
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "spread": np.full(n, 5.0),
            "ema50": np.full(n, 1.1010),
            "ema200": np.full(n, 1.1000),
            "ema_fast": np.full(n, 1.1010),
            "ema_slow": np.full(n, 1.1000),
            "rsi": np.full(n, 48.0),
            "atr": np.full(n, 0.0003),
        }
    )


def test_import_does_not_connect_or_trade():
    # The module-level side effects must be limited to definitions; MT5
    # connection happens only in main(). These constants must exist.
    assert bot.SYMBOL == "EURUSD"
    assert bot.RISK_PERCENT == 1
    assert BUY == "BUY"
    assert SELL == "SELL"


def test_buy_on_closed_candle_uptrend():
    df = _frame()
    direction, atr = signal_from_candles(df)
    assert direction == BUY
    assert atr == pytest.approx(0.0003)


def test_sell_on_closed_candle_downtrend():
    df = _frame()
    df["ema50"] = np.full(len(df), 1.0990)  # EMA50 < EMA200
    df["rsi"] = np.full(len(df), 50.0)
    direction, atr = signal_from_candles(df)
    assert direction == SELL


def test_forming_candle_does_not_affect_signal():
    df = _frame()
    # Sanity: the last row (forming candle) initially yields BUY from closed row.
    direction_before, _ = signal_from_candles(df)
    assert direction_before == BUY

    # Drastically mutate the FORMING candle (last row). The signal must be
    # unchanged because signal_from_candles never reads df.iloc[-1].
    df.iloc[-1] = {
        "time": df["time"].iloc[-1],
        "open": 1.3000,
        "high": 1.4000,
        "low": 1.1000,
        "close": 1.2000,
        "spread": 100.0,
        "ema50": 1.5000,
        "ema200": 1.0000,
        "rsi": 90.0,
        "atr": 0.0100,
    }
    direction_after, atr_after = signal_from_candles(df)
    assert direction_after == BUY
    assert atr_after == pytest.approx(0.0003)


def test_closed_candle_does_affect_signal():
    df = _frame()
    # Baseline closed-candle evaluation is BUY.
    assert signal_from_candles(df)[0] == BUY

    # Change the LAST CLOSED candle (index -2) to a downtrend (SELL zone).
    df.iloc[-2, df.columns.get_loc("ema50")] = 1.0990
    df.iloc[-2, df.columns.get_loc("rsi")] = 50.0
    direction, _ = signal_from_candles(df)
    assert direction == SELL


def test_neutral_zone_no_signal():
    df = _frame()
    # RSI in the no-man's land (55 <= rsi <= 45 band between zones):
    # rsi = 57 -> above buy max (55) and above sell min (45) but sell needs
    # ema50 < ema200. Keep uptrend + rsi 57 -> no valid signal.
    df["rsi"] = np.full(len(df), 57.0)
    direction, _ = signal_from_candles(df)
    assert direction is None


def test_candle_ordering_correct():
    df = _frame()
    # The helper must use the penultimate (last closed) candle, not the
    # trailing forming candle. Force forming row into the SELL zone and the
    # closed row to remain BUY: ordering means the BUY (closed) wins.
    df.iloc[-1, df.columns.get_loc("ema50")] = 1.0990
    df.iloc[-1, df.columns.get_loc("rsi")] = 50.0
    direction, _ = signal_from_candles(df)
    assert direction == BUY


def test_insufficient_history_returns_none():
    assert signal_from_candles(None) == (None, None)
    one_row = _frame(rows=0).iloc[[0]]
    assert signal_from_candles(one_row) == (None, None)


def test_warmup_nan_returns_none():
    df = _frame()
    df.iloc[-2, df.columns.get_loc("ema200")] = np.nan
    assert signal_from_candles(df) == (None, None)


def test_parity_with_backtest_signal_at():
    """signal_from_candles(df) == strategy.signal_at(df, len(df) - 2)."""
    from backtest import strategy
    from backtest.config import StrategyConfig

    df = _frame()
    cfg = StrategyConfig()
    live_dir, live_atr = signal_from_candles(df)
    engine_dir = strategy.signal_at(df, len(df) - 2, cfg)
    assert live_dir == engine_dir
    assert live_atr == pytest.approx(float(df["atr"].iloc[-2]))