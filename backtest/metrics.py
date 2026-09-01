"""Performance metrics computed from the backtest trade list and equity curve."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .backtester import Trade


def _money(trades: list[Trade]) -> np.ndarray:
    return np.array([t.net_money for t in trades], dtype=float)


def compute_metrics(trades: list[Trade], equity: pd.DataFrame, starting_balance: float) -> dict[str, Any]:
    money = _money(trades)
    total = len(trades)
    wins = [t for t in trades if t.result == "WIN"]
    losses = [t for t in trades if t.result == "LOSS"]
    win_count = len(wins)
    loss_count = len(losses)
    be_count = total - win_count - loss_count

    winning_money = money[money > 0]
    losing_money = money[money < 0]
    gross_profit = float(winning_money.sum()) if len(winning_money) else 0.0
    gross_loss = float(losing_money.sum()) if len(losing_money) else 0.0  # negative

    profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else float("inf")
    if total == 0:
        profit_factor = 0.0

    avg_win = float(np.mean(winning_money)) if len(winning_money) else 0.0
    avg_loss = float(np.mean(losing_money)) if len(losing_money) else 0.0

    net_profit = float(money.sum()) if total else 0.0
    expectancy = net_profit / total if total else 0.0
    total_return = net_profit / starting_balance

    # Streaks based on WIN/LOSS/BE sign.
    streaks, cur_streak = [], 0
    for t in trades:
        if t.result == "WIN":
            cur_streak = cur_streak + 1 if cur_streak > 0 else 1
        elif t.result == "LOSS":
            cur_streak = cur_streak - 1 if cur_streak < 0 else -1
        else:  # BE breaks the streak
            cur_streak = 0
        streaks.append(cur_streak)
    longest_win_streak = max([s for s in streaks if s > 0], default=0)
    longest_loss_streak = max([-s for s in streaks if s < 0], default=0)

    # Drawdown from the equity curve (per-trade snapshots).
    balances = equity["balance"].to_numpy(dtype=float)
    peak = np.maximum.accumulate(balances)
    dd = peak - balances
    dd_pct = dd / np.where(peak == 0, 1, peak)
    max_dd = float(dd.max())
    max_dd_pct = float(dd_pct.max() * 100.0)

    final_balance = float(balances[-1])

    win_rate = win_count / total if total else 0.0
    # gross_loss reported as a positive magnitude for readability
    gross_loss_mag = abs(gross_loss)

    monthly = build_monthly_table(trades)
    long_perf = build_direction_table(trades, "BUY")
    short_perf = build_direction_table(trades, "SELL")

    return {
        "starting_balance": starting_balance,
        "final_balance": final_balance,
        "total_trades": total,
        "winning_trades": win_count,
        "losing_trades": loss_count,
        "breakeven_trades": be_count,
        "win_rate": win_rate,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss_mag,
        "net_profit": net_profit,
        "profit_factor": profit_factor,
        "avg_winning_trade": avg_win,
        "avg_losing_trade": avg_loss,
        "expectancy_per_trade": expectancy,
        "expectancy_pips": float(np.mean([t.net_pips for t in trades])) if total else 0.0,
        "max_drawdown": max_dd,
        "max_drawdown_pct": max_dd_pct,
        "longest_winning_streak": longest_win_streak,
        "longest_losing_streak": longest_loss_streak,
        "total_return": total_return,
        "total_return_pct": total_return * 100.0,
        "monthly": monthly,
        "long_performance": long_perf,
        "short_performance": short_perf,
    }


def build_monthly_table(trades: list[Trade]) -> pd.DataFrame:
    rows = []
    for t in trades:
        rows.append({"month": str(pd.Timestamp(t.exit_time).to_period("M")), "net_pips": t.net_pips, "net_money": t.net_money, "result": t.result})
    if not rows:
        return pd.DataFrame()
    month = pd.DataFrame(rows).groupby("month").agg(
        trades=("result", "size"),
        wins=("result", lambda s: int((s == "WIN").sum())),
        losses=("result", lambda s: int((s == "LOSS").sum())),
        total_pips=("net_pips", "sum"),
        total_money=("net_money", "sum"),
    )
    month["win_rate"] = month["wins"] / month["trades"]
    return month[["trades", "wins", "losses", "win_rate", "total_pips", "total_money"]]


def build_direction_table(trades: list[Trade], direction: str) -> pd.DataFrame:
    sel = [t for t in trades if t.direction == direction]
    money = np.array([t.net_money for t in sel], dtype=float)
    n = len(sel)
    wins = int((money > 0).sum())
    losses = int((money < 0).sum())
    gross_profit = float(money[money > 0].sum())
    gross_loss = float(money[money < 0].sum())
    net = float(money.sum())
    pf = gross_profit / abs(gross_loss) if gross_loss != 0 else float("inf")
    return pd.DataFrame(
        {
            "trades": [n],
            "wins": [wins],
            "losses": [losses],
            "win_rate": [wins / n if n else 0.0],
            "net_pips": [float(sum(t.net_pips for t in sel))],
            "net_money": [net],
            "profit_factor": [pf],
        }
    )
