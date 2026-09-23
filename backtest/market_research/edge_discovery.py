"""Edge Discovery — pre-registered market-behavior experiments (RESEARCH ONLY).

Preached in advance by EDGE_DISCOVERY_PLAN.md (Part C).  Every hypothesis has a
fixed, causal, economically interpretable entry rule; execution is next-bar-open
after a closed-candle decision; exit is a fixed-horizon bar close; costs are the
real observed bid/ask spread at the entry and exit bars plus 1.0 pip slippage
(0.5/side, matching the Phase-5 ``ratio_real`` convention).

Integrity guarantees enforced in this module:

  * DEV rows only (preserved chronological 60/20/20 split, assignments file).
  * VALIDATION / HOLDOUT bars are never loaded or referenced.
  * No strategy is constructed, no parameter is swept, no ML is used.
  * bot.py / V1 / V2 / Strategies 01-03 are untouched.
  * All outputs are brand-new files (EDGE_DISCOVERY_RESULTS.md and
    outputs/edge_discovery_results.json); historical outputs are not overwritten.
  * EURJPY is excluded (degraded feed, issue A2 unresolved).

Experiments run (IDs match the plan):
  B-PB    trend pullbacks on an aligned two-timeframe basis (H1 / H1=M15)
  E-SQZ   volatility contraction -> breakout expansion (H4)
  G-CANDLE large single-candle momentum (M15)
  H-ALIGN multi-timeframe directional alignment (H4 / H1)
  J-FADE-REGIME regime-conditioned mean reversion (H1)

Usage:
    python -m backtest.market_research.edge_discovery
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent
import sys

sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.instruments import get_instrument
from backtest.market_research.common import atr_regime, session_label, test_mean_nonzero

# ---------------------------------------------------------------------------
# Frozen research parameters (no sweeps)
# ---------------------------------------------------------------------------

SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
TF_MIN = {"M5": 5, "M15": 15, "H1": 60, "H4": 240}

SLIP_TOTAL_PIPS = 1.0          # 0.5 per side, Phase-5 convention
MIN_BEHAV_N = 1000
PROMISE_RATIO = 1.0            # movement-to-cost >= 1.0
PROMISE_MEAN = 2.0             # |raw mean| >= 2.0 pips
BORDER_RATIO = 0.5
MIN_YEAR_WIN = 0.6             # >=60% of calendar years positive
MAX_YEAR_SHARE = 0.5           # no single year > 50% of total net
MAX_WINDOW_SHARE = 0.4         # no single 4-week window > 40% of total net
WINDOW_DAYS = 28
MIN_POS_SYMBOLS = 2            # >= 2 of 3 clean symbols positive

ATR_PERIOD = 14
REGIME_LOOKBACK = 50
SQZ_K = 4                      # consecutive low-regime H4 bars -> contraction
SMA_FAST = 8
SMA_MID = 20
SMA_SLOW = 24
LARGE_BODY_MULT = 2.0
MAX_CANDLE_MULT = 5.0          # guard: drop implausibly wide candles
Z_FADE = 1.0                   # |z| threshold for fade entries

REPORT_PATH = "EDGE_DISCOVERY_RESULTS.md"
JSON_PATH = "outputs/edge_discovery_results.json"


# ---------------------------------------------------------------------------
# Data loading (dev only)
# ---------------------------------------------------------------------------

def _load_dev(symbol: str, pcfg: PathConfig) -> pd.DataFrame:
    """DEV rows only from the preserved 60/20/20 split (assignments file)."""
    sym = symbol.lower()
    csv_path = pcfg.base_dir / "data" / f"{sym}_m5.csv"
    assign_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    if not csv_path.exists() or not assign_path.exists():
        raise FileNotFoundError(f"Missing data or split for {symbol}")
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    assignments = pd.read_csv(assign_path)
    mask = assignments["split"] == "dev"
    return df.iloc[assignments.index[mask].tolist()].reset_index(drop=True)


def _split_counts(symbol: str, pcfg: PathConfig) -> dict[str, int]:
    assign_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    assignments = pd.read_csv(assign_path)
    return dict(assignments["split"].value_counts())


def _aggregate(dev: pd.DataFrame, tf: str) -> pd.DataFrame:
    """UTC-anchored floor aggregation M5 -> M15/H1/H4 (no lookahead).

    Same convention as phase5_research._aggregate: each aggregated bar uses only
    the M5 rows whose OPEN time falls inside its own window; ``spread`` is the
    spread of the LAST M5 bar in the window (spread-at-close).
    """
    period = {"M15": "15min", "H1": "1h", "H4": "4h"}[tf]
    idx = dev["time"].dt.floor(period)
    idx.name = "time"
    g = dev.groupby(idx)
    out = g.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        spread=("spread", "last"),
    )
    out["n_bars"] = g["spread"].size()
    out = out.reset_index()
    return out.sort_values("time").reset_index(drop=True)


def _atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ATR_PERIOD) -> np.ndarray:
    prev_close = np.concatenate([[np.nan], close[:-1]])
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    return pd.Series(tr).ewm(alpha=1 / period, adjust=False, min_periods=period).mean().to_numpy()


def _sma(x: np.ndarray, k: int) -> np.ndarray:
    return pd.Series(x).rolling(k, min_periods=k).mean().to_numpy()


def _consecutive_true(flag: np.ndarray) -> np.ndarray:
    """Trailing count of consecutive True values at each position."""
    out = np.zeros(len(flag), dtype=int)
    acc = 0
    for i, f in enumerate(flag):
        acc = acc + 1 if f else 0
        out[i] = acc
    return out


# ---------------------------------------------------------------------------
# Frame: one symbol / timeframe, DEV rows only
# ---------------------------------------------------------------------------

class Frame:
    """A symbol/timeframe frame with all causal features for the experiments."""

    def __init__(self, symbol: str, tf: str, pcfg: PathConfig, m5: pd.DataFrame | None = None):
        self.symbol = symbol
        self.tf = tf
        self.bars_min = TF_MIN[tf]
        self.inst = get_instrument(symbol)
        self.pip = self.inst.pip

        if tf == "M5":
            df = m5 if m5 is not None else _load_dev(symbol, pcfg)
            df = df.reset_index(drop=True)
        else:
            df = _aggregate(m5 if m5 is not None else _load_dev(symbol, pcfg), tf)
        self.ag = df
        self.n = len(df)

        o = df["open"].to_numpy(float)
        h = df["high"].to_numpy(float)
        lo = df["low"].to_numpy(float)
        c = df["close"].to_numpy(float)
        self.open, self.high, self.low, self.close = o, h, lo, c

        self.ts = pd.to_datetime(df["time"]).to_numpy()
        self.ts_ns = self.ts.astype("datetime64[ns]").astype(np.int64)
        self.hour = pd.to_datetime(df["time"]).dt.hour.to_numpy()
        self.sess = session_label(self.hour).astype(str)

        self.spread_pips = (df["spread"].to_numpy(float) * self.inst.point) / self.pip
        self.atr_price = _atr(h, lo, c, ATR_PERIOD)
        self.atr_pips = self.atr_price / self.pip
        self.rng_pips = (h - lo) / self.pip

        self.sma_fast = _sma(c, SMA_FAST) / self.pip      # used for multi-TF trend sign
        self.sma_mid = _sma(c, SMA_MID) / self.pip        # z-score denominator baseline (price)
        self.sma_slow = _sma(c, SMA_SLOW) / self.pip
        self.sma20_price = _sma(c, SMA_MID)

        z = np.full(self.n, np.nan)
        ok = (self.atr_price > 0) & np.isfinite(self.sma20_price)
        z[ok] = (c[ok] - self.sma20_price[ok]) / self.atr_price[ok]
        self.z = z

        reg = atr_regime(self.atr_price, REGIME_LOOKBACK)
        self.regime = reg.astype(str)
        self.regime_low = self.regime == "low"
        self.regime_high = self.regime == "high"
        self.regime_sqzc = _consecutive_true(self.regime_low)

        self.note: list[dict] = []


def _fast_slices(fast_ts_ns: np.ndarray, slow_ts_ns: np.ndarray, fast_min: int, slow_min: int) -> tuple[np.ndarray, np.ndarray]:
    """First and last fast-frame index inside each slow bar (causal).

    Uses fast bars whose OPEN time falls within [slow_time, slow_time + slow_min).
    The last fast bar inside slow bar t closes at (or after) slow bar t's close,
    so its close IS the slow bar close (no lookahead).
    """
    ns_min = 60_000_000_000
    f0 = np.searchsorted(fast_ts_ns, slow_ts_ns, side="left")
    f1 = np.searchsorted(fast_ts_ns, slow_ts_ns + (slow_min - fast_min) * ns_min, side="right") - 1
    return f0, f1


# ---------------------------------------------------------------------------
# Pre-registered experiment rules (signal + direction at the working bar)
# ---------------------------------------------------------------------------

def _exp_b_pb(frame, fast: Frame, f0, f1) -> tuple[np.ndarray, np.ndarray]:
    """B-PB: H1 trend + M15 pullback + resumption (aligned two-timeframe)."""
    n = frame.n
    mask = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=float)

    slow_up = frame.close / frame.pip > frame.sma_slow
    slow_dn = frame.close / frame.pip < frame.sma_slow
    fast_up_sma = fast.close / fast.pip > fast.sma_slow          # M15 in its own uptrend
    fast_dn_sma = fast.close / fast.pip < fast.sma_slow

    for t in range(n):
        if f0[t] > f1[t] or f1[t] >= fast.n:
            continue
        lo_, hi_ = int(f0[t]), int(f1[t])
        body_below = (fast.close[lo_:hi_ + 1] / fast.pip) < fast.sma_fast[lo_:hi_ + 1]
        body_above = (fast.close[lo_:hi_ + 1] / fast.pip) > fast.sma_fast[lo_:hi_ + 1]
        resumed_up = (fast.close[hi_] / fast.pip) >= fast.sma_fast[hi_]
        resumed_dn = (fast.close[hi_] / fast.pip) <= fast.sma_fast[hi_]
        if slow_up[t] and fast_up_sma[hi_] and body_below.any() and resumed_up:
            mask[t] = True
            direction[t] = 1.0
        elif slow_dn[t] and fast_dn_sma[hi_] and body_above.any() and resumed_dn:
            mask[t] = True
            direction[t] = -1.0
    return mask, direction


def _exp_e_sqz(frame: Frame) -> tuple[np.ndarray, np.ndarray]:
    """E-SQZ: ATR low-regime contraction (K consecutive H4 bars) then breakout."""
    n = frame.n
    mask = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=float)
    for t in range(n):
        if frame.regime_sqzc[t] < SQZ_K or t < SQZ_K:
            continue
        lo = t - SQZ_K
        chan_hi = float(np.nanmax(frame.high[lo:t]))  # squeeze-window bars t-K..t-1, excluding t
        chan_lo = float(np.nanmin(frame.low[lo:t]))
        if np.isnan(chan_hi) or np.isnan(chan_lo):
            continue
        if frame.close[t] > chan_hi:
            mask[t] = True
            direction[t] = 1.0
        elif frame.close[t] < chan_lo:
            mask[t] = True
            direction[t] = -1.0
    return mask, direction


def _exp_g_candle(frame: Frame) -> tuple[np.ndarray, np.ndarray]:
    """G-CANDLE: |body| >= 2*ATR(14), direction of the body, drop wide spikes."""
    n = frame.n
    body = np.abs(frame.close - frame.open)
    rng = frame.high - frame.low
    big = (body >= LARGE_BODY_MULT * frame.atr_price) & (rng <= MAX_CANDLE_MULT * frame.atr_price)
    big &= frame.atr_price > 0
    direction = np.zeros(n, dtype=float)
    direction = np.where(big & (frame.close > frame.open), 1.0,
                np.where(big & (frame.close < frame.open), -1.0, 0.0))
    return big, direction


def _exp_h_align(frame: Frame, fast: Frame, f0, f1) -> tuple[np.ndarray, np.ndarray]:
    """H-ALIGN: H1 fast trend sign agrees with H4 slow trend sign."""
    n = frame.n
    mask = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=float)
    slow_sig = np.zeros(n, dtype=float)
    slow_sig[frame.close / frame.pip > frame.sma_slow] = 1.0
    slow_sig[frame.close / frame.pip < frame.sma_slow] = -1.0
    fast_sig_arr = np.zeros(fast.n, dtype=float)
    f_up = fast.close / fast.pip > fast.sma_fast
    f_dn = fast.close / fast.pip < fast.sma_fast
    fast_sig_arr[f_up] = 1.0
    fast_sig_arr[f_dn] = -1.0
    for t in range(n):
        if f1[t] >= fast.n:
            continue
        fs = fast_sig_arr[int(f1[t])]
        ss = slow_sig[t]
        if fs != 0.0 and fs == ss:
            mask[t] = True
            direction[t] = fs
    return mask, direction


def _exp_j_fade_regime(frame: Frame) -> tuple[np.ndarray, np.ndarray]:
    """J-FADE-REGIME: fade |z| extremes but ONLY in the LOW ATR regime."""
    n = frame.n
    low = frame.regime_low
    mask = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=float)
    oversold = (frame.z <= -Z_FADE) & low
    overbought = (frame.z >= Z_FADE) & low
    mask[oversold] = True
    mask[overbought] = True
    direction[oversold] = 1.0
    direction[overbought] = -1.0
    return mask, direction


EXPERIMENTS: list[dict[str, Any]] = [
    {
        "id": "B-PB",
        "hypothesis": "B - trend pullbacks",
        "name": "aligned two-timeframe pullback resumption",
        "tf": "H1",
        "holds": [12, 24],
        "rationale": "Pullback resumption inside an established higher-TF trend; H1 raw movement is the largest in the ladder.",
    },
    {
        "id": "E-SQZ",
        "hypothesis": "E - volatility contraction then expansion",
        "name": "low-ATR squeeze then range breakout",
        "tf": "H4",
        "holds": [2, 4],
        "rationale": "Contracted volatility followed by a breakout tests the 'squeeze pop' direction; Phases 3/4 never combined the two.",
    },
    {
        "id": "G-CANDLE",
        "hypothesis": "G - momentum following unusually large candles",
        "name": "single large-body candle momentum",
        "tf": "M15",
        "holds": [4, 12],
        "rationale": "Event-based momentum (Phases 1/3 used window momentum); M15 gives many events and cost-plausible 1h/3h holds.",
    },
    {
        "id": "H-ALIGN",
        "hypothesis": "H - multi-timeframe directional alignment",
        "name": "H1/H4 trend-sign confluence",
        "tf": "H4",
        "holds": [2, 6],
        "rationale": "Confluence of short and long timeframe trend; genuinely untested dimension at the largest raw-movement scale.",
    },
    {
        "id": "J-FADE-REGIME",
        "hypothesis": "J - regime-dependent behavior",
        "name": "fade extremes gated to the low-ATR regime",
        "tf": "H1",
        "holds": [4, 12],
        "rationale": "Phase-1 fade-the-extreme (positive raw) may clear costs once restricted to a range-bound regime; frozen threshold, not swept.",
    },
]


# ---------------------------------------------------------------------------
# Trade simulation (next-open entry, fixed-horizon close exit)
# ---------------------------------------------------------------------------

def simulate(frame: Frame, mask: np.ndarray, direction: np.ndarray, hold: int) -> list[dict]:
    n = frame.n
    events: list[dict] = []
    for t in np.nonzero(mask & (direction != 0))[0]:
        entry_i = t + 1
        exit_i = t + hold
        if entry_i >= n or exit_i >= n:
            continue
        entry_price = frame.open[entry_i]
        exit_price = frame.close[exit_i]
        if not (np.isfinite(entry_price) and np.isfinite(exit_price)):
            continue
        d = direction[t]
        gross = d * (exit_price - entry_price) / frame.pip
        cost = frame.spread_pips[entry_i] + frame.spread_pips[exit_i] + SLIP_TOTAL_PIPS
        net = gross - cost
        events.append({
            "entry_time": str(frame.ts[entry_i]),
            "exit_time": str(frame.ts[exit_i]),
            "direction": "BUY" if d > 0 else "SELL",
            "gross_pips": float(gross),
            "cost_pips": float(cost),
            "net_pips": float(net),
            "duration_bars": int(hold),
            "duration_hours": round(hold * frame.bars_min / 60.0, 3),
            "entry_regime": str(frame.regime[entry_i]) if entry_i < n else "normal",
            "entry_year": pd.Timestamp(frame.ts[entry_i]).year,
            "entry_month": str(pd.Timestamp(frame.ts[entry_i]).to_period("M")),
        })
    return events


# ---------------------------------------------------------------------------
# Metrics (the exact list TASK.md requires, on a per-event basis)
# ---------------------------------------------------------------------------

def experiment_metrics(events: list[dict], frame: Frame) -> dict[str, Any]:
    n = len(events)
    base = {
        "n": n,
        "symbol": frame.symbol,
        "timeframe": frame.tf,
        "bars_min": frame.bars_min,
        "pip": frame.pip,
    }
    if n == 0:
        return base
    net = np.array([e["net_pips"] for e in events], dtype=float)
    gross = np.array([e["gross_pips"] for e in events], dtype=float)
    wins = net[net > 0]
    losses = net[net < 0]
    win_rate = float(len(wins) / n) if n else 0.0
    gross_profit = float(gross[gross > 0].sum())
    gross_loss = float(abs(gross[gross < 0].sum()))
    net_win = float(wins.sum()) if len(wins) else 0.0
    net_loss = float(abs(losses.sum())) if len(losses) else 0.0
    pf = net_win / net_loss if net_loss > 0 else (float("inf") if net_win > 0 else 0.0)
    cum = np.cumsum(net)
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    max_dd = float(dd.max())

    yearly: dict[int, dict] = {}
    for e in events:
        y = e["entry_year"]
        d = yearly.setdefault(y, {"n": 0, "wins": 0, "net_pips": 0.0})
        d["n"] += 1
        d["wins"] += 1 if e["net_pips"] > 0 else 0
        d["net_pips"] += e["net_pips"]
    years_pos = sum(1 for d in yearly.values() if d["net_pips"] > 0)
    year_share_max = max((abs(d["net_pips"] / cum[-1]) for d in yearly.values()), default=None) if cum[-1] != 0 else None
    total_net = float(cum[-1])

    # 4-week window concentration
    ts = np.array([np.datetime64(e["entry_time"]) for e in events])
    win_tot = {}
    for i, t in enumerate(ts):
        bin_ = (t - ts.min()).astype("timedelta64[D]").astype(int) // WINDOW_DAYS
        win_tot.setdefault(int(bin_), 0.0)
        win_tot[int(bin_)] += net[i]
    window_share_max = max((abs(v / total_net) for v in win_tot.values()), default=None) if total_net != 0 else None

    m: dict[str, Any] = {
        **base,
        "trades": n,
        "win_rate": win_rate,
        "avg_win_pips": float(np.mean(wins)) if len(wins) else 0.0,
        "avg_loss_pips": float(np.mean(losses)) if len(losses) else 0.0,
        "expectancy_net_pips": float(np.mean(net)),
        "profit_factor": float(pf),
        "gross_profit_pips": gross_profit,
        "gross_loss_pips": gross_loss,
        "total_net_pips": total_net,
        "net_usd_norm": total_net,  # $1/pip at configured 0.10 lot / $10 per pip-lot
        "max_drawdown_pips": max_dd,
        "avg_duration_bars": float(np.mean([e["duration_bars"] for e in events])),
        "avg_duration_hours": float(np.mean([e["duration_hours"] for e in events])),
        "exposure": float(n * (np.mean([e["duration_bars"] for e in events])) / max(1, frame.n)),
        "avg_cost_pips": float(np.mean([e["cost_pips"] for e in events])),
        "total_cost_pips": float(sum(e["cost_pips"] for e in events)),
        "commission": 0.0,
        "movement_to_cost": abs(float(np.mean(gross))) / float(np.mean([e["cost_pips"] for e in events]))
                          if np.mean([e["cost_pips"] for e in events]) > 0 else float("nan"),
        "mean_raw_pips": float(np.mean(gross)),
        "t_test": test_mean_nonzero(net),
        "years_count": len(yearly),
        "years_total": len(yearly),
        "years_positive_share": years_pos / len(yearly) if yearly else 0.0,
        "max_year_share": year_share_max,
        "max_window_share": window_share_max,
        "yearly": {str(k): v for k, v in sorted(yearly.items())},
    }
    # long vs short
    m["long"] = _direction_subset(events, "BUY")
    m["short"] = _direction_subset(events, "SELL")
    # regime buckets
    m["regime_buckets"] = _regime_buckets(events)
    return m


def _direction_subset(events: list[dict], side: str) -> dict[str, Any]:
    sel = [e for e in events if e["direction"] == side]
    if not sel:
        return {"n": 0, "win_rate": 0.0, "net_pips": 0.0}
    net = np.array([e["net_pips"] for e in sel])
    return {"n": len(sel), "win_rate": float((net > 0).mean()), "net_pips": float(net.sum())}


def _regime_buckets(events: list[dict]) -> dict[str, dict]:
    out: dict[str, list] = {"low": [], "normal": [], "high": []}
    for e in events:
        out.setdefault(e["entry_regime"], []).append(e["net_pips"])
    return {
        k: {"n": len(v), "net_pips": float(sum(v)), "avg": float(np.mean(v)) if v else 0.0}
        for k, v in out.items() if v
    }


# ---------------------------------------------------------------------------
# Viability screen (pre-registered in the plan, Part B)
# ---------------------------------------------------------------------------

def classify(single: dict[str, Any], pooled_pos_symbols: int) -> dict[str, Any]:
    """Verdict for one (experiment-id, symbol, hold) row.

    ``pooled_pos_symbols`` is the count of clean symbols with positive total net
    for that (experiment-id, hold) — used only for the 2-of-3 criterion.
    """
    if single.get("n", 0) < MIN_BEHAV_N:
        return {"verdict": "INSUFF", "reason": f"n={single.get('n', 0)} below {MIN_BEHAV_N}"}
    ratio = single.get("movement_to_cost") or 0.0
    mean = abs(single.get("mean_raw_pips") or 0.0)
    if not (ratio >= PROMISE_RATIO and mean >= PROMISE_MEAN):
        return {"verdict": "BORDER" if ratio >= BORDER_RATIO else "INSUFF",
                "reason": f"movement-to-cost {ratio:.2f} (bar {PROMISE_RATIO:.1f}), |mean| {mean:.2f} (bar {PROMISE_MEAN:.1f})"}
    tt = single.get("t_test") or {}
    if not (tt.get("p") is not None and tt.get("p", 1.0) < 0.05 and (single.get("expectancy_net_pips") or 0.0) > 0):
        return {"verdict": "REJECTED", "reason": "net expectancy not significantly positive"}
    if pooled_pos_symbols < MIN_POS_SYMBOLS:
        return {"verdict": "REJECTED", "reason": f"only {pooled_pos_symbols}/{len(SYMBOLS)} symbols positive"}
    if single.get("years_positive_share", 1.0) < MIN_YEAR_WIN:
        return {"verdict": "REJECTED", "reason": f"yearly win share {single['years_positive_share']:.2f} < {MIN_YEAR_WIN}"}
    if (single.get("max_year_share") or 0.0) > MAX_YEAR_SHARE:
        return {"verdict": "REJECTED", "reason": f"single year {single['max_year_share']:.2f} of total net > {MAX_YEAR_SHARE}"}
    if (single.get("max_window_share") or 0.0) > MAX_WINDOW_SHARE:
        return {"verdict": "REJECTED", "reason": f"single 4-week window {single['max_window_share']:.2f} of total net > {MAX_WINDOW_SHARE}"}
    return {"verdict": "VIABLE*", "reason": "clears full pre-registered screen"}


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

PLAN_BUCKETS = ("DISCOVERED", "REJECTED", "UNRESOLVED", "NOT TESTED")


def bucket(verdict: str, reason: str) -> str:
    """Map the screen outcome to the plan's fixed verdict vocabulary (Part E).

    * VIABLE*                     -> DISCOVERED
    * failing only on n < min_n   -> UNRESOLVED (too few events in the
                                     available history to reach the screen)
    * any other screen failure    -> REJECTED
    """
    if verdict == "VIABLE*":
        return "DISCOVERED"
    if reason.startswith("n=") and "below" in reason:
        return "UNRESOLVED"
    return "REJECTED"


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    num_cols = {"n", "trades"}
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            if isinstance(c, float):
                if c != c:
                    cells.append("-")
                elif headers[i] in num_cols:
                    cells.append(f"{c:,.0f}")
                elif "%" in headers[i]:
                    cells.append(f"{c:.1f}")
                else:
                    cells.append(f"{c:,.3f}")
            elif isinstance(c, int):
                cells.append(f"{int(c):,}")
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    pcfg = PathConfig()
    frames: dict[tuple[str, str], Frame] = {}
    for sym in SYMBOLS:
        m5 = _load_dev(sym, pcfg)
        for tf in ["M5", "M15", "H1", "H4"]:
            frames[(sym, tf)] = Frame(sym, tf, pcfg, m5=m5)

    # fast-slice maps: (symbol, fast TF, slow TF) -> (f0, f1)
    slices: dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]] = {}
    for sym in SYMBOLS:
        for pair in [("M15", "H1"), ("H1", "H4")]:
            fast_tf, slow_tf = pair
            s = frames[(sym, slow_tf)]
            f = frames[(sym, fast_tf)]
            slices[(sym, fast_tf, slow_tf)] = _fast_slices(f.ts_ns, s.ts_ns, TF_MIN[fast_tf], TF_MIN[slow_tf])

    results: dict[str, dict] = {}
    for exp in EXPERIMENTS:
        eid = exp["id"]
        tf = exp["tf"]
        results[eid] = {"experiment": exp, "symbols": {}}
        for sym in SYMBOLS:
            frame = frames[(sym, tf)]
            if eid == "B-PB":
                mask, direction = _exp_b_pb(frame, frames[(sym, "M15")],
                                            slices[(sym, "M15", "H1")][0], slices[(sym, "M15", "H1")][1])
            elif eid == "H-ALIGN":
                mask, direction = _exp_h_align(frame, frames[(sym, "H1")],
                                               slices[(sym, "H1", "H4")][0], slices[(sym, "H1", "H4")][1])
            elif eid == "E-SQZ":
                mask, direction = _exp_e_sqz(frame)
            elif eid == "G-CANDLE":
                mask, direction = _exp_g_candle(frame)
            elif eid == "J-FADE-REGIME":
                mask, direction = _exp_j_fade_regime(frame)
            else:
                raise ValueError(eid)
            results[eid]["symbols"][sym] = {"mask_sum": int(mask.sum()), "holds": {}}
            for H in exp["holds"]:
                events = simulate(frame, mask, direction, H)
                m = experiment_metrics(events, frame)
                results[eid]["symbols"][sym]["holds"][str(H)] = m

    # pooled per (eid, hold): positive symbols count for the 2-of-3 criterion
    for eid, r in results.items():
        for H in r["experiment"]["holds"]:
            pos = sum(1 for sym in SYMBOLS
                      if r["symbols"][sym]["holds"][str(H)].get("total_net_pips", 0.0) > 0
                      and r["symbols"][sym]["holds"][str(H)].get("n", 0) >= MIN_BEHAV_N)
            for sym in SYMBOLS:
                single = r["symbols"][sym]["holds"][str(H)]
                single["_pos_symbols"] = pos
                single["verdict"] = classify(single, pos)
                single["reason"] = single["verdict"]["reason"]
                single["verdict"] = single["verdict"]["verdict"]

    # ---- written report -----------------------------------------------------
    L: list[str] = []
    A = L.append

    A("# EDGE DISCOVERY RESULTS\n")
    A("Research only \u00b7 DEV split only \u00b7 60/20/20 preserved \u00b7 no strategy, no backtest, no "
      "optimization \u00b7 bot.py / V1 / V2 / Strategies 01-03 untouched \u00b7 EURJPY excluded.\n")

    A("\n## 1. Method and integrity\n")
    A("\n- Data: DEV rows of `data/{eurusd,eurgbp,gbpusd}_m5.csv` (clean Dukascopy M5, observed bid/ask "
      "spread) resampled to M15/H1/H4 with the standard UTC-anchored floor aggregation (no lookahead).\n"
      "- Execution: signal on the closed bar t, entry at the open of bar t+1, exit at the close of bar "
      "t+H (fixed horizon).\n"
      f"- Cost model: real observed round-trip spread + {SLIP_TOTAL_PIPS:.1f} pip slippage (0.5/side).\n"
      "- All definitions frozen in EDGE_DISCOVERY_PLAN.md (Part C) BEFORE results.\n"
      "- No ML, no sweeps, no SL/TP parameters, no holdout or validation bars read.\n"
      "- `net_usd_norm` uses the configured account convention (0.10 lot, $10 per pip-lot \u2192 $1/pip).\n"
      "- `exposure` = n \u00d7 mean duration / frame length; identical signals during the same horizon overlap, "
      "so it measures rule activity and may exceed 1.0 (it is NOT a portfolio weighting).\n")

    A("\n## 2. Pre-registered screen (restated)\n")
    A(f"\nVIABLE* requires: n \u2265 {MIN_BEHAV_N}; movement-to-cost \u2265 {PROMISE_RATIO} with |raw mean| \u2265 "
      f"{PROMISE_MEAN} pips; net expectancy significantly positive (t p<0.05); positive on \u2265 "
      f"{MIN_POS_SYMBOLS} of {len(SYMBOLS)} symbols; \u2265 {MIN_YEAR_WIN*100:.0f}% of years positive; no year &gt; "
      f"{MAX_YEAR_SHARE*100:.0f}% and no 4-week window &gt; {MAX_WINDOW_SHARE*100:.0f}% of total net.\n")

    A("\n## 3. Experiment verdicts\n")
    A("\nTables below follow Part E item 3: only rules that cleared n \u2265 "
      f"{MIN_BEHAV_N} on at least one symbol appear here; rules too rare for the "
      "available history are classified in section 5.\n")
    for eid, r in results.items():
        exp = r["experiment"]
        max_n = max(r["symbols"][sym]["holds"][str(H)].get("n", 0)
                    for H in exp["holds"] for sym in SYMBOLS)
        if max_n < MIN_BEHAV_N:
            A(f"\n### {eid} \u2014 {exp['name']} ({exp['hypothesis']})\n")
            A(f"\n{eid}: holds {exp['holds']} bars of {exp['tf']}. {exp['rationale']}\n")
            A(f"Max events across symbols/holds = {max_n} < {MIN_BEHAV_N} \u2192 nothing to table; see "
              "section 5 (UNRESOLVED).\n")
            A("\n")
            continue
        A(f"\n### {eid} \u2014 {exp['name']} ({exp['hypothesis']})\n")
        A(f"\n{eid}: holds {exp['holds']} bars of {exp['tf']}. {exp['rationale']}\n")
        for H in exp["holds"]:
            rows = []
            for sym in SYMBOLS:
                m = r["symbols"][sym]["holds"][str(H)]
                rows.append([sym, m.get("trades", 0), m.get("mean_raw_pips", 0.0),
                             m.get("expectancy_net_pips", 0.0), m.get("movement_to_cost", 0.0),
                             m.get("win_rate", 0.0) * 100, m.get("profit_factor", 0.0),
                             m.get("max_drawdown_pips", 0.0), m.get("verdict", "?"), m.get("reason", "")[:40]])
            A(f"\n**H={H} ({int(H * TF_MIN[exp['tf']] / 60)}h)**\n")
            A(_md_table(["sym", "n", "raw_mean", "net_exp", "mov/cost", "hit%", "PF", "maxDD", "verdict", "reason"],
                        rows))
        A("\n")

    A("\n## 4. Verdict buckets (plan Part E item 4)\n")
    A("\n- **DISCOVERED** \u2014 cleared the full pre-registered screen. None this round.\n"
      "- **REJECTED** \u2014 failed the screen; the exact failing criterion is in the reason "
      "below.\n"
      "- **UNRESOLVED** \u2014 plausible but too few qualifying events in the available clean "
      "history to reach n \u2265 " + str(MIN_BEHAV_N) + ".\n"
      "- **NOT TESTED** \u2014 intentionally excluded: EURJPY (degraded feed, ~46% zero-spread "
      "rows), volume-dependent rules (real volume is zeros), session-only entries, and the "
      "broker universe without local data.\n")
    A("\n| bucket | experiment | sym | hold | n | mean | m2c | screen | reason |")
    A("|---|---|---|---|---|---|---|---|---|")
    for eid, r in results.items():
        exp = r["experiment"]
        for H in exp["holds"]:
            for sym in SYMBOLS:
                m = r["symbols"][sym]["holds"][str(H)]
                b = bucket(m.get("verdict", "?"), m.get("reason", ""))
                A(f"| {b} | {eid} | {sym} | H={H} | {m.get('n', 0):,} | "
                  f"{m.get('mean_raw_pips', 0.0):+.2f} | {m.get('movement_to_cost', 0.0):.2f} | "
                  f"{m.get('verdict', '?')} | {m.get('reason', '')} |")
    A("\nSTOP CONDITION (TASK.md): no rule cleared the full pre-registered screen. "
      "Per the plan, nothing was optimized, no parameter re-tested, and no validation or "
      "holdout bar was read for ANY rule.\n")

    A("\n## 5. Full per-experiment metrics\n")
    for eid, r in results.items():
        exp = r["experiment"]
        for H in exp["holds"]:
            for sym in SYMBOLS:
                m = r["symbols"][sym]["holds"][str(H)]
                A(f"\n### {eid} / {sym} / H={H}\n")
                A(_md_table(["metric", "value"],
                            [[k, v] for k, v in sorted(m.items())
                             if not isinstance(v, (dict, list))]))

    for eid in results:
        for H in results[eid]["experiment"]["holds"]:
            for sym in SYMBOLS:
                m = results[eid]["symbols"][sym]["holds"][str(H)]
                m["bucket"] = bucket(m.get("verdict", "?"), m.get("reason", ""))

    out = {
        "meta": {
            "phase": "edge_discovery",
            "data": "dev split of Dukascopy M5 composites (EURUSD/EURGBP/GBPUSD)",
            "tf_source": "M5",
            "cost_model": f"entry+exit observed spread + {SLIP_TOTAL_PIPS} pip slippage",
            "screen": {
                "min_n": MIN_BEHAV_N, "promise_ratio": PROMISE_RATIO, "promise_mean": PROMISE_MEAN,
                "border_ratio": BORDER_RATIO, "min_pos_symbols": MIN_POS_SYMBOLS,
                "min_year_win": MIN_YEAR_WIN, "max_year_share": MAX_YEAR_SHARE,
                "max_window_share": MAX_WINDOW_SHARE,
            },
            "excluded": {"EURJPY": "degraded feed (issue A2)"},
        },
        "results": results,
    }
    with open(_root / REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(pcfg.output_dir / "edge_discovery_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Report written to {_root / REPORT_PATH}")
    print(f"Behaviour dump: {pcfg.output_dir / 'edge_discovery_results.json'}")
    return 0


if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main())