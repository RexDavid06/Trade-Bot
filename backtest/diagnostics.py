"""Diagnostic analysis of the existing backtest results.

This is analysis ONLY. It does not change the strategy rules, entry conditions,
SL/TP, or bot.py. It re-runs the same strategy under alternative *cost* models
(which is a reporting exercise, not a strategy change) and slices the resulting
4,109 trades along several axes to understand WHY the strategy loses.

Run with:
    python -m backtest.diagnostics
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .backtester import Trade, run_backtest
from .config import CostConfig, PathConfig, StrategyConfig
from .indicators import add_indicators
from .strategy import BUY, SELL

R = "r_multiple"


def _trade_frame(trades: list[Trade]) -> pd.DataFrame:
    rows = []
    for t in trades:
        rows.append(
            {
                "entry_time": pd.Timestamp(t.entry_time),
                "exit_time": pd.Timestamp(t.exit_time),
                "direction": t.direction,
                "result": t.result,
                "exit_reason": t.exit_reason,
                R: t.r_multiple,
                "net_pips": t.net_pips,                "net_money": t.net_money,
                "atr": t.atr,
                "signal_rsi": t.signal_rsi,
                "ema_sep": t.ema_sep,
                "duration_min": (pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)).total_seconds() / 60.0,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Cost sensitivity
# ---------------------------------------------------------------------------
def cost_sensitivity(df: pd.DataFrame, s_cfg: StrategyConfig, base_cfg: CostConfig) -> list[dict]:
    variants = {
        "zero_costs": CostConfig(
            starting_balance=base_cfg.starting_balance,
            lot_size=base_cfg.lot_size,
            base_contract=base_cfg.base_contract,
            commission_per_lot=0.0,
            slippage_pips=0.0,
            point=0.0,  # forces spread to 0 in _cost_price
            pip=base_cfg.pip,
            conservative_intrabar=base_cfg.conservative_intrabar,
        ),
        "spread_only": CostConfig(
            starting_balance=base_cfg.starting_balance,
            lot_size=base_cfg.lot_size,
            base_contract=base_cfg.base_contract,
            commission_per_lot=0.0,
            slippage_pips=0.0,
            point=base_cfg.point,
            pip=base_cfg.pip,
            conservative_intrabar=base_cfg.conservative_intrabar,
        ),
        "baseline": base_cfg,
    }

    results = []
    for name, c_cfg in variants.items():
        trades, _ = run_backtest(df, s_cfg, c_cfg)
        frame = _trade_frame(trades)
        money = frame["net_money"].to_numpy()
        gross_profit = float(money[money > 0].sum())
        gross_loss = float(abs(money[money < 0].sum()))
        pf = gross_profit / gross_loss if gross_loss else float("inf")
        total_r = float(frame[R].sum())
        results.append(
            {
                "variant": name,
                "spread": "0" if c_cfg.point == 0 else "CSV",
                "slippage_pips": c_cfg.slippage_pips,
                "commission_per_lot": c_cfg.commission_per_lot,
                "trades": len(trades),
                "net_pl": float(money.sum()),
                "profit_factor": pf,
                "expectancy_money": float(money.mean()),
                "expectancy_r": float(frame[R].mean()),
                "win_rate": float((money > 0).mean()),
                "total_r": total_r,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Helpers for grouped stats
# ---------------------------------------------------------------------------
def _group_stats(group: pd.DataFrame) -> dict:
    if len(group) == 0:
        return {
            "trades": 0, "win_rate": np.nan, "profit_factor": np.nan,
            "expectancy_r": np.nan, "total_r": 0.0, "net_pl": 0.0,
            "expectancy_money": np.nan,
        }
    money = group["net_money"].to_numpy()
    wins = money[money > 0]
    losses = money[money < 0]
    gp = float(wins.sum())
    gl = float(abs(losses.sum()))
    pf = gp / gl if gl else float("inf")
    return {
        "trades": len(group),
        "win_rate": float((money > 0).mean()),
        "profit_factor": pf,
        "expectancy_r": float(group[R].mean()),
        "total_r": float(group[R].sum()),
        "net_pl": float(money.sum()),
        "expectancy_money": float(money.mean()),
    }


def r_multiple_analysis(frame: pd.DataFrame) -> dict:
    wins = frame[frame[R] > 0][R]
    losses = frame[frame[R] <= 0][R]
    return {
        "avg_winner_r": float(wins.mean()) if len(wins) else 0.0,
        "avg_loser_r": float(losses.mean()) if len(losses) else 0.0,
        "median_winner_r": float(wins.median()) if len(wins) else 0.0,
        "median_loser_r": float(losses.median()) if len(losses) else 0.0,
        "expectancy_r": float(frame[R].mean()),
        "total_r": float(frame[R].sum()),
    }


def r_distribution(frame: pd.DataFrame) -> pd.Series:
    bins = [-np.inf, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, np.inf]
    labels = ["<-3", "-3..-2", "-2..-1", "-1..-0.5", "-0.5..0", "0..0.5", "0.5..1", "1..2", "2..3", ">3"]
    return pd.cut(frame[R], bins=bins, labels=labels, right=True).value_counts().sort_index()


def long_short(frame: pd.DataFrame) -> dict:
    return {
        "BUY": _group_stats(frame[frame["direction"] == BUY]),
        "SELL": _group_stats(frame[frame["direction"] == SELL]),
    }


def rsi_zones(frame: pd.DataFrame, s_cfg: StrategyConfig) -> dict:
    zones = {
        "BUY_40_45": (BUY, s_cfg.rsi_buy_min, 45.0),
        "BUY_45_50": (BUY, 45.0, 50.0),
        "BUY_50_55": (BUY, 50.0, s_cfg.rsi_buy_max),
        "SELL_45_50": (SELL, s_cfg.rsi_sell_min, 50.0),
        "SELL_50_55": (SELL, 50.0, 55.0),
        "SELL_55_60": (SELL, 55.0, s_cfg.rsi_sell_max),
    }
    out = {}
    for key, (direction, lo, hi) in zones.items():
        sub = frame[(frame["direction"] == direction) & (frame["signal_rsi"] >= lo) & (frame["signal_rsi"] < hi)]
        out[key] = _group_stats(sub)
    return out


def regime_analysis(frame: pd.DataFrame) -> dict:
    # EMA separation buckets (in price units, absolute).
    sep = frame["ema_sep"].abs()
    ema_buckets = pd.cut(
        sep,
        bins=[0, 5e-5, 1e-4, 2e-4, 4e-4, np.inf],
        labels=["tiny<0.5p", "0.5-1p", "1-2p", "2-4p", "strong>4p"],
    )
    ema_sep_perf = _bucket_stats(frame, ema_buckets)

    # ATR buckets.
    atr_buckets = pd.cut(
        frame["atr"],
        bins=[0, 5e-4, 8e-4, 1.1e-3, 1.5e-3, np.inf],
        labels=["low<5p", "5-8p", "8-11p", "11-15p", "high>15p"],
    )
    atr_perf = _bucket_stats(frame, atr_buckets)

    # Trend strength: normalize EMA separation by ATR (dimensionless).
    tren = frame.copy()
    tren["sep_ratio"] = frame["ema_sep"].abs() / frame["atr"].replace(0, np.nan)
    tren_buckets = pd.cut(
        tren["sep_ratio"],
        bins=[0, 0.05, 0.1, 0.2, 0.4, np.inf],
        labels=["weak<5%", "5-10%", "10-20%", "20-40%", "strong>40%"],
    )
    trend_strength = _bucket_stats(tren, tren_buckets)

    return {"ema_separation": ema_sep_perf, "atr_level": atr_perf, "trend_strength": trend_strength}


def _bucket_stats(frame: pd.DataFrame, buckets: pd.Series) -> list[dict]:
    out = []
    group = pd.DataFrame(frame).groupby(buckets, observed=True)
    for name, sub in group:
        stats = _group_stats(sub)
        stats["bucket"] = str(name)
        out.append(stats)
    return out


# ---------------------------------------------------------------------------
# Duration and sequences
# ---------------------------------------------------------------------------
def duration_analysis(frame: pd.DataFrame) -> dict:
    d = frame["duration_min"]
    return {
        "avg_duration_min": float(d.mean()),
        "median_duration_min": float(d.median()),
        "avg_win_duration_min": float(frame[frame["result"] == "WIN"]["duration_min"].mean()),
        "avg_loss_duration_min": float(frame[frame["result"] == "LOSS"]["duration_min"].mean()),
    }


def sequence_analysis(frame: pd.DataFrame) -> dict:
    wins, losses = [], []
    cur = 0  # positive = win streak, negative = loss streak
    for result in frame["result"]:
        if result == "WIN":
            if cur < 0:  # a losing streak just ended -> record it
                losses.append(-cur)
            cur = cur + 1 if cur > 0 else 1
        elif result == "LOSS":
            if cur > 0:  # a winning streak just ended -> record it
                wins.append(cur)
            cur = cur - 1 if cur < 0 else -1
        else:  # breakeven breaks any streak
            if cur > 0:
                wins.append(cur)
            elif cur < 0:
                losses.append(-cur)
            cur = 0
    if cur > 0:
        wins.append(cur)
    elif cur < 0:
        losses.append(-cur)
    return {
        "longest_winning_streak": max(wins, default=0),
        "longest_losing_streak": max(losses, default=0),
        "avg_winning_streak": float(np.mean(wins)) if wins else 0.0,
        "avg_losing_streak": float(np.mean(losses)) if losses else 0.0,
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def build_report(
    df: pd.DataFrame, s_cfg: StrategyConfig, c_cfg: CostConfig, trades: list[Trade], frame: pd.DataFrame
) -> dict:
    return {
        "cost_sensitivity": cost_sensitivity(df, s_cfg, c_cfg),
        "r_multiple": r_multiple_analysis(frame),
        "r_distribution": r_distribution(frame).to_dict(),
        "long_short": long_short(frame),
        "rsi_zones": rsi_zones(frame, s_cfg),
        "regime": regime_analysis(frame),
        "duration": duration_analysis(frame),
        "sequences": sequence_analysis(frame),
    }


def write_report(report: dict, path: Path) -> None:
    lines = []
    w = lines.append
    w("# DIAGNOSTIC REPORT")
    w("")

    w("## 1. COST SENSITIVITY")
    w("| variant | spread | slippage/pip | comm/lot | trades | net P/L | profit factor | expectancy | win rate | total R |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for r in report["cost_sensitivity"]:
        w(
            f"| {r['variant']} | {r['spread']} | {r['slippage_pips']} | {r['commission_per_lot']} | "
            f"{r['trades']} | ${r['net_pl']:,.0f} | {r['profit_factor']:.2f} | "
            f"${r['expectancy_money']:,.2f} ({r['expectancy_r']:.3f}R) | {r['win_rate']*100:.1f}% | {r['total_r']:.0f}R |"
        )
    w("")

    w("## 2. R-MULTIPLE ANALYSIS")
    rm = report["r_multiple"]
    w(f"- Average winner: {rm['avg_winner_r']:.3f}R")
    w(f"- Average loser: {rm['avg_loser_r']:.3f}R")
    w(f"- Median winner: {rm['median_winner_r']:.3f}R")
    w(f"- Median loser: {rm['median_loser_r']:.3f}R")
    w(f"- Expectancy: {rm['expectancy_r']:.3f}R per trade")
    w(f"- Total R: {rm['total_r']:.0f}R")
    w(f"- Distribution: {report['r_distribution']}")
    w("")

    w("## 3. LONG VS SHORT")
    w("| side | trades | win rate | profit factor | expectancy | total R | net P/L |")
    w("|---|---|---|---|---|---|---|")
    for side, s in report["long_short"].items():
        w(
            f"| {side} | {s['trades']} | {s['win_rate']*100:.1f}% | {s['profit_factor']:.2f} | "
            f"{s['expectancy_r']:.3f}R | {s['total_r']:.0f}R | ${s['net_pl']:,.0f} |"
        )
    w("")

    w("## 4. RSI ENTRY ZONES")
    w("| zone | trades | win rate | profit factor | expectancy R | total R |")
    w("|---|---|---|---|---|---|")
    zone_labels = {
        "BUY_40_45": "BUY 40-45", "BUY_45_50": "BUY 45-50", "BUY_50_55": "BUY 50-55",
        "SELL_45_50": "SELL 45-50", "SELL_50_55": "SELL 50-55", "SELL_55_60": "SELL 55-60",
    }
    for key, s in report["rsi_zones"].items():
        w(
            f"| {zone_labels[key]} | {s['trades']} | {s['win_rate']*100:.1f}% | "
            f"{s['profit_factor']:.2f} | {s['expectancy_r']:.3f}R | {s['total_r']:.0f}R |"
        )
    w("")

    w("## 5. MARKET REGIME")
    w("### EMA50/EMA200 separation (absolute)")
    w("| bucket | trades | win rate | profit factor | expectancy R | total R |")
    w("|---|---|---|---|---|---|")
    for r in report["regime"]["ema_separation"]:
        w(f"| {r['bucket']} | {r['trades']} | {r['win_rate']*100:.1f}% | {r['profit_factor']:.2f} | {r['expectancy_r']:.3f}R | {r['total_r']:.0f}R |")
    w("### ATR level")
    w("| bucket | trades | win rate | profit factor | expectancy R | total R |")
    w("|---|---|---|---|---|---|")
    for r in report["regime"]["atr_level"]:
        w(f"| {r['bucket']} | {r['trades']} | {r['win_rate']*100:.1f}% | {r['profit_factor']:.2f} | {r['expectancy_r']:.3f}R | {r['total_r']:.0f}R |")
    w("### Trend strength (EMA separation / ATR)")
    w("| bucket | trades | win rate | profit factor | expectancy R | total R |")
    w("|---|---|---|---|---|---|")
    for r in report["regime"]["trend_strength"]:
        w(f"| {r['bucket']} | {r['trades']} | {r['win_rate']*100:.1f}% | {r['profit_factor']:.2f} | {r['expectancy_r']:.3f}R | {r['total_r']:.0f}R |")
    w("")

    w("## 6. TRADE DURATION")
    d = report["duration"]
    w(f"- Average duration: {d['avg_duration_min']:.0f} min")
    w(f"- Median duration: {d['median_duration_min']:.0f} min")
    w(f"- Avg winning trade duration: {d['avg_win_duration_min']:.0f} min")
    w(f"- Avg losing trade duration: {d['avg_loss_duration_min']:.0f} min")
    w("")

    w("## 7. LOSS/WIN SEQUENCES")
    s = report["sequences"]
    w(f"- Longest winning streak: {s['longest_winning_streak']}")
    w(f"- Longest losing streak: {s['longest_losing_streak']}")
    w(f"- Average winning streak: {s['avg_winning_streak']:.1f}")
    w(f"- Average losing streak: {s['avg_losing_streak']:.1f}")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    s_cfg = StrategyConfig()
    c_cfg = CostConfig()
    df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])
    df = add_indicators(df, s_cfg)

    trades, _ = run_backtest(df, s_cfg, c_cfg)
    frame = _trade_frame(trades)

    out_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_dir / "diagnostics_trades.csv", index=False)

    report = build_report(df, s_cfg, c_cfg, trades, frame)
    write_report(report, out_dir / "diagnostics_report.md")
    print(f"Diagnostics written to {out_dir}")
    print(f"  - {out_dir / 'diagnostics_report.md'}")
    print(f"  - {out_dir / 'diagnostics_trades.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())