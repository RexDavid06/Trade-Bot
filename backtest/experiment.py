"""Controlled experiment: does requiring stronger EMA separation improve results?

Tests the hypothesis that the strategy performs poorly because EMA50 >/= EMA200
triggers when the EMAs are too close (market ranging). For each configurable
threshold of the normalized separation ``abs(EMA50 - EMA200) / ATR``, the SAME
strategy is re-run (only the separation filter changes; every other parameter,
SL/TP, one-position rule, closed-candle/next-open execution and costs are
unchanged). Results are compared against the baseline threshold of 0.

This is an INVESTIGATION of the trend-strength/profitability relationship — it
does NOT select a best threshold, does not modify bot.py, and does not add any
new indicator.

Run with:
    python -m backtest.experiment
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .backtester import Trade, run_backtest
from .config import CostConfig, PathConfig, StrategyConfig
from .indicators import add_indicators

THRESHOLDS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]


def _sequence_max_losses(trades: list[Trade]) -> int:
    cur = 0
    worst = 0
    for t in trades:
        if t.result == "LOSS":
            cur += 1
            worst = max(worst, cur)
        elif t.result == "WIN":
            cur = 0
        # breakeven breaks the streak too
        else:
            cur = 0
    return worst


def _run_once(df: pd.DataFrame, s_cfg: StrategyConfig, c_cfg: CostConfig) -> dict:
    trades, equity = run_backtest(df, s_cfg, c_cfg)
    total = len(trades)
    buys = [t for t in trades if t.direction == "BUY"]
    sells = [t for t in trades if t.direction == "SELL"]
    money = np.array([t.net_money for t in trades])
    rvals = np.array([t.r_multiple for t in trades])

    wins = money[money > 0]
    losses = money[money < 0]
    gp = float(wins.sum())
    gl = float(abs(losses.sum()))
    pf = gp / gl if gl else float("inf")

    balances = equity["balance"].to_numpy(dtype=float)
    peak = np.maximum.accumulate(balances)
    max_dd = float((peak - balances).max())
    max_dd_pct = float(((peak - balances) / np.where(peak == 0, 1, peak)).max() * 100.0)

    return {
        "threshold": s_cfg.ema_sep_min,
        "total_trades": total,
        "buy_trades": len(buys),
        "sell_trades": len(sells),
        "win_rate": float((money > 0).mean()) if total else 0.0,
        "profit_factor": pf,
        "expectancy_r": float(rvals.mean()) if total else 0.0,
        "total_r": float(rvals.sum()),
        "net_pl": float(money.sum()),
        "max_drawdown": max_dd,
        "max_drawdown_pct": max_dd_pct,
        "longest_losing_streak": _sequence_max_losses(trades),
    }


def run_experiment(
    df: pd.DataFrame, s_cfg: StrategyConfig, c_cfg: CostConfig, thresholds: list[float]
) -> pd.DataFrame:
    rows = []
    for t in thresholds:
        cfg = StrategyConfig(**{**s_cfg.__dict__, "ema_sep_min": t})
        rows.append(_run_once(df, cfg, c_cfg))
    return pd.DataFrame(rows)


def write_report(table: pd.DataFrame, path: Path) -> None:
    lines = []
    w = lines.append
    w("# EMA SEPARATION EXPERIMENT (abs(EMA50-EMA200)/ATR threshold)")
    w("")
    w("Threshold 0.00 = baseline (bot.py rules, no separation filter).")
    w("Every other parameter is unchanged; only the separation filter varies.")
    w("")
    w("| threshold | total | BUY | SELL | win rate | PF | exp R | total R | net P/L | max DD | max DD% | worst loss streak |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in table.iterrows():
        w(
            f"| {r['threshold']:.2f} | {r['total_trades']} | {r['buy_trades']} | {r['sell_trades']} | "
            f"{r['win_rate']*100:.1f}% | {r['profit_factor']:.2f} | {r['expectancy_r']:.3f} | "
            f"{r['total_r']:.0f} | ${r['net_pl']:,.0f} | ${r['max_drawdown']:,.0f} | "
            f"{r['max_drawdown_pct']:.1f}% | {r['longest_losing_streak']} |"
        )

    baseline = table.iloc[0]
    w("")
    w("## Change vs baseline (threshold 0.00)")
    w("| threshold | trades chg | win rate chg | PF chg | exp R | total R chg | net P/L chg |")
    w("|---|---|---|---|---|---|---|")
    for _, r in table.iloc[1:].iterrows():
        w(
            f"| {r['threshold']:.2f} | {int(r['total_trades'] - baseline['total_trades']):+d} | "
            f"{(r['win_rate']-baseline['win_rate'])*100:+.1f}pp | {r['profit_factor']-baseline['profit_factor']:+.2f} | "
            f"{r['expectancy_r']:+.3f} | {float(r['total_r']-baseline['total_r']):+.0f} | "
            f"{float(r['net_pl']-baseline['net_pl']):+,.0f} |"
        )

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EMA separation experiment")
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--thresholds", type=str, default="", help="comma-separated list to override defaults")
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    thresholds = THRESHOLDS if not args.thresholds else [float(x) for x in args.thresholds.split(",")]

    s_cfg = StrategyConfig()
    c_cfg = CostConfig()
    df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])
    df = add_indicators(df, s_cfg)

    out_dir.mkdir(parents=True, exist_ok=True)
    table = run_experiment(df, s_cfg, c_cfg, thresholds)
    table.to_csv(out_dir / "separation_experiment.csv", index=False)
    write_report(table, out_dir / "separation_experiment.md")

    print(f"Experiment written to {out_dir}")
    print(f"  - {out_dir / 'separation_experiment.csv'}")
    print(f"  - {out_dir / 'separation_experiment.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())