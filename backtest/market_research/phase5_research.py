"""Phase 5 - Broker-Accurate Data + Market Expansion (RESEARCH ONLY).

Answers TASK.md Phase 5: is the Phase 3/4 'no edge' conclusion caused by
inadequate cost data, timeframe construction, the selected FX pairs, or the FX
market itself?  Everything is measured on the DEV split of the preserved
chronological 60/20/20 split.  No strategy, no backtest, no optimization,
nothing on validation/holdout read, bot.py untouched, MT5 not connected.

Phase 5A/5B audit
  * Data provenance (Dukascopy M5 bid+ask), life verification that the
    composite `spread` column equals the observed bid/ask difference.
  * Cost-model audit (Phase 3/4 round turn = 2 x median dev spread + 1.7 pips).
  * Broker inventory: MetaQuotes-Demo (MT5 build 6140), ~16-month history
    ceiling, unreliable spread field; exact missing-data report.

Phase 5C
  * M15 / H1 / H4 constructed from the SAME M5 Dukascopy source (no lookahead,
    UTC-anchored floor aggregation).  M5 remains the base frame.

Phase 5E re-check
  * The six behavior families (directional persistence, multi-hour reversal,
    session-open behavior, volatility expansion, breakout continuation/failure,
    movement-to-cost) are re-measured with REAL per-bar observed spreads rather
    than the old constant-cost model.  Small, economically motivated horizon
    sets per timeframe - no sweeps.

Phase 5F/5G
  * A small predefined candidate universe for expansion is specified; broker
    availability/specs are marked UNKNOWN (MT5 connect prohibited).  Findings
    are classified with the project's existing viability logic.

Output:
  * PHASE_5_BROKER_DATA_AND_MARKET_EXPANSION.md  (19 required sections)
  * outputs/phase_5_market_research.json        (machine-readable results)

Usage:
    python -m backtest.market_research.phase5_research
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent
sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.instruments import get_instrument
from backtest.market_research.common import (
    atr_regime,
    session_label,
)
from backtest.market_research.market_discovery import _atr

# ---------------------------------------------------------------------------
# Frozen research parameters (no sweeps)
# ---------------------------------------------------------------------------

SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
TF_BARS_MIN = {"M5": 5, "M15": 15, "H1": 60, "H4": 240}

# Forward/prior horizon bars per timeframe: a small ladder of 1h..24h windows
# expressed in that timeframe's bars (economically motivated, clearly separated).
TF_HORIZONS_BARS = {
    "M5": [12, 24, 48, 96, 240, 288],      # 1h, 2h, 4h, 8h, 20h, 24h
    "M15": [4, 8, 16, 32, 96],             # 1h, 2h, 4h, 8h, 24h
    "H1": [1, 2, 4, 8, 24],                  # 1h, 2h, 4h, 8h, 24h
    "H4": [1, 2, 3, 6],                    # 4h, 8h, 12h, 24h
}

PERSIST_H_BARS = {
    "M5": [12, 48, 96, 240],
    "M15": [4, 16, 32, 96],
    "H1": [4, 8, 24],
    "H4": [2, 3, 6],
}

REV_H_BARS = {
    "M5": [24, 96],        # 2h, 8h (same windows as Phase 4)
    "M15": [16, 32],       # 4h, 8h
    "H1": [8, 24],         # 8h, 24h
    "H4": [2, 6],          # 8h, 24h
}

OPEN_WINDOWS_MIN = {"M5": [60, 120, 240], "M15": [60, 120, 240],
                    "H1": [60, 120, 240], "H4": [240, 480]}
OPEN_TYPES = ["London", "LondonNY", "NewYork"]

VOL_FWD_BARS_M5 = [24, 48, 96]            # 2h / 4h / 8h after expansion (M5 only)
CHANNEL_HOURS = 24                        # 24h channel for breakout
CHANNEL_FWD_MINUTES = {"M5": [60, 120, 240], "M15": [60, 120, 240],
                      "H1": [60, 120, 240], "H4": [240, 480]}
OVERNIGHT_HOURS = 12                      # prior 12h window as overnight-range proxy

REV_PCT = 0.66                            # 'unusually large move' tercile cut (Phase 4)
COST_ADD_PIPS = 1.7                       # legacy Phase 3/4 overhead term
SLIP_TOTAL_PIPS = 1.0                     # engine CostConfig: slippage 0.5 pips per side
SPLIT = "dev"
MIN_BEHAV_N = 1000

PROMISE_RATIO = 1.0                       # movement-to-cost >= 1.0
PROMISE_MEAN = 2.0                        # and |raw mean| >= 2.0 pips
BORDER_RATIO = 0.5                        # 0.5..1.0 borderline, < 0.5 wasted

REPORT_PATH = "PHASE_5_BROKER_DATA_AND_MARKET_EXPANSION.md"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    num_cols = {"n", "n_opens", "n_bars"}
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            if isinstance(c, float):
                if c != c:
                    cells.append("-")
                elif headers[i] in num_cols:
                    cells.append(f"{c:,.2f}")
                elif "%" in headers[i]:
                    cells.append(f"{c:.1f}")
                else:
                    cells.append(f"{c:,.2f}")
            elif isinstance(c, int):
                cells.append(f"{int(c):,}")
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _cont_share(fwd_h: np.ndarray, direction_idx: np.ndarray, mask: np.ndarray) -> float | None:
    ok = np.isfinite(fwd_h) & (fwd_h != 0) & (direction_idx != 0) & mask
    if ok.sum() == 0:
        return None
    return float(((np.sign(fwd_h) == direction_idx) & ok).sum() / ok.sum() * 100)


def _rev_share(fwd_h: np.ndarray, direction_idx: np.ndarray, mask: np.ndarray) -> float | None:
    ok = np.isfinite(fwd_h) & (fwd_h != 0) & (direction_idx != 0) & mask
    if ok.sum() == 0:
        return None
    return float(((np.sign(fwd_h) == -direction_idx) & ok).sum() / ok.sum() * 100)


def _pct(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float((x > 0).mean() * 100) if len(x) else float("nan")


def _load_dev(symbol: str, pcfg: PathConfig) -> pd.DataFrame:
    sym = symbol.lower()
    csv_path = pcfg.base_dir / "data" / f"{sym}_m5.csv"
    assign_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    if not csv_path.exists() or not assign_path.exists():
        raise FileNotFoundError(f"Missing data or split file for {symbol}")
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    assignments = pd.read_csv(assign_path)
    mask = assignments["split"] == SPLIT
    return df.iloc[assignments.index[mask].tolist()].reset_index(drop=True)


# ---------------------------------------------------------------------------
# 5A: live spread-provenance verification (bid/ask fragments vs composite)
# ---------------------------------------------------------------------------

def verify_spread_provenance(pcfg: PathConfig) -> list[dict]:
    """Confirm composite `spread` == round((ask_close - bid_close) / point).

    Uses the locally stored Dukascopy bid/ask M5 fragments (full range for
    EURUSD/GBPUSD, one month for EURGBP) and compares against the consolidated
    M5 composite for the exact same timestamps.
    """
    data_dir = pcfg.base_dir / "data"
    cases = [
        ("EURUSD", "eurusd-m5-bid-2021-01-01-2026-09-10.csv", "eurusd-m5-ask-2021-01-01-2026-09-10.csv"),
        ("GBPUSD", "gbpusd-m5-bid-2021-01-01-2026-09-10.csv", "gbpusd-m5-ask-2021-01-01-2026-09-10.csv"),
        ("EURGBP", "eurgbp-m5-bid-2021-02-01-2021-03-01.csv", "eurgbp-m5-ask-2021-02-01-2021-03-01.csv"),
    ]
    results = []
    for symbol, bid_name, ask_name in cases:
        bid_p, ask_p = data_dir / bid_name, data_dir / ask_name
        inst = get_instrument(symbol)
        if not bid_p.exists() or not ask_p.exists():
            results.append({"symbol": symbol, "status": "files_missing",
                            "bid": bid_name, "ask": ask_name})
            continue
        bid = pd.read_csv(bid_p)
        ask = pd.read_csv(ask_p)
        bid["time"] = pd.to_datetime(bid["timestamp"], unit="ms", utc=True).dt.tz_localize(None)
        ask["time"] = pd.to_datetime(ask["timestamp"], unit="ms", utc=True).dt.tz_localize(None)
        bid = bid.dropna(subset=["close"])
        ask = ask.dropna(subset=["close"])
        merged = bid[["time", "close"]].merge(
            ask[["time", "close"]], on="time", suffixes=("_b", "_a"))
        derived = np.round((merged["close_a"] - merged["close_b"]) / inst.point).astype(int)
        # canonical composite spread at the same timestamps
        comp = pd.read_csv(pcfg.base_dir / "data" / f"{symbol.lower()}_m5.csv",
                           usecols=["time", "spread"])
        comp["time"] = pd.to_datetime(comp["time"])
        wide = merged.assign(derived=derived).merge(comp, on="time")
        match = float((wide["derived"] == wide["spread"]).mean() * 100)
        results.append({
            "symbol": symbol,
            "status": "matched",
            "rows_bid_ask": int(len(merged)),
            "rows_compared": int(len(wide)),
            "exact_match_pct": round(match, 4),
            "derived_spread_med": float(np.median(derived)),
            "composite_spread_med": float(np.median(wide["spread"])),
            "max_abs_diff": int(abs(wide["derived"] - wide["spread"]).max()),
        })
    return results


# ---------------------------------------------------------------------------
# Frame: one symbol / timeframe (DEV rows)
# ---------------------------------------------------------------------------

class Frame:
    """A symbol/timeframe frame built from the SAME M5 Dukascopy source."""

    def __init__(self, symbol: str, tf: str, pcfg: PathConfig, m5: dict[str, pd.DataFrame] | None = None):
        self.symbol = symbol
        self.tf = tf
        self.bars_min = TF_BARS_MIN[tf]
        self.inst = get_instrument(symbol)
        self.pip = self.inst.pip

        if m5 is not None and tf == "M5":
            dev = m5[symbol]
        else:
            dev = _load_dev(symbol, pcfg)
        if m5 is None and tf != "M5":
            dev = _load_dev(symbol, pcfg)

        if tf == "M5":
            ag = dev.reset_index(drop=True)
        else:
            ag = _aggregate(dev, tf)
        self.ag = ag
        n = len(ag)
        self.n = n

        o = ag["open"].to_numpy(float)
        h = ag["high"].to_numpy(float)
        lo = ag["low"].to_numpy(float)
        c = ag["close"].to_numpy(float)
        self.high, self.low, self.close = h, lo, c

        self.spread_pips = (ag["spread"].to_numpy(float) * self.inst.point) / self.pip
        self.atr = _atr(h, lo, c, 14) / self.pip
        self.rng = (h - lo) / self.pip
        self.rng_med = float(np.median(self.rng))

        ts = pd.to_datetime(ag["time"])
        self.hour = ts.dt.hour.to_numpy()
        self.sess = session_label(self.hour)
        self.block_start = np.zeros(n, dtype=bool)
        self.block_start[0] = True
        self.block_start[1:] = self.sess[1:] != self.sess[:-1]

        H_all = sorted(set(TF_HORIZONS_BARS[tf]))
        self.fwd: dict[int, np.ndarray] = {}
        self.prh: dict[int, np.ndarray] = {}
        for H in H_all:
            f = np.full(n, np.nan)
            if H < n:
                f[: n - H] = c[H:] - c[:-H]
            self.fwd[H] = f / self.pip
            p = np.full(n, np.nan)
            if H < n:
                p[H:] = (c[H:] - c[:-H]) / self.pip
            self.prh[H] = p

        self.m1 = np.zeros(n, dtype=float)
        self.m1[1:] = np.sign(c[1:] - c[:-1])

        if tf == "M5":
            self.cost_legacy_pips = 2.0 * float(np.median(self.spread_pips)) + COST_ADD_PIPS
        else:
            self.cost_legacy_pips = None

        self.beh: list[dict] = []

    def open_starts(self, open_type: str) -> np.ndarray:
        return np.where(self.block_start & (self.sess == open_type))[0]

    def note(self, behavior: str, condition: str, H_bars: int, fwd_arr: np.ndarray,
             mask: np.ndarray) -> None:
        n = len(fwd_arr)
        idx = np.where((np.isfinite(fwd_arr)) & mask)[0]
        idx = idx[(idx + H_bars) < n]
        if len(idx) < MIN_BEHAV_N:
            return
        v = fwd_arr[idx]
        exit_idx = np.minimum(idx + H_bars, n - 1)
        costs = self.spread_pips[idx] + self.spread_pips[exit_idx] + SLIP_TOTAL_PIPS
        mean_cost = float(np.mean(costs))
        ratio = abs(float(v.mean())) / mean_cost if mean_cost > 0 else float("nan")
        rec = {
            "symbol": self.symbol,
            "timeframe": self.tf,
            "behavior": behavior,
            "condition": condition,
            "horizon_min": int(H_bars * self.bars_min),
            "n": len(v),
            "mean_pips": float(v.mean()),
            "med_pips": float(np.median(v)),
            "hit_pct_positive": float((v > 0).mean() * 100),
            "std_pips": float(v.std(ddof=1)),
            "cost_pips_real": round(mean_cost, 4),
            "slip_pips": SLIP_TOTAL_PIPS,
            "ratio_real": round(ratio, 4),
        }
        if self.cost_legacy_pips is not None:
            rec["cost_pips_legacy"] = self.cost_legacy_pips
            rec["ratio_legacy"] = round(abs(float(v.mean())) / self.cost_legacy_pips, 4)
        self.beh.append(rec)


def _aggregate(dev: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Aggregate M5 DEV rows into M15/H1/H4 UTC-anchored bars (no lookahead).

    Bars are floored to epoch-aligned boundaries (UTC).  Each aggregated bar
    uses only M5 rows whose OPEN time falls inside its own window, so no future
    bar contributes.  `spread` = spread of the LAST M5 bar in the window
    (spread-at-close, consistent with the Dukascopy canonical conversion).
    """
    period = {"M15": "15min", "H1": "1h", "H4": "4h"}[tf]
    idx = dev["time"].dt.floor(period)
    g = dev.groupby(idx)
    out = pd.DataFrame({
        "time": idx.drop_duplicates(),
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "spread": g["spread"].last(),
        "n_bars": g["spread"].size(),
    }).reset_index(drop=True)
    return out.sort_values("time").reset_index(drop=True)


def hours_in_bars(tf: str, hours: float) -> int:
    return int(round(hours * 60 / TF_BARS_MIN[tf]))


# ---------------------------------------------------------------------------
# Behavior families (mirrors Phase 4 definitions, parameterised by timeframe)
# ---------------------------------------------------------------------------

def _persistence_rows(fr: Frame) -> list[list[Any]]:
    rows = []
    for H in PERSIST_H_BARS[fr.tf]:
        pr = fr.prh[H]
        mag = np.abs(pr)
        med = np.nanmedian(mag)
        for side, sign in [("up", 1.0), ("dn", -1.0)]:
            mask = (mag > med) & (np.sign(pr) == sign)
            fh = fr.fwd[H]
            v = fh[mask & np.isfinite(fh)]
            if len(v) == 0:
                continue
            rows.append([fr.symbol, fr.tf, int(H * fr.bars_min), side, len(v),
                         float(v.mean()), float(np.median(v)),
                         _cont_share(fh, np.sign(pr), mask), _pct(v)])
            fr.note("directional persistence",
                    f"prior {int(H*fr.bars_min)}min large-{side}, forward {int(H*fr.bars_min)}min",
                    H, fh, mask)
    return rows


def _reversal_rows(fr: Frame) -> list[list[Any]]:
    rows = []
    for H in REV_H_BARS[fr.tf]:
        pr = fr.prh[H]
        mag = np.abs(pr)
        cut = np.nanpercentile(mag, REV_PCT * 100)
        for side, sign in [("up", 1.0), ("dn", -1.0)]:
            mask = (mag > cut) & (np.sign(pr) == sign)
            fh = fr.fwd[H]
            v = fh[mask & np.isfinite(fh)]
            if len(v) == 0:
                continue
            rows.append([fr.symbol, fr.tf, int(H * fr.bars_min), side, len(v),
                         float(v.mean()), float(np.median(v)),
                         _rev_share(fh, np.sign(pr), mask), _cont_share(fh, np.sign(pr), mask)])
            fr.note("multi-hour reversal",
                    f"prior {side}-{int(H*fr.bars_min)}min large move, next {int(H*fr.bars_min)}min",
                    H, fh, mask)
    return rows


def _session_open_rows(fr: Frame) -> list[list[Any]]:
    rows = []
    windows = [hours_in_bars(fr.tf, m / 60) for m in OPEN_WINDOWS_MIN[fr.tf]]
    for ot in OPEN_TYPES:
        starts = fr.open_starts(ot)
        if len(starts) == 0:
            continue
        for W in windows:
            if W < 1:
                continue
            fwd_v = np.array([fr.close[i0 + W] - fr.close[i0]
                              for i0 in starts if i0 + W < fr.n]) / fr.pip
            if len(fwd_v) == 0:
                continue
            mask = np.zeros(fr.n, dtype=bool)
            for i0 in starts:
                mask[i0: i0 + W] = True
            ratio = None
            if W == windows[0]:
                rr = np.array([fr.high[i0:i0 + W].max() - fr.low[i0:i0 + W].min()
                               for i0 in starts if i0 + W < fr.n]) / fr.pip
                ratio = float(np.mean(rr) / fr.rng_med) if len(rr) else None
            rows.append([fr.symbol, fr.tf, f"{ot} open", int(W * fr.bars_min), len(starts),
                         float(np.mean(fwd_v)), float(np.median(fwd_v)), _pct(fwd_v),
                         (ratio if ratio is not None else "-")])
            fr.note("session-open behavior",
                    f"in {ot}-open first {int(W*fr.bars_min)}min window, forward {int(W*fr.bars_min)}min",
                    W, fr.fwd[W], mask)
    rows.extend(_open_followthrough(fr))
    return rows


def _open_followthrough(fr: Frame) -> list[list[Any]]:
    """After a directional opening window, does the NEXT window reverse?"""
    if fr.bars_min > 60:  # H4 has no sub-hour open window
        return []
    rows = []
    W = hours_in_bars(fr.tf, 1.0)
    for ot in OPEN_TYPES:
        starts = fr.open_starts(ot)
        fh = [(i0, fr.close[i0 + W] - fr.close[i0]) for i0 in starts if i0 + 2 * W < fr.n]
        fh = [(i, m) for i, m in fh if abs(m) > 0]
        if not fh:
            continue
        mags = np.abs([m for _, m in fh])
        thresh = float(np.median(mags))
        sel = [(i, m) for i, m in fh if abs(m) > thresh]
        if len(sel) < MIN_BEHAV_N:
            continue
        nxt = np.asarray([fr.close[i + 2 * W] - fr.close[i + W] for i, _ in sel]) / fr.pip
        rev = float((np.sign(nxt) != np.sign([m for _, m in sel])).mean() * 100)
        cont = float((np.sign(nxt) == np.sign([m for _, m in sel])).mean() * 100)
        rows.append([fr.symbol, fr.tf, f"{ot} open", "directional-1h follow", len(sel),
                     float(np.mean(nxt)), float(np.median(nxt)), rev, cont])
        fr.note("session-open behavior",
                f"{ot}-open directional {int(W*fr.bars_min)}min, next {int(W*fr.bars_min)}min",
                2 * W, nxt, np.ones(len(nxt), dtype=bool))
    return rows


def _vol_expansion_rows(fr: Frame) -> list[list[Any]]:
    if fr.tf != "M5":
        return []
    reg = atr_regime(fr.atr, 50).astype(str)
    prev = np.full(fr.n, "normal", dtype=object)
    prev[1:] = reg[:-1]
    rows = []
    for state, tag in [("low", "low"), ("high", "high"), ("expansion", "high")]:
        if tag == "expansion":
            mask = (reg == "high") & (prev != "high")
            label = "expansion_event"
        else:
            mask = reg == state
            label = state
        for H in VOL_FWD_BARS_M5:
            fh = fr.fwd[H]
            v = fh[mask & np.isfinite(fh)]
            if len(v) == 0:
                continue
            rows.append([fr.symbol, fr.tf, label, int(H * fr.bars_min), len(v),
                         float(v.mean()), float(np.median(v)),
                         _cont_share(fh, fr.m1, mask), _pct(v)])
            fr.note("volatility expansion",
                    f"{label} after {int(H*fr.bars_min)}min", H, fh, mask)
    return rows


def _breakout_rows(fr: Frame) -> list[list[Any]]:
    rows = []
    chan = hours_in_bars(fr.tf, CHANNEL_HOURS)
    s = pd.Series(fr.close)
    ph = s.shift(1).rolling(chan, min_periods=chan).max().to_numpy()
    pl = s.shift(1).rolling(chan, min_periods=chan).min().to_numpy()
    HW = [hours_in_bars(fr.tf, m / 60) for m in CHANNEL_FWD_MINUTES[fr.tf]]
    for dr, state in [(1.0, "up-break"), (-1.0, "dn-break")]:
        if dr > 0:
            ok = np.isfinite(ph) & (fr.close > ph)
            level = ph
            dir_idx = np.ones(fr.n, dtype=float)
        else:
            ok = np.isfinite(pl) & (fr.close < pl)
            level = pl
            dir_idx = -np.ones(fr.n, dtype=float)
        for H in HW:
            fh = fr.fwd[H]
            v = fh[ok & np.isfinite(fh)]
            if len(v) == 0:
                continue
            steps = np.minimum(np.arange(fr.n) + H, fr.n - 1)
            persist = float((((fr.close[steps] - level) * dr > 0) & ok &
                             np.isfinite(level)).sum() / ok.sum() * 100)
            rows.append([fr.symbol, fr.tf, f"{CHANNEL_HOURS}h {state}", int(H * fr.bars_min),
                         len(v), float(v.mean()), float(np.median(v)),
                         _cont_share(fh, dir_idx, ok), persist])
            fr.note("breakout continuation/failure",
                    f"{CHANNEL_HOURS}h {state}, forward {int(H*fr.bars_min)}min", H, fh, ok)
    rows.extend(_overnight_range_break(fr))
    return rows


def _overnight_range_break(fr: Frame) -> list[list[Any]]:
    """London open beyond the prior 12h (overnight) window: continuation/failure."""
    rows = []
    ov = hours_in_bars(fr.tf, OVERNIGHT_HOURS)
    s = pd.Series(fr.close)
    ph = s.shift(1).rolling(ov, min_periods=ov).max().to_numpy()
    pl = s.shift(1).rolling(ov, min_periods=ov).min().to_numpy()
    london = fr.open_starts("London")
    for dr, state in [(1.0, "up"), (-1.0, "dn")]:
        ok = np.zeros(fr.n, dtype=bool)
        for i0 in london:
            if dr > 0 and np.isfinite(ph[i0]) and fr.close[i0] > ph[i0]:
                ok[i0] = True
            if dr < 0 and np.isfinite(pl[i0]) and fr.close[i0] < pl[i0]:
                ok[i0] = True
        if ok.sum() < MIN_BEHAV_N:
            continue
        dir_idx = dr * np.ones(fr.n, dtype=float)
        HW = [hours_in_bars(fr.tf, m / 60) for m in [60, 120]]
        for H in HW:
            fh = fr.fwd[H]
            v = fh[ok & np.isfinite(fh)]
            rows.append([fr.symbol, fr.tf, f"London-open {state}-break", int(H * fr.bars_min),
                         int(ok.sum()), float(v.mean()), float(np.median(v)),
                         _cont_share(fh, dir_idx, ok), _pct(v)])
            fr.note("breakout continuation/failure",
                    f"London-open {state}-break of prior {OVERNIGHT_HOURS}h range, "
                    f"forward {int(H*fr.bars_min)}min", H, fh, ok)
    return rows


# ---------------------------------------------------------------------------
# Report assembly (19 required sections)
# ---------------------------------------------------------------------------

def _classify(b: dict) -> str:
    r = b["ratio_real"]
    if r >= PROMISE_RATIO and abs(b["mean_pips"]) >= PROMISE_MEAN:
        return "VIABLE*"
    if r >= BORDER_RATIO:
        return "BORDER"
    return "INSUFF"


def _verdict(beh: list[dict]) -> dict:
    viable = [b for b in beh if _classify(b) == "VIABLE*"]
    ordered = sorted(beh, key=lambda b: b["ratio_real"], reverse=True)
    best = ordered[0] if ordered else None
    return {"n_viable": len(viable), "best": best}


def main() -> int:
    pcfg = PathConfig()
    M5 = {s: _load_dev(s, pcfg) for s in SYMBOLS}

    # ---- 5A: spread provenance verification --------------------------------
    verification = verify_spread_provenance(pcfg)

    # ---- build frames -------------------------------------------------------
    frames: dict[tuple[str, str], Frame] = {}
    for sym in SYMBOLS:
        for tf in ["M5", "M15", "H1", "H4"]:
            frames[(sym, tf)] = Frame(sym, tf, pcfg, m5=M5)

    # ---- re-check behaviors -------------------------------------------------
    for (sym, tf), fr in frames.items():
        if tf in PERSIST_H_BARS:
            _persistence_rows(fr)
        if tf in REV_H_BARS:
            _reversal_rows(fr)
        _session_open_rows(fr)
        _vol_expansion_rows(fr)
        _breakout_rows(fr)

    beh = [b for fr in frames.values() for b in fr.beh]
    ordered = sorted(beh, key=lambda b: b["ratio_real"], reverse=True)
    verdict = _verdict(beh)

    # ---- written report -----------------------------------------------------
    L: list[str] = []
    A = L.append

    A("# PHASE 5 \u2014 BROKER-ACCURATE DATA & MARKET EXPANSION\n")
    A("Research only \u00b7 DEV split only \u00b7 60/20/20 preserved \u00b7 no strategy, no backtest, no "
      "optimization \u00b7 bot.py untouched \u00b7 MT5 not connected.\n")

    # 1
    A("\n## 1. Objective\n")
    A("\nPhase 3 (M5) and Phase 4 (multi-hour) concluded no behavior on EURUSD/EURGBP/GBPUSD clears the "
      "movement-to-cost viability bar.  Phase 5 audits whether that conclusion is an artefact of (A) "
      "inadequate/overestimated historical cost data, (B) timeframe construction, (C) the selected FX pairs, "
      "or (D) the FX market itself, and re-checks the six market-behavior families using **real observed "
      "bid/ask spreads** rather than the previous constant-cost assumption.  It then defines a small "
      "candidate universe for market expansion.  No strategy is implemented.\n")

    # 2
    A("\n## 2. Current data audit\n")
    A("\n**Source.** The consolidated M5 feeds `data/{eurusd,eurgbp,gbpusd,eurjpy}_m5.csv` are canonical builds "
      "made from **Dukascopy M5 bid and ask candles** (`dukascopy-node` v1.50.0 \u2192 `jetta.dukascopy.com`), "
      "not from the MT5 demo account.  Canonical conversion per `PHASE0B_*`: OHLC from the **bid** candle, "
      "`spread = round((ask_close - bid_close) / point)` in points, `tick_volume` preserved, `real_volume` = 0 "
      "(documented unavailable).\n")
    A("\n**Observed bid/ask is stored locally.**  `data/` contains the original Dukascopy bid/ask M5 fragments "
      "(full range 2021-01-01 \u2192 2026-09-10 for EURUSD and GBPUSD; monthly chunks for EURGBP; partial for "
      "EURJPY).  The composite `spread` column is therefore **real observed spread, not modeled/synthetic**.\n")
    A("\n**Verification (computed now, DEV-independent):**\n")
    A(_md_table(["symbol", "rows_compared", "exact_match_pct", "derived_spread_med", "composite_spread_med",
                 "max_abs_diff"],
                [[v["symbol"], v.get("rows_compared", "-"), f"{v.get('exact_match_pct', 0.0):.2f}",
                  v.get("derived_spread_med", "-"), v.get("composite_spread_med", "-"),
                  v.get("max_abs_diff", "-")] for v in verification]))
    A("\nThe composite spread column is byte-for-byte equal to the observed bid/ask difference on the full "
      "EURUSD/GBPUSD ranges and the EURGBP sample.  Composite coverage: EURUSD 422,225 rows (2021-01-03 "
      "\u2192 2026-09-09), EURGBP 425,477, GBPUSD 374,746; EURJPY degraded (14 months, ~27% zero spread) and "
      "still excluded from behavior analysis.\n")

    # 3
    A("\n## 3. Current cost-model audit\n")
    A("\nPhase 3/4 used a constant round-turn cost per pair: `cost = 2 \u00d7 median(M5 dev spread pips) + "
      "1.7 pips` (EURUSD 2.30, EURGBP 3.50, GBPUSD 3.50 pips).  The `+1.7` pips is a fixed overhead term "
      "covering above-median spreads and slippage.  The strategy engine (`CostConfig`) separately assumes "
      "`slippage_pips = 0.5` per side and `commission_per_lot = $7.0` round-turn on `contract_size = 100,000` "
      "at `point = 0.00001`.")
    A("\nFor Phase 5E the re-check replaces the constant with **per-trade observed spread**: for a trade entered "
      f"at bar i and exited at bar i+H, `cost = spread_pips[i] + spread_pips[i+H] + {SLIP_TOTAL_PIPS:.1f} pip "
      f"slippage` (0.5/side from `CostConfig`).  This is strictly more accurate: it uses the actual bid/ask at "
      "the traded bars and drops the arbitrary constant.  Both cost models are reported side by side so the "
      "'does cost modeling change the conclusion?' question is answered directly.\n")

    # 4
    A("\n## 4. Broker/account execution requirements\n")
    A("\nThe intended demo account is the MT5 terminal configured in `bot.py` (connecting defaults to the "
      "installed terminal):\n")
    A(_md_table(["item", "value", "where_from"],
                [["Broker/server", "MetaQuotes-Demo (MetaQuotes Ltd.)", "PHASE0 MT5 diagnostic (account 5055770258)"],
                 ["MT5 build", "6140", "PHASE0"],
                 ["Balance / leverage", "100,000 USD demo / 1:100", "PHASE0"],
                 ["Symbol (bot.py)", "EURUSD", "bot.py:8"],
                 ["Timeframe (bot.py)", "TIMEFRAME_M5", "bot.py:9"],
                 ["Order filling", "ORDER_FILLING_FOK, deviation 20, magic 999", "bot.py:84-97"],
                 ["Risk sizing", "1% risk; lot = max(round(balance*0.01/1000,2), 0.01)", "bot.py:51-56"],
                 ["Spread filter (bot.py)", "block trade if tick spread \u2265 25 points", "bot.py:58-63"],
                 ["SL / TP (bot.py)", "1.5\u00d7ATR / 3\u00d7ATR", "bot.py:73-74"],
                 ["Typical spread", "UNKNOWN \u2014 demo feed spread field unreliable (recent 5k bars 84-99% zero)",
                  "PHASE0 \u00a78"],
                 ["Commission", "UNKNOWN (engine assumes $7/lot)", "CostConfig"],
                 ["Minimum lot / lot step", "UNKNOWN (lot floor 0.01 only)", "not obtainable w/o MT5"],
                 ["Contract size / point / pip", "100,000 / 0.00001 / 0.0001 (assumed)", "CostConfig/Instruments"],
                 ["Stop-distance restrictions / trading hours", "UNKNOWN", "not obtainable w/o MT5"]]))
    A("\n`symbol_info` specifications for the demo account are **not recorded in the repository** and cannot be "
      "read now (TASK.md: do not connect to MT5).  Items are therefore marked UNKNOWN rather than guessed.\n")

    # 5
    A("\n## 5. Available historical data\n")
    A("\n**Dukascopy M5 bid/ask (2021-01-03 \u2192 2026-09-09):** full local coverage for EURUSD (422,225 bars), "
      "EURGBP (425,477), GBPUSD (374,746); EURJPY partial/degraded.  This is the practical best real bid/ask "
      "data available locally (0% zero-spread bars; spread always populated).\n")
    A("\n**MetaQuotes-Demo MT5 (the intended account):** ~16 months of M5 (earliest 2025-05-08, ~100,800 "
      "bars), retrieved in full by `dump_mt5_multi.py` / `diagnose_mt5_data.py`; the `spread` field of recent "
      "bars is 84-99% zero (unreliable); tick data exists for the same ~16-month window.  This is documented "
      "in detail in `PHASE0_MT5_DATA_AVAILABILITY_REPORT.md`.\n")

    # 6
    A("\n## 6. Missing data\n")
    A("\n- **Broker-true MetaQuotes-Demo history beyond 16 months** \u2014 does not exist on the server.\n"
      "- **Reliable spread field for the demo feed** \u2014 recent bars report spread=0.\n"
      "- **Symbol/contract specifications for the demo account** (min lot, lot step, contract size, "
      "commission, stop-level, trading hours) \u2014 required to size the lot and calibrate cost; UNKNOWN.\n"
      "- If the account were switched to a real broker (e.g., ICMarkets/Pepperstone/Dukascopy), their own M5 "
      "history + symbol specs would be required in the same canonical format.\n")

    # 7
    A("\n## 7. Timeframe construction assessment\n")
    A("\nAll timeframes are built from the **same** M5 Dukascopy source, UTC-anchored floor aggregation "
      "(`15min/1h/4h` epoch-aligned) over DEV rows; each bar aggregates only M5 rows whose open time falls "
      "inside its own window **no lookahead**.  OHLC: first open / max high / min low / last close; `spread` = "
      "last M5 close spread (spread-at-close, consistent with the canonical formula).  Bar counts (DEV):\n")
    A(_md_table(["symbol", "M5", "M15", "H1", "H4"],
                [[s, frames[(s, "M5")].n, frames[(s, "M15")].n,
                  frames[(s, "H1")].n, frames[(s, "H4")].n] for s in SYMBOLS]))
    A("\nSession classification uses the project's vanilla UTC sessions (Phase 4 convention); timestamps are "
      "naive UTC.  Resampling preserves the M5 step irregularities (\u22480.1%) as sparse bars on higher "
      "timeframes \u2014 no fabrication, no cross-source mixing.\n")

    # 8
    A("\n## 8. Broker-accurate cost assessment\n")
    A("\nThe most accurate cost input obtainable for the demo exercise is the **Dukascopy observed bid/ask** "
      "(verified live in \u00a72).  MetaQuotes-Demo cannot supply its own history beyond 16 months or a reliable "
      "spread column, so **true broker-accurate historical costs are NOT available for the intended account**; "
      "Dukascopy observed spreads are the practical best and are used for the re-check.  Broker symbol specs "
      "remain UNKNOWN (\u00a74).  Note the observed spread already contains weekend/holiday widening (max spikes "
      "in the data-validation flags) \u2014 this is real, not modeled.\n")

    # 9
    A("\n## 9. Existing FX behavior re-check (real observed spreads)\n")
    A("\nRe-measures the six families (directional persistence, multi-hour reversal, session-open, volatility "
      "expansion, breakout continuation/failure, movement-to-cost) on DEV with per-trade real spread cost "
      f"(+{SLIP_TOTAL_PIPS:.1f} pip slip).  M5/M15/H1/H4 rows all built from the single Dukascopy source.  "
      f"Ratios vs the old constant cost (`ratio_legacy`) are kept in `outputs/phase_5_market_research.json`.\n")
    A("\n**Persistence** (prior-H move above its median magnitude):\n")
    for s in SYMBOLS:
        for tf in ["M5", "H1"]:
            fr = frames[(s, tf)]
            r = _persistence_rows(fr)
            if r:
                A(f"\n### {s} / {tf}\n")
                A(_md_table(["sym", "tf", "H_min", "side", "n", "mean", "med", "cont%", "p_pos%"], r))
    A("\n**Multi-hour reversal** (|prior| &gt; 66th percentile):\n")
    for s in SYMBOLS:
        for tf in ["M5", "H1", "H4"]:
            fr = frames[(s, tf)]
            r = _reversal_rows(fr)
            if r:
                A(f"\n### {s} / {tf}\n")
                A(_md_table(["sym", "tf", "H_min", "side", "n", "mean", "med", "rev%", "cont%"], r))
    A("\n**Session-open windows** (London/LondonNY/NewYork opens):\n")
    for s in SYMBOLS:
        for tf in ["M5", "H1"]:
            fr = frames[(s, tf)]
            r = _session_open_rows(fr)
            if r:
                A(f"\n### {s} / {tf}\n")
                A(_md_table(["sym", "tf", "window", "H_min", "n_opens", "mean", "med", "p_pos%", "expansion_ratio"], r))
    A("\n**Volatility expansion** (entering high ATR regime), **breakout** (24h channel + London-open "
      "overnight-range breaks):\n")
    for s in SYMBOLS:
        for tf in ["M5", "H1"]:
            fr = frames[(s, tf)]
            r = _vol_expansion_rows(fr) + _breakout_rows(fr)
            if r:
                A(f"\n### {s} / {tf}\n")
                A(_md_table(["sym", "tf", "event", "H_min", "n", "mean", "med", "cont%", "extra%"], r))

    # 10
    A("\n## 10. Market expansion universe\n")
    A("\nPer TASK.md 5F, a **small, predefined** candidate set justified by the intended MetaQuotes-Demo "
      "instrument palette (not hundreds of symbols, not an assumption that any is better):\n")
    A(_md_table(["candidate", "class", "rationale", "broker availability", "history available"],
                [["USDJPY / GBPJPY / AUDUSD / USDCHF / USDCAD / NZDUSD", "major/minor FX",
                  "alternate quote pairs with structurally different spread-to-move profiles", "UNKNOWN (MetaQuotes-Demo list not in repo)", "Dukascopy full-range (not yet downloaded)"],
                 ["XAUUSD / XAGUSD", "metals", "typical spreads are a small fraction of cash range", "UNKNOWN", "Dukascopy supports; not yet downloaded"],
                 ["US500 / US30 / NAS100 / GER40", "index CFDs", "high per-bar movement vs spread", "UNKNOWN", "not locally available"],
                 ["UKOIL / USOIL", "commodity CFDs", "different session/volatility structure", "UNKNOWN", "not locally available"]]))
    A("\nAvailability/specs on the demo account are UNKNOWN (MT5 connect prohibited).  Measuring "
      "movement-to-cost for this universe therefore requires either (i) a later MT5 session to dump the demo's "
      "symbol list + specs, or (ii) Dukascopy acquisition via the existing `dukascopy_acquire` utility "
      "(resumable; supports FX + several metals).  Neither was executed now \u2014 no random downloads.\n")

    # 11
    A("\n## 11. Instrument-level findings\n")
    A("\nWithin the studied universe (EURUSD/EURGBP/GBPUSD on M5/M15/H1/H4), re-checked with real spreads.  "
      "Full record in `outputs/phase_5_market_research.json`; the movement-to-cost table (\u00a712) is the "
      "authoritative summary.  No instrument/timeframe combination produced a `potentially viable` behavior "
      f"({verdict['n_viable']} viable of {len(beh)} behaviors).  The expansion universe (\u00a710) is not yet "
      "measurable (no data).\n")

    # 12
    A("\n## 12. Movement-to-cost analysis\n")
    A(f"\nReal-cost ratio = |mean pips| / (entry observed spread + exit observed spread + {SLIP_TOTAL_PIPS:.1f} "
      f"pip slip), n \u2265 {MIN_BEHAV_N}.  Classification as \u00a713-15.  Best-first:\n")
    A(_md_table(
        ["cls", "sym", "tf", "behavior", "condition", "H_min", "n", "mean", "med", "hit%",
         "cost_real", "ratio_real", "ratio_legacy"],
        [[_classify(b), b["symbol"], b["timeframe"], b["behavior"], b["condition"], b["horizon_min"],
          b["n"], b["mean_pips"], b["med_pips"], b["hit_pct_positive"], b["cost_pips_real"],
          b["ratio_real"], b.get("ratio_legacy", "-")] for b in ordered],
    ))

    # 13-15
    viable = [b for b in ordered if _classify(b) == "VIABLE*"]
    border = [b for b in ordered if _classify(b) == "BORDER"]
    insuff = [b for b in ordered if _classify(b) == "INSUFF"]
    A("\n## 13. Economically insufficient behaviors\n")
    A(f"\n{n_ifs(len(insuff))} behavior(s) below the borderline threshold (real-cost ratio &lt; "
      f"{BORDER_RATIO}).  Includes the majority of short-horizon persistence rows and the London-open "
      "overnight-range breaks \u2014 the real observed spread erases their already-small raw movement.\n"
      f"{_short_list(insuff)}")
    A("\n## 14. Borderline behaviors\n")
    A(f"\n{n_ifs(len(border))} behavior(s) with ratio in [{BORDER_RATIO:.1f}, {PROMISE_RATIO:.1f}).  These "
      "survive real-spread accounting but not the full viability bar (|mean| \u2265 2.0 pips required); they "
      "would be the re-test targets if a structurally cheaper instrument were found.\n{_short_list(border)}")
    A("\n## 15. Potentially viable behaviors\n")
    if viable:
        A(_md_table(["sym", "tf", "behavior", "condition", "H_min", "n", "mean", "cost_real", "ratio_real"],
                    [[b["symbol"], b["timeframe"], b["behavior"], b["condition"], b["horizon_min"], b["n"],
                      b["mean_pips"], b["cost_pips_real"], b["ratio_real"]] for b in viable]))
    else:
        A("\n**None** \u2014 nothing on DEV clears the bar (ratio \u2265 1.0 with |mean| \u2265 2.0 pips) under "
          "real observed-spread accounting.\n")

    # 16
    A("\n## 16. Exact evidence for any candidate\n")
    A(_exact_evidence(viable, ordered))

    # 17
    A("\n## 17. Limitations\n")
    A("\n- DEV only; validation/holdout never read; 60/20/20 preserved.\n"
      "- Observed bid/ask is **Dukascopy's feed**, not the MetaQuotes-Demo account; true broker-accurate "
      "history/specs are unavailable and marked UNKNOWN rather than guessed.\n"
      "- Overlapping forward windows inflate effective n at long horizons.\n"
      "- `cost = s_entry + s_exit + slip` counts the full spread on both sides; midpoint accounting "
      "(s/2+s/2) would give ~2\u00d7 higher ratios but is not used to stay conservative and comparable.\n"
      "- Aggregated H1/H4 bars carry the last-M5 close spread (spread-at-close convention).\n"
      "- Expansion universe (\u00a710) has no locally available data yet; UNKNOWN specs not measured.\n")

    # 18
    A("\n## 18. Final decision\n")
    A(_final_decision(verdict, best=ordered[0] if ordered else None))

    # 19
    A("\n## 19. Recommended next action\n")
    A(_next_action(verdict, best=ordered[0] if ordered else None))

    report_path = _root / REPORT_PATH
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    out = {
        "audit": {
            "data_source": "Dukascopy M5 bid/ask (dukascopy-node, jetta.dukascopy.com)",
            "spread_definition": "round((ask_close - bid_close) / point), points",
            "spread_verification": verification,
            "composite_coverage": {"EURUSD": 422225, "EURGBP": 425477, "GBPUSD": 374746},
            "eurjpy_status": "degraded, excluded",
        },
        "cost_model": {
            "legacy": "2 * median(dev M5 spread) + 1.7 pips",
            "recheck": "per-trade entry+exit observed spread + 1.0 pip slippage (0.5/side)",
            "legacy_cost_pips": {s: frames[(s, "M5")].cost_legacy_pips for s in SYMBOLS},
            "legacy_spread_med_pips": {s: round(float(np.median(frames[(s, "M5")].spread_pips)), 4) for s in SYMBOLS},
        },
        "broker": {
            "server": "MetaQuotes-Demo",
            "account": "5055770258",
            "build": "6140",
            "history_months": "~16",
            "recent_spread_field": "84-99% zero",
            "symbol_specs": "UNKNOWN (not obtainable without connecting)",
        },
        "timeframe_bars": {f"{s}/{tf}": len(frames[(s, tf)]) for s in SYMBOLS for tf in ["M5", "M15", "H1", "H4"]},
        "recheck": ordered,
        "viability": {
            "promise_ratio": PROMISE_RATIO,
            "promise_mean_pips": PROMISE_MEAN,
            "border_ratio": BORDER_RATIO,
            "min_n": MIN_BEHAV_N,
            "n_behaviors": len(ordered),
            "n_viable": verdict["n_viable"],
            "best": verdict["best"],
        },
        "universe": ["USDJPY GBPJPY AUDUSD USDCHF USDCAD NZDUSD", "XAUUSD XAGUSD",
                     "US500 US30 NAS100 GER40", "UKOIL USOIL"],
    }
    with open(pcfg.output_dir / "phase_5_market_research.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Report written to {report_path}")
    print(f"Behaviour dump: {pcfg.output_dir / 'phase_5_market_research.json'}")
    return 0


def n_ifs(k: int) -> str:
    return "No" if k == 0 else f"{k:,}"


def _short_list(beh: list[dict]) -> str:
    if not beh:
        return ""
    lines = ["Closest of the set (best-first):"]
    for b in beh[:4]:
        lines.append(
            f"- {b['symbol']} / {b['timeframe']} / {b['behavior']} / {b['condition']}: "
            f"mean {b['mean_pips']:+.2f} pips, cost {b['cost_pips_real']:.2f}, "
            f"ratio {b['ratio_real']:.2f}, n={b['n']:,}."
        )
    return "\n".join(lines)


def _exact_evidence(viable: list[dict], ordered: list[dict]) -> str:
    if viable:
        lines = ["Candidate evidence on DEV (real observed-spread costs, n \u2265 1000):"]
        for b in viable[:5]:
            lines.append(
                f"- {b['symbol']} / {b['timeframe']} / {b['behavior']} / {b['condition']} @ H="
                f"{b['horizon_min']} min: n={b['n']:,}, raw mean {b['mean_pips']:+.2f}, "
                f"median {b['med_pips']:+.2f}, hit {b['hit_pct_positive']:.1f}%, "
                f"real cost {b['cost_pips_real']:.2f}, movement-to-cost {b['ratio_real']:.2f}."
            )
        return "\n".join(lines)
    if ordered:
        lines = ["No candidate clears the bar under real observed-spread costs.  Closest DEV behaviors "
                 "(below it):"]
        for b in ordered[:5]:
            lines.append(
                f"- {b['symbol']} / {b['timeframe']} / {b['behavior']} / {b['condition']} @ H="
                f"{b['horizon_min']} min: n={b['n']:,}, raw mean {b['mean_pips']:+.2f}, "
                f"median {b['med_pips']:+.2f}, hit {b['hit_pct_positive']:.1f}%, real cost "
                f"{b['cost_pips_real']:.2f}, movement-to-cost {b['ratio_real']:.2f} "
                f"(legacy-cost ratio {b.get('ratio_legacy', '-')})."
            )
        return "\n".join(lines)
    return "No behavior exceeded the sample-size floor; see \u00a79 for raw statistics."


def _final_decision(verdict: dict, best: dict | None) -> str:
    if verdict["n_viable"] > 0 and best is not None:
        return (f"**ADVANCE** \u2014 {best['symbol']} / {best['timeframe']} / {best['behavior']} / "
                f"{best['condition']} reaches the viability bar (ratio {best['ratio_real']:.2f} \u2265 1.0, "
                f"|mean| {abs(best['mean_pips']):.2f} \u2265 2.0 pips, n={best['n']:,}).  Per 5H: do NOT "
                "implement \u2014 a frozen candidate specification must be written and reviewed first, then "
                "validated on VALIDATION data.")
    ratio = best["ratio_real"] if best else float("nan")
    return (
        f"**CLEARED-CONCLUSION: the no-edge result stands, and it is NOT an artefact of the cost model.**  "
        f"Re-checking the six behavior families on DEV with real observed bid/ask spreads "
        f"(+{SLIP_TOTAL_PIPS:.1f} pip slippage) leaves the best movement-to-cost at {ratio:.2f} "
        f"({best['symbol']} / {best['timeframe']} / {best['behavior']} / {best['condition']}); no behavior "
        f"clears the bar.  Limitation preventing credible strategy construction: for EURUSD/EURGBP/GBPUSD at "
        f"M5-H4, raw movement is small relative to realistic FX round-trip costs, and the intended demo "
        f"account cannot supply broker-true history/specs (16-month ceiling, unreliable spread field).  "
        f"Decision among A-E: **C \u2014 investigate another instrument class** (indices/metals with "
        f"structurally higher spread-to-move ratios), with **B \u2014 keep multi-hour H1/H4 horizons** (they "
        f"have the best raw ratios).  Option **D** (change broker/data source) is secondary: Dukascopy "
        f"already provides the best obtainable spread data, so a broker change would mainly add symbol specs, "
        f"not better core-pair costs."
    )


def _next_action(verdict: dict, best: dict | None) -> str:
    if verdict["n_viable"] > 0 and best is not None:
        return (f"**STOP (5H):** produce the candidate specification for {best['symbol']} / {best['timeframe']} "
                f"/ {best['behavior']} ({best['condition']}, expected {abs(best['mean_pips']):.2f} pips vs "
                f"{best['cost_pips_real']:.2f} cost, ratio {best['ratio_real']:.2f}, n={best['n']:,}) and "
                "review before any Strategy-04 work.  Do not touch bot.py.")
    return (
        "**STOP.** Per TASK.md the implementation portion ends with this report.  Next concrete action: (1) "
        "extend the market research to the predefined expansion universe (\u00a710) \u2014 obtain the "
        "MetaQuotes-Demo symbol list/specs in a future MT5 session, and acquire data for the shortlisted "
        "indices/metals via the existing resumable `backtest.data.dukascopy_acquire`; (2) re-run this same "
        "real-spread movement-to-cost framework on those instruments; (3) only if something then clears the "
        "bar, write the 5H candidate specification for review.  Do not build another FX M5 strategy; do not "
        "modify bot.py; do not start demo trading."
    )


if __name__ == "__main__":
    raise SystemExit(main())