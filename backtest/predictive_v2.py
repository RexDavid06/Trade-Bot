"""Raw directional predictive power of the V2 (trend-pullback) signals.

Measures whether V2 signals are followed by price movement in the predicted
direction, INDEPENDENT of SL/TP, using the identical forward-return framework
used for V1 (see `predictive.py`) so the two can be compared directly. For
every V2 signal candle the forward move to close[i+H] (sign-flipped for SELL so
positive = predicted direction) is measured at H = 1/3/5/10/20/40/80 candles,
in pips and R (1R = 1.5 x ATR at the signal candle), plus how often price
reaches +0.5R/+1R/+2R before -1R.

Pure analysis: it does not trade, does not modify bot.py / V1 / strategy_v2,
and does not optimise anything.

Optimizations:
  - V1 results loaded from existing CSVs when available (skips recomputation).
  - V1 signal collection vectorized with numpy when recomputation is needed.
  - Reach computation vectorized: replaces per-candle Python loop with
    numpy cumulative-OR operations over the full forward window.

    python -m backtest.predictive_v2
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PathConfig, StrategyConfig
from .indicators import add_indicators
from .predictive import ADVERSE_R, HORIZONS, PIP, REACH_TARGETS_R, forward_stats
from .strategy import BUY, SELL
from .strategy_v2 import LOOKBACK, PULLBACK_ATR, ZONE_ATR, collect_v2_signals


# ---------------------------------------------------------------------------
# Fast V1 signal collection (vectorized, replaces Python for-loop)
# ---------------------------------------------------------------------------

def _collect_signals_fast(df: pd.DataFrame, cfg: StrategyConfig) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized V1 signal collection — identical rules to strategy.signal_at."""
    ema_f = df["ema_fast"].to_numpy()
    ema_s = df["ema_slow"].to_numpy()
    rsi = df["rsi"].to_numpy()
    atr = df["atr"].to_numpy()

    valid = ~(np.isnan(ema_f) | np.isnan(ema_s) | np.isnan(rsi) | np.isnan(atr))

    buy = valid & (ema_f > ema_s) & (cfg.rsi_buy_min < rsi) & (rsi < cfg.rsi_buy_max)
    sell = valid & (ema_f < ema_s) & (cfg.rsi_sell_min < rsi) & (rsi < cfg.rsi_sell_max)

    if cfg.ema_sep_min > 0:
        sep = np.abs(ema_f - ema_s) / atr
        mask = sep > cfg.ema_sep_min
        buy &= mask
        sell &= mask

    buy_idx = np.flatnonzero(buy)
    sell_idx = np.flatnonzero(sell)
    idx = np.concatenate([buy_idx, sell_idx])
    buy_flag = np.concatenate([np.ones(len(buy_idx), dtype=bool),
                               np.zeros(len(sell_idx), dtype=bool)])
    order = idx.argsort()
    return idx[order].astype(np.int64), buy_flag[order]


# ---------------------------------------------------------------------------
# Vectorized reach computation
# ---------------------------------------------------------------------------

def _reach_pct_vec(close: np.ndarray, high: np.ndarray, low: np.ndarray,
                   atr: np.ndarray, idx: np.ndarray, buy: np.ndarray,
                   H: int, target_r: float) -> float:
    """Vectorized reach: fraction reaching +target_r R before -1R.

    Replaces the per-candle Python loop with numpy cumulative-OR over the
    full (n, H) forward window.  Mathematically equivalent to the original
    conservative-intrabar logic in predictive.reach_pct.
    """
    keep = idx + H < len(high)
    i = idx[keep]
    b = buy[keep]
    n = len(i)
    if n == 0:
        return float("nan")

    close0 = close[i]
    dist_r = 1.5 * atr[i]
    adv_level = np.where(b, close0 - ADVERSE_R * dist_r,
                         close0 + ADVERSE_R * dist_r)
    tgt_level = np.where(b, close0 + target_r * dist_r,
                         close0 - target_r * dist_r)

    offsets = np.arange(1, H + 1)
    idx_2d = i[:, None] + offsets          # (n, H)
    fwd_hi = high[idx_2d]
    fwd_lo = low[idx_2d]

    adv_2d = adv_level[:, None]
    tgt_2d = tgt_level[:, None]

    # Adverse / target hit per candle
    adv_hit = np.where(b[:, None], fwd_lo <= adv_2d, fwd_hi >= adv_2d)
    tgt_hit = np.where(b[:, None], fwd_hi >= tgt_2d, fwd_lo <= tgt_2d)

    # Conservative adverse-first: reached at candle c requires
    # target_hit[c] AND no adverse from candles 1..c-1.
    # (matches the original code's cumulative logic exactly)
    cum_adv = np.cumsum(adv_hit, axis=1)
    cum_adv_before = np.concatenate(
        [np.zeros((n, 1), dtype=np.intp), cum_adv[:, :-1]], axis=1
    )
    reached_at_c = tgt_hit & (cum_adv_before == 0)
    reached = np.any(reached_at_c, axis=1)
    return float(reached.mean() * 100.0)


# ---------------------------------------------------------------------------
# Groups & analysis
# ---------------------------------------------------------------------------

def build_groups(idx: np.ndarray, buy: np.ndarray) -> dict:
    buy_total = int(buy.sum())
    return {
        "BUY": (idx[buy], np.ones(buy_total, dtype=bool)),
        "SELL": (idx[~buy], np.zeros(len(idx) - buy_total, dtype=bool)),
        "ALL": (idx, buy),
    }


def analyze_groups(df: pd.DataFrame, groups: dict) -> dict:
    close = df["close"].to_numpy(dtype=float)
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    atr = df["atr"].to_numpy(dtype=float)

    out = {}
    for gname, (gidx, gbuy) in groups.items():
        rows = []
        for H in HORIZONS:
            st = forward_stats(close, atr, gidx, gbuy, H)
            row = dict(st)
            for tgt in REACH_TARGETS_R:
                row[f"reach_{tgt}R"] = _reach_pct_vec(
                    close, high, low, atr, gidx, gbuy, H, tgt
                )
            row["horizon"] = H
            rows.append(row)
        out[gname] = pd.DataFrame(rows).set_index("horizon")
    return out


# ---------------------------------------------------------------------------
# V1 loading from CSV (reuse existing results)
# ---------------------------------------------------------------------------

def _load_v1_csv(out_dir: Path) -> tuple[dict | None, dict | None]:
    """Try to load pre-existing V1 predictive CSVs.  Return (v1, v1_meta)."""
    frames = {}
    for gname in ("ALL", "BUY", "SELL"):
        p = out_dir / f"v1_predictive_{gname}.csv"
        if not p.exists():
            return None, None
        frames[gname] = pd.read_csv(p).set_index("horizon")

    total = int(frames["ALL"].loc[1, "n"])
    buy_n = int(frames["BUY"].loc[1, "n"])
    sell_n = int(frames["SELL"].loc[1, "n"])
    meta = {"total": total, "buy": buy_n, "sell": sell_n}
    return frames, meta


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _fmt(x: float) -> str:
    if x != x:
        return "-"
    return f"{x:.2f}"


def write_report(df: pd.DataFrame, v2: dict, v1: dict, v2_meta: dict,
                 v1_meta: dict, path: Path) -> None:
    lines = []
    w = lines.append

    w("# V2 DIRECTIONAL PREDICTIVE POWER (trend-pullback) vs V1")
    w("")
    w("## V2 rule summary")
    w("")
    w("BUY requires **all** of the following on the closed signal candle:")
    w("")
    w("* **Trend**: EMA50 > EMA200, EMA50 rising, EMA200 rising "
      "(rising/falling = EMA vs its previous candle).")
    w("* **Impulse + pullback**: a recent local high (highest high over the "
      "trailing `LOOKBACK=20` candles")
    w("  strictly before the signal candle); price closed below it (retraced), "
      "the retracement is at least")
    w("  `PULLBACK_ATR=0.5` ATR, and price reached within `ZONE_ATR=0.25` ATR "
      "of EMA50 during the pullback.")
    w("* **Rejection candle**: touches the EMA50 pullback zone "
      "(low <= EMA50 + 0.25 ATR), closes bullish,")
    w("  above its midpoint, above EMA50.")
    w("* **Momentum**: RSI14 crosses from <=50 to >50 on that candle.")
    w("")
    w("SELL mirrors all of these (EMA50 < EMA200 with both falling, pullback "
      "up from a recent local low,")
    w("bearish rejection below midpoint/EMA50, RSI crossing), all using only "
      "data <= the signal candle.")
    w("")
    w("Signal count V2: "
      f"**{v2_meta['total']}** total ({v2_meta['buy']} BUY, "
      f"{v2_meta['sell']} SELL).  "
      f"V1 for comparison: {v1_meta['total']} total "
      f"({v1_meta['buy']} BUY, {v1_meta['sell']} SELL).")
    w("")
    w("Forward returns: move to close[i+H] from the signal close, sign-flipped "
      "for SELL (positive =>")
    w("predicted direction); pips = move / 0.0001; R = move / (1.5 x ATR at "
      "signal candle). Reach stats")
    w("+0.5R/+1R/+2R before -1R use the conservative adverse-first intrabar "
      "rule, identical to V1. Only")
    w("bars after the signal are used (no look-ahead); signals inside the last "
      "H candles are dropped at")
    w("that horizon, so n can shrink for long horizons.")
    w("")

    w("## V2 results")
    w("")
    for gname, subtitle in [
        ("BUY", "BUY (predicted = up)"),
        ("SELL", "SELL (predicted = down)"),
        ("ALL", "ALL combined"),
    ]:
        grp = v2[gname]
        w(f"### V2 {subtitle}")
        w("")
        w("| H | n | in dir% | avg pips | med pips | avg R | med R "
          "| +0.5R<1R | +1R<1R | +2R<1R |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for H in HORIZONS:
            r = grp.loc[H]
            w(
                f"| {H} | {int(r['n'])} | {_fmt(r['pred_pct'])} | "
                f"{_fmt(r['avg_pips'])} | "
                f"{_fmt(r['med_pips'])} | {_fmt(r['avg_r'])} | "
                f"{_fmt(r['med_r'])} | "
                f"{_fmt(r['reach_0.5R'])} | {_fmt(r['reach_1.0R'])} | "
                f"{_fmt(r['reach_2.0R'])} |"
            )
        w("")

    w("## V2 vs V1 (ALL signals combined)")
    w("")
    w("| H | V2 n | V2 in dir% | V1 n | V1 in dir% "
      "| V2 avg R | V1 avg R | V2 +1R<1R | V1 +1R<1R |")
    w("|---|---|---|---|---|---|---|---|---|")
    for H in HORIZONS:
        r2 = v2["ALL"].loc[H]
        r1 = v1["ALL"].loc[H]
        w(
            f"| {H} | {int(r2['n'])} | {_fmt(r2['pred_pct'])} | "
            f"{int(r1['n'])} | {_fmt(r1['pred_pct'])} | "
            f"{_fmt(r2['avg_r'])} | {_fmt(r1['avg_r'])} | "
            f"{_fmt(r2['reach_1.0R'])} | {_fmt(r1['reach_1.0R'])} |"
        )
    w("")
    w("## V2 notes")
    w("")
    w("Configurable structural constants are fixed and NOT optimized: "
      f"LOOKBACK={LOOKBACK}, ZONE_ATR={ZONE_ATR}, "
      f"PULLBACK_ATR={PULLBACK_ATR}. "
      "The primary objective is directional predictive power, not money P&L.")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="V2 directional predictive power vs V1"
    )
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    s_cfg = StrategyConfig()

    t0 = time.perf_counter()
    df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])
    df = add_indicators(df, s_cfg)
    t_indicators = time.perf_counter()

    v2_idx, v2_buy = collect_v2_signals(df)
    t_v2 = time.perf_counter()

    v1, v1_meta = _load_v1_csv(out_dir)
    if v1 is not None:
        t_v1 = t_v2
        v1_source = "loaded from CSV"
    else:
        v1_idx, v1_buy = _collect_signals_fast(df, s_cfg)
        groups_v1 = build_groups(v1_idx, v1_buy)
        v1 = analyze_groups(df, groups_v1)
        v1_meta = {
            "total": int(len(v1_idx)),
            "buy": int(v1_buy.sum()),
            "sell": int((~v1_buy).sum()),
        }
        t_v1 = time.perf_counter()
        v1_source = "computed (vectorized)"

    groups_v2 = build_groups(v2_idx, v2_buy)
    v2 = analyze_groups(df, groups_v2)
    t_analysis = time.perf_counter()

    v2_meta = {
        "total": int(len(v2_idx)),
        "buy": int(v2_buy.sum()),
        "sell": int((~v2_buy).sum()),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in ("BUY", "SELL", "ALL"):
        v2[gname].to_csv(out_dir / f"v2_predictive_{gname}.csv")
        v1[gname].to_csv(out_dir / f"v1_predictive_{gname}.csv")

    report_path = out_dir / "v2_predictive_report.md"
    write_report(df, v2, v1, v2_meta, v1_meta, report_path)

    elapsed = time.perf_counter() - t0
    print(f"V2 predictive-power analysis written to {out_dir}")
    print(f"  - {report_path}")
    print(f"  - v2_predictive_BUY/SELL/ALL.csv (+ v1_predictive_*.csv)")
    print(f"  V1 source: {v1_source}")
    print(f"  Timing: indicators={t_indicators-t0:.2f}s  "
          f"v2_signals={t_v2-t_indicators:.2f}s  "
          f"v1={t_v1-t_v2:.2f}s  "
          f"analysis={t_analysis-t_v1:.2f}s  "
          f"total={elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
