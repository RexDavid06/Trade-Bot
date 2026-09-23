"""Scalper probe — fixed 'high win-rate' geometry measured on DEV, RESEARCH ONLY.

This module answers one question: can a retail-style scalper exit structure
(tight take-profit / wide stop-loss -> mechanically high win rate) produce
positive net expectancy after real observed spreads + slippage on the clean
M5 DEV data of the three clean pairs?

Entry is deliberately trivial and unbiased (direction of the closed M5 bar),
so the result measures the *exit-structure economics* rather than any claimed
edge.  Execution follows the repository engine conventions: signal on the
closed bar t, entry at the open of t+1, intrabar stops with SL checked first
(conservative), time-stop at a fixed bar count.

Three fixed exit geometries, all declared before running (no sweep):
  A symmetric  TP 14 pips / SL 14 pips
  B winrate   TP  8 pips / SL 20 pips   (classic high-hit-rate scalper shape)
  C trend     TP 20 pips / SL  8 pips   (inverted shape, low hit rate)

Integrity: DEV rows only; VALIDATION/HOLDOUT never loaded; EURJPY excluded
(degraded feed); no strategy/bot/backtester/config changes; outputs are new
files (SCALPER_PROBE_RESULTS.md, outputs/scalper_probe_results.json).

Usage:
    python -m backtest.market_research.scalper_probe
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent
import sys

sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.market_research.edge_discovery import _load_dev
from backtest.instruments import get_instrument

SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
SLIP_TOTAL_PIPS = 1.0
TIME_STOP_BARS = 60
GEOMETRIES = [
    ("A-symmetric", 14.0, 14.0),
    ("B-winrate", 8.0, 20.0),
    ("C-trend", 20.0, 8.0),
]
REPORT_PATH = "SCALPER_PROBE_RESULTS.md"


def _simulate(df: pd.DataFrame, pip_price: float, tp_pips: float, sl_pips: float):
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    ts = df["time"].to_numpy()
    spread = (df["spread"].to_numpy(float) * get_instrument(df.attrs.get("symbol", "EURUSD")).point) / pip_price

    n = len(o)
    tp = tp_pips * pip_price
    sl = sl_pips * pip_price
    events: list[dict] = []
    for t in range(n - 1):
        body = c[t] - o[t]
        if not (np.isfinite(body) and body != 0.0):
            continue
        entry_i = t + 1
        if entry_i >= n:
            continue
        entry = o[entry_i]
        if not np.isfinite(entry):
            continue
        d = 1.0 if body > 0 else -1.0
        tp_price = entry + d * tp
        sl_price = entry - d * sl
        exit_i = entry_i
        exit_price = None
        reached = None
        last = min(entry_i + TIME_STOP_BARS, n)
        for i in range(entry_i, last):
            hi, lo_i = h[i], lo[i]
            if not (np.isfinite(hi) and np.isfinite(lo_i)):
                continue
            if d > 0:
                hit_sl = lo_i <= sl_price
                hit_tp = hi >= tp_price
            else:
                hit_sl = hi >= sl_price
                hit_tp = lo_i <= tp_price
            if hit_sl and hit_tp:
                exit_i, exit_price, reached = i, sl_price, "SL"
            elif hit_sl:
                exit_i, exit_price, reached = i, sl_price, "SL"
            elif hit_tp:
                exit_i, exit_price, reached = i, tp_price, "TP"
            else:
                continue
            break
        if exit_price is None:
            exit_i = (entry_i + TIME_STOP_BARS - 1) if (entry_i + TIME_STOP_BARS - 1) < n else n - 1
            exit_price = c[exit_i]
            reached = "time"
        if not (np.isfinite(exit_price) and np.isfinite(spread[entry_i]) and np.isfinite(spread[exit_i])):
            continue
        gross = d * (exit_price - entry) / pip_price
        cost = spread[entry_i] + spread[exit_i] + SLIP_TOTAL_PIPS
        net = gross - cost
        events.append({
            "dir": "BUY" if d > 0 else "SELL",
            "entry_time": str(ts[entry_i]),
            "exit_time": str(ts[exit_i]),
            "exit_reason": reached,
            "gross_pips": float(gross),
            "cost_pips": float(cost),
            "net_pips": float(net),
            "year": pd.Timestamp(ts[entry_i]).year,
        })
    return events


def _summarize(events: list[dict]) -> dict:
    if not events:
        return {"n": 0}
    gross = np.array([e["gross_pips"] for e in events])
    net = np.array([e["net_pips"] for e in events])
    cost = np.array([e["cost_pips"] for e in events])
    wins = net[net > 0]
    losses = net[net <= 0]
    years = {}
    for e in events:
        d = years.setdefault(e["year"], {"n": 0, "net": 0.0})
        d["n"] += 1
        d["net"] += e["net_pips"]
    reasons = {}
    for e in events:
        reasons[e["exit_reason"]] = reasons.get(e["exit_reason"], 0) + 1
    gross_win = float(abs(gross[gross > 0]).sum())
    gross_loss = float(abs(gross[gross < 0]).sum())
    net_win = float(wins.sum())
    net_loss = float(abs(losses.sum()))
    pf = net_win / net_loss if net_loss > 0 else (float("inf") if net_win > 0 else 0.0)
    return {
        "n": len(events),
        "win_rate_net": float((net > 0).mean()),
        "win_rate_raw": float((gross > 0).mean()),
        "avg_win_pips": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss_pips": float(losses.mean()) if len(losses) else 0.0,
        "expectancy_net_pips": float(net.mean()),
        "mean_gross_pips": float(gross.mean()),
        "mean_cost_pips": float(cost.mean()),
        "profit_factor": pf,
        "raw_pf": (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0),
        "total_net_pips": float(net.sum()),
        "hitrate_raw_m2cost": float(gross.mean()) / float(cost.mean()) if float(cost.mean()) > 0 else float("nan"),
        "exit_reasons": reasons,
        "years_positive": sum(1 for d in years.values() if d["net"] > 0),
        "years_total": len(years),
        "years": {str(k): v for k, v in sorted(years.items())},
    }


def main() -> int:
    pcfg = PathConfig()
    results: dict[str, dict] = {}
    for sym in SYMBOLS:
        pips_px = get_instrument(sym).pip
        m5 = _load_dev(sym, pcfg)
        m5.attrs["symbol"] = sym
        results[sym] = {}
        for gid, tp, sl in GEOMETRIES:
            events = _simulate(m5, pips_px, tp, sl)
            results[sym][gid] = {"geometry": {"tp_pips": tp, "sl_pips": sl}, ** _summarize(events)}

    lines: list[str] = []
    A = lines.append
    A("# SCALPER PROBE RESULTS — fixed high-win-rate geometry on DEV (research only)\n")
    A("\nEntry: direction of the closed M5 bar (unbiased); entry at next bar open; intrabar stops, "
      f"SL checked first; time-stop {TIME_STOP_BARS} bars. Cost = entry + exit observed spread + "
      f"{SLIP_TOTAL_PIPS:.1f} pip slippage. DEV rows only, {', '.join(SYMBOLS)}, EURJPY excluded.\n")
    A("\n## Win rate vs expectancy (net, after costs)\n")
    A("\n| symbol | geometry | n | win% | avg_win | avg_loss | exp_net | PF | m2c | years+ |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for sym in SYMBOLS:
        for gid, tp, sl in GEOMETRIES:
            r = results[sym][gid]
            if r["n"] == 0:
                A(f"| {sym} | {gid} | 0 | - | - | - | - | - | - | - |")
                continue
            A(f"| {sym} | {gid} | {r['n']:,} | {r['win_rate_net']*100:.1f} | {r['avg_win_pips']:+.2f} | "
              f"{r['avg_loss_pips']:+.2f} | {r['expectancy_net_pips']:+.3f} | {r['profit_factor']:.3f} | "
              f"{r['hitrate_raw_m2cost']:.3f} | {r['years_positive']}/{r['years_total']} |")

    A("\n## The 60:40 tradeoff\n")
    A("\nA tight TP / wide SL (B-winrate) mechanically raises win% — the question is whether the "
      "win% is high enough to pay for the larger losses plus ~2 pips of spreads+slippage per round trip.\n")
    A("\n| symbol | geometry | win% (raw) | win% (net) | expectancy | years+ |")
    A("|---|---|---|---|---|---|")
    for sym in SYMBOLS:
        for gid, tp, sl in GEOMETRIES:
            r = results[sym][gid]
            if r["n"] == 0:
                continue
            A(f"| {sym} | {gid} | {r['win_rate_raw']*100:.1f} | {r['win_rate_net']*100:.1f} | "
              f"{r['expectancy_net_pips']:+.3f} | {r['years_positive']}/{r['years_total']} |")

    A("\n## Full metrics\n")
    for sym in SYMBOLS:
        for gid, tp, sl in GEOMETRIES:
            A(f"\n### {sym} / {gid} (TP {tp:g} / SL {sl:g})\n")
            r = results[sym][gid]
            A("| metric | value |")
            A("|---|---|")
            for k in ("n", "win_rate_net", "win_rate_raw", "avg_win_pips", "avg_loss_pips",
                      "expectancy_net_pips", "mean_gross_pips", "mean_cost_pips",
                      "profit_factor", "total_net_pips", "hitrate_raw_m2cost", "exit_reasons",
                      "years_positive", "years_total"):
                if r.get(k) is not None:
                    A(f"| {k} | {r[k]} |")
    A("\n")
    out = {"meta": {"data": "dev split of clean Dukascopy M5 composites", "cost_model":
                    "entry+exit observed spread + 1.0 pip slippage", "time_stop_bars": TIME_STOP_BARS,
                    "geometries": GEOMETRIES}, "results": results}
    with open(_root / REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(pcfg.output_dir / "scalper_probe_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Report written to {_root / REPORT_PATH}")
    print(f"Probe dump: {pcfg.output_dir / 'scalper_probe_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())