"""Raw directional predictive power of the existing BUY/SELL signals.

Independent of the SL/TP implementation, this module measures whether a signal
is followed by price movement in the predicted direction. For every candle that
produces a BUY or SELL signal under the EXACT existing strategy rules (no
filters, no new indicators), it measures forward movement over several M5-candle
horizons and reports direction hit rate, forward return (pips and R), and how
often price reaches +0.5R/+1R/+2R before falling to -1R.

This is purely analysis — it does not trade, does not modify bot.py or the
strategy, and does not optimise anything.

    python -m backtest.predictive
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PathConfig, StrategyConfig
from .indicators import add_indicators
from .strategy import BUY, SELL, signal_at

HORIZONS = [1, 3, 5, 10, 20, 40, 80]
REACH_TARGETS_R = [0.5, 1.0, 2.0]
ADVERSE_R = 1.0
PIP = 0.0001


def collect_signals(df: pd.DataFrame, cfg: StrategyConfig) -> tuple[np.ndarray, np.ndarray]:
    """Return (signal_indices, direction_buy_is_1) for every signal candle.

    Every closed candle that satisfies the exact BUY/SELL rules is counted
    independently (the one-position rule from the backtester is NOT applied
    here because we are measuring the signal's predictive power, not the
    simulated trade sequence).
    """
    idx = []
    buy = []
    close = df["close"].to_numpy()
    for i in range(len(df)):
        if _indicator_valid(df, i) and not pd.isna(close[i]):
            sig = signal_at(df, i, cfg)
            if sig == BUY:
                idx.append(i)
                buy.append(True)
            elif sig == SELL:
                idx.append(i)
                buy.append(False)
    return np.array(idx, dtype=np.int64), np.array(buy, dtype=bool)


def _indicator_valid(df: pd.DataFrame, i: int) -> bool:
    return not (
        pd.isna(df["ema_fast"].iat[i])
        or pd.isna(df["ema_slow"].iat[i])
        or pd.isna(df["rsi"].iat[i])
        or pd.isna(df["atr"].iat[i])
    )


def forward_stats(
    close: np.ndarray, atr: np.ndarray, idx: np.ndarray, buy: np.ndarray, H: int
) -> dict:
    """Aggregate forward stats for a signal group at horizon H (in candles).

    Forward move for BUY = close[i+H] - close[i]; for SELL = close[i] - close[i+H]
    (so a positive move is always in the predicted direction). R uses the signal
    candle's ATR with 1R = SL distance = 1.5 * ATR.
    """
    keep = idx + H < len(close)
    i = idx[keep]
    b = buy[keep]
    e0 = close[i]
    fwd = close[i + H] - e0
    move = np.where(b, fwd, -fwd)  # positive => predicted direction
    dist_r = 1.5 * atr[i]
    move_r = move / np.where(dist_r != 0, dist_r, np.nan)

    return {
        "n": int(keep.sum()),
        "pred_pct": float((move > 0).mean() * 100.0) if keep.sum() else float("nan"),
        "avg_pips": float((move / PIP).mean()) if keep.sum() else float("nan"),
        "med_pips": float(np.median(move / PIP)) if keep.sum() else float("nan"),
        "avg_r": float(np.nanmean(move_r)) if keep.sum() else float("nan"),
        "med_r": float(np.nanmedian(move_r)) if keep.sum() else float("nan"),
    }


def reach_pct(
    close: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    atr: np.ndarray,
    idx: np.ndarray,
    buy: np.ndarray,
    H: int,
    target_r: float,
) -> float:
    """Fraction that reach +target_r*R (predicted direction) before -1R.

    Walks candles 1..H from the signal close using the conservative intrabar
    rule (adverse first, matching the backtester): a signal only counts as
    reaching the target if it touches +target R on some candle before -1R was
    ever touched on that or any earlier candle.
    """
    keep = idx + H < len(high)
    i = idx[keep]
    b = buy[keep]
    if len(i) == 0:
        return float("nan")
    close0 = close[i]
    dist_r = 1.5 * atr[i]
    adverse_level = np.where(b, close0 - ADVERSE_R * dist_r, close0 + ADVERSE_R * dist_r)
    target_level = np.where(b, close0 + target_r * dist_r, close0 - target_r * dist_r)

    adverse_hit = np.zeros(len(i), dtype=bool)
    target_done = np.zeros(len(i), dtype=bool)
    reached = np.zeros(len(i), dtype=bool)

    for c in range(1, H + 1):
        hi = high[i + c]
        lo = low[i + c]
        # adverse condition (direction aware): BUY low <= adverse_level, SELL high >= adverse_level
        adv = np.where(b, lo <= adverse_level, hi >= adverse_level)
        # target condition: BUY high >= target_level, SELL low <= target_level
        tgt = np.where(b, hi >= target_level, lo <= target_level)
        # conservative: adverse first within the candle
        reached |= tgt & ~adverse_hit & ~target_done
        target_done |= tgt
        adverse_hit |= adv

    return float(reached.mean() * 100.0)


def analyze(df: pd.DataFrame, cfg: StrategyConfig) -> dict:
    close = df["close"].to_numpy(dtype=float)
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    atr = df["atr"].to_numpy(dtype=float)

    idx_all, buy_all = collect_signals(df, cfg)
    buy_total = int(buy_all.sum())
    groups = {
        "BUY": (idx_all[buy_all], np.ones(buy_total, dtype=bool)),
        "SELL": (idx_all[~buy_all], np.zeros(len(idx_all) - buy_total, dtype=bool)),
        "ALL": (idx_all, buy_all),
    }

    result = {}
    for gname, (gidx, gbuy) in groups.items():
        rows = []
        for H in HORIZONS:
            st = forward_stats(close, atr, gidx, gbuy, H)
            row = dict(st)
            for tgt in REACH_TARGETS_R:
                row[f"reach_{tgt}R"] = reach_pct(close, high, low, atr, gidx, gbuy, H, tgt)
            row["horizon"] = H
            rows.append(row)
        result[gname] = pd.DataFrame(rows).set_index("horizon")

    result["meta"] = {
        "total_signals": int(len(idx_all)),
        "buy_signals": int(buy_all.sum()),
        "sell_signals": int((~buy_all).sum()),
    }
    return result


def _fmt_float(x: float, nd: int = 2) -> str:
    if x != x:  # NaN
        return "-"
    return f"{x:.{nd}f}"


def write_report(result: dict, path: Path) -> None:
    meta = result["meta"]
    lines = []
    w = lines.append
    w("# RAW DIRECTIONAL PREDICTIVE POWER OF BUY/SELL SIGNALS")
    w("")
    w(f"Signal count: **{meta['total_signals']}** total "
      f"({meta['buy_signals']} BUY, {meta['sell_signals']} SELL).")
    w("")
    w("## Methodology (no look-ahead)")
    w("")
    w("1. **Signals** — every closed candle matching the exact existing strategy")
    w("   rules (BUY: EMA50>EMA200 AND 40<RSI<55; SELL: EMA50<EMA200 AND 45<RSI<60)")
    w("   is counted independently. The one-position-at-a-time *execution* rule is")
    w("   intentionally NOT applied: we measure the predictive power of the signal")
    w("   itself, not the simulated trade sequence.")
    w("2. **Forward momentum** — after the signal candle `i`, the forward move to")
    w("   the close of candle `i+H` is measured. For a BUY it is `close[i+H] -")
    w("   close[i]`; for a SELL it is `close[i] - close[i+H]`, so a positive move")
    w("   is always *in the predicted direction*. Only future bars are used, and only")
    w("   information available at candle `i` (close, ATR) defines the prediction, so")
    w("   there is no look-ahead.")
    w("3. **Pips** — move / pip, with pip = 0.0001 (EURUSD).")
    w("4. **R** — move / (1.5 x ATR at the signal candle). 1R is the stop-distance the")
    w("   strategy would use (SL = 1.5 x ATR), letting forward returns be compared to")
    w("   the strategy's own risk scale.")
    w("5. **'Reached +X R before -1R'** — walking candles 1..H from the signal close, a")
    w("   signal counts if it touches +X R (in the predicted direction) on some candle")
    w("   before it ever touches -1 R. The conservative intrabar rule is used (adverse")
    w("   first), matching the backtest engine, so both-touched-in-one-candle counts as")
    w("   not reaching the target first.")
    w("6. **Coverage** — signals within the last H candles of the dataset are excluded")
    w("   at that horizon (their forward window is incomplete), so `n` may shrink for")
    w("   the longest horizons.")
    w("")

    subtitle = {
        "BUY": "BUY signals (predicted direction = up)",
        "SELL": "SELL signals (predicted direction = down)",
        "ALL": "ALL signals combined (predicted-direction space)",
    }
    for gname in ["BUY", "SELL", "ALL"]:
        grp = result[gname]
        w(f"## {subtitle[gname]}")
        w("")
        w("| H (candles) | n | in dir% | avg pips | med pips | avg R | med R | +0.5R before -1R | +1R before -1R | +2R before -1R |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for H in HORIZONS:
            r = grp.loc[H]
            w(
                f"| {H} | {int(r['n'])} | {_fmt_float(r['pred_pct'])} | "
                f"{_fmt_float(r['avg_pips'])} | {_fmt_float(r['med_pips'])} | "
                f"{_fmt_float(r['avg_r'])} | {_fmt_float(r['med_r'])} | "
                f"{_fmt_float(r['reach_0.5R'])} | {_fmt_float(r['reach_1.0R'])} | "
                f"{_fmt_float(r['reach_2.0R'])} |"
            )
        w("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Raw signal predictive power")
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    s_cfg = StrategyConfig()
    df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])
    df = add_indicators(df, s_cfg)

    out_dir.mkdir(parents=True, exist_ok=True)
    result = analyze(df, s_cfg)

    for gname in ["BUY", "SELL", "ALL"]:
        result[gname].to_csv(out_dir / f"predictive_{gname}.csv")

    report_path = out_dir / "predictive_report.md"
    write_report(result, report_path)

    print(f"Predictive-power analysis written to {out_dir}")
    print(f"  - {report_path}")
    print(f"  - predictive_BUY.csv / predictive_SELL.csv / predictive_ALL.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
