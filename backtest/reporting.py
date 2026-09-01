"""Write backtest outputs: summary, trade log CSV, equity CSV, equity PNG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .backtester import Trade


def save_trade_log(trades: list[Trade], path: Path) -> None:
    pd.DataFrame([t.to_dict() for t in trades]).to_csv(path, index=False)


def save_equity_csv(equity: pd.DataFrame, path: Path) -> None:
    equity.to_csv(path, index=False)


def save_equity_plot(equity: pd.DataFrame, path: Path, starting_balance: float) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(equity["time"], equity["balance"], linewidth=1.2)
    ax.axhline(starting_balance, color="gray", linestyle="--", linewidth=0.8, label="Start")
    ax.set_title("Backtest Equity Curve (long + short combined)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Balance (USD)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def save_summary(metrics: dict[str, Any], path: Path) -> None:
    serializable = dict(metrics)
    serializable["monthly"] = metrics["monthly"].reset_index().to_dict("records")
    serializable["long_performance"] = metrics["long_performance"].to_dict("records")
    serializable["short_performance"] = metrics["short_performance"].to_dict("records")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, indent=2, default=str)


def print_report(metrics: dict[str, Any]) -> None:
    m = metrics
    bar = "=" * 52
    print(f"\n{bar}\nBACKTEST SUMMARY\n{bar}")
    print(f"Starting balance      : ${m['starting_balance']:,.2f}")
    print(f"Final balance         : ${m['final_balance']:,.2f}")
    print(f"Total return          : {m['total_return_pct']:+.2f}%")
    print(f"\nTrades (total)        : {m['total_trades']}")
    print(f"  Winning             : {m['winning_trades']}")
    print(f"  Losing              : {m['losing_trades']}")
    print(f"  Breakeven           : {m['breakeven_trades']}")
    print(f"  Win rate            : {m['win_rate'] * 100:.2f}%")
    print(f"\nGross profit          : ${m['gross_profit']:,.2f}")
    print(f"Gross loss            : ${m['gross_loss']:,.2f}")
    print(f"Net profit / loss     : ${m['net_profit']:,.2f}")
    print(f"Profit factor         : {m['profit_factor']:.3f}")
    print(f"Avg winning trade     : ${m['avg_winning_trade']:,.2f}")
    print(f"Avg losing trade      : ${m['avg_losing_trade']:,.2f}")
    print(f"Expectancy / trade    : ${m['expectancy_per_trade']:,.2f}  ({m['expectancy_pips']:+.1f} pips)")
    print(f"\nMax drawdown          : ${m['max_drawdown']:,.2f}  ({m['max_drawdown_pct']:.2f}%)")
    print(f"Longest win streak    : {m['longest_winning_streak']}")
    print(f"Longest loss streak   : {m['longest_losing_streak']}")
