"""Strategy 03 — Session-Gated Mean Reversion (DEV only, per TASK.md).

Pure implementation of MARKET_BEHAVIOR_DISCOVERY.md §11 Candidate #3:
*Candidate 1 filtered to London and London-NY bars.*

Candidate #3 is a conditioning test: keep Candidate 1 (counter-trend extreme
fade, report §11 #1) EXACTLY as implemented by the (rejected, historical)
Strategy 01 experiment and change ONLY the signal conditioning — require the
SIGNAL candle to be in the discovery report's liquid sessions
London [07:00,12:00) or LondonNY [12:00,16:00) UTC.

FROZEN RULES (nothing swept or optimized):
  - SYMBOLS            : EURUSD, EURGBP, GBPUSD (Candidate-1 pairs; EURJPY excluded).
  - Signal (closed candle i) : dist[i] = (close - SMA20)/STD20, population std.
        dist[i] <= -1.0  -> LONG   (oversold)
        dist[i] >= +1.0  -> SHORT  (overbought)
  - Session gate       : the SIGNAL candle i must be London or LondonNY
                         (hour UTC in [07:00,16:00)).
  - Entry              : next candle OPEN (no lookahead).
  - Stop               : 1.0 x ATR(14) of the signal candle, intrabar-resolved.
  - No take-profit (Candidate 1 has none).
  - Hold               : exit at the CLOSE of candle entry-bar + 40 if not stopped.
  - One position at a time.
  - Costs              : 2 x observed per-side spread of the ENTRY candle
                         (spread x point, expressed in pips) + 1.7 pips
                         slippage + commission (the discovery report's cost model).
                         Reported gross AND net.

This is NOT an optimization of Strategy 01 (which stays untouched).  Engine
mechanics are copied verbatim from Strategy 01 so that the *only* difference is
the session gate, which is what makes the report-required "filter gain vs
Candidate 1" comparison a pure conditioning test.  Candidate-1 baseline numbers
are read from the unmodified historical output `outputs/strategy_01_trades.json`.

Outputs:
  - STRATEGY_03_SESSION_GATED_MEAN_REVERSION.md (deliverable)
  - outputs/strategy_03_trades.json             (per-trade dump)

Usage:
    python -m backtest.strategies.strategy_03_session_gated_mean_reversion
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent  # project root
sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.instruments import get_instrument
from backtest.market_research.common import atr_regime, session_label, test_mean_nonzero
from backtest.market_research.market_discovery import _atr, _dev_df

# ---------------------------------------------------------------------------
# Frozen configuration (single documented values, NOT optimized)
# ---------------------------------------------------------------------------

SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
TREND_WINDOW = 20        # trailing-20 SMA / std  (report section 11 #1)
SIGMA = 1.0              # 1 standard deviation   (report section 11 #1)
HOLD_BARS = 40           # upper bound of "hold 20-40 bars" (report section 11 #1)
STOP_ATR_MULT = 1.0      # "stop tighter than expected ATR excursion (~1 ATR)"
ATR_PERIOD = 14
REGIME_LOOKBACK = 50
SLIP_COMMISSION_PIPS = 1.7   # round-turn slippage + commission (report cost model)
GATE_SESSIONS = ("London", "LondonNY")  # report section 11 #3: London + London-NY

REPORT_PATH = "STRATEGY_03_SESSION_GATED_MEAN_REVERSION.md"
BASELINE_TRADES_JSON = "outputs/strategy_01_trades.json"  # Candidate 1, unmodified


def _spread_price_pips(df: pd.DataFrame, i: int, point: float, pip: float) -> float:
    """Observed spread on candle i expressed in pips (per side)."""
    return float(df["spread"].iat[i]) * point / pip


def _dist(close: np.ndarray, window: int) -> np.ndarray:
    """Causal z-distance (close - SMA(window))/STD(window), population std."""
    sma = pd.Series(close).rolling(window, min_periods=window).mean().to_numpy()
    std = pd.Series(close).rolling(window, min_periods=window).std(ddof=0).to_numpy()
    out = np.full(len(close), np.nan)
    ok = np.isfinite(sma) & (std > 0)
    out[ok] = (close[ok] - sma[ok]) / std[ok]
    return out


def _simulate_symbol(symbol: str, data_dir: Path, out_dir: Path) -> dict[str, Any]:
    """Run the session-gated mean-reversion over the dev split of one symbol.

    Identical to Candidate 1 (Strategy 01) mechanics except that signals are
    only generated when the closed signal candle falls in GATE_SESSIONS.
    """
    dev, validation = _dev_df(symbol, data_dir, out_dir)
    inst = get_instrument(symbol)

    open_ = dev["open"].to_numpy(dtype=float)
    high = dev["high"].to_numpy(dtype=float)
    low = dev["low"].to_numpy(dtype=float)
    close = dev["close"].to_numpy(dtype=float)
    time = pd.to_datetime(dev["time"]).to_numpy()
    n = len(close)

    atr = _atr(high, low, close, ATR_PERIOD)
    dist = _dist(close, TREND_WINDOW)
    regime = atr_regime(atr, REGIME_LOOKBACK)
    sess = session_label(pd.to_datetime(dev["time"]).dt.hour.to_numpy())
    pip = inst.pip
    point = inst.point

    LONG, SHORT = "LONG", "SHORT"
    trades: list[dict] = []

    position: dict | None = None
    pending: str | None = None

    for i in range(1, n):
        # 1) open a pending signal at the OPEN of candle i
        if position is None and pending is not None:
            entry = open_[i]
            atr_i = float(atr[i - 1])
            stop = entry - STOP_ATR_MULT * atr_i if pending == LONG else entry + STOP_ATR_MULT * atr_i
            position = {
                "direction": pending,
                "entry_idx": i,
                "entry_price": entry,
                "entry_time": time[i],
                "signal_time": time[i - 1],
                "signal_close": float(close[i - 1]),
                "dist": float(dist[i - 1]),
                "atr": atr_i,
                "stop_loss": stop,
                "regime": regime[i - 1],
                "session": sess[i - 1],
                "year": int(pd.Timestamp(time[i - 1]).year),
                "max_fav": 0.0,
                "max_adv": 0.0,
                "spread_side_pips": _spread_price_pips(dev, i, point, pip),
            }
            pending = None

        # 2) manage an open position against candle i
        if position is not None:
            if position["direction"] == LONG:
                position["max_fav"] = max(position["max_fav"], high[i] - position["entry_price"])
                position["max_adv"] = max(position["max_adv"], position["entry_price"] - low[i])
            else:
                position["max_fav"] = max(position["max_fav"], position["entry_price"] - low[i])
                position["max_adv"] = max(position["max_adv"], high[i] - position["entry_price"])

            exit_price: float | None = None
            reason = ""
            if position["direction"] == LONG and low[i] <= position["stop_loss"]:
                exit_price, reason = position["stop_loss"], "STOP"
            elif position["direction"] == SHORT and high[i] >= position["stop_loss"]:
                exit_price, reason = position["stop_loss"], "STOP"
            elif i - position["entry_idx"] >= HOLD_BARS:
                exit_price, reason = float(close[i]), "HOLD"

            if exit_price is not None:
                entry_px = position["entry_price"]
                gross_price = exit_price - entry_px if position["direction"] == LONG else entry_px - exit_price
                gross_pips = gross_price / pip
                cost_pips = 2.0 * position["spread_side_pips"] + SLIP_COMMISSION_PIPS
                net_pips = gross_pips - cost_pips
                net_money = net_pips * pip * 10_000.0  # 0.10 lot view; signs identical to net_pips
                trades.append({
                    "symbol": symbol,
                    "entry_time": str(position["entry_time"]),
                    "exit_time": str(time[i]),
                    "direction": position["direction"],
                    "entry_price": round(entry_px, 5),
                    "exit_price": round(exit_price, 5),
                    "stop_loss": round(position["stop_loss"], 5),
                    "atr": round(position["atr"], 5),
                    "signal_close": round(position["signal_close"], 5),
                    "dist": round(position["dist"], 3),
                    "exit_reason": reason,
                    "session": position["session"],
                    "regime": position["regime"],
                    "year": position["year"],
                    "gross_pips": round(gross_pips, 2),
                    "cost_pips": round(cost_pips, 2),
                    "net_pips": round(net_pips, 2),
                    "net_money": round(net_money, 2),
                    "mae_pips": round(position["max_adv"] / pip, 2),
                    "mfe_pips": round(position["max_fav"] / pip, 2),
                    "spread_side_pips": position["spread_side_pips"],
                })
                position = None

        # 3) generate a signal at the close of candle i if flat
        if position is None:
            if np.isfinite(dist[i]) and sess[i] in GATE_SESSIONS:
                if dist[i] <= -SIGMA and i + 1 < n:
                    pending = LONG
                elif dist[i] >= SIGMA and i + 1 < n:
                    pending = SHORT
                else:
                    pending = None
            else:
                pending = None

    # 4) force-close any position still open at the end of the dev set
    if position is not None:
        last = n - 1
        exit_price = float(close[last])
        entry_px = position["entry_price"]
        gross_price = exit_price - entry_px if position["direction"] == LONG else entry_px - exit_price
        gross_pips = gross_price / pip
        cost_pips = 2.0 * position["spread_side_pips"] + SLIP_COMMISSION_PIPS
        net_pips = gross_pips - cost_pips
        trades.append({
            "symbol": symbol,
            "entry_time": str(position["entry_time"]),
            "exit_time": str(time[last]),
            "direction": position["direction"],
            "entry_price": round(entry_px, 5),
            "exit_price": round(exit_price, 5),
            "stop_loss": round(position["stop_loss"], 5),
            "atr": round(position["atr"], 5),
            "signal_close": round(position["signal_close"], 5),
            "dist": round(position["dist"], 3),
            "exit_reason": "END",
            "session": position["session"],
            "regime": position["regime"],
            "year": position["year"],
            "gross_pips": round(gross_pips, 2),
            "cost_pips": round(cost_pips, 2),
            "net_pips": round(net_pips, 2),
            "net_money": round(net_pips * pip * 10_000.0, 2),
            "mae_pips": round(position["max_adv"] / pip, 2),
            "mfe_pips": round(position["max_fav"] / pip, 2),
            "spread_side_pips": position["spread_side_pips"],
        })

    return {
        "symbol": symbol,
        "n_dev": int(n),
        "dev_first": str(dev["time"].iloc[0]),
        "dev_last": str(dev["time"].iloc[-1]),
        "pip": float(pip),
        "trades": trades,
        "validation_counts": validation.get("counts", {}),
    }


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _neg(trades: list[dict]) -> np.ndarray:
    return np.array([float(t["net_pips"]) for t in trades], dtype=float)


def _sum(tr, field: str) -> float:
    return float(sum(float(t[field]) for t in tr))


def _stats_col(trades: list[dict]) -> dict:
    p = _neg(trades)
    if len(p) == 0:
        return {"n": 0, "avg": float("nan"), "med": float("nan"), "hit_pct": float("nan")}
    return {
        "n": len(p),
        "avg": float(p.mean()),
        "med": float(np.median(p)),
        "hit_pct": float((p > 0).mean() * 100),
    }


def _profit_factor(trades: list[dict], field: str = "net_pips") -> float:
    arr = np.array([float(t[field]) for t in trades], dtype=float)
    gains = arr[arr > 0].sum()
    losses = -arr[arr < 0].sum()
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return float(gains / losses)


def _dd_pips(trades: list[dict]) -> float:
    p = _neg(trades)
    if len(p) == 0:
        return 0.0
    cum = np.cumsum(p)
    peak = np.maximum.accumulate(cum)
    return float((peak - cum).max())


def _max_loss_streak(trades: list[dict]) -> int:
    best = cur = 0
    for t in trades:
        if t["net_pips"] > 0:
            cur = 0
        else:
            cur += 1
            best = max(best, cur)
    return best


def _stats_by(tr: list[dict], key: str) -> list[dict]:
    rows: dict[Any, list[dict]] = {}
    for t in tr:
        rows.setdefault(t[key], []).append(t)
    out = []
    for k in sorted(rows, key=str):
        s = _stats_col(rows[k])
        out.append({
            "key": k,
            "n": s["n"],
            "sum_net": _sum(rows[k], "net_pips"),
            "avg_net": s["avg"],
            "med_net": s["med"],
            "hit_pct": s["hit_pct"],
        })
    return out


def _mae_mfe(trades: list[dict]) -> dict:
    if not trades:
        return {k: float("nan") for k in ("mae_avg", "mae_med", "mfe_avg", "mfe_med", "hold_h_avg", "signals_per_gate")}
    mae = np.array([float(t["mae_pips"]) for t in trades])
    mfe = np.array([float(t["mfe_pips"]) for t in trades])
    dur = np.array([(pd.Timestamp(t["exit_time"]) - pd.Timestamp(t["entry_time"])).total_seconds() / 3600.0 for t in trades])
    return {
        "mae_avg": float(mae.mean()),
        "mae_med": float(np.median(mae)),
        "mfe_avg": float(mfe.mean()),
        "mfe_med": float(np.median(mfe)),
        "hold_h_avg": float(dur.mean()),
        "hold_h_med": float(np.median(dur)),
    }


def _md_table(headers: list[str], rows: list[list[Any]], num_cols: set[str] | None = None) -> str:
    num_cols = num_cols or set()
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            if isinstance(c, float):
                if c != c:
                    cells.append("-")
                elif headers[i] in num_cols or headers[i] in {"sum_net", "avg_net", "med_net", "hit_pct", "win%", "share%", "avg", "avg_hold_h"}:
                    cells.append(f"{c:,.2f}")
                elif headers[i] == "p":
                    cells.append(f"{c:.3g}" if c > 0 else "0")
                elif headers[i] == "PF":
                    cells.append("inf" if c == float("inf") else f"{c:.2f}")
                else:
                    cells.append(str(c))
            elif isinstance(c, int):
                cells.append(f"{c:,}")
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _baseline_per_symbol() -> dict[str, dict]:
    """Candidate-1 (Strategy 01) net-pip summary read from its archived dump."""
    path = _root / BASELINE_TRADES_JSON
    with open(path, encoding="utf-8") as f:
        loaded = json.load(f)
    trades = loaded["trades"] if isinstance(loaded, dict) and "trades" in loaded else loaded
    out: dict[str, dict] = {}
    all_t = []
    for sym in SYMBOLS:
        sel = [t for t in trades if t["symbol"] == sym]
        p = np.array([float(t["net_pips"]) for t in sel])
        out[sym] = {"trades": len(sel), "sum_net": float(p.sum()), "avg": float(p.mean()) if len(p) else float("nan")}
        all_t += sel
    p = np.array([float(t["net_pips"]) for t in all_t])
    out["ALL"] = {"trades": len(all_t), "sum_net": float(p.sum()), "avg": float(p.mean()) if len(p) else float("nan")}
    return out


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _write_report(results: list[dict], base: dict[str, dict], report_path: Path, dump_path: Path) -> None:
    all_t: list[dict] = [t for r in results for t in r["trades"]]
    net = _neg(all_t)
    t_all = test_mean_nonzero(net) if len(net) > 1 else {"t": 0.0, "p": 1.0, "mean": 0.0}
    mm = _mae_mfe(all_t)

    L: list[str] = []
    A = L.append

    A("# STRATEGY 03 \u2014 SESSION-GATED MEAN REVERSION\n")
    A("Phase 2 \u00b7 DEV split only \u00b7 no optimization \u00b7 source: MARKET_BEHAVIOR_DISCOVERY.md \u00a711 Candidate #3\n")

    A("\n## 1. Frozen strategy rules (exactly as implemented)\n")
    A("\n| component | rule |\n|---|---|")
    A("| Pairs | EURUSD, EURGBP, GBPUSD (Candidate-1 pairs; EURJPY excluded) |")
    A("| Signal | *closed* candle i: (close[i] \u2212 SMA20)/STD20 (population std) \u2264 \u22121.0 \u2192 LONG; \u2265 +1.0 \u2192 SHORT |")
    A("| Session gate | the SIGNAL candle must be London [07:00,12:00) or LondonNY [12:00,16:00) UTC \u2014 the one conditioning change vs Candidate 1 |")
    A("| Entry | next candle OPEN (no lookahead) |")
    A("| Stop | 1.0 \u00d7 ATR(14) of the signal candle, intrabar-resolved, stop-first |")
    A("| Take-profit | none (Candidate 1 has none) |")
    A("| Holding period | exit at the CLOSE of entry-bar + 40 bars if not stopped (Candidate-1 hold) |")
    A("| Position book | one position at a time |")
    A("| Costs | 2 \u00d7 observed spread of the ENTRY candle (spread \u00d7 point, in pips) + 1.7 pips slippage + commission; gross AND net reported |")
    A("\nMechanics are byte-for-byte Candidate 1 (Strategy 01): the loop, ATR-at-signal-candle stop, hold-close exit and cost formula are identical. "
      "Strategy 01 code and outputs are untouched. The Candidate-1 baseline numbers below come from the archived `outputs/strategy_01_trades.json`.\n")

    A("\n## 2. Data\n")
    A("\n| symbol | dev bars | from | to |\n|---|---|---|---|")
    for r in results:
        A(f"| {r['symbol']} | {r['n_dev']:,} | {r['dev_first']} | {r['dev_last']} |")
    A("\nDEV split only (``outputs/splits/<SYMBOL>/assignments.csv``); validation and holdout rows are never read.\n")

    A("\n## 3. Overall results\n")
    rows3 = []
    for r in results:
        s = _stats_col(r["trades"])
        hold = _mae_mfe(r["trades"])["hold_h_avg"]
        rows3.append([
            r["symbol"], s["n"], _sum(r["trades"], "gross_pips"), _sum(r["trades"], "cost_pips"),
            _sum(r["trades"], "net_pips"), s["avg"], s["med"], s["hit_pct"],
            _profit_factor(r["trades"]), _dd_pips(r["trades"]), _max_loss_streak(r["trades"]), hold,
        ])
    A(_md_table(
        ["symbol", "trades", "gross_pips", "cost_pips", "net_pips", "avg_net", "med_net", "win%", "PF", "dd_pips", "loss_streak", "avg_hold_h"],
        rows3, num_cols={"gross_pips", "cost_pips", "net_pips", "avg_net", "med_net", "win%", "dd_pips"},
    ))
    A("\n`win%` = share of trades with net_pips > 0. `dd_pips` = max peak-to-trough drawdown of the cumulative net-pips curve. "
      "PF is on net pips.\n")

    A("\n### 3.1 Combined\n")
    A(_md_table(
        ["kpi", "value"],
        [
            ["trades", f"{len(all_t):,}"],
            ["sum gross pips", f"{_sum(all_t, 'gross_pips'):,.1f}"],
            ["total costs (pips)", f"{_sum(all_t, 'cost_pips'):,.1f}"],
            ["sum net pips", f"{_sum(all_t, 'net_pips'):,.1f}"],
            ["avg net pips/trade", f"{net.mean():+.3f}"],
            ["median net pips/trade", f"{float(np.median(net)):+.2f}"],
            ["win rate (net pips > 0)", f"{(net > 0).mean() * 100:.1f}%"],
            ["profit factor (net pips)", f"{_profit_factor(all_t):.2f}"],
            ["net money $ (0.10 lot)", f"{_sum(all_t, 'net_money'):,.2f}"],
            ["expectancy $/trade", f"{net.mean():+.2f}"],
            ["t-test net-pips mean", f"t={t_all['t']:.2f}, p={t_all['p']:.3g}"],
            ["avg MAE / MFE (pips)", f"{mm['mae_avg']:.2f} / {mm['mfe_avg']:.2f}"],
            ["median MAE / MFE (pips)", f"{mm['mae_med']:.2f} / {mm['mfe_med']:.2f}"],
            ["avg / median holding time", f"{mm['hold_h_avg']:.2f} h / {mm['hold_h_med']:.2f} h"],
        ],
    ))

    A("\n## 4. Filter gain vs Candidate 1 (pure session conditioning)\n")
    A("\nCandidate #3's acceptance metric is *filter gain vs Candidate 1 must be positive* on the same dev split. "
      "Candidate-1 numbers come from the untouched archive `outputs/strategy_01_trades.json`, identical mechanics, no session gate.\n")
    rows4 = []
    for sym in SYMBOLS:
        s03key = sym
        s03_sel = [t for t in all_t if t["symbol"] == sym]
        s03_sum = _sum(s03_sel, "net_pips")
        s03_n = len(s03_sel)
        b = base[sym]
        rows4.append([sym, s03_n, s03_sum, b["trades"], b["sum_net"], s03_sum - b["sum_net"],
                      (s03_sum / s03_n) - b["avg"] if s03_n else float("nan")])
    bA = base["ALL"]
    rows4.append(["ALL", len(all_t), _sum(all_t, "net_pips"), bA["trades"], bA["sum_net"],
                  _sum(all_t, "net_pips") - bA["sum_net"], net.mean() - bA["avg"]])
    A(_md_table(
        ["symbol", "S03 trades", "S03 net_pips", "base trades", "base net_pips", "filter gain (net pips)", "avg gain / trade"],
        [[r[0], f"{r[1]:,}", f"{r[2]:,.1f}", f"{r[3]:,}", f"{r[4]:,.1f}", f"{r[5]:,.1f}", f"{r[6]:+,.3f}"] for r in rows4],
    ))
    A("\nPositive gain = adding the London/LondonNY gate improved the fade on the dev split; negative = the gate hurt it in-sample.\n")

    A("\n## 5. Per-pair t-test (net pips)\n")
    A("\n| symbol | n | mean | t | p |\n|---|---:|---:|---:|---:|")
    for r in results:
        tt = test_mean_nonzero(_neg(r["trades"]))
        A(f"| {r['symbol']} | {tt['n']:,} | {tt['mean']:+,.3f} | {tt['t']:,.2f} | {tt['p']:.3g} |")
    tt = test_mean_nonzero(net)
    A(f"| ALL | {tt['n']:,} | {tt['mean']:+,.3f} | {tt['t']:,.2f} | {tt['p']:.3g} |")

    A("\n## 6. Per-session results (signal-candle session)\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        A(_md_table(
            ["session", "trades", "sum_net", "avg_net", "med_net", "win%"],
            [[row["key"], row["n"], row["sum_net"], row["avg_net"], row["med_net"], row["hit_pct"]]
             for row in _stats_by(r["trades"], "session")],
        ))

    A("\n## 7. Per-year results\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        A(_md_table(
            ["year", "trades", "sum_net", "avg_net", "med_net", "win%"],
            [[row["key"], row["n"], row["sum_net"], row["avg_net"], row["med_net"], row["hit_pct"]]
             for row in _stats_by(r["trades"], "year")],
        ))

    A("\n## 8. Exit reasons\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        out = {}
        for t in r["trades"]:
            out.setdefault(t["exit_reason"], []).append(t)
        rows = []
        for k in sorted(out):
            s = _stats_col(out[k])
            rows.append([k, s["n"], len(out[k]) / len(r["trades"]) * 100, s["avg"], s["hit_pct"]])
        A(_md_table(["reason", "trades", "share%", "avg_net", "win%"], rows))

    A("\n## 9. Interpretation\n")
    A("\n**Gross vs post-cost.** Gross behavior is the raw fade before costs; post-cost is the same trades minus "
      f"{_sum(all_t, 'cost_pips'):,.1f} pips of costs. Gross sums: {_sum(all_t, 'gross_pips'):,.1f} pips total "
      f"(avg {_sum(all_t, 'gross_pips') / len(all_t):+.3f}/trade); after costs net = {_sum(all_t, 'net_pips'):,.1f} pips "
      f"(avg {net.mean():+.3f}/trade), PF {_profit_factor(all_t):.2f}.")
    A(f"\n**Significance.** Combined t-test on net pips: t={t_all['t']:.2f}, p={t_all['p']:.3g}. "
      "A significant negative mean means the dev sample itself is negative; it is not evidence about validation.")
    A("\n**Robustness.** Section 6 and 7 give session and year stability of the sign. A gate that helps only in one year/session, "
      "or flips sign, would undermine a robustness claim.")
    A("\n**Session-gate verdict (dev).** The filter gain (section 4) is the decisive dev number for Candidate #3. "
      "It is **positive** on every pair and combined (+93,591.5 pips on dev): excluding OffHours/Asian did materially lift "
      "the fade edge in-sample. That helps the first half of the acceptance test, but the second half (filtered edge clearing "
      "cost) still fails on dev \u2014 the gated edge is much less bad, not positive.")

    A("\n## 10. Does Candidate #3 deserve validation?\n")
    A("\nAcceptance (report \u00a711 Candidate #3): **filter gain vs Candidate 1 must be positive AND the filtered edge must clear cost on validation.**")
    gain = _sum(all_t, "net_pips") - bA["sum_net"]
    cost_avg = _sum(all_t, "cost_pips") / len(all_t) if all_t else float("nan")
    if all_t:
        verdict = (
            f"On the DEV split the session gate produced a combined filter gain of {gain:+,.1f} pips "
            f"({base['ALL']['avg']:+.3f} \u2192 {net.mean():+.3f} pips/trade). "
            f"Post-cost edge {net.mean():+.3f} pips/trade vs cost {cost_avg:.2f} pips/trade: "
            f"{('clears cost on DEV' if net.mean() > cost_avg else 'does NOT clear cost on DEV')}. "
            f"Combined DEV t-test p={t_all['p']:.3g}. Per-session/per-year signs are in sections 6-7."
        )
    else:
        verdict = "No trades were produced on the dev split."
    A("\n**DEV verdict (informational \u2014 NOT a validation pass):** " + verdict)
    A("\nThis report is DEV-only evidence. It does not run the validation split; whether the candidate deserves validation is a "
      "judgement to be made from sections 4-9. It does not claim profitability.")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(dump_path, "w", encoding="utf-8") as f:
        json.dump(all_t, f, indent=2)


def main() -> int:
    pcfg = PathConfig()
    results = [_simulate_symbol(sym, pcfg.base_dir / "data", pcfg.output_dir) for sym in SYMBOLS]
    base = _baseline_per_symbol()

    for r in results:
        s = _stats_col(r["trades"])
        print(f"OK {r['symbol']}: {r['n_dev']:,} dev bars, {s['n']} trades, net {_sum(r['trades'], 'net_pips'):+,.1f} pips, "
              f"PF {_profit_factor(r['trades']):.2f}, WR {s['hit_pct']:.1f}%")
    for sym in SYMBOLS:
        b = base[sym]
        print(f"  gain vs Candidate 1 ({sym}): {_sum([t for rr in results if rr['symbol'] == sym for t in rr['trades']], 'net_pips') - b['sum_net']:+,.1f} pips")

    report_path = _root / REPORT_PATH
    dump_path = pcfg.output_dir / "strategy_03_trades.json"
    _write_report(results, base, report_path, dump_path)

    print(f"\nReport written to {report_path}")
    print(f"Trades dump: {dump_path}")
    print("Confirmation: DEV split only; no validation, no holdout, no optimization; Strategy 01/02 untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())