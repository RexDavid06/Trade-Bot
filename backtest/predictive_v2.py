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

    python -m backtest.predictive_v2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PathConfig, StrategyConfig
from .indicators import add_indicators
from .predictive import HORIZONS, REACH_TARGETS_R, PIP, collect_signals, forward_stats, reach_pct
from .strategy_v2 import LOOKBACK, PULLBACK_ATR, ZONE_ATR, collect_v2_signals


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
                row[f"reach_{tgt}R"] = reach_pct(close, high, low, atr, gidx, gbuy, H, tgt)
            row["horizon"] = H
            rows.append(row)
        out[gname] = pd.DataFrame(rows).set_index("horizon")
    return out


def _fmt(x: float) -> str:
    if x != x:
        return "-"
    return f"{x:.2f}"


def write_report(df: pd.DataFrame, v2: dict, v1: dict, v2_meta: dict, v1_meta: dict, path: Path) -> None:
    lines = []
    w = lines.append

    w("# V2 DIRECTIONAL PREDICTIVE POWER (trend-pullback) vs V1")
    w("")
    w("## V2 rule summary")
    w("")
    w("BUY requires **all** of the following on the closed signal candle:")
    w("")
    w("* **Trend**: EMA50 > EMA200, EMA50 rising, EMA200 rising (rising/falling = EMA vs its previous candle).")
    w("* **Impulse + pullback**: a recent local high (highest high over the trailing `LOOKBACK=20` candles")
    w("  strictly before the signal candle); price closed below it (retraced), the retracement is at least")
    w("  `PULLBACK_ATR=0.5` ATR, and price reached within `ZONE_ATR=0.25` ATR of EMA50 during the pullback.")
    w("* **Rejection candle**: touches the EMA50 pullback zone (low <= EMA50 + 0.25 ATR), closes bullish,")
    w("  above its midpoint, above EMA50.")
    w("* **Momentum**: RSI14 crosses from <=50 to >50 on that candle.")
    w("")
    w("SELL mirrors all of these (EMA50 < EMA200 with both falling, pullback up from a recent local low,")
    w("bearish rejection below midpoint/EMA50, RSI crossing), all using only data <= the signal candle.")
    w("")
    w("Signal count V2: "
      f"**{v2_meta['total']}** total ({v2_meta['buy']} BUY, {v2_meta['sell']} SELL).  "
      f"V1 for comparison: {v1_meta['total']} total ({v1_meta['buy']} BUY, {v1_meta['sell']} SELL).")
    w("")
    w("Forward returns: move to close[i+H] from the signal close, sign-flipped for SELL (positive =>")
    w("predicted direction); pips = move / 0.0001; R = move / (1.5 x ATR at signal candle). Reach stats")
    w("+0.5R/+1R/+2R before -1R use the conservative adverse-first intrabar rule, identical to V1. Only")
    w("bars after the signal are used (no look-ahead); signals inside the last H candles are dropped at")
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
        w("| H | n | in dir% | avg pips | med pips | avg R | med R | +0.5R<1R | +1R<1R | +2R<1R |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for H in HORIZONS:
            r = grp.loc[H]
            w(
                f"| {H} | {int(r['n'])} | {_fmt(r['pred_pct'])} | {_fmt(r['avg_pips'])} | "
                f"{_fmt(r['med_pips'])} | {_fmt(r['avg_r'])} | {_fmt(r['med_r'])} | "
                f"{_fmt(r['reach_0.5R'])} | {_fmt(r['reach_1.0R'])} | {_fmt(r['reach_2.0R'])} |"
            )
        w("")

    w("## V2 vs V1 (ALL signals combined)")
    w("")
    w("| H | V2 n | V2 in dir% | V1 n | V1 in dir% | V2 avg R | V1 avg R | V2 +1R<1R | V1 +1R<1R |")
    w("|---|---|---|---|---|---|---|---|---|")
    for H in HORIZONS:
        r2 = v2["ALL"].loc[H]
        r1 = v1["ALL"].loc[H]
        w(
            f"| {H} | {int(r2['n'])} | {_fmt(r2['pred_pct'])} | {int(r1['n'])} | {_fmt(r1['pred_pct'])} | "
            f"{_fmt(r2['avg_r'])} | {_fmt(r1['avg_r'])} | {_fmt(r2['reach_1.0R'])} | {_fmt(r1['reach_1.0R'])} |"
        )
    w("")
    w("## V2 notes")
    w("")
    w("Configurable structural constants are fixed and NOT optimized: "
      f"LOOKBACK={LOOKBACK}, ZONE_ATR={ZONE_ATR}, PULLBACK_ATR={PULLBACK_ATR}. "
      "The primary objective is directional predictive power, not money P&L.")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="V2 directional predictive power vs V1")
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

    v2_idx, v2_buy = collect_v2_signals(df)
    v1_idx, v1_buy = collect_signals(df, s_cfg)

    groups_v2 = build_groups(v2_idx, v2_buy)
    groups_v1 = build_groups(v1_idx, v1_buy)
    v2 = analyze_groups(df, groups_v2)
    v1 = analyze_groups(df, groups_v1)

    v2_meta = {"total": int(len(v2_idx)), "buy": int(v2_buy.sum()), "sell": int((~v2_buy).sum())}
    v1_meta = {"total": int(len(v1_idx)), "buy": int(v1_buy.sum()), "sell": int((~v1_buy).sum())}

    out_dir.mkdir(parents=True, exist_ok=True)
    for gname in ["BUY", "SELL", "ALL"]:
        v2[gname].to_csv(out_dir / f"v2_predictive_{gname}.csv")
        v1[gname].to_csv(out_dir / f"v1_predictive_{gname}.csv")

    report_path = out_dir / "v2_predictive_report.md"
    write_report(df, v2, v1, v2_meta, v1_meta, report_path)

    print(f"V2 predictive-power analysis written to {out_dir}")
    print(f"  - {report_path}")
    print(f"  - v2_predictive_BUY/SELL/ALL.csv (+ v1_predictive_*.csv for comparison)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
