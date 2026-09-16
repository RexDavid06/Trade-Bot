"""Phase 5 — Strategy benchmark runner.

Runs every candidate strategy (V1 baseline, mean-reversion, breakout-fade)
across all available symbols and all chronological splits (dev/val/holdout)
using the standard backtester with realistic costs.

Outputs:
  - outputs/benchmark/results.json    (machine-readable)
  - outputs/benchmark/results.md      (human-readable comparison table)

Usage:
    python -m backtest.strategies.benchmark
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Sibling imports — use relative paths so the package works as -m backtest.strategies.benchmark
_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent  # project root
sys.path.insert(0, str(_root))

from backtest.backtester import run_backtest, Trade
from backtest.config import CostConfig, StrategyConfig, PathConfig
from backtest.indicators import add_indicators
from backtest.metrics import compute_metrics

# --- Import candidate strategies -------------------------------------------
from backtest.strategy import signal_at as v1_signal
from backtest.strategies.mean_reversion import signal_at as mr_signal, _ensure_columns as mr_setup
from backtest.strategies.breakout_fade import signal_at as bf_signal, _ensure_columns as bf_setup


# Strategy registry: name -> (signal_fn, setup_fn_or_None, description)
STRATEGIES: dict[str, tuple] = {
    "v1_trend_rsi": (v1_signal, None, "EMA50/200 + RSI pullback (baseline V1)"),
    "mean_reversion": (mr_signal, mr_setup, "Fade extreme distance from SMA(10)"),
    "breakout_fade": (bf_signal, bf_setup, "Follow downside breaks, fade upside breaks (CH=160)"),
}

# Symbols to benchmark
SYMBOLS = ["eurusd", "eurgbp", "eurjpy", "gbpusd"]
SPLITS = ["dev", "val", "holdout"]


def _load_split(csv_path: Path, assignments_path: Path, split_name: str) -> pd.DataFrame:
    """Load CSV and filter to rows belonging to *split_name*."""
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])

    assignments = pd.read_csv(assignments_path)
    mask = assignments["split"] == split_name
    indices = assignments.index[mask].tolist()
    return df.iloc[indices].reset_index(drop=True)


def _run_one(
    df: pd.DataFrame,
    signal_fn,
    setup_fn,
    s_cfg: StrategyConfig,
    c_cfg: CostConfig,
) -> dict[str, Any]:
    """Run a single strategy on a single split and return metrics dict."""
    if setup_fn is not None:
        df = setup_fn(df)
    df = add_indicators(df, s_cfg)
    trades, equity = run_backtest(df, s_cfg, c_cfg, signal_fn=signal_fn)
    metrics = compute_metrics(trades, equity, c_cfg.starting_balance)
    return metrics


def main() -> int:
    pcfg = PathConfig()
    c_cfg = CostConfig()
    s_cfg = StrategyConfig()
    out_dir = pcfg.output_dir / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {}

    for sym in SYMBOLS:
        csv_path = pcfg.base_dir / "data" / f"{sym}_m5.csv"
        assignments_path = pcfg.output_dir / sym / "reports" / "data_split_assignments.csv"

        if not csv_path.exists():
            print(f"SKIP {sym}: {csv_path} not found")
            continue
        if not assignments_path.exists():
            print(f"SKIP {sym}: split assignments not found at {assignments_path}")
            continue

        print(f"\n{'='*60}")
        print(f"  {sym.upper()}")
        print(f"{'='*60}")

        sym_results: dict[str, Any] = {}

        for split in SPLITS:
            df_split = _load_split(csv_path, assignments_path, split)
            print(f"\n  Split: {split} ({len(df_split)} bars)")

            split_results: dict[str, Any] = {}

            for strat_name, (sig_fn, setup_fn, desc) in STRATEGIES.items():
                metrics = _run_one(df_split, sig_fn, setup_fn, s_cfg, c_cfg)
                split_results[strat_name] = {
                    "description": desc,
                    "trades": metrics.get("total_trades", 0),
                    "win_rate": round(metrics.get("win_rate", 0) * 100, 2),
                    "profit_factor": round(metrics.get("profit_factor", 0), 3),
                    "expectancy_pips": round(metrics.get("expectancy_pips", 0), 3),
                    "net_profit": round(metrics.get("net_profit", 0), 2),
                    "max_drawdown_pct": round(metrics.get("max_drawdown_pct", 0), 2),
                    "total_return_pct": round(metrics.get("total_return_pct", 0), 2),
                }
                t = metrics.get("total_trades", 0)
                wr = metrics.get("win_rate", 0) * 100
                pf = metrics.get("profit_factor", 0)
                ep = metrics.get("expectancy_pips", 0)
                print(f"    {strat_name:20s}  trades={t:5d}  WR={wr:5.1f}%  PF={pf:.3f}  exp_pips={ep:+.3f}")

            sym_results[split] = split_results

        results[sym] = sym_results

    # --- Write JSON ---
    json_path = out_dir / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    # --- Write Markdown report ---
    md_path = out_dir / "results.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Phase 5 Strategy Benchmark Results\n\n")
        f.write(f"**Symbols**: {', '.join(SYMBOLS)}\n")
        f.write(f"**Splits**: dev (60%), val (20%), holdout (20%)\n")
        f.write(f"**Strategies**: {', '.join(STRATEGIES.keys())}\n\n")

        for sym in SYMBOLS:
            if sym not in results:
                continue
            f.write(f"## {sym.upper()}\n\n")
            f.write("| Split | Strategy | Trades | Win% | PF | Exp(pips) | Net P/L | MaxDD% | Return% |\n")
            f.write("|-------|----------|--------|------|----|-----------|---------|--------|----------|\n")
            for split in SPLITS:
                if split not in results[sym]:
                    continue
                for strat_name in STRATEGIES:
                    r = results[sym][split].get(strat_name, {})
                    f.write(f"| {split} | {strat_name} | {r.get('trades',0)} | "
                            f"{r.get('win_rate',0):.1f}% | {r.get('profit_factor',0):.3f} | "
                            f"{r.get('expectancy_pips',0):+.3f} | "
                            f"${r.get('net_profit',0):+,.2f} | "
                            f"{r.get('max_drawdown_pct',0):.1f}% | "
                            f"{r.get('total_return_pct',0):+.1f}% |\n")
            f.write("\n")

        f.write("## Key Observations\n\n")
        f.write("- Compare dev vs val vs holdout for each strategy.\n")
        f.write("- A strategy that performs well on dev but poorly on val/holdout is likely overfitted.\n")
        f.write("- Look for consistent (or at least non-catastrophic) performance across splits.\n")
        f.write("- All strategies use the same SL/TP (ATR-based) and cost model.\n")

    print(f"\nBenchmark results written to {out_dir}")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
