"""Excursion analysis (MAE/MFE) of the existing strategy's trades.

Investigation of what happens AFTER each entry signal. This is ANALYSIS ONLY:
it does not change entry rules, RSI thresholds, EMA periods, SL/TP, add filters,
or modify bot.py. It reads the already-computed trade log (which carries
per-trade MAE/MFE and signal context from the engine) and reports distributions,
before-stop behavior, entry timing and signal-context comparisons.

Run with:
    python -m backtest.excursion
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PathConfig


def _percentiles(s: pd.Series) -> dict:
    return {
        "median": float(s.median()) if len(s) else np.nan,
        "average": float(s.mean()) if len(s) else np.nan,
        "p25": float(s.quantile(0.25)) if len(s) else np.nan,
        "p75": float(s.quantile(0.75)) if len(s) else np.nan,
        "p90": float(s.quantile(0.90)) if len(s) else np.nan,
    }


def _fmt_pct(d: dict) -> str:
    return (
        f"median {d['median']:.1f} | avg {d['average']:.1f} | "
        f"p25 {d['p25']:.1f} | p75 {d['p75']:.1f} | p90 {d['p90']:.1f}"
    )


def _excursion_stats(frame: pd.DataFrame) -> dict:
    out = {}
    for key, sub in (("all", frame), ("wins", frame[frame["result"] == "WIN"]), ("losses", frame[frame["result"] == "LOSS"])):
        out[key] = {
            "mae_pips": _percentiles(sub["mae_pips"]),
            "mae_r": _percentiles(sub["mae_r"]),
            "mfe_pips": _percentiles(sub["mfe_pips"]),
            "count": len(sub),
        }
    return out


def before_stop_analysis(frame: pd.DataFrame) -> dict:
    sl = frame[frame["exit_reason"] == "SL"]
    n = len(sl)
    ever_favorable = int((sl["mfe_pips"] > 0).sum())
    return {
        "count": n,
        "avg_mae_pips": float(sl["mae_pips"].mean()) if n else np.nan,
        "median_mae_pips": float(sl["mae_pips"].median()) if n else np.nan,
        "avg_mae_r": float(sl["mae_r"].mean()) if n else np.nan,
        "ever_favorable_count": ever_favorable,
        "ever_favorable_pct": ever_favorable / n if n else 0.0,
        "avg_mfe_pips_before_sl": float(sl["mfe_pips"].mean()) if n else np.nan,
        "median_mfe_pips_before_sl": float(sl["mfe_pips"].median()) if n else np.nan,
    }


def entry_timing(frame: pd.DataFrame, pip: float = 0.0001) -> dict:
    """For losing trades, bucket by favorable room in R before the stop.

    MAE for a losing trade is always >= ~1R (it hit the stop), so bucketing MAE
    is degenerate. The meaningful timing question — did the loser move AGAINST
    immediately (no favorable room) or move favorably and then reverse to SL —
    is answered by each loser's MFE in R:
        * MFE < 0.25R  -> immediate adverse, no breathing room
        * MFE 0.25-0.5R
        * MFE 0.5-1R
        * MFE >= 1R    -> moved a full R in favor yet still hit SL
    """
    losses = frame[frame["result"] == "LOSS"].copy()
    sl_dist_pips = (losses["entry_price"] - losses["stop_loss"]).abs() / pip
    mfe_r = losses["mfe_pips"] / sl_dist_pips.replace(0, np.nan)
    bins = [0, 0.25, 0.5, 1.0, np.inf]
    labels = ["MFE<0.25R (immediate adverse)", "0.25-0.5R", "0.5-1R", "1R+ (had room, still lost)"]
    bucket = pd.cut(mfe_r, bins=bins, labels=labels, right=False)
    counts = bucket.value_counts().reindex(labels, fill_value=0)
    total = len(losses)
    return {
        "total_losses": total,
        "buckets": {k: int(v) for k, v in counts.items()},
        "buckets_pct": {k: float(v / total) if total else 0.0 for k, v in counts.items()},
    }


def signal_context(frame: pd.DataFrame) -> dict:
    """Compare entry-time observational features between winners and losers."""
    features = {
        "RSI": "signal_rsi",
        "EMA50": "signal_ema_fast",
        "EMA200": "signal_ema_slow",
        "EMA_sep": "ema_sep",
        "ATR": "atr",
        "candle_range": "signal_range",
        "dist_price_EMA50": "dist_ema50",
        "dist_price_EMA200": "dist_ema200",
    }
    f = frame.copy()
    f["dist_ema50"] = f["entry_price"] - f["signal_ema_fast"]
    f["dist_ema200"] = f["entry_price"] - f["signal_ema_slow"]

    wins = f[f["result"] == "WIN"]
    losses = f[f["result"] == "LOSS"]
    rows = []
    for label, col in features.items():
        rows.append(
            {
                "feature": label,
                "wins_mean": float(wins[col].mean()) if len(wins) else np.nan,
                "wins_median": float(wins[col].median()) if len(wins) else np.nan,
                "losses_mean": float(losses[col].mean()) if len(losses) else np.nan,
                "losses_median": float(losses[col].median()) if len(losses) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def write_report(
    stats: dict, before_sl: dict, timing: dict, context: pd.DataFrame, path: Path, frame: pd.DataFrame
) -> None:
    lines = []
    w = lines.append
    w("# EXCURSION ANALYSIS REPORT")
    w("")

    w("## 1. MAE (maximum adverse excursion)")
    w("| group | count | MAE pips | MAE R |")
    w("|---|---|---|---|")
    for key, g in stats.items():
        w(f"| {key} | {g['count']} | {_fmt_pct(g['mae_pips'])} | {_fmt_pct(g['mae_r'])} |")
    w("")

    w("## 2. MFE (maximum favorable excursion)")
    w("| group | count | MFE pips |")
    w("|---|---|---|")
    for key, g in stats.items():
        w(f"| {key} | {g['count']} | {_fmt_pct(g['mfe_pips'])} |")
    w("")

    w("## 3. BEFORE STOP ANALYSIS (trades that hit SL)")
    w(f"- Count: {before_sl['count']}")
    w(f"- Average MAE at stop: {before_sl['avg_mae_pips']:.1f} pips ({before_sl['avg_mae_r']:.2f}R)")
    w(f"- Median MAE at stop: {before_sl['median_mae_pips']:.1f} pips")
    w(f"- Ever moved favorable before SL: {before_sl['ever_favorable_count']} of {before_sl['count']} ({before_sl['ever_favorable_pct']*100:.1f}%)")
    w(f"- Avg MFE before SL: {before_sl['avg_mfe_pips_before_sl']:.1f} pips (median {before_sl['median_mfe_pips_before_sl']:.1f})")
    w("")

    w("## 4. ENTRY TIMING (losing trades, first adverse move in R)")
    w(f"- Total losing trades: {timing['total_losses']}")
    for k in timing["buckets"]:
        w(f"  - {k}: {timing['buckets'][k]} ({timing['buckets_pct'][k]*100:.1f}%)")
    w("")

    w("## 5. SIGNAL CONTEXT (win vs loss at entry)")
    w("| feature | wins mean | wins median | losses mean | losses median |")
    w("|---|---|---|---|---|")
    for _, r in context.iterrows():
        w(
            f"| {r['feature']} | {r['wins_mean']:.4f} | {r['wins_median']:.4f} | "
            f"{r['losses_mean']:.4f} | {r['losses_median']:.4f} |"
        )

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MAE/MFE excursion analysis")
    parser.add_argument("--trades", type=Path, default=None, help="path to trade_log.csv")
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    trades_path = args.trades if args.trades is not None else pcfg.output_dir / "trade_log.csv"
    out_dir = args.out if args.out is not None else pcfg.output_dir
    if not trades_path.exists():
        raise SystemExit(f"Trade log not found: {trades_path}\nRun `python -m backtest.run` first.")

    frame = pd.read_csv(trades_path)

    stats = _excursion_stats(frame)
    before_sl = before_stop_analysis(frame)
    timing = entry_timing(frame)
    context = signal_context(frame)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_report(stats, before_sl, timing, context, out_dir / "excursion_report.md", frame)

    print(f"Excursion analysis written to {out_dir}")
    print(f"  - {out_dir / 'excursion_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())