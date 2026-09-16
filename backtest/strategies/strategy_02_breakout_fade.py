"""Strategy 02 — Breakout Fade (DEV only, per TASK.md).

Tests whether failed short-term breakouts tend to reverse during liquid
sessions.  Pure implementation of MARKET_BEHAVIOR_DISCOVERY.md §11
Candidate #2 (EURGBP/GBPUSD, London + London-NY).

FROZEN RULES (nothing here is swept or optimized):
  - SYMBOLS            : EURGBP, GBPUSD only (EURJPY excluded per TASK.md).
  - Signal bar         : a *closed* candle i whose close pierces the prior-20
                         bar high/low (causal: window excludes bar i, identical
                         to the discovery report's ``_breakout_states``).
      close[i] > max(high[i-20 .. i-1])  -> upside breakout -> FADE = SELL
      close[i] < min(low[i-20 .. i-1])   -> downside breakout -> FADE = BUY
  - Session gate       : the SIGNAL candle must be in the discovery report's
                         liquid sessions London [07:00,12:00) UTC or
                         LondonNY [12:00,16:00) UTC  (hour in [7,16) UTC).
  - Entry              : next candle OPEN (no lookahead, standard engine fill).
  - Stop               : 1.5 x ATR(14) from entry (existing backtester's fixed
                         StrategyConfig default; not invented, not tuned).
  - Target             : 3.0 x ATR(14) from entry (existing backtester default).
  - Holding period     : see [1,1]  ->  exit at the CLOSE of the candle
                         entry-bar + 20 (max_hold_bars=20, the discovery
                         headline horizon H=20), unless SL/TP was hit first
                         (conservative: stop is resolved before the horizon).
  - One position at a time (engine default).
  - Costs              : engine CostConfig defaults — observed spread of the
                         ENTRY candle (x1, point-scaled) + 0.5 pip slippage per
                         side + $7/lot commission at 0.10 lots.

The only engine change required to express the candidate exactly was adding an
optional fixed-horizon exit (``max_hold_bars``) to ``run_backtest``.  The
backtester itself was not redesigned.

Outputs:
  - STRATEGY_02_BREAKOUT_FADE.md   (human-readable report, the deliverable)
  - outputs/strategy_02_trades.json (per-trade dump)

Usage:
    python -m backtest.strategies.strategy_02_breakout_fade
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

from backtest.backtester import run_backtest, Trade
from backtest.config import CostConfig, PathConfig, StrategyConfig
from backtest.indicators import add_indicators
from backtest.market_research.common import session_label, test_mean_nonzero
from backtest.metrics import compute_metrics

# ---------------------------------------------------------------------------
# Frozen parameters
# ---------------------------------------------------------------------------

SYMBOLS = ["EURGBP", "GBPUSD"]
LOOKBACK = 20          # breakout channel = previous 20 candles (prior-20 high/low)
HOLD_BARS = 20         # discovery headline horizon H=20 -> max_hold_bars exit
SESSION_MIN_HOUR = 7   # London 07-12 UTC
SESSION_MAX_HOUR = 16  # LondonNY 12-16 UTC
SPLIT = "dev"          # DEV ONLY, per TASK.md

REPORT_NAME = "STRATEGY_02_BREAKOUT_FADE.md"


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Append the causal breakout bands used by the signal (prior-20 high/low)."""
    out = df.copy()
    out["s02_prior_high"] = out["high"].shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    out["s02_prior_low"] = out["low"].shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    return out


def signal_at(df: pd.DataFrame, i: int, cfg: StrategyConfig) -> str | None:
    """Fade the breakout: SELL after an upside close-break, BUY after a downside one.

    Only evaluated when the backtester is flat; returns on *closed* candle i,
    entry fills at the open of candle i+1.  Session gate applies to candle i.
    """
    ph = df["s02_prior_high"].iat[i]
    pl = df["s02_prior_low"].iat[i]
    if pd.isna(ph) or pd.isna(pl):
        return None
    hour = int(pd.Timestamp(df["time"].iat[i]).hour)
    if not (SESSION_MIN_HOUR <= hour < SESSION_MAX_HOUR):
        return None
    close = float(df["close"].iat[i])
    if close > float(ph):
        return "SELL"
    if close < float(pl):
        return "BUY"
    return None


# ---------------------------------------------------------------------------
# Data loading (DEV split only — validation/holdout are never read)
# ---------------------------------------------------------------------------

def _load_dev(pcfg: PathConfig, symbol: str) -> pd.DataFrame:
    sym = symbol.lower()
    csv_path = pcfg.base_dir / "data" / f"{sym}_m5.csv"
    assignments_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Prices not found: {csv_path}")
    if not assignments_path.exists():
        raise FileNotFoundError(f"Split assignments not found: {assignments_path}")

    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])

    assignments = pd.read_csv(assignments_path)
    mask = assignments["split"] == SPLIT
    dev_indices = assignments.index[mask].tolist()
    if not dev_indices:
        raise RuntimeError(f"Empty {SPLIT} split for {symbol}")
    return df.iloc[dev_indices].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _net_pips(trades: list[Trade]) -> np.ndarray:
    return np.array([t.net_pips for t in trades], dtype=float)


def _session_stats(trades: list[Trade]) -> pd.DataFrame:
    rows = []
    for s in ["Asian", "London", "LondonNY", "NewYork", "OffHours"]:
        sel = [t for t in trades if session_label(np.array([pd.Timestamp(t.entry_time).hour]))[0] == s]
        if not sel:
            continue
        p = _net_pips(sel)
        rows.append(
            {
                "session": s,
                "trades": len(sel),
                "sum_net": p.sum(),
                "avg_net": p.mean(),
                "med_net": float(np.median(p)),
                "win%": float((p > 0).mean() * 100),
            }
        )
    return pd.DataFrame(rows)


def _year_stats(trades: list[Trade]) -> pd.DataFrame:
    rows = []
    for year in sorted({pd.Timestamp(t.entry_time).year for t in trades}):
        sel = [t for t in trades if pd.Timestamp(t.entry_time).year == year]
        p = _net_pips(sel)
        rows.append(
            {
                "year": year,
                "trades": len(sel),
                "sum_net": p.sum(),
                "avg_net": p.mean(),
                "med_net": float(np.median(p)),
                "win%": float((p > 0).mean() * 100),
            }
        )
    return pd.DataFrame(rows)


def _exit_stats(trades: list[Trade]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for reason in sorted({t.exit_reason for t in trades}):
        sel = [t for t in trades if t.exit_reason == reason]
        p = _net_pips(sel)
        out[reason] = {
            "trades": len(sel),
            "share_pct": len(sel) / len(trades) * 100,
            "avg_net": float(p.mean()) if len(p) else float("nan"),
            "win%": float((p > 0).mean() * 100),
        }
    return out


def _mae_mfe(trades: list[Trade]) -> dict[str, float]:
    mae = np.array([t.mae_pips for t in trades])
    mfe = np.array([t.mfe_pips for t in trades])
    hours = np.array([(pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)).total_seconds() / 3600.0 for t in trades])
    return {
        "mae_avg": float(mae.mean()),
        "mae_med": float(np.median(mae)),
        "mfe_avg": float(mfe.mean()),
        "mfe_med": float(np.median(mfe)),
        "hold_h_avg": float(hours.mean()),
        "hold_h_med": float(np.median(hours)),
    }


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    num_cols = {
        "sum_net", "avg_net", "med_net", "win%", "share_pct", "avg", "med",
    }
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            if isinstance(c, (float, np.floating)):
                if c != c:
                    cells.append("-")
                elif headers[i] in num_cols:
                    cells.append(f"{c:,.2f}")
                elif headers[i] in ("p", "t_p"):
                    cells.append(f"{c:.3g}" if c > 0 else "0")
                elif headers[i] == "PF":
                    cells.append("inf" if c == float("inf") else f"{c:.2f}")
                else:
                    cells.append(f"{c:,.3g}")
            elif isinstance(c, (int, np.integer)):
                cells.append(f"{int(c):,}")
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-symbol run
# ---------------------------------------------------------------------------

def _run_symbol(symbol: str, pcfg: PathConfig, s_cfg: StrategyConfig, c_cfg: CostConfig) -> dict[str, Any]:
    df = _load_dev(pcfg, symbol)
    df = _ensure_columns(df)
    df = add_indicators(df, s_cfg)

    trades, equity = run_backtest(df, s_cfg, c_cfg, signal_fn=signal_at, max_hold_bars=HOLD_BARS)
    metrics = compute_metrics(trades, equity, c_cfg.starting_balance)
    return {
        "symbol": symbol,
        "n_bars": len(df),
        "t_start": str(df["time"].iat[0]),
        "t_end": str(df["time"].iat[-1]),
        "trades": trades,
        "metrics": metrics,
        "session": _session_stats(trades),
        "years": _year_stats(trades),
        "exit_reasons": _exit_stats(trades),
        "mae_mfe": _mae_mfe(trades),
        "ttest": test_mean_nonzero(_net_pips(trades)),
    }


def _pair_row(s: dict[str, Any]) -> list[Any]:
    m = s["metrics"]
    med = float(np.median(_net_pips(s["trades"])))
    return [
        s["symbol"],
        f"{s['n_bars']:,}",
        f"{m['total_trades']:,}",
        f"{m['gross_profit']:,.2f}",
        f"{m['gross_loss']:,.2f}",
        f"{m['net_profit']:,.2f}",
        f"{m['expectancy_pips']:,.2f}",
        f"{med:,.2f}",
        f"{m['win_rate'] * 100:.1f}",
        f"{m['profit_factor']:.2f}",
        f"{m['max_drawdown']:,.2f}",
        f"{m['longest_losing_streak']}",
        f"{s['mae_mfe']['hold_h_avg']:.2f}",
    ]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _all_trades(results: list[dict[str, Any]]) -> list[Trade]:
    return [t for r in results for t in r["trades"]]


def _write_report(results: list[dict[str, Any]], out_path: Path, trades_path: Path) -> None:
    all_t = _all_trades(results)
    mon = np.array([t.net_money for t in all_t], dtype=float)
    gross_mon = np.array([t.gross_money for t in all_t], dtype=float)
    cost_mon = gross_mon - mon
    gross_pips = np.array([t.gross_pips for t in all_t])
    cost_pips = np.array([t.cost_pips for t in all_t])
    net_pips = _net_pips(all_t)
    all_pf = float((net_pips[net_pips > 0].sum()) / abs(net_pips[net_pips < 0].sum())) if (net_pips < 0).any() else float("inf")
    med_all = float(np.median(net_pips))
    t_all = test_mean_nonzero(net_pips)
    mae_mfe_all = _mae_mfe(all_t)

    L: list[str] = []
    A = L.append
    A("# STRATEGY 02 \u2014 BREAKOUT FADE\n")
    A("Phase 2 \u00b7 DEV split only \u00b7 no optimization \u00b7 source: MARKET_BEHAVIOR_DISCOVERY.md \u00a711 Candidate #2\n")
    A("\n## 1. Frozen strategy rules (exactly as implemented)\n")
    A("\n| component | rule |\n|---|---|")
    A("| Pairs | EURGBP, GBPUSD (EURJPY excluded per TASK.md) |")
    A("| Signal (breakout) | *closed* candle i: `close[i] > max(high[i-20..i-1])` \u2192 upside breakout; `close[i] < min(low[i-20..i-1])` \u2192 downside breakout (causal prior-20 channel, identical to discovery `_breakout_states`) |")
    A("| Trade (fade) | SELL after an upside breakout, BUY after a downside breakout |")
    A("| Session gate | signal candle hour UTC \u2208 [07:00, 16:00) = London [7,12) \u222a LondonNY [12,16) \u2014 the discovery report's liquid-session condition |")
    A("| Entry | next candle OPEN (no lookahead) |")
    A("| Stop | 1.5 \u00d7 ATR(14) from entry, invalidation of the fade \u2014 existing backtester's fixed StrategyConfig default (not invented, not tuned) |")
    A("| Target | 3.0 \u00d7 ATR(14) \u2014 existing backtester default |")
    A("| Holding period | exit at close of entry-bar + 20 (max_hold_bars=20, discovery headline horizon H=20); SL/TP resolved first, conservatively |")
    A("| Position book | one position at a time (engine default); re-entry allowed on the next bar after an exit |")
    A("| Costs | observed spread of the ENTRY candle (\u00d71, point-scaled) + 0.5 pip slippage per side + $7/lot commission at 0.10 lots |")
    A("\nOnly implementation detail the discovery report left unspecified \u2014 the fixed-horizon exit \u2014 "
      "was expressed with the **minimal** additive engine extension `max_hold_bars` in `run_backtest` "
      "(existing callers unaffected). The backtester was not redesigned.\n")

    A("\n## 2. Data\n")
    A("\n| symbol | dev bars | from | to |\n|---|---|---|---|")
    for r in results:
        A(f"| {r['symbol']} | {r['n_bars']:,} | {r['t_start']} | {r['t_end']} |")
    A(f"\nDEV split only (split column = `{SPLIT}`); validation and holdout rows are never read.\n")

    A("\n## 3. Overall results\n")
    A("\n| symbol | bars | trades | gross$ | gross_l$ | net$ | avg_net_pips | med_net_pips | win% | PF | maxDD$ | loss_streak | avg_hold_h |")
    A("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in results:
        A("| " + " | ".join(str(x) for x in _pair_row(r)) + " |")
    A("\nGross$ / gross_l$ / net$ and maxDD$ are USD at 0.10 lots. `win%` = share of trades with net_pips > 0. "
      "`loss_streak` = longest consecutive losing trades. `avg_hold_h` = mean holding time in hours.\n")

    A("\n### 3.1 All pairs combined\n")
    A(_md_table(
        ["kpi", "value"],
        [
            ["trades", f"{len(all_t):,}"],
            ["sum gross pips", f"{gross_pips.sum():,.1f}"],
            ["total costs (pips)", f"{cost_pips.sum():,.1f}"],
            ["sum net pips", f"{net_pips.sum():,.1f}"],
            ["avg net pips/trade", f"{net_pips.mean():+.3f}"],
            ["median net pips/trade", f"{med_all:+.2f}"],
            ["win rate (net pips > 0)", f"{(net_pips > 0).mean() * 100:.1f}%"],
            ["profit factor (net pips)", f"{all_pf:.2f}"],
            ["gross profit $ (winners)", f"{gross_mon[gross_mon > 0].sum():,.2f}"],
            ["gross loss $ (losers)", f"{gross_mon[gross_mon < 0].sum():,.2f}"],
            ["total costs $", f"{cost_mon.sum():,.2f}"],
            ["net profit $", f"{mon.sum():,.2f}"],
            ["expectancy $/trade", f"{mon.mean():+,.2f}"],
            ["t-test net-pips mean", f"t={t_all['t']:.2f}, p={t_all['p']:.3g}"],
            ["avg MAE / MFE (pips)", f"{mae_mfe_all['mae_avg']:.2f} / {mae_mfe_all['mfe_avg']:.2f}"],
            ["median MAE / MFE (pips)", f"{mae_mfe_all['mae_med']:.2f} / {mae_mfe_all['mfe_med']:.2f}"],
            ["avg holding time", f"{mae_mfe_all['hold_h_avg']:.2f} h"],
        ],
    ))
    A("\nMax drawdown across pairs is not a single pooled curve; per-pair maxDD$ is in the table above.\n")

    A("\n## 4. Per-pair t-test (net pips)\n")
    A("\n| symbol | n | mean | t | p |\n|---|---:|---:|---:|---:|")
    for r in results:
        tt = r["ttest"]
        A(f"| {r['symbol']} | {tt['n']} | {tt['mean']:,.3f} | {tt['t']:,.2f} | {tt['p']:.3g} |")

    A("\n## 5. Per-session results (entry-candle session)\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        A(_md_table(list(r["session"].columns), r["session"].itertuples(index=False, name=None)))

    A("\n## 6. Per-year results\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        A(_md_table(list(r["years"].columns), r["years"].itertuples(index=False, name=None)))

    A("\n## 7. Exit reasons\n")
    for r in results:
        A(f"\n### {r['symbol']}\n")
        A(_md_table(
            ["reason", "trades", "share%", "avg_net", "win%"],
            [[rk, v["trades"], v["share_pct"], v["avg_net"], v["win%"]] for rk, v in r["exit_reasons"].items()],
        ))

    A("\n## 8. Interpretation\n")
    A("\n**Gross edge vs post-cost edge.** Report the gross sums explicitly: "
      f"gross profit = {gross_mon[gross_mon > 0].sum():,.2f}$, gross loss = {gross_mon[gross_mon < 0].sum():,.2f}$, "
      f"total costs = {cost_mon.sum():,.2f}$.  The net result is **{mon.sum():,.2f}$** ({net_pips.sum():,.1f} pips) "
      f"on {len(all_t):,} trades, avg {mon.mean():,.2f}$/trade, PF {all_pf:.2f}, win rate {(net_pips > 0).mean() * 100:.1f}%.")
    A(f"\n**Significance.** Combined t-test of net pips: t={t_all['t']:.2f}, p={t_all['p']:.3g}. "
      "A negative/positive mean at p<0.05 means the DEV sample itself deviates from zero; it says nothing yet about validation or the future.")
    A("\n**Robustness.** Year-by-year sign stability (section 6) and session-by-session stability (section 5) are the check: "
      "any year or session that flips sign to the opposite of the overall direction weakens the candidate's robustness claim. "
      "Note the session gate is applied to the signal candle, but entries can fill in an adjacent session boundary bar.")
    A("\n**No stop-optimization.** The 1.5/3.0 ATR risk model is the backtester's pre-existing default; the fixed 20-bar hold is the discovery headline horizon. "
      "No parameter was swept at any point and no alternative variant was evaluated. Strategy 01 remains untouched as the rejected historical experiment.")

    A("\n## 9. Does Candidate #2 deserve validation?\n")
    A("\nPre-registered acceptance test (from discovery \u00a711 Candidate #2), to be applied on the untouched VALIDATION split: "
      "**avg net >= cost + 0.5 pips AND hit >= 50% AND direction stable per session.**")
    cost_pip_avg = float(cost_pips.mean())
    net_pip_avg = float(net_pips.mean())
    threshold = cost_pip_avg + 0.5
    if len(all_t) > 0:
        verdict = (
            f"DEV post-cost edge = {net_pip_avg:+.3f} pips/trade vs an acceptance threshold of about "
            f"{threshold:+.3f} pips/trade (avg cost {cost_pip_avg:.2f} pips + 0.5). "
            f"DEV sample {('meets' if net_pip_avg >= threshold else 'FAILS')} the threshold, "
            f"win rate {float((net_pips > 0).mean() * 100):.1f}% is {('at least' if float((net_pips > 0).mean() * 100) >= 50.0 else 'below')} 50%. "
            f"Per-session direction stability must be judged from section 5."
        )
    else:
        verdict = "No trades were produced on the DEV split."
    A("\n**Verdict on the DEV sample (informational only \u2014 it is NOT a validation pass):** " + verdict)
    A("\nThis report is DEV-only evidence: it does **not** test the validation split and therefore cannot approve or reject the "
      "candidate by itself. It records whether the dev numbers even point in the acceptance direction before any validation spend.")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(trades_path, "w", encoding="utf-8") as f:
        dump = []
        for t in all_t:
            d = t.to_dict()
            d["entry_time"] = str(pd.Timestamp(d["entry_time"]))
            d["exit_time"] = str(pd.Timestamp(d["exit_time"]))
            dump.append(d)
        json.dump(dump, f, indent=2)


def main() -> int:
    pcfg = PathConfig()
    s_cfg = StrategyConfig()
    c_cfg = CostConfig()

    results: list[dict[str, Any]] = []
    for symbol in SYMBOLS:
        res = _run_symbol(symbol, pcfg, s_cfg, c_cfg)
        m = res["metrics"]
        print(f"OK {symbol}: {res['n_bars']:,} dev bars, {m['total_trades']} trades, "
              f"net {m['net_profit']:+,.2f}$, PF {m['profit_factor']:.2f}, WR {m['win_rate']*100:.1f}%")
        results.append(res)

    report_path = _root / REPORT_NAME
    trades_path = pcfg.output_dir / "strategy_02_trades.json"
    _write_report(results, report_path, trades_path)

    print(f"\nReport written to {report_path}")
    print(f"Trades dump: {trades_path}")
    print("Confirmation: DEV split only; no validation, no holdout, no optimization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())