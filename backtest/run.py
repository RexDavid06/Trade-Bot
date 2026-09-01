"""CLI entry point for the backtester.

Usage:
    python -m backtest.run [--data path] [--out dir]

Reads historical EURUSD M5 data (CSV), runs the strategy, prints a summary and
writes outputs (trade log, equity CSV + PNG, summary JSON) to the output dir.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .backtester import run_backtest
from .config import CostConfig, PathConfig, StrategyConfig
from .indicators import add_indicators
from .metrics import compute_metrics
from .reporting import print_report, save_equity_csv, save_equity_plot, save_summary, save_trade_log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EURUSD M5 backtester")
    parser.add_argument("--data", type=Path, default=None, help="CSV path (default: data/eurusd_m5.csv)")
    parser.add_argument("--out", type=Path, default=None, help="output directory (default: outputs)")
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir

    if not data_path.exists():
        sys.stderr.write(f"Data file not found: {data_path}\n")
        sys.stderr.write("Generate it first with dump_mt5_data.py (requires MT5).\n")
        return 1

    s_cfg = StrategyConfig()
    c_cfg = CostConfig()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])

    df = add_indicators(df, s_cfg)
    trades, equity = run_backtest(df, s_cfg, c_cfg)
    metrics = compute_metrics(trades, equity, c_cfg.starting_balance)

    save_trade_log(trades, out_dir / "trade_log.csv")
    save_equity_csv(equity, out_dir / "equity_curve.csv")
    save_equity_plot(equity, out_dir / "equity_curve.png", c_cfg.starting_balance)
    save_summary(metrics, out_dir / "summary.json")

    print_report(metrics)

    print(f"\nOutputs written to: {out_dir}")
    print(f"  - trade_log.csv")
    print(f"  - equity_curve.csv / equity_curve.png")
    print(f"  - summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
