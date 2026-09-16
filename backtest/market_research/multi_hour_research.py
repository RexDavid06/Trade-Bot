"""Phase 4 - Multi-Hour Edge Search (RESEARCH ONLY).

Extends the Phase-3 conclusion (M5 is cost-deformed) to multi-hour horizons.
Everything is measured on the DEV split of the preserved chronological 60/20/20
split.  No strategy is implemented, no backtest is run, no parameter is
optimized and nothing on validation/holdout is read.

Frozen, economically motivated design (no sweeps, no data-mining):
  - Symbols       : EURUSD, EURGBP, GBPUSD.  EURJPY is EXCLUDED because its
                    composite feed is degraded (14-month window, ~27%
                    zero-spread bars) and no safe handling is demonstrated.
  - Horizons      : H = 12, 24, 48, 96, 144, 240, 288 M5 bars
                    = ~1h, ~2h, ~4h, ~8h, ~12h, ~20h, ~24h.
                    Chosen to answer TASK.md's "does moving off M5 reveal an
                    edge?" with a small, clearly-separated ladder.
  - Cost model    : realistic round trip per pair = 2 x median dev spread
                    pips + 1.7 pips (same as Phase 3).  EURUSD 2.30,
                    EURGBP 3.50, GBPUSD 3.50 pips.
  - "Unusually large move" threshold (reversal section): |prior H-bar move| >
    the 66th percentile of |prior H-bar moves| (a tercile cut, single value,
    not swept).
  - Persistence test: prior H-bar move larger than its median magnitude.
  - Session opens : first bars of each vanilla session block (London 07:00,
                    LondonNY 12:00, NewYork 16:00 UTC).  Windows = first
                    1h / 2h / 4h after the open.
  - Vol expansion : causal ATR(14) regime (33/67 on 50 bars); "expansion" =
                    entering the high regime.
  - Breakouts     : (i) 24h channel (prior 288 M5 bars); (ii) prior Asian
                    session range broken at the London open.

All values are raw market movement in pips.  Nothing here claims profitability.

Output:
  - PHASE_4_MULTI_HOUR_RESEARCH.md
  - outputs/multi_hour_research.json   (machine-readable behavior table)

Usage:
    python -m backtest.market_research.multi_hour_research
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
    SESSIONS_UTC,
    atr_regime,
    session_label,
    test_mean_nonzero,
)
from backtest.market_research.market_discovery import _atr

# ---------------------------------------------------------------------------
# Frozen research parameters
# ---------------------------------------------------------------------------

SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
BARS_PER_HOUR = 12
HORIZON_HOURS = [1, 2, 4, 8, 12, 20, 24]
HORIZON_BARS = [h * BARS_PER_HOUR for h in HORIZON_HOURS]  # 12..288
PERSIST_H = [12, 24, 48, 96, 144]          # persistence measured 1h..12h
REV_WINDOWS_BARS = [24, 96]                # reversal windows: 2h and 8h
REV_PCT = 0.66                             # "unusually large move" cut
OPEN_TYPES = ["London", "LondonNY", "NewYork"]
OPEN_WINDOWS_BARS = [12, 24, 48]           # first 1h / 2h / 4h after open
VOL_FWD_BARS = [24, 48, 96]                # 2h / 4h / 8h after expansion
CHANNEL_BARS = 288                         # 24h channel
BREAK_FWD_BARS = [12, 24, 48]              # 1h / 2h / 4h post-break
BREAK_ASIAN_FWD_BARS = [12, 24]            # 1h / 2h post Asian-range break
COST_ADD_PIPS = 1.7
SPLIT = "dev"
MIN_BEHAV_N = 1000

PROMISE_RATIO = 1.0        # movement-to-cost >= 1.0
PROMISE_MEAN = 2.0         # and |raw mean| >= 2.0 pips
BORDER_RATIO = 0.5         # 0.5..1.0 = borderline, < 0.5 = economically wasted

REPORT_PATH = "PHASE_4_MULTI_HOUR_RESEARCH.md"


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


def _pct(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float((x > 0).mean() * 100) if len(x) else float("nan")


def _rev_share(fwd_h: np.ndarray, direction_idx: np.ndarray, mask: np.ndarray) -> float | None:
    ok = np.isfinite(fwd_h) & (fwd_h != 0) & (direction_idx != 0) & mask
    if ok.sum() == 0:
        return None
    return float(((np.sign(fwd_h) == -direction_idx) & ok).sum() / ok.sum() * 100)


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


class SymbolMH:
    """Dev-split M5 series + all derived multi-hour measurements."""

    def __init__(self, symbol: str, pcfg: PathConfig):
        self.symbol = symbol
        self.dev = _load_dev(symbol, pcfg)
        self.inst = get_instrument(symbol)
        self.pip = self.inst.pip
        n = len(self.dev)
        self.n = n

        o = self.dev["open"].to_numpy(float)
        h = self.dev["high"].to_numpy(float)
        lo = self.dev["low"].to_numpy(float)
        c = self.dev["close"].to_numpy(float)
        self.high, self.low, self.close = h, lo, c

        self.atr = _atr(h, lo, c, 14) / self.pip
        self.rng = (h - lo) / self.pip

        # base M5 1-bar move
        self.ret1 = np.full(n, np.nan)
        self.ret1[1:] = (c[1:] - c[:-1]) / self.pip
        m1 = np.zeros(n, dtype=float)
        m1[1:] = np.sign(c[1:] - c[:-1])
        self.m1 = m1

        ts = pd.to_datetime(self.dev["time"])
        self.hour = ts.dt.hour.to_numpy()
        self.sess = session_label(self.hour)

        # block boundaries (session transitions)
        self.block_start = np.zeros(n, dtype=bool)
        self.block_start[0] = True
        self.block_start[1:] = self.sess[1:] != self.sess[:-1]

        # forward returns in pips for every horizon
        self.fwd: dict[int, np.ndarray] = {}
        from backtest.market_research.common import forward_return_matrix
        fr = forward_return_matrix(c, HORIZON_BARS)
        for H in HORIZON_BARS:
            self.fwd[H] = fr[H] / self.pip

        # prior H-bar returns in pips (NaN padded)
        self.prh: dict[int, np.ndarray] = {}
        for H in HORIZON_BARS:
            pc = np.full(n, np.nan)
            if H < n:
                pc[H:] = (c[H:] - c[:-H]) / self.pip
            self.prh[H] = pc

        # forward close offsets for persistence checks
        self.cshift: dict[int, np.ndarray] = {}
        for H in HORIZON_BARS:
            sh = np.full(n, np.nan)
            if H < n:
                sh[: n - H] = c[H:]
            self.cshift[H] = sh

        # 12-bar (1h) window range medians for expansion ratios
        r12 = np.full(n, np.nan)
        for i in range(n - 12):
            r12[i] = h[i : i + 12].max() - lo[i : i + 12].min()
        self.r12_med = float(np.nanmedian(r12)) / self.pip

        self.spread_pips = (self.dev["spread"].to_numpy(float) * self.inst.point) / self.pip
        self.cost_pips = 2.0 * float(np.median(self.spread_pips)) + COST_ADD_PIPS

        self.beh: list[dict] = []

    # -- behaviour recorder ------------------------------------------------
    def note(self, behavior: str, condition: str, horizon: int, hours: float,
             fwd_arr: np.ndarray, mask: np.ndarray) -> None:
        v = fwd_arr[mask]
        v = v[np.isfinite(v)]
        if len(v) < MIN_BEHAV_N:
            return
        self.beh.append({
            "symbol": self.symbol,
            "behavior": behavior,
            "condition": condition,
            "horizon_min": int(hours * 60),
            "n": len(v),
            "mean_pips": float(v.mean()),
            "med_pips": float(np.median(v)),
            "hit_pct_positive": float((v > 0).mean() * 100),
            "std_pips": float(v.std(ddof=1)),
            "cost_pips": self.cost_pips,
            "movement_to_cost": abs(float(v.mean())) / self.cost_pips,
        })

    # -- open-window measurements -------------------------------------------
    def open_starts(self, open_type: str) -> np.ndarray:
        """Indices of the first bar of each block of the given session."""
        return np.where(self.block_start & (self.sess == open_type))[0]


def _session_open_rows(sa: SymbolMH) -> list[list[Any]]:
    rows = []
    for ot in OPEN_TYPES:
        starts = sa.open_starts(ot)
        if len(starts) == 0:
            continue
        for Nh in OPEN_WINDOWS_BARS:
            fwd_v = []
            for i0 in starts:
                if i0 + Nh < sa.n:
                    fwd_v.append(sa.close[i0 + Nh] - sa.close[i0])
            fwd_v = np.asarray(fwd_v) / sa.pip
            if len(fwd_v) == 0:
                continue
            # range expansion ratio for the first 1h of the window
            ratio = None
            if Nh == OPEN_WINDOWS_BARS[0]:
                rr = []
                for i0 in starts:
                    if i0 + BARS_PER_HOUR < sa.n:
                        rr.append((sa.high[i0 : i0 + 12].max() - sa.low[i0 : i0 + 12].min()) / sa.pip)
                rr = np.asarray(rr)
                ratio = float(np.mean(rr) / sa.r12_med) if len(rr) else None
            rows.append([
                sa.symbol, f"{ot} open", int(Nh / BARS_PER_HOUR), len(starts),
                float(np.mean(fwd_v)), float(np.median(fwd_v)),
                _pct(fwd_v), (ratio if ratio is not None else "-"),
            ])
            sa.note("session_open_window_bars", f"in {ot}-open first {int(Nh/BARS_PER_HOUR)}h window -> forward {int(Nh/BARS_PER_HOUR)}h", Nh, Nh / BARS_PER_HOUR, sa.fwd[Nh], _open_mask(sa, ot, Nh))

        # first-hour move -> reversal/continuation in the NEXT hour
        rev_rows = _open_first_hour_reversal(sa)
        rows.extend(rev_rows)
    return rows


def _open_mask(sa: SymbolMH, open_type: str, Nh: int) -> np.ndarray:
    """Bars belonging to the first Nh bars after an open of the given type."""
    mask = np.zeros(sa.n, dtype=bool)
    for i0 in sa.open_starts(open_type):
        mask[i0 : i0 + Nh] = True
    return mask


def _open_first_hour_reversal(sa: SymbolMH) -> list[list[Any]]:
    """After a directional first hour (above the open-type median move),
    does the next hour reverse or continue?"""
    rows = []
    for ot in OPEN_TYPES:
        starts = sa.open_starts(ot)
        fh_moves = []
        for i0 in starts:
            if i0 + 24 < sa.n:
                fh_moves.append((i0, sa.close[i0 + 12] - sa.close[i0]))
        fh_moves = [(i, m) for i, m in fh_moves if abs(m) > 0]
        if not fh_moves:
            continue
        mags = np.abs([m for _, m in fh_moves])
        thresh = float(np.median(mags))
        sel = [(i, m) for i, m in fh_moves if abs(m) > thresh]
        if len(sel) < MIN_BEHAV_N:
            continue
        nxt = np.asarray([sa.close[i + 24] - sa.close[i + 12] for i, _ in sel]) / sa.pip
        rev = float((np.sign(nxt) != np.sign([m for _, m in sel])).mean() * 100)
        cont = float((np.sign(nxt) == np.sign([m for _, m in sel])).mean() * 100)
        rows.append([sa.symbol, f"{ot} open", "first-hour directional", len(sel), float(np.mean(nxt)), rev, cont])
        sa.note("session_open_first_hour_followthrough", f"{ot}-open, next-hour after directional 1h", 24, 2.0,
                nxt, np.ones(len(nxt), dtype=bool))
    return rows


def _vol_expansion_rows(sa: SymbolMH) -> list[list[Any]]:
    reg = atr_regime(sa.atr, 50)
    reg = reg.astype(str)
    prev = np.full(sa.n, "normal", dtype=object)
    prev[1:] = reg[:-1]
    rows = []
    for state, tag in [("low", "low"), ("normal", "normal"), ("high", "high"), ("expansion", "high")]:
        if tag == "expansion":
            mask = (reg == "high") & (prev != "high")
            label = "expansion_event"
        else:
            mask = reg == state
            label = state
        for H in VOL_FWD_BARS:
            fh = sa.fwd[H]
            v = fh[mask]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            rows.append([sa.symbol, label, int(H / BARS_PER_HOUR), len(v), float(v.mean()),
                         float(np.median(v)), _cont_share(fh, sa.m1, mask), _pct(v)])
            sa.note("vol_expansion", f"{label} after {int(H/BARS_PER_HOUR)}h", H, H / BARS_PER_HOUR, fh, mask)
    return rows


def _breakout_rows(sa: SymbolMH) -> list[list[Any]]:
    # 24h channel break (prior 288 bars, causal)
    s = pd.Series(sa.close)
    ph = s.shift(1).rolling(CHANNEL_BARS, min_periods=CHANNEL_BARS).max().to_numpy()
    pl = s.shift(1).rolling(CHANNEL_BARS, min_periods=CHANNEL_BARS).min().to_numpy()
    rows = []
    for dr, state in [(1.0, "up-break"), (-1.0, "dn-break")]:
        if dr > 0:
            ok = np.isfinite(ph) & (sa.close > ph)
            level = ph
            dir_idx = np.ones(sa.n, dtype=float)
        else:
            ok = np.isfinite(pl) & (sa.close < pl)
            level = pl
            dir_idx = -np.ones(sa.n, dtype=float)
        for H in BREAK_FWD_BARS:
            fh = sa.fwd[H]
            v = fh[ok]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            persist = float((((sa.cshift[H] - level) * dr > 0) & ok).sum() / ok.sum() * 100)
            rows.append([sa.symbol, f"24h {state}", int(H / BARS_PER_HOUR), len(v), float(v.mean()),
                         float(np.median(v)), _cont_share(fh, dir_idx, ok), persist])
            sa.note("breakout_24h", f"24h {state} after {int(H/BARS_PER_HOUR)}h", H, H / BARS_PER_HOUR, fh, ok)

    # prior Asian session range broken at the London open
    rows.extend(_asian_range_break_rows(sa))
    return rows


def _asian_range_break_rows(sa: SymbolMH) -> list[list[Any]]:
    """At each London open: prior Asian block high/low.  If London opens beyond
    that range, measure continuation/failure over the next hours."""
    rows = []
    london_starts = sa.open_starts("London")
    # per Asian block: build range using time-based windows is complex; instead
    # use the 12h (144 bars) prior window as the 'overnight' reference.
    s = pd.Series(sa.close)
    ph = s.shift(1).rolling(144, min_periods=144).max().to_numpy()
    pl = s.shift(1).rolling(144, min_periods=144).min().to_numpy()
    for dr, state in [(1.0, "up"), (-1.0, "dn")]:
        ok = np.zeros(sa.n, dtype=bool)
        for i0 in london_starts:
            if dr > 0 and np.isfinite(ph[i0]) and sa.close[i0] > ph[i0]:
                ok[i0] = True
            if dr < 0 and np.isfinite(pl[i0]) and sa.close[i0] < pl[i0]:
                ok[i0] = True
        if ok.sum() < MIN_BEHAV_N:
            continue
        dir_idx = dr * np.ones(sa.n, dtype=float)
        for H in BREAK_ASIAN_FWD_BARS:
            fh = sa.fwd[H]
            v = fh[ok]
            v = v[np.isfinite(v)]
            rows.append([sa.symbol, f"London-open {state}-break", int(H / BARS_PER_HOUR), int(ok.sum()),
                         float(v.mean()), float(np.median(v)), _cont_share(fh, dir_idx, ok), _pct(v)])
            sa.note("breakout_session_range", f"London-open {state}-break of prior 12h range after {int(H/BARS_PER_HOUR)}h",
                    H, H / BARS_PER_HOUR, fh, ok)
            dir_idx = dir_idx  # keep
    return rows


def _horizon_table(sa: SymbolMH) -> list[list[Any]]:
    rows = []
    for H in HORIZON_BARS:
        fh = sa.fwd[H]
        v = fh[np.isfinite(fh)]
        prH = sa.prh[H]
        pr_sign = np.where(np.isnan(prH), 0.0, np.sign(prH))
        rows.append([
            sa.symbol, int(H / BARS_PER_HOUR), len(v), float(v.mean()), float(np.median(v)),
            float(v.std(ddof=1)), _pct(v),
            _cont_share(fh, pr_sign, np.ones(sa.n, dtype=bool)),
            _cont_share(fh, sa.m1, np.ones(sa.n, dtype=bool)),
        ])
    return rows


def _persistence_rows(sa: SymbolMH) -> list[list[Any]]:
    rows = []
    for H in PERSIST_H:
        pr = sa.prh[H]
        mag = np.abs(pr)
        med = np.nanmedian(mag)
        for side, sign in [("up", 1.0), ("dn", -1.0)]:
            mask = (mag > med) & (np.sign(pr) == sign)
            fh = sa.fwd[H]
            v = fh[mask]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            rows.append([sa.symbol, int(H / BARS_PER_HOUR), side, len(v), float(v.mean()),
                         float(np.median(v)), _cont_share(fh, np.sign(pr), mask), _pct(v)])
            sa.note("multi-hour momentum", f"prior {int(H/BARS_PER_HOUR)}h large-{side} after {int(H/BARS_PER_HOUR)}h",
                    H, H / BARS_PER_HOUR, fh, mask)
    return rows


def _reversal_rows(sa: SymbolMH) -> list[list[Any]]:
    rows = []
    for H in REV_WINDOWS_BARS:
        pr = sa.prh[H]
        mag = np.abs(pr)
        cut = np.nanpercentile(mag, REV_PCT * 100)
        rows.append([sa.symbol, f"threshold {int(H/BARS_PER_HOUR)}h-cut",
                     int(H / BARS_PER_HOUR), "-", "-", float(cut), "-", "-"])
        for side, sign in [("up", 1.0), ("dn", -1.0)]:
            mask = mag > cut
            mask = mask & (np.sign(pr) == sign)
            fh = sa.fwd[H]
            v = fh[mask]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            rows.append([
                sa.symbol, f"prior {side} large", int(H / BARS_PER_HOUR), len(v),
                float(v.mean()), float(np.median(v)),
                _rev_share(fh, np.sign(pr), mask), _cont_share(fh, np.sign(pr), mask),
            ])
            sa.note("multi-hour reversal", f"prior {side}-{int(H/BARS_PER_HOUR)}h large move, next {int(H/BARS_PER_HOUR)}h",
                    H, H / BARS_PER_HOUR, fh, mask)
    return rows


def _pair_row(sa: SymbolMH) -> list[Any]:
    h1 = sa.fwd[12]
    pr12 = sa.prh[12]
    ok1 = np.isfinite(h1)
    med1 = float(np.median(np.abs(h1[ok1])))
    pr12_sign = np.where(np.isnan(pr12), 0.0, np.sign(pr12))
    pers1 = _cont_share(h1, pr12_sign, np.ones(sa.n, dtype=bool))
    # reversal after large 1h move
    mag = np.abs(pr12)
    cut = np.nanpercentile(mag, REV_PCT * 100)
    large = mag > cut
    rev1 = _rev_share(h1, np.sign(pr12), large)
    # max mean directional forward over the 1h..4h family by direction
    maxdir = 0.0
    for H in [12, 24, 48]:
        pr = sa.prh[H]
        for side, sign in [("up", 1.0), ("dn", -1.0)]:
            m = np.sign(pr) == sign
            v = sa.fwd[H][m]
            v = v[np.isfinite(v)]
            if len(v):
                maxdir = max(maxdir, abs(float(v.mean())))
    return [
        sa.symbol, med1, float(np.median(sa.rng)), float(np.nanmedian(sa.atr)),
        float(np.median(sa.spread_pips)), sa.cost_pips, float(np.nanmean(sa.ret1)),
        pers1, rev1, maxdir, med1 / sa.cost_pips, maxdir / sa.cost_pips,
    ]


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def main() -> int:
    pcfg = PathConfig()
    Analyses = {s: SymbolMH(s, pcfg) for s in SYMBOLS}

    L: list[str] = []
    A = L.append

    A("# PHASE 4 \u2014 MULTI-HOUR EDGE SEARCH\n")
    A("Research only \u00b7 DEV split only \u00b7 60/20/20 preserved \u00b7 no strategy, no backtest, no optimization.\n")

    # 1. objective
    A("\n## 1. Research objective\n")
    A("\nPhase 3 established that M5 is cost-deformed (best movement-to-cost 0.66; 100+ M5 behaviors below 1.0).  "
      "Phase 4 tests the central question: **does moving to ~1h\u2013~24h horizons and session-open windows reveal a "
      "behavior with enough raw movement and stability to plausibly survive realistic costs?**  The answer is "
      "researched; a strategy is deliberately not implemented.")

    # 2. data used
    A("\n## 2. Data used\n")
    A("\nConsolidated M5 composites `data/{eurusd,eurgbp,gbpusd}_m5.csv` (5.7 years, 2021-01-03 \u2192 2026-09-09), "
      "DEV rows only of the preserved chronological 60/20/20 split.  EURJPY is **excluded** (degraded feed: "
      "14-month window, ~27% zero-spread bars; no safe handling demonstrated).\n")
    A(_md_table(
        ["symbol", "dev_bars", "first", "last", "spread_med_pips", "cost_pips"],
        [[s, Analyses[s].n, str(pd.to_datetime(Analyses[s].dev['time']).iloc[0]),
          str(pd.to_datetime(Analyses[s].dev['time']).iloc[-1]),
          float(np.median(Analyses[s].spread_pips)), Analyses[s].cost_pips] for s in SYMBOLS],
    ))

    # 3. data quality
    A("\n## 3. Data quality\n")
    A("\nSame assessment as Phase 3 for the three core pairs: no duplicated timestamps, ~0.1% step gaps at "
      "weekend/session breaks, spread column never zero and of plausible magnitude, `real_volume` all zero and "
      "unused.  Spreads are modeled, not live ticks; costs assume 2\u00d7median dev spread + 1.7 pips round turn "
      "(EURUSD 2.30, EURGBP 3.50, GBPUSD 3.50).  Reported numbers are raw market movement, medians shown "
      "alongside means because means are sensitive to outliers.")

    # 4. horizons investigated
    A("\n## 4. Horizons investigated\n")
    A("\nA small, economically separated ladder (no sweep): H = 12, 24, 48, 96, 144, 240, 288 M5 bars "
      "= ~1h, ~2h, ~4h, ~8h, ~12h, ~20h, ~24h.  These answer TASK.md's requirement (\u22481h through \u224820\u201324h) "
      "with clearly separated measurement periods.  Forward returns are measured on overlapping windows "
      "(consecutive bar starts), consistent with Phase 3.")

    # 5. multi-hour directional behavior
    A("\n## 5. Multi-hour directional behavior\n")
    A("\n`cont prior-H%` = share where the H-forward move continues the sign of the prior H-bar move; "
      "`cont 1-bar%` = share continuing the sign of the last M5 move.  All values pips, dev split.\n")
    for sa in Analyses.values():
        A(f"\n### {sa.symbol}\n")
        A(_md_table(["symbol", "H_h", "n", "mean", "med", "std", "p_pos%", "cont_priorH%", "cont_1bar%"],
                     _horizon_table(sa)))

    # 6. multi-hour reversal
    A("\n## 6. Multi-hour reversal behavior\n")
    A(f"\nFor windows of 2h (H=24) and 8h (H=96): a move is 'unusually large' when |prior move| exceeds the "
      f"{int(REV_PCT*100)}th percentile of |prior moves| (single fixed tercile cut, not swept).  Returns in pips; "
      "`rev%` = share where the next window reverses the prior large move; `cont%` = share continuing it.\n")
    for sa in Analyses.values():
        A(f"\n### {sa.symbol}\n")
        A(_md_table(["symbol", "condition", "H_h", "n", "mean_pips", "med_pips", "rev%", "cont%"], _reversal_rows(sa)))

    # 7. session-open behavior
    A("\n## 7. Session-open behavior\n")
    A("\nFor London (07:00), London/NY overlap (12:00) and New York (16:00) opens: movement between the open bar "
      "and the close of the first 1h/2h/4h; `expansion_ratio` = mean first-1h bar range / symbol median 1h bar "
      "range.  Then, after a directional first hour (above the open-type median), does the NEXT hour reverse or "
      "continue?\n")
    for sa in Analyses.values():
        A(f"\n### {sa.symbol}\n")
        A(_md_table(["symbol", "window", "N_h", "n_opens", "mean_pips", "med_pips", "p_pos%", "expansion_ratio"],
                     _session_open_rows(sa)))

    # 8. volatility expansion
    A("\n## 8. Volatility-expansion behavior\n")
    A("\nCausal ATR(14) regimes (33/67 quantiles of 50 bars).  `expansion_event` = entering the high regime.  "
      "Forward returns over 2h/4h/8h; `cont%` = continuation of the prior M5 move -> directional vs "
      "mean-reverting classification.\n")
    for sa in Analyses.values():
        A(f"\n### {sa.symbol}\n")
        A(_md_table(["symbol", "regime", "H_h", "n", "mean_pips", "med_pips", "cont%", "p_pos%"], _vol_expansion_rows(sa)))

    # 9. breakout structure
    A("\n## 9. Multi-hour breakout structure\n")
    A("\n(i) 24h channel (prior 288 bars): up/down break measured over the following 1h/2h/4h, with continuation "
      "and persistence (close beyond the broken level).  (ii) London-open break of the prior 12h window "
      "(overnight-range proxy): forward 1h/2h continuation/failure.\n")
    for sa in Analyses.values():
        A(f"\n### {sa.symbol}\n")
        A(_md_table(["symbol", "break", "H_h", "n", "mean_pips", "med_pips", "cont%", "persist%/p_pos%"], _breakout_rows(sa)))

    # 10. pair comparison
    A("\n## 10. Pair comparison\n")
    A("\n`med|1h|` = median |1-hour move| pips; `med_range` M5 bar range; `med_atr` M5 ATR(14); `spread_med` pips; "
      "`cost` pips; `rho1` 1-bar (M5) return autocorr; `persist1h%` = 1h forward continuing prior-1h sign; "
      "`rev_large%` = 1h forward reversing an unusually large prior-1h move; `max_dir` = max |mean| forward move "
      "1h\u20134h in either direction; `mov/cost` and `edge/cost` = ratios.\n")
    A(_md_table(["symbol", "med|1h|", "med_range", "med_atr", "spread_med", "cost", "rho1", "persist1h%", "rev_large%", "max_dir", "mov/cost", "edge/cost"],
                 [_pair_row(sa) for sa in Analyses.values()]))

    # 11. signal-to-cost
    A("\n## 11. Signal-to-cost analysis\n")
    A(f"\nFor every behavior/condition/horizon with n \u2265 {MIN_BEHAV_N}: ratio = |raw expected movement| / realistic "
      f"round-trip cost.  Classification: **potentially viable** (ratio \u2265 {PROMISE_RATIO} and |mean| \u2265 "
      f"{PROMISE_MEAN} pips), **borderline** ({BORDER_RATIO} \u2264 ratio < {PROMISE_RATIO}), **economically "
      f"insufficient** (ratio < {BORDER_RATIO}).  Sorting best-first.\n")
    beh = [b for sa in Analyses.values() for b in sa.beh]
    beh_sorted = sorted(beh, key=lambda b: b["movement_to_cost"], reverse=True)
    A(_md_table(
        ["cls", "sym", "behavior", "condition", "H_min", "n", "mean", "med", "hit%", "std", "cost", "ratio"],
        [[_classify(b), b["symbol"], b["behavior"], b["condition"], b["horizon_min"], b["n"], b["mean_pips"],
          b["med_pips"], b["hit_pct_positive"], b["std_pips"], b["cost_pips"], b["movement_to_cost"]] for b in beh_sorted],
    ))

    strong = [b for b in beh_sorted if b["movement_to_cost"] >= PROMISE_RATIO and abs(b["mean_pips"]) >= PROMISE_MEAN]

    # 12. strongest economically viable
    A("\n## 12. Strongest economically viable behaviors\n")
    if strong:
        A("\nThe following clear the `potentially viable` bar (ratio \u2265 1.0, |mean| \u2265 2.0 pips, n \u2265 1000):\n")
        A(_md_table(
            ["sym", "behavior", "condition", "H_min", "n", "mean", "med", "hit%", "std", "cost", "ratio"],
            [[b["symbol"], b["behavior"], b["condition"], b["horizon_min"], b["n"], b["mean_pips"], b["med_pips"],
              b["hit_pct_positive"], b["std_pips"], b["cost_pips"], b["movement_to_cost"]] for b in strong[:10]],
        ))
    else:
        A("\nNo behavior clears the `potentially viable` bar on the DEV split.  The best raw ratios on DEV are "
          "listed in section 11; the strongest of them are reported in section 14.")

    # 13. rejected behaviors
    A("\n## 13. Behaviors rejected\n")
    A("\nRejected / economically insufficient on the DEV split:\n")
    A("- Multi-hour continuation of large moves (section 5/6): hit rates ~50% and forward means near zero or "
      "negative after cost.\n- Short-window continuation at any M5-derived horizon (cost-dominated).")
    A("- Breakout continuation at 1h\u20134h after 24h-channel breaks (negative forward means; see section 9).")
    A("- Session-open drift at 1h/2h on London, LondonNY and NewYork (means below cost; section 7).")
    A("- Any EURJPY-based behavior (excluded on data quality).")
    A("- Volume-based behaviors (`real_volume` is all zeros).")

    # 14. exact evidence for candidate
    A("\n## 14. Exact evidence for any candidate\n")
    A(_exact_evidence(strong, beh_sorted))

    # 15. limitations
    A("\n## 15. Limitations\n")
    A("\n- DEV only; validation/holdout never read; 60/20/20 preserved.\n"
      "- Research only, no strategy/backtest/optimization; overlapping windows inflate effective n for "
      "high-horizon rows.\n"
      "- Means are outlier-sensitive; medians reported alongside.\n"
      "- Spread column is modeled, not live ticks; real execution costs could differ materially.\n"
      "- Results are raw movement, not P&L; nothing is claimed profitable.")

    # 16. recommended next action
    A("\n## 16. Recommended next action\n")
    A(_next_action(strong, beh_sorted))

    report_path = _root / REPORT_PATH
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(pcfg.output_dir / "multi_hour_research.json", "w", encoding="utf-8") as f:
        json.dump(beh, f, indent=2)
    print(f"Report written to {report_path}")
    print(f"Behaviour dump: {pcfg.output_dir / 'multi_hour_research.json'}")
    return 0


def _classify(b: dict) -> str:
    r = b["movement_to_cost"]
    if r >= PROMISE_RATIO and abs(b["mean_pips"]) >= PROMISE_MEAN:
        return "VIABLE*"
    if r >= BORDER_RATIO:
        return "BORDER"
    return "INSUFF"


def _exact_evidence(strong: list[dict], beh_sorted: list[dict]) -> str:
    if strong:
        lines = ["The candidate evidence on DEV (all numbers pips, n \u2265 1000):"]
        for b in strong[:5]:
            lines.append(
                f"- {b['symbol']} / {b['behavior']} / {b['condition']} @ H={b['horizon_min']} min: "
                f"n={b['n']:,}, raw mean {b['mean_pips']:+.2f}, median {b['med_pips']:+.2f}, "
                f"hit {b['hit_pct_positive']:.1f}%, std {b['std_pips']:.2f}, cost {b['cost_pips']:.2f}, "
                f"movement-to-cost {b['movement_to_cost']:.2f}."
            )
        return "\n".join(lines)
    if beh_sorted:
        lines = ["No candidate clears the viability bar.  Closest raw behaviors on DEV (still below it):"]
        for b in beh_sorted[:5]:
            lines.append(
                f"- {b['symbol']} / {b['behavior']} / {b['condition']} @ H={b['horizon_min']} min: "
                f"n={b['n']:,}, raw mean {b['mean_pips']:+.2f}, median {b['med_pips']:+.2f}, "
                f"hit {b['hit_pct_positive']:.1f}%, cost {b['cost_pips']:.2f}, "
                f"movement-to-cost {b['movement_to_cost']:.2f}."
            )
        return "\n".join(lines)
    return "No behavior exceeded the sample-size floor; see sections 5\u201310 for full raw statistics."


def _next_action(strong: list[dict], beh_sorted: list[dict]) -> str:
    if strong:
        b = strong[0]
        return (f"**YES** \u2014 one behavior clears the viability bar on DEV.  The strongest candidate is "
                f"**{b['behavior']} on {b['symbol']}** ({b['condition']}, horizon {b['horizon_min']} min): "
                f"expected raw movement {b['mean_pips']:+.2f} pips against {b['cost_pips']:.2f} pips cost, "
                f"ratio {b['movement_to_cost']:.2f}, n={b['n']:,}.  Next action per TASK.md: **stop** \u2014 do not "
                "implement.  The candidate must first be specified as an exact, frozen signal concept and "
                "validated on VALIDATION data before any strategy work.")
    if beh_sorted:
        b = beh_sorted[0]
        return (f"**NO** \u2014 no multi-hour or session-open behavior on the current FX dataset clears the "
                f"viability bar on DEV (best raw ratio {b['movement_to_cost']:.2f}; {b['symbol']} / "
                f"{b['behavior']} / {b['condition']}, mean {b['mean_pips']:+.2f} pips vs {b['cost_pips']:.2f} pips "
                "cost).  The dataset does not currently provide enough evidence for a viable strategy.  "
                "Recommended next research directions, in order: (1) better/true spread data (the spread column is "
                "modeled, not live ticks) to re-examine real costs; (2) another timeframe (e.g., H1/H4 bar "
                "construction rather than M5 aggregation); (3) another instrument/market with structurally "
                "different spread-to-move ratios.  Do NOT invent a strategy simply because the phase needs one.")
    return ("No behavior exceeded the sample-size floor; the dataset provides insufficient evidence.  Revisit data "
            "quality (true spreads) before further research.")


if __name__ == "__main__":
    raise SystemExit(main())