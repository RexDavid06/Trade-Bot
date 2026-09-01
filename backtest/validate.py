"""Validation checks required by the task.

Run with:
    python -m backtest.validate [--data data/eurusd_m5.csv]

Checks:
  1. Strategy rules reproduce bot.py exactly (spot check signal flags).
  2. Indicators computed without look-ahead (EMA/RSI/ATR at row i only use rows <= i).
  3. Trades never overlap.
  4. SL/TP handled correctly (exit prices match levels; conservative intrabar rule).
  5. Results are deterministic for the same dataset.
  6. No entries inside the signal candle (entry uses the next candle's open).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .backtester import run_backtest
from .config import CostConfig, PathConfig, StrategyConfig
from .indicators import add_indicators
from .strategy import BUY, SELL, signal_at

PASS, FAIL = "+", "-"
_ok = True


def _report(check: str, passed: bool) -> None:
    global _ok
    print(f"[{'PASS' if passed else 'FAIL'}] {check}")
    _ok = _ok and passed


def _ma_equal(series_a: pd.Series, series_b: pd.Series) -> bool:
    """Compare two series over their overlapping prefix (no-look-ahead check).

    `series_a` is the truncated (partial) computation, `series_b` the full one.
    Values in the overlap must match exactly; a mismatch means the full-series
    indicator used a future row.
    """
    import numpy as np

    a = series_a.to_numpy()
    b = series_b.to_numpy()
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    mask = ~(np.isnan(a) | np.isnan(b))
    return bool(np.allclose(a[mask], b[mask], rtol=1e-9, atol=1e-12))


def _ema_at(close: pd.Series, period: int, end: int) -> pd.Series:
    """Compute EMA using only data up to index `end` (manual no-look-ahead check)."""
    if end < 0:
        return pd.Series([float("nan")] * len(close))
    values = close.iloc[: end + 1]
    ema = values.ewm(span=period, adjust=False).mean()
    return ema


def run_validation(data_path: Path) -> int:
    global _ok

    s_cfg = StrategyConfig()
    c_cfg = CostConfig()
    df0 = pd.read_csv(data_path)
    df0["time"] = pd.to_datetime(df0["time"])
    df = add_indicators(df0, s_cfg)

    # --- Check 5: determinism (also computed forward, reused below) ---
    t1, eq1 = run_backtest(df, s_cfg, c_cfg)
    t2, eq2 = run_backtest(df, s_cfg, c_cfg)
    same_trades = len(t1) == len(t2) and all(a.to_dict() == b.to_dict() for a, b in zip(t1, t2))
    same_equity = eq1.equals(eq2)
    _report("Deterministic (two runs identical)", same_trades and same_equity)

    # --- Check 1: strategy rule reproduction (manual recomputation) ---
    nav = 0
    sample = df.index[200: len(df)][:: 2000]  # sparse sample across whole series
    mismatches = 0
    for i in sample:
        manual = _manual_signal(df, s_cfg, i)
        got = signal_at(df, i, s_cfg)
        if manual != got:
            mismatches += 1
    _report(f"Strategy rules match bot.py (sampled {len(sample)}, mismatches={mismatches})", mismatches == 0)

    # --- Check 2: indicator look-ahead ---
    # EMA must be identical when recomputed only up to a row vs. the full series.
    from ta.momentum import RSIIndicator
    from ta.trend import EMAIndicator
    from ta.volatility import AverageTrueRange

    idx = len(df) // 2
    sub = df.iloc[: idx + 1]
    ema50_partial = EMAIndicator(sub["close"], s_cfg.ema_fast).ema_indicator()
    ema200_partial = EMAIndicator(sub["close"], s_cfg.ema_slow).ema_indicator()
    rsi_partial = RSIIndicator(sub["close"], s_cfg.rsi_period).rsi()
    atr_partial = AverageTrueRange(sub["high"], sub["low"], sub["close"], s_cfg.atr_period).average_true_range()

    checks = [
        ("EMA50", ema50_partial, df["ema_fast"]),
        ("EMA200", ema200_partial, df["ema_slow"]),
        ("RSI", rsi_partial, df["rsi"]),
        ("ATR", atr_partial, df["atr"]),
    ]
    ok_la = all(_ma_equal(b, full) for _, b, full in checks)
    for name, partial, full in checks:
        _report(f"Look-ahead check {name} (value@row={idx} deps only <= row)", _ma_equal(partial, full))

    # --- Check 3: no overlapping trades ---
    times = [(pd.Timestamp(t.entry_time), pd.Timestamp(t.exit_time)) for t in t1]
    overlap = 0
    prev_exit = pd.Timestamp.min
    for entry, exit_ in times:
        if entry < prev_exit:
            overlap += 1
        prev_exit = max(prev_exit, exit_)
    _report("No overlapping trades", overlap == 0)

    # --- Check 4: SL/TP handling ---
    ts_ix = {pd.Timestamp(e["time"]): i for i, e in df.iterrows()}
    bad_sl_tp = 0
    err_msgs = 0
    for t in t1:
        entry_i = ts_ix[pd.Timestamp(t.entry_time)]
        exit_i = ts_ix[pd.Timestamp(t.exit_time)]
        # (a) SL/TP levels must be derived exactly from entry price + ATR.
        if t.direction == BUY:
            sl_exact = t.entry_price - s_cfg.atr_sl_mult * t.atr
            tp_exact = t.entry_price + s_cfg.atr_tp_mult * t.atr
        else:
            sl_exact = t.entry_price + s_cfg.atr_sl_mult * t.atr
            tp_exact = t.entry_price - s_cfg.atr_tp_mult * t.atr
        if not (abs(t.stop_loss - sl_exact) < 1e-9 and abs(t.take_profit - tp_exact) < 1e-9):
            bad_sl_tp += 1
            err_msgs += 1
            continue
        # (b) Exit must be a genuine SL/TP touch on the exit candle (or a forced close).
        if t.exit_reason == "OPEN":
            continue
        row = df.iloc[exit_i]
        if t.direction == BUY:
            touched = (t.exit_reason == "SL" and row["low"] <= t.stop_loss) or (
                t.exit_reason == "TP" and row["high"] >= t.take_profit
            )
        else:
            touched = (t.exit_reason == "SL" and row["high"] >= t.stop_loss) or (
                t.exit_reason == "TP" and row["low"] <= t.take_profit
            )
        if not touched:
            bad_sl_tp += 1
            err_msgs += 1
            continue
        # (c) No earlier candle between entry and exit may have touched either level
        #     (exit must be the FIRST touch).
        for j in range(entry_i + 1 if t.exit_reason == "SL" or t.exit_reason == "TP" else 0, exit_i):
            row2 = df.iloc[j]
            if t.direction == BUY:
                touched_earlier = row2["low"] <= t.stop_loss or row2["high"] >= t.take_profit
            else:
                touched_earlier = row2["high"] >= t.stop_loss or row2["low"] <= t.take_profit
            if touched_earlier:
                bad_sl_tp += 1
                err_msgs += 1
                break
    _report(f"SL/TP levels & first-touch exits correct (errors={err_msgs} of {len(t1)})", bad_sl_tp == 0)

    # --- Check 6: no entry inside the signal candle (fills on next open) ---
    bad_entry = 0
    for t in t1:
        entry_ts = pd.Timestamp(t.entry_time)
        if entry_ts not in ts_ix:
            bad_entry += 1
            continue
        entry_i = ts_ix[entry_ts]
        # Entry must be exactly the close/open of bar entry_i, and the signal must
        # have been generated on bar entry_i-1 (the previous closed candle).
        if entry_i <= 0:
            bad_entry += 1
            continue
        sig_prev = signal_at(df, entry_i - 1, s_cfg)
        if sig_prev != t.direction:
            bad_entry += 1
            continue
        if abs(t.entry_price - float(df["open"].iat[entry_i])) > 1e-9:
            bad_entry += 1
    _report("Entries only at next candle open after signal", bad_entry == 0)

    print(f"\nOverall: {'ALL CHECKS PASSED' if _ok else 'SOME CHECKS FAILED'}")
    return 0 if _ok else 1


def _manual_signal(df: pd.DataFrame, cfg: StrategyConfig, i: int) -> str | None:
    if (
        pd.isna(df["ema_fast"].iat[i])
        or pd.isna(df["ema_slow"].iat[i])
        or pd.isna(df["rsi"].iat[i])
    ):
        return None
    ema_fast = float(df["ema_fast"].iat[i])
    ema_slow = float(df["ema_slow"].iat[i])
    rsi = float(df["rsi"].iat[i])
    if ema_fast > ema_slow and cfg.rsi_buy_min < rsi < cfg.rsi_buy_max:
        return BUY
    if ema_fast < ema_slow and cfg.rsi_sell_min < rsi < cfg.rsi_sell_max:
        return SELL
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=None)
    args = parser.parse_args(argv)
    data_path = args.data if args.data is not None else PathConfig().data_file
    if not data_path.exists():
        sys.stderr.write(f"Data file not found: {data_path}\n")
        return 1
    return run_validation(data_path)


if __name__ == "__main__":
    raise SystemExit(main())