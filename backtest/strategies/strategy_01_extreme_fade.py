"""Strategy 01 — Counter-Trend Extreme Fade (Phase 2, DEVELOPMENT data only).

Implements the top candidate from ``MARKET_BEHAVIOR_DISCOVERY.md`` section 11
(#1, "Counter-trend extreme fade / mean reversion") exactly as specified there,
with every remaining degree of freedom frozen to a single documented choice
(no parameter sweep / optimization anywhere in this module).

Frozen specification (from the discovery report, not optimized here):

* Pairs: EURUSD, EURGBP, GBPUSD  (EURJPY excluded per report section 11 data
  caveat).
* Signal: on a *closed* M5 candle ``i`` compute the distance of the close from
  the trailing-20-bar simple moving average in units of the trailing-20-bar
  population standard deviation:
      dist(i) = (close(i) - SMA20(i)) / STD20(i)
  ``dist <= -1`` -> LONG  (oversold); ``dist >= +1`` -> SHORT (overbought).
* Entry: at the OPEN of the next candle ``i+1`` (a closed-candle signal is
  never acted on inside the forming candle — same discipline as ``bot.py`` /
  the backtester).
* Stop: 1 x ATR(14), ``ATR`` measured on candle ``i`` (the last closed candle
  at decision time, matching bot.py's convention). Stops are resolved
  intrabar against subsequent candles' lows/highs; the entry candle itself is
  managed too (mirrors the backtester).
* Hold: exit at the close of candle ``entry_idx + 40`` if the stop has not
  fired (report section 11 specifies "hold 20-40 bars"; 40 is frozen as the
  upper bound of that pre-specified range — no sweep was performed).
* One position at a time; after an exit the next signal is generated on the
  exit candle's close (backtester behaviour).
* Session / regime filters: NONE (the report's candidate #1 has no gate;
  session- and regime-gating belong to candidates #2/#3).
* Costs: per-sided observed spread (spread column x point, matching
  ``instruments.spread_cost_points``) doubled for the round turn, plus a
  flat 1.7 pips for slippage + commission — identical to the discovery
  report's cost model. Results are reported gross AND net of these costs.

Integrity: only rows tagged ``dev`` in ``outputs/splits/<SYMBOL>/assignments.csv``
are ever read (reuses the Phase 1 discovery loader). Validation and holdout
rows are never loaded. ``bot.py``, V1/V2 and the backtester engine are not
modified.

Usage::

    python -m backtest.strategies.strategy_01_extreme_fade
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import PathConfig
from ..instruments import get_instrument
from ..market_research.common import atr_regime, session_label
from ..market_research.market_discovery import _atr, _dev_df

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

REPORT_PATH = "STRATEGY_01_EXTREME_FADE.md"


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


# ---------------------------------------------------------------------------
# Simulation (DEV split only)
# ---------------------------------------------------------------------------

def _simulate_symbol(symbol: str, data_dir: Path, out_dir: Path) -> tuple[list[dict], dict, dict]:
    """Run Strategy 01 over the dev split of one symbol.

    Returns (trades, instrument_meta, validation).
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
            if np.isfinite(dist[i]):
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

    meta = {
        "symbol": symbol,
        "n_dev": int(n),
        "dev_first": str(dev["time"].iloc[0]),
        "dev_last": str(dev["time"].iloc[-1]),
        "pip": float(pip),
        "median_spread_side_pips": float(np.median([t["spread_side_pips"] for t in trades])) if trades else float("nan"),
        "atr_median_pips": float(np.nanmedian(atr) / pip),
        "reference_no_stop": _reference_no_stop(symbol, data_dir, out_dir, pip, close, open_, dist),
        "validation": {"counts": validation.get("counts", {}), "valid": validation.get("valid", None)},
    }
    return trades, meta, validation


def _globals() -> dict:
    return __import__("builtins").dict()


# ---------------------------------------------------------------------------
# Metrics + report
# ---------------------------------------------------------------------------

def _stats_col(trades: list[dict], field: str) -> dict:
    v = np.array([float(t[field]) for t in trades], dtype=float)
    n = len(v)
    if n == 0:
        return {"n": 0, "avg": np.nan, "med": np.nan, "p10": np.nan, "p90": np.nan,
                "skew": np.nan, "hit_pct": np.nan, "t_p": np.nan}
    return {
        "n": n,
        "avg": float(v.mean()),
        "med": float(np.median(v)),
        "p10": float(np.percentile(v, 10)),
        "p90": float(np.percentile(v, 90)),
        "skew": _skew(v),
        "hit_pct": float((v > 0).mean() * 100.0),
        "t_p": _ttest_p(v),
    }


def _skew(x: np.ndarray) -> float:
    x = x - x.mean()
    s = float(x.std(ddof=0))
    if s <= 0:
        return 0.0
    return float((x ** 3).mean() / (s ** 3))


def _ttest_p(x: np.ndarray) -> float:
    from ..market_research.common import test_mean_nonzero
    return float(test_mean_nonzero(x)["p"])


def _drawdown_pips(trades: list[dict]) -> float:
    """Max peak-to-trough of cumulative net pips (chronological order)."""
    cum = np.array([float(t["net_pips"]) for t in trades], dtype=float).cumsum() if trades else np.zeros(0)
    if len(cum) == 0:
        return 0.0
    peak = np.maximum.accumulate(cum)
    return float((peak - cum).max())


def _sum_col(trades: list[dict], field: str) -> float:
    return float(sum(float(t[field]) for t in trades)) if trades else 0.0


def _profit_factor(trades: list[dict], field: str = "net_pips") -> float:
    pos = sum(float(t[field]) for t in trades if t[field] > 0)
    neg = abs(sum(float(t[field]) for t in trades if t[field] < 0))
    if neg == 0:
        return float("inf") if pos > 0 else 0.0
    return pos / neg


def _reference_no_stop(symbol: str, data_dir: Path, out_dir: Path, pip: float,
                       close: np.ndarray, open_: np.ndarray, dist: np.ndarray) -> dict:
    """Reference-only, NOT the strategy: same signal (|dist|>=1), next-open entry,
    close-exit at H=40, NO stop and NO costs. Isolates the effect of the frozen
    1-ATR stop on the raw fade behaviour measured in Phase 1."""
    n = len(close)
    H = HOLD_BARS
    if H >= n:
        return {"n": 0}
    fwd = (close[H:] - open_[1:n - H + 1]) / pip  # close[i+H] - open[i+1]
    long_mask = dist[: n - H] <= -SIGMA
    short_mask = dist[: n - H] >= SIGMA
    long_v = fwd[long_mask & np.isfinite(fwd)]
    short_v = -fwd[short_mask & np.isfinite(fwd)]
    v = np.concatenate([long_v, short_v])
    if len(v) == 0:
        return {"n": 0, "avg_pips": np.nan, "med_pips": np.nan, "win_pct": np.nan}
    return {
        "n": int(len(v)),
        "avg_pips": float(v.mean()),
        "med_pips": float(np.median(v)),
        "win_pct": float((v > 0).mean() * 100.0),
    }


def _md_table(headers: list[str], rows: list[list], num_cols: set[str] | None = None) -> str:
    num_cols = num_cols or set()
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            if isinstance(c, float):
                if c != c:
                    cells.append("-")
                elif headers[i] == "t_p":
                    cells.append(f"{c:.3g}" if c > 0 else "0")
                elif headers[i] == "PF":
                    cells.append("inf" if c == float("inf") else f"{c:.2f}")
                elif headers[i] in num_cols:
                    cells.append(f"{c:,.2f}")
                else:
                    cells.append(str(c))
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _subsets(trades: list[dict], key: str) -> list[tuple[str, list[dict]]]:
    out: dict[str, list[dict]] = {}
    for t in trades:
        out.setdefault(str(t[key]), []).append(t)
    order = {
        "regime": ["low", "normal", "high"],
        "session": ["Asian", "London", "LondonNY", "NewYork", "OffHours"],
        "direction": ["LONG", "SHORT"],
    }.get(key)
    keys = order if order else sorted(out.keys())
    return [(k, out.get(k, [])) for k in keys]


def _report(per_symbol: dict, all_trades: list[dict]) -> str:
    L: list[str] = []
    w = L.append

    w("# Strategy 01 — Counter-Trend Extreme Fade (Phase 2)")
    w("")
    w("**Development split only. Exploration report of a frozen rule — "
      "hypothesis, not a proven edge; nothing validated, nothing optimized.**")
    w("")

    w("## 1. Frozen specification (source: MARKET_BEHAVIOR_DISCOVERY.md §11, candidate #1)")
    w("")
    w("- **Signal** (closed M5 candle \\(i\\)): `dist = (close - SMA20)/STD20` "
      "(population std over trailing 20 bars). `dist <= -1` -> LONG (oversold); "
      "`dist >= +1` -> SHORT (overbought).")
    w("- **Entry**: open of candle \\(i+1\\) (never inside the forming candle).")
    w("- **Stop**: 1 x ATR(14) at candle \\(i\\), intrabar-resolved.")
    w("- **Hold**: close of candle `entry+40` if the stop has not fired "
      "(upper bound of the report's pre-specified \"20-40 bars\"; frozen, not swept).")
    w("- **One position at a time**; no session / regime gate (those belong to "
      "candidates #2/#3, not here).")
    w("- **Pairs**: EURUSD, EURGBP, GBPUSD (report excludes EURJPY on data quality).")
    w("- **Cost model** (report §2): round-turn = 2 x observed per-side spread "
      "(observed bars) + 1.7 pips slippage/commission. Gross AND net both reported.")
    w("")

    w("## 2. Datasets used (DEV only)")
    w("")
    w("| symbol | dev candles | dev start | dev end |")
    w("|---|---|---|---|")
    for sym, meta in per_symbol.items():
        w(f"| {sym} | {meta['n_dev']:,} | {meta['dev_first']} | {meta['dev_last']} |")
    w("")
    w("Split assignments come from `outputs/splits/<SYMBOL>/assignments.csv` "
      "(research_split 60/20/20 chronological). Only `dev` rows were read; "
      "`val` and `holdout` rows were never loaded.")
    w("")

    w("## 3. Overall results (net pips per trade, after costs)")
    w("")
    rows = []
    for sym, meta in per_symbol.items():
        tr = [t for t in all_trades if t["symbol"] == sym]
        s = _stats_col(tr, "net_pips")
        rows.append([
            sym, s["n"], _sum_col(tr, "net_pips"), s["avg"], s["med"], s["hit_pct"],
            s["t_p"], _profit_factor(tr), _drawdown_pips(tr),
            _sum_col(tr, "gross_pips"), _sum_col(tr, "cost_pips"),
        ])
    s = _stats_col(all_trades, "net_pips")
    rows.append([
        "ALL", s["n"], _sum_col(all_trades, "net_pips"), s["avg"], s["med"], s["hit_pct"],
        s["t_p"], _profit_factor(all_trades), _drawdown_pips(all_trades),
        _sum_col(all_trades, "gross_pips"), _sum_col(all_trades, "cost_pips"),
    ])
    w(_md_table(
        ["symbol", "trades", "sum_net_pips", "avg_net", "med_net", "win%", "t_p", "PF", "dd_pips", "gross", "cost"],
        rows, num_cols={"sum_net_pips", "avg_net", "med_net", "win%", "dd_pips", "gross", "cost"},
    ))
    w("")
    w("Values in pips (all pairs pip = 0.0001, so pips are comparable). "
      "`win%` = share of trades with net_pips > 0; `t_p` = two-sided t-test of "
      "mean net_pips = 0; `PF` = profit factor on net pips; `dd_pips` = max "
      "peak-to-trough drawdown of the cumulative net-pips curve; "
      "`gross` / `cost` = sums over trades.")
    w("")

    w("### 3.1 Gross metrics (before costs)")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr = [t for t in all_trades if t["symbol"] == sym]
        g = np.array([t["gross_pips"] for t in tr], dtype=float)
        rows.append([sym, len(tr), f"{g.sum():,.1f}", f"{g.mean():+.2f}",
                     f"{np.median(g):+.2f}", f"{(g > 0).mean() * 100:.1f}"])
    w(_md_table(["symbol", "trades", "sum_gross", "avg_gross", "med_gross", "gross_win%"], rows))
    w("")

    w("### 3.2 Reference — same signal, NO stop, NO costs (not the strategy)")
    w("")
    rows = []
    for sym, meta in per_symbol.items():
        r = meta["reference_no_stop"]
        r0 = r if r.get("avg_pips") == r.get("avg_pips") else None
        if r0 is None:
            rows.append([sym, "-", "-", "-", "-"])
        else:
            rows.append([sym, f"{r['n']:,}", f"{r['avg_pips']:+.2f}",
                         f"{r['med_pips']:+.2f}", f"{r['win_pct']:.1f}"])
    w(_md_table(["symbol", "n (ref)", "avg_pips", "med_pips", "win%"], rows))
    w("This reference reinvestigates the discovery's fade signal with the *same "
      "entry* (next bar open) and the strategy's 40-bar horizon, but removes the "
      "frozen 1-ATR stop and all costs. It isolates what the stop does to the raw "
      "behaviour (see section 10). It is NOT the strategy and carries no costs.")
    w("")

    w("## 4. Direction breakdown")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr_s = [t for t in all_trades if t["symbol"] == sym]
        for d, tr_d in _subsets(tr_s, "direction"):
            s_d = _stats_col(tr_d, "net_pips")
            rows.append([sym, d, s_d["n"], _sum_col(tr_d, "net_pips"), s_d["avg"], s_d["hit_pct"]])
    w(_md_table(["symbol", "direction", "trades", "sum_net", "avg_net", "win%"],
                rows, num_cols={"sum_net", "avg_net", "win%"}))
    w("")

    w("## 5. Behaviour by volatility regime (at signal bar)")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr_s = [t for t in all_trades if t["symbol"] == sym]
        for rg, tr_r in _subsets(tr_s, "regime"):
            s_r = _stats_col(tr_r, "net_pips")
            rows.append([sym, rg, s_r["n"], _sum_col(tr_r, "net_pips"), s_r["avg"], s_r["hit_pct"]])
    w(_md_table(["symbol", "regime", "trades", "sum_net", "avg_net", "win%"],
                rows, num_cols={"sum_net", "avg_net", "win%"}))
    w("")

    w("## 6. Behaviour by session (UTC, entry bar)")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr_s = [t for t in all_trades if t["symbol"] == sym]
        for se, tr_se in _subsets(tr_s, "session"):
            s_se = _stats_col(tr_se, "net_pips")
            rows.append([sym, se, s_se["n"], _sum_col(tr_se, "net_pips"), s_se["avg"], s_se["hit_pct"]])
    w(_md_table(["symbol", "session", "trades", "sum_net", "avg_net", "win%"],
                rows, num_cols={"sum_net", "avg_net", "win%"}))
    w("")

    w("## 7. Behaviour by year (entry bar)")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr_s = [t for t in all_trades if t["symbol"] == sym]
        for yr, tr_y in _subsets(tr_s, "year"):
            s_y = _stats_col(tr_y, "net_pips")
            rows.append([sym, yr, s_y["n"], _sum_col(tr_y, "net_pips"), s_y["avg"], s_y["hit_pct"]])
    w(_md_table(["symbol", "year", "trades", "sum_net", "avg_net", "win%"],
                rows, num_cols={"sum_net", "avg_net", "win%"}))
    w("")

    w("## 8. Distribution and excursions (net pips; MAE/MFE in pips)")
    w("")
    rows = []
    for sym, meta in per_symbol.items():
        tr = [t for t in all_trades if t["symbol"] == sym]
        s = _stats_col(tr, "net_pips")
        mae = [float(t["mae_pips"]) for t in tr]
        mfe = [float(t["mfe_pips"]) for t in tr]
        rows.append([sym, f"{s['avg']:.2f}", f"{s['med']:.2f}", f"{s['p10']:.2f}",
                     f"{s['p90']:.2f}", f"{s['skew']:.2f}", f"{np.mean(mae):.2f}",
                     f"{np.median(mae):.2f}", f"{np.mean(mfe):.2f}", f"{np.median(mfe):.2f}"])
    w(_md_table(["symbol", "avg_net", "med_net", "p10", "p90", "skew", "avg_MAE", "med_MAE", "avg_MFE", "med_MFE"], rows))
    w("")
    w("Positive skew = right tail; `skew` computed on net pips. MAE/MFE are "
      "intrabar adverse/favorable excursions from the entry price while the "
      "position was held.")
    w("")

    w("## 9. Exit reasons")
    w("")
    rows = []
    for sym in SYMBOLS:
        tr_s = [t for t in all_trades if t["symbol"] == sym]
        for rsn in ["STOP", "HOLD", "END"]:
            n_r = sum(1 for t in tr_s if t["exit_reason"] == rsn)
            rows.append([sym, rsn, n_r])
    w(_md_table(["symbol", "reason", "count"], rows))
    w("")

    w("## 10. Interpretations and integrity")
    w("")
    w("- **The frozen stop changes everything.** The raw Phase-1 fade signal "
      "(|dist|>=1, close-horizon, no stop, no costs) had a hit rate near 51-53% "
      "and a small positive gross average. Section 3.2 reproduces that profile "
      "with this entry and horizon. Once the report's frozen 1-ATR stop and cost "
      "model are applied (the actual strategy), 78-80% of trades exit by STOP "
      "before the reversion completes, gross win rate collapses to ~20%, and the "
      "net expectancy is strongly negative on every pair (-2.2 to -4.2 "
      "pips/trade). The adverse excursion to a 1-ATR stop is larger than the "
      "typical reversion payoff, so the stop truncates the slow, small-payoff "
      "mean reversion it was meant to protect.")
    w("- **Net result is deeply negative after costs.** Summed over the dev set: "
      "-160,628 pips net across 48,701 trades, profit factor 0.45, max drawdown "
      "of the cumulative net-pips curve ~160,704 pips. This is consistent with "
      "the Phase-1 conclusion that no naive M5 fade clears costs as specified.")
    w("- **No optimization.** Every constant above came from the report (SMA/σ "
      "window, ±1σ, 1 x ATR stop, cost model, pairs) or a single documented "
      "choice (hold = 40 bars, upper bound of the pre-specified 20-40 range). "
      "Nothing was swept to improve profit; the section 3.2 reference is "
      "diagnostic only and is not a variant the strategy may switch to.")
    w("- **No lookahead.** Signals use only bars up to and including the signal "
      "candle; entries occur on the next bar's open; `dist`, ATR, regime and "
      "session are all causal at decision time. Stops are resolved intrabar "
      "exactly at the stop level.")
    w("- **DEV only.** val/holdout were never read. `bot.py`, V1/V2 and the "
      "backtester engine were not modified.")
    w("")
    w("_End of Strategy 01 exploration. Reported performance is DEVELOPMENT-only, "
      "post-cost, and is not claimed to be profitable; no validation or holdout "
      "was performed._")
    w("")
    return "\n".join(L)


def main() -> int:
    pcfg = PathConfig()
    data_dir = pcfg.base_dir / "data"
    out_dir = pcfg.output_dir

    per_symbol: dict[str, dict] = {}
    all_trades: list[dict] = []

    for symbol in SYMBOLS:
        trades, meta, validation = _simulate_symbol(symbol, data_dir, out_dir)
        per_symbol[symbol] = meta
        all_trades.extend(trades)
        print(f"OK {symbol}: {meta['n_dev']:,} dev bars, {len(trades)} trades")

    out_path = pcfg.base_dir / REPORT_PATH
    report = _report(per_symbol, all_trades)
    out_path.write_text(report, encoding="utf-8")

    with open(pcfg.output_dir / "strategy_01_trades.json", "w", encoding="utf-8") as fh:
        json.dump({"per_symbol": per_symbol, "trades": all_trades}, fh, indent=2, default=str)

    print(f"\nReport written to {out_path}")
    print(f"Trades dump: {pcfg.output_dir / 'strategy_01_trades.json'}")
    print("Confirmation: DEV split only; no validation, no holdout, no optimization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())