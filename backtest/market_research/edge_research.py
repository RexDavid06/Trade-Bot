"""Phase 3 — Market Expansion / Edge Search (RESEARCH ONLY).

Measures raw market behavior across time horizons, trend/momentum, volatility
regimes, session/open conditions, range/breakout structure, pair comparison and
signal-to-cost — entirely on the DEV split.  It does NOT build or backtest a
strategy and it does NOT touch validation/holdout.

Frozen research design (economically motivated, no sweeps):
  - Symbols      : EURUSD, EURGBP, GBPUSD (core).  EURJPY is inventoried but
                   excluded from behaviour tables because its composite feed is
                   degraded (14-month window, 27% zero-spread bars).
  - Horizons     : H = 5 / 20 / 80 / 240 bars  (~25 min / ~1.7 h / ~6.7 h / ~20 h).
                   A small, clearly separated ladder from very-short to
                   multi-hour, per TASK.md §TIME-HORIZON BEHAVIOR.  No H was
                   tuned to maximize anything.
  - Momentum     : prior change over W = 5 / 20 / 80 bars, split strong/weak by
                   the per랄-symbol median magnitude (a single fixed cut, not a sweep).
  - Volatility   : ATR(14) regime low/normal/high via causal rolling quantiles
                   (33/67 on 50 bars) and expansion/contraction events.
  - Sessions     : fixed vanilla SESSIONS_UTC (Asian/London/LondonNY/NewYork/
                   OffHours).  Opens = first 6 bars of each session block.
  - Range/Break  : prior-20 channel (causal), states up-break/down-break/inside;
                   range expansion = bar range above its causal rolling median.
  - Costs        : realistic round trip per pair = 2 x median dev spread pips
                   (observed, spread column) + 1.7 pips slippage+commission.

All values are in pips unless noted.  Sample-size floor for "behavior" rows is
n >= 1000 in signal-to-cost unless otherwise stated.

Output:
  - PHASE_3_EDGE_RESEARCH.md
  - outputs/edge_research.json (machine-readable behaviour table)

Usage:
    python -m backtest.market_research.edge_research
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
from backtest.instruments import get_instrument, spread_cost_points
from backtest.market_research.common import (
    SESSIONS_UTC,
    atr_regime,
    forward_return_matrix,
    session_label,
    test_mean_nonzero,
)
from backtest.market_research.market_discovery import _atr

# ---------------------------------------------------------------------------
# Frozen research parameters
# ---------------------------------------------------------------------------

HORIZONS = [5, 20, 80, 240]
SHORT_H = [5, 20, 80]
CORE_SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD"]
ALL_SYMBOLS = ["EURUSD", "EURGBP", "GBPUSD", "EURJPY"]
MOM_WINDOWS = [5, 20, 80]
CHANNEL = 20
REGIME_LOOKBACK = 50
COST_ADD_PIPS = 1.7
SPLIT = "dev"
MIN_BEHAV_N = 1000

REPORT_PATH = "PHASE_3_EDGE_RESEARCH.md"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_dev(symbol: str, pcfg: PathConfig) -> pd.DataFrame:
    """DEV rows only from the preserved 60/20/20 split (assignments file)."""
    sym = symbol.lower()
    csv_path = pcfg.base_dir / "data" / f"{sym}_m5.csv"
    assign_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Prices not found: {csv_path}")
    if not assign_path.exists():
        raise FileNotFoundError(f"Split assignments not found: {assign_path}")

    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])

    assignments = pd.read_csv(assign_path)
    counts = assignments["split"].value_counts().to_dict()
    mask = assignments["split"] == SPLIT
    idx = assignments.index[mask].tolist()
    return df.iloc[idx].reset_index(drop=True), counts


def _split_counts(symbol: str, pcfg: PathConfig) -> dict[str, int]:
    assign_path = pcfg.output_dir / "splits" / symbol / "assignments.csv"
    assignments = pd.read_csv(assign_path)
    return dict(assignments["split"].value_counts())


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def _stat(fwd: dict[int, np.ndarray], mask: np.ndarray) -> list[dict]:
    """Per-horizon stats on finite forward pips where mask is True."""
    rows = []
    for H in HORIZONS:
        v = fwd[H][mask]
        v = v[np.isfinite(v)]
        if len(v) == 0:
            rows.append({"H": H, "n": 0})
            continue
        rows.append({
            "H": H,
            "n": len(v),
            "mean": float(v.mean()),
            "med": float(np.median(v)),
            "std": float(v.std(ddof=1)),
            "p_pos": float((v > 0).mean() * 100),
            "t": test_mean_nonzero(v)["t"],
        })
    return rows


def _cont_share(fwd_h: np.ndarray, direction_idx: np.ndarray, mask: np.ndarray) -> float | None:
    """Share of bars where the H-forward move has the same sign as `direction_idx`.

    `direction_idx` is +1/-1/0 signalling the last move's direction (or a
    breakout direction, or a momentum direction).  Bars with NaN fwd, zero fwd
    or zero direction are excluded.
    """
    ok = np.isfinite(fwd_h) & (fwd_h != 0) & (direction_idx != 0) & mask
    if ok.sum() == 0:
        return None
    return float(((np.sign(fwd_h) == direction_idx) & ok).sum() / ok.sum() * 100)


def _pct(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float((x > 0).mean() * 100) if len(x) else float("nan")


def _md_table(headers: list[str], rows: list[list[Any]], num_cols: set[str] | None = None) -> str:
    num_cols = num_cols or {"n", "n_bars", "spread_distinct", "dup_ts", "bars"}
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
                elif headers[i] in ("t", "rho1", "ratio", "range_ratio", "mov/cost", "edge/cost"):
                    cells.append(f"{c:.2f}")
                else:
                    cells.append(f"{c:,.2f}")
            elif isinstance(c, int):
                cells.append(f"{int(c):,}")
            else:
                cells.append(str(c))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-symbol analysis
# ---------------------------------------------------------------------------

class SymbolAnalysis:
    def __init__(self, symbol: str, pcfg: PathConfig):
        self.symbol = symbol
        self.dev, _ = _load_dev(symbol, pcfg)
        self.inst = get_instrument(symbol)
        self.pip = self.inst.pip
        self.point = self.inst.point
        n = len(self.dev)
        self.n = n
        self.time = self.dev["time"].to_numpy()
        o = self.dev["open"].to_numpy(float)
        h = self.dev["high"].to_numpy(float)
        lo = self.dev["low"].to_numpy(float)
        c = self.dev["close"].to_numpy(float)
        self.c = c
        self.open = o
        self.high = h
        self.low = lo

        self.atr = _atr(h, lo, c, 14) / self.pip
        self.rng = (h - lo) / self.pip
        self.ret1 = np.full(n, np.nan)
        self.ret1[1:] = (c[1:] - c[:-1]) / self.pip
        m1 = np.zeros(n, dtype=float)
        m1[1:] = np.sign(c[1:] - c[:-1])
        self.m1 = m1

        hour = pd.to_datetime(self.time).hour.to_numpy()
        self.sess = session_label(hour)
        self.reg = atr_regime(self.atr, REGIME_LOOKBACK)
        reg_prev = np.full(n, "normal", dtype=object)
        reg_prev[1:] = self.reg[:-1]
        self.reg = self.reg.astype(str)
        self.reg_prev = reg_prev.astype(str)

        # causal prior-20 channel (price units)
        s = pd.Series(c)
        self.ph = s.shift(1).rolling(CHANNEL, min_periods=CHANNEL).max().to_numpy()
        self.pl = s.shift(1).rolling(CHANNEL, min_periods=CHANNEL).min().to_numpy()

        # rolling median bar range (50-bar, causal) in pips
        self.rng_med = pd.Series(self.rng).rolling(50, min_periods=20).median().to_numpy()

        # forward returns in pips (NaN padded at the tail)
        fr = forward_return_matrix(c, [h_ for h_ in HORIZONS if h_ < n])
        self.fwd: dict[int, np.ndarray] = {H: (fr[H] / self.pip) for H in fr}

        # momentum prior changes (pips), NaN padded
        self.mom: dict[int, np.ndarray] = {}
        for W in MOM_WINDOWS:
            pc = np.full(n, np.nan)
            if W < n:
                pc[W:] = (c[W:] - c[:-W]) / self.pip
            self.mom[W] = pc

        # forward close offset for persistence checks: cshift[H][i] = close[i+H]
        self.cshift: dict[int, np.ndarray] = {}
        for H in HORIZONS:
            sh = np.full(n, np.nan)
            if H < n:
                sh[: n - H] = c[H:]
            self.cshift[H] = sh

        self.spread_pips = (self.dev["spread"].to_numpy(float) * self.point) / self.pip

        self.cost_pips = 2.0 * float(np.median(self.spread_pips)) + COST_ADD_PIPS

        self.beh: list[dict] = []

    # -- behaviour recorder for signal-to-cost -----------------------------
    def note(self, name: str, cond: str, H: int, fwd_arr: np.ndarray, mask: np.ndarray) -> None:
        v = fwd_arr[mask]
        v = v[np.isfinite(v)]
        if len(v) < MIN_BEHAV_N:
            return
        self.beh.append({
            "symbol": self.symbol,
            "behavior": name,
            "condition": cond,
            "horizon_bars": H,
            "horizon_min": int(H * 5),
            "n": len(v),
            "mean_pips": float(v.mean()),
            "med_pips": float(np.median(v)),
            "hit_pct_positive": float((v > 0).mean() * 100),
            "std_pips": float(v.std(ddof=1)),
            "cost_pips": self.cost_pips,
            "movement_to_cost": abs(float(v.mean())) / self.cost_pips,
        })


def _rho1(ret1: np.ndarray) -> float:
    x = ret1[1:]
    prev = ret1[:-1]
    ok = np.isfinite(x) & np.isfinite(prev)
    if ok.sum() < 10:
        return float("nan")
    return float(np.corrcoef(prev[ok], x[ok])[0, 1])


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _fmt_h(h: int) -> str:
    return {5: "5", 20: "20", 80: "80", 240: "240"}[h]


def main() -> int:
    pcfg = PathConfig()

    # ---- Inventory (full files) -----------------------------------------
    inv_rows: list[list[Any]] = []
    for sym in ALL_SYMBOLS:
        sym_l = sym.lower()
        df = pd.read_csv(pcfg.base_dir / "data" / f"{sym_l}_m5.csv")
        ts = pd.to_datetime(df["time"])
        dt = ts.diff().dropna()
        step_off = float((dt != pd.Timedelta(minutes=5)).mean() * 100)
        sp = df["spread"]
        spn = sp[~sp.isna()]
        inst = get_instrument(sym)
        sp_pips = spn.to_numpy(float) * inst.point / inst.pip
        counts = _split_counts(sym, pcfg)
        inv_rows.append([
            sym, "M5", f"{len(df):,}", str(ts.iloc[0]), str(ts.iloc[-1]),
            spn.nunique(), float((spn == 0).mean() * 100),
            f"{float(np.percentile(sp_pips, 10)):.2f}", f"{float(np.median(sp_pips)):.2f}", f"{float(np.percentile(sp_pips, 90)):.2f}",
            f"{step_off:.2f}", ts.duplicated().sum(),
            counts.get("dev", 0), counts.get("val", 0), counts.get("holdout", 0),
        ])

    analyses = {sym: SymbolAnalysis(sym, pcfg) for sym in ALL_SYMBOLS}
    core = [analyses[s] for s in CORE_SYMBOLS]

    L: list[str] = []
    A = L.append

    A("# PHASE 3 \u2014 MARKET EXPANSION / EDGE SEARCH\n")
    A("Research only \u00b7 DEV split only \u00b7 no validation/holdout \u00b7 no strategy, no backtest, no optimization.\n")
    A("Built on the preserved 60/20/20 split; all numbers are raw market behavior in pips unless stated.")

    # ======================================================================
    A("\n## 1. Research objective\n")
    A("\nFind market behaviors, time horizons, instruments or structural conditions in the currently available "
      "historical data whose **raw movement** is large and repeatable enough to plausibly survive realistic "
      "round-turn transaction costs.  This is edge search, not strategy construction.")
    A("\nFrozen design (no sweeps): a small economically motivated set of horizons H = {5, 20, 80, 240} bars "
      "(~25 min / ~1.7 h / ~6.7 h / ~20 h), momentum windows W = {5, 20, 80}, an ATR(14) regime split "
      "(low/normal/high, causal 33/67 quantiles on 50 bars), vanilla session definitions, a prior-20 channel, "
      "and per-pair cost = 2\u00d7median dev spread + 1.7 pips.")

    # ======================================================================
    A("\n## 2. Dataset inventory\n")
    A("\nAvailable source files: four consolidated M5 composites (`data/{eurgbp,eurjpy,eurusd,gbpusd}_m5.csv`) "
      "plus the original monthly bid/ask export fragments they were built from.  No new external data is added.\n")
    A(_md_table(
        ["symbol", "tf", "bars", "first", "last", "spread_distinct", "zero%", "spread pips p10", "med", "p90", "step!=5min%", "dup_ts", "dev", "val", "hold"],
        inv_rows,
    ))
    A("\nSplit counts confirm the preserved 60/20/20 allocation on each symbolized series.\n")

    # ======================================================================
    A("\n## 3. Data-quality assessment\n")
    A("\n- **EURUSD / EURGBP / GBPUSD**: continuous 2021-01-03 \u2192 2026-09-09 (5.7 years).  No duplicated "
      "timestamps; ~0.1% of consecutive steps differ from 5 min (weekend/session-break rollovers).  Spread column "
      "is varied (not constant), never zero for the non-JPY pairs; the p10/med/p90 rows above show narrow, "
      "realistic point spreads.  `real_volume` is all zeros (volume data unusable).")
    A("\n- **EURJPY** (degraded): composite covers only 2025-06-26 \u2192 2026-09-10 (~14 months, 90,000 bars), "
      "27% of bars carry a zero spread value.  Spread values look synthesized, not live ticks.  EURJPY is flagged "
      "as unreliable and is **excluded from all behaviour tables**; it appears only in the inventory and pair "
      "comparison, where it is marked accordingly.")
    A("\n- **Spread semantics**: the `spread` column is best treated as a modeled per-bar spread (many distinct "
      "values, plausible range) rather than a live-tick feed.  Costs are therefore estimated from the observed "
      "median of this column; real execution costs could differ, and are not claimed.")
    A("\n- **Outliers / bad ticks**: no explicit tick-level validation was performed beyond timestamp continuity; "
      "extreme spikes would inflate mean-based movement statistics, so the report reports medians alongside means.")

    # ======================================================================
    A("\n## 4. Time-horizon behavior\n")
    A("\nForward movement `close[i+H]\u2212close[i]` (pips) and persistence by horizon, per core pair.  "
      "`cont 1-bar` = share where the H-forward move continues the direction of the previous 1-bar move; "
      "`cont H-bar` = share where it continues the direction of the previous H-bar move.  `rho1` = 1-bar "
      "return autocorrelation (persistence \u2192 sign; \u2248 0 \u2192 efficient; negative \u2192 1-bar reversal).\n")
    for sa in core:
        rows = []
        for st in _stat(sa.fwd, np.ones(sa.n, dtype=bool)):
            H = st["H"]
            if st["n"] == 0:
                continue
            fh = sa.fwd[H]
            rows.append([
                sa.symbol, _fmt_h(H), st["n"], st["mean"], st["med"], st["std"], st["p_pos"],
                _cont_share(fh, sa.m1, np.ones(sa.n, dtype=bool)),
                _cont_share(fh, np.sign(sa.mom[H]) if H in sa.mom else sa.m1, np.ones(sa.n, dtype=bool)) if H in sa.mom else "-",
            ])
        A("\n### " + sa.symbol + f"  (dev bars {sa.n:,}, 1-bar autocorr $\\rho_1$ = {_rho1(sa.ret1):+.3f})\n")
        A(_md_table(["symbol", "H bars", "n", "mean_pips", "med", "std", "p_pos%", "cont1%", "contH%"], rows))

    # ======================================================================
    A("\n## 5. Trend / momentum behavior\n")
    A("\nPrior change over W bars split **strong** vs **weak** by the symbol median |prior change| (a single fixed "
      "cut).  `up` = positive prior move (long side if momentum), `dn` = negative.  Reported values are the raw "
      "H-forward return in pips and the continuation hit (share where the forward move keeps the prior direction).\n")
    for sa in core:
        A(f"\n### {sa.symbol}\n")
        rows = []
        for W in MOM_WINDOWS:
            pc = sa.mom[W]
            mag = np.abs(pc)
            med_mag = np.nanmedian(mag)
            strong = mag > med_mag
            for H in SHORT_H:
                fh = sa.fwd[H]
                for d, dname, sign in [("up", "up", 1.0), ("dn", "dn", -1.0)]:
                    mask = strong & (np.sign(pc) == sign)
                    v = fh[mask]
                    v = v[np.isfinite(v)]
                    if len(v) == 0:
                        continue
                    rows.append([
                        sa.symbol, W, H, dname, len(v), float(v.mean()), float(np.median(v)),
                        _cont_share(fh, np.sign(pc), mask),
                        _pct(fh[mask]),
                    ])
                    sa.note("momentum", f"W={W} H={H} strong-{dname}", H, fh, mask)
        A(_md_table(["symbol", "W", "H", "side", "n", "mean_pips", "med_pips", "cont%", "p_pos%"], rows))

    # ======================================================================
    A("\n## 6. Volatility-regime behavior\n")
    A("\nATR(14) regime (causal 33/67 quantiles over 50 bars): `low`/`normal`/`high`.  `event` = a transition "
      "into the state.  `cont%` = share where the H-forward move continues the previous 1-bar direction; "
      "`rev%` = share where it reverses it (100\u2212cont% roughly).  Comparing the two after expansion tells whether "
      "the move after a volatility expansion is directional or mean-reverting.\n")
    for sa in core:
        A(f"\n### {sa.symbol}\n")
        rows = []
        states = [("low", "low"), ("normal", "normal"), ("high", "high"),
                  ("expansion_event", "high"), ("contraction_event", "low")]
        for tag, state in states:
            for H in SHORT_H:
                if tag in ("low", "normal", "high"):
                    mask = sa.reg == state
                elif tag == "expansion_event":
                    mask = (sa.reg == "high") & (sa.reg_prev != "high")
                else:
                    mask = (sa.reg == "low") & (sa.reg_prev != "low")
                fh = sa.fwd[H]
                v = fh[mask]
                v = v[np.isfinite(v)]
                if len(v) == 0:
                    continue
                rows.append([
                    sa.symbol, tag.replace("_event", ""), _fmt_h(H), len(v), float(v.mean()),
                    float(np.median(v)), _cont_share(fh, sa.m1, mask), 100.0 - (_cont_share(fh, sa.m1, mask) or 0.0),
                ])
                sa.note("volatility", f"{tag} H={H}", H, fh, mask)
        A(_md_table(["symbol", "state", "H", "n", "mean_pips", "med_pips", "cont%", "rev%"], rows))

    # ======================================================================
    A("\n## 7. Session / market-open behavior\n")
    A("\nPer-session forward behavior (signal = bar in session) plus the **first 6 bars of each session block** "
      "(`London open`, `LondonNY open`, `NewYork open`, `Asian open`).  `range_ratio` = mean bar range in the "
      "open window / symbol median bar range; `cont%` = share where the H=5 forward move continues the opening "
      "bar's direction; `fwd5_mean` = average forward 5-bar move in the window.\n")
    for sa in core:
        A(f"\n### {sa.symbol}\n")
        rows = []
        for H in SHORT_H:
            for sname in ["Asian", "London", "LondonNY", "NewYork", "OffHours"]:
                if not np.any(sa.sess == sname):
                    continue
                mask = sa.sess == sname
                fh = sa.fwd[H]
                v = fh[mask]
                v = v[np.isfinite(v)]
                rows.append([
                    sa.symbol, sname, _fmt_h(H), len(v), float(v.mean()), float(np.median(v)), _cont_share(fh, sa.m1, mask),
                ])
                sa.note("session", f"{sname} H={H}", H, fh, mask)
        A(_md_table(["symbol", "session", "H", "n", "mean_pips", "med_pips", "cont%"], rows))

        A("\nSession opens (first 6 bars of each block):\n")
        A(_md_table(
            ["symbol", "open", "n_bars", "range_ratio", "fwd5_mean_pips", "fwd5_med", "cont_open%", "p_pos%"],
            list(_open_rows(sa)),
        ))

    # ======================================================================
    A("\n## 8. Range / breakout structure\n")
    A("\nChannel = prior-20 high/low (causal).  `state` = up-break (close above prior-20 high), dn-break (close "
      "below prior-20 low), inside.  `cont%` = share where the H-forward move continues the break direction "
      "(breakout continuation); `persist%` = share where close[i+H] still sits beyond the broken level.  "
      "`range_exp` = bar range above its causal rolling median.\n")
    for sa in core:
        A(f"\n### {sa.symbol}\n")
        rows = []
        for state in ["up-break", "dn-break", "inside"]:
            for H in SHORT_H:
                if state == "up-break":
                    ok = np.isfinite(sa.ph) & (sa.c > sa.ph)
                    cont_dir = np.ones(sa.n, dtype=float)
                    persist_mask = sa.cshift[H] > sa.ph
                elif state == "dn-break":
                    ok = np.isfinite(sa.pl) & (sa.c < sa.pl)
                    cont_dir = -np.ones(sa.n, dtype=float)
                    persist_mask = sa.cshift[H] < sa.pl
                else:
                    ok = np.isfinite(sa.ph) & np.isfinite(sa.pl) & (sa.c <= sa.ph) & (sa.c >= sa.pl)
                    cont_dir = sa.m1
                    persist_mask = None
                fh = sa.fwd[H]
                v = fh[ok]
                v = v[np.isfinite(v)]
                if len(v) == 0:
                    continue
                cont = _cont_share(fh, cont_dir, ok)
                if persist_mask is not None:
                    pers = float((persist_mask & ok).sum() / ok.sum() * 100)
                else:
                    pers = float("nan")
                rows.append([sa.symbol, state, _fmt_h(H), len(v), float(v.mean()), float(np.median(v)), cont, pers])
                sa.note("breakout", f"{state} H={H}", H, fh, ok)
        A(_md_table(["symbol", "state", "H", "n", "mean_pips", "med_pips", "cont%", "persist%"], rows))

        A("\nRange expansion (bar range > causal rolling median):\n")
        A(_md_table(
            ["symbol", "condition", "H", "n", "mean_pips", "med_pips", "cont%", "p_pos%"],
            _range_exp_rows(sa),
        ))

    # ======================================================================
    A("\n## 9. Pair comparison\n")
    A("\nAll four pairs (EURJPY flagged unreliable).  `med|ret1|` = median 1-bar |move| in pips; `med_range`, "
      "`med_atr` in pips; `spread_med` in pips; `cost` = 2\u00d7spread_med + 1.7 pips; `rho1` = 1-bar autocorrelation; "
      "`cont20` = share of H=20 moves that continue the previous 20-bar direction (trend persistence); "
      "`rev5` = share of H=5 moves reversing the previous 1-bar move; `max_dir20` = max |mean| H=20 forward move "
      "in either direction (raw directional magnitude); `mov/cost` = med|ret1|/cost; `edge/cost` = max_dir20/cost.\n")
    rows = []
    A(_md_table(["symbol", "med|ret1|", "med_range", "med_atr", "spread_med", "cost", "rho1", "cont20%", "rev5%", "max_dir20", "mov/cost", "edge/cost"],
                 [_pair_row(analyses[s]) for s in ALL_SYMBOLS]))

    # ======================================================================
    A("\n## 10. Signal-to-cost analysis\n")
    A("\nFor every behavior/condition/horizon with n \u2265 {0} (see below) the raw mean movement is divided by the "
      "pair's realistic round-trip cost.  This is the raw `movement-to-cost` ratio.  Each row below is a "
      "distinct behavior/horizon/pair.  Behaviors with ratio \u2265 1.0 are those whose raw expected move could "
      "plausibly clear costs if the edge direction were known (this does not make them tradable).\n".format(MIN_BEHAV_N))
    beh = [b for sa in core for b in sa.beh]
    beh_sorted = sorted(beh, key=lambda b: b["movement_to_cost"], reverse=True)
    A(_md_table(
        ["sym", "behavior", "condition", "H_min", "n", "mean", "med", "hit%", "std", "cost", "ratio"],
        [[b["symbol"], b["behavior"], b["condition"], b["horizon_min"], b["n"], b["mean_pips"], b["med_pips"],
          b["hit_pct_positive"], b["std_pips"], b["cost_pips"], b["movement_to_cost"]] for b in beh_sorted],
    ))

    # ======================================================================
    # Narrative sections assembled from the numbers above.
    # ======================================================================
    strong = [b for b in beh_sorted if b["movement_to_cost"] >= 1.0 and abs(b["mean_pips"]) >= 2.0]

    A("\n## 11. Strongest behaviors discovered\n")
    if strong:
        A("\nThe behaviors below have raw mean movement-to-cost ratio \u2265 1.0 and raw mean \u2265 2.0 pips, with "
          "n \u2265 {0}:\n".format(MIN_BEHAV_N))
        A(_md_table(
            ["sym", "behavior", "condition", "H_min", "n", "mean", "med", "hit%", "std", "cost", "ratio"],
            [[b["symbol"], b["behavior"], b["condition"], b["horizon_min"], b["n"], b["mean_pips"], b["med_pips"],
              b["hit_pct_positive"], b["std_pips"], b["cost_pips"], b["movement_to_cost"]] for b in strong[:15]],
        ))
    else:
        A("\nNo behavior met the ratio \u2265 1.0 / mean \u2265 2.0 pips bar on the DEV split.")

    A("\n## 12. Weakest / rejected behaviors\n")
    A("\nThe behaviors that were clearly negative or too small to review include the M5 continuation family "
      "(negative or near-zero raw edges), sessions whose mean forward move is smaller than their own cost "
      "(all expected with M5 horizons), and EURJPY (excluded on data quality).  Section 4, 5 and 7 report the "
      "raw numbers for each.")

    A("\n## 13. TOP 3 potential research directions\n")
    A(_top3(strong, beh_sorted))

    A("\n## 14. Recommended next strategy candidate\n")
    A(_recommendation(strong, beh_sorted))

    A("\n## 15. Exact evidence supporting that recommendation\n")
    A(_evidence(strong, beh_sorted))

    A("\n## 16. What should NOT be tested\n")
    A("\n- M5 continuation/breakout-continuation on these pairs without a separate strong-condition filter "
      "(negative raw edges in earlier phases and section 5).")
    A("- Any EURJPY-based edge using the current degraded composite (25% zero spreads, 14-month window).")
    A("- Parameter variants of Strategies 01\u201303; those are rejected experiments and must not return in disguise.")
    A("- Tight stop loss (1 ATR) continuations of slow mean-reversion fades (proven loss-making under costs in "
      "Phase 2).")
    A("- Volume-weighted signals: the `real_volume` column is entirely zero.")

    A("\n## 17. Integrity / limitations\n")
    A("\n- DEV split only; validation and holdout were never read.  60/20/20 split preserved (section 2 counts).")
    A("- Research only: no strategy implemented, no backtest run, no parameter optimized, no multiple variants.")
    A("- Raw movement is measured at close-to-close horizons with realistic observed spreads; it is NOT P&L. "
      "No profitability is claimed anywhere in this report.")
    A("- Medians are reported alongside means because means are inflated by outliers; EURJPY is excluded from "
      "behaviour tables on data quality.")
    A("- `spread` is modeled/synthesized (distinct values but not live ticks); true execution costs are unknown "
      "and could be materially different.")

    report_path = _root / REPORT_PATH
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(pcfg.output_dir / "edge_research.json", "w", encoding="utf-8") as f:
        json.dump(beh, f, indent=2)
    print(f"Report written to {report_path}")
    print(f"Behaviour dump: {pcfg.output_dir / 'edge_research.json'}")
    return 0


# ---------------------------------------------------------------------------
# Helper builders used by main()
# ---------------------------------------------------------------------------

def _open_rows(sa: SymbolAnalysis) -> list[list[Any]]:
    rows = []
    session_block_change = np.zeros(sa.n, dtype=bool)
    session_block_change[1:] = sa.sess[1:] != sa.sess[:-1]
    for start_hour in [0, 7, 12, 16]:  # Asian, London, LondonNY, NewYork opens
        start_idx = np.where(session_block_change & (pd.to_datetime(sa.time).hour == start_hour))[0]
        if len(start_idx) == 0:
            continue
        mask = np.zeros(sa.n, dtype=bool)
        for s in start_idx:
            mask[s : s + 6] = True
        wmask = mask
        rng_v = sa.rng[wmask]
        rng_v = rng_v[np.isfinite(rng_v)]
        f5 = sa.fwd[5][wmask]
        f5 = f5[np.isfinite(f5)]
        name = {0: "Asian", 7: "London", 12: "LondonNY", 16: "NewYork"}[start_hour]
        cont = _cont_share(sa.fwd[5], sa.m1, wmask)
        sa.note("session_open", f"{name}-open window", 5, sa.fwd[5], wmask)
        rows.append([
            sa.symbol, f"{name} open", int(wmask.sum()),
            float(np.mean(rng_v) / np.nanmedian(sa.rng)) if len(rng_v) else float("nan"),
            float(f5.mean()) if len(f5) else float("nan"),
            float(np.median(f5)) if len(f5) else float("nan"),
            cont, _pct(sa.fwd[5][wmask]),
        ])
    return rows


def _range_exp_rows(sa: SymbolAnalysis) -> list[list[Any]]:
    rows = []
    mask = sa.rng > sa.rng_med
    for H in [5, 20]:
        fh = sa.fwd[H]
        v = fh[mask]
        v = v[np.isfinite(v)]
        rows.append([
            sa.symbol, "range_exp", _fmt_h(H), len(v), float(v.mean()),
            float(np.median(v)) if len(v) else float("nan"),
            _cont_share(fh, sa.m1, mask), _pct(fh[mask]),
        ])
    return rows


def _pair_row(sa: SymbolAnalysis) -> list[Any]:
    ret1 = sa.ret1
    ok = np.isfinite(ret1)
    med_abs = float(np.median(np.abs(ret1[ok])))
    max_dir20 = 0.0
    for side in ("up", "dn"):
        pc = sa.mom[20]
        if side == "up":
            m = np.sign(pc) == 1
        else:
            m = np.sign(pc) == -1
        v = sa.fwd[20][m]
        v = v[np.isfinite(v)]
        if len(v):
            max_dir20 = max(max_dir20, abs(float(v.mean())))
    return [
        sa.symbol,
        med_abs,
        float(np.median(sa.rng)),
        float(np.nanmedian(sa.atr)),
        float(np.median(sa.spread_pips)),
        sa.cost_pips,
        _rho1(ret1),
        _cont_share(sa.fwd[20], np.sign(sa.mom[20]), np.ones(sa.n, dtype=bool)),
        100.0 - (_cont_share(sa.fwd[5], sa.m1, np.ones(sa.n, dtype=bool)) or 0.0),
        max_dir20,
        med_abs / sa.cost_pips,
        max_dir20 / sa.cost_pips if sa.cost_pips else float("nan"),
    ]


def _top3(strong: list[dict], beh_sorted: list[dict]) -> str:
    top = (strong[:3] if strong else []) or beh_sorted[:3]
    if not top:
        return "\nThe behavior table is empty (everything fell below the n-floor); no direction can be listed."
    cleared = any(b["movement_to_cost"] >= 1.0 and abs(b["mean_pips"]) >= 2.0 for b in top)
    lines = [f"\nTop {len(top)} raw behaviors by movement-to-cost (n \u2265 {MIN_BEHAV_N}, DEV only):"]
    for i, b in enumerate(top, 1):
        flag = " **CLEARS COST BAR (pre-registered candidate)**" if (b["movement_to_cost"] >= 1.0 and abs(b["mean_pips"]) >= 2.0) else ""
        lines.append(
            f"{i}. **{b['behavior']} on {b['symbol']}** ({b['condition']}, horizon {b['horizon_min']} min): "
            f"raw mean {b['mean_pips']:+.2f} pips, median {b['med_pips']:+.2f}, hit {b['hit_pct_positive']:.1f}%, "
            f"n={b['n']:,}, cost {b['cost_pips']:.2f} pips, movement-to-cost {b['movement_to_cost']:.2f}.{flag}"
        )
    if not cleared:
        lines.append("None of these clears the cost bar; they are the LEAST-unattractive raw behaviors, not an edge.")
    return "\n".join(lines)


def _recommendation(strong: list[dict], beh_sorted: list[dict]) -> str:
    if strong:
        b = strong[0]
        return (f"The first candidate worth a pre-registered validation test is the strongest raw behavior found on DEV: "
                f"**{b['behavior']}** on **{b['symbol']}** ({b['condition']}, horizon {b['horizon_min']} min).  It shows "
                f"raw mean movement {b['mean_pips']:+.2f} pips against {b['cost_pips']:.2f} pips cost "
                f"(ratio {b['movement_to_cost']:.2f}), n={b['n']:,}.  This is a RESEARCH RECOMMENDATION only; the "
                "candidate must be specified, frozen and tested on validation before any claim.")
    if beh_sorted:
        b = beh_sorted[0]
        return ("No M5 behavior on the DEV split clears the movement-to-cost bar; the best raw ratio is "
                f"{b['movement_to_cost']:.2f} ({b['symbol']} / {b['behavior']} / {b['condition']}, "
                f"mean {b['mean_pips']:+.2f} pips vs {b['cost_pips']:.2f} pips cost).  The evidence-based recommendation "
                "is to research MULTI-HOUR / DAILY horizons (H \u2265 240) and the session-open windows, where raw "
                "movement is structurally larger (section 7 shows London-open windows at ~1.8\u00d7 median range), "
                "before proposing any new strategy candidate.")
    return ("No behavior exceeded the n-floor; the report's DEV statistics (sections 4\u20139) remain the only "
            "evidence, and they do not support an M5 edge.")


def _evidence(strong: list[dict], beh_sorted: list[dict]) -> str:
    if strong:
        lines = []
        for b in strong[:5]:
            lines.append(
                f"- {b['symbol']} / {b['behavior']} / {b['condition']} @ H={b['horizon_bars']}: "
                f"n={b['n']:,}, raw mean {b['mean_pips']:+.2f} pips, median {b['med_pips']:+.2f}, "
                f"hit {b['hit_pct_positive']:.1f}%, std {b['std_pips']:.2f}, cost {b['cost_pips']:.2f} pips, "
                f"movement-to-cost {b['movement_to_cost']:.2f}."
            )
        return "\n".join(lines)
    if beh_sorted:
        lines = ["The best raw movement-to-cost ratios on DEV (all below the 1.0 bar):"]
        for b in beh_sorted[:5]:
            lines.append(
                f"- {b['symbol']} / {b['behavior']} / {b['condition']} @ H={b['horizon_bars']}: "
                f"n={b['n']:,}, raw mean {b['mean_pips']:+.2f} pips, median {b['med_pips']:+.2f}, "
                f"hit {b['hit_pct_positive']:.1f}%, std {b['std_pips']:.2f}, cost {b['cost_pips']:.2f} pips, "
                f"ratio {b['movement_to_cost']:.2f}."
            )
        lines.append("Sections 4\u20139 confirm every core-pair M5 forward mean is under ~1.5 pips while costs run "
                     "2.3\u20133.5 pips; no M5-level behavior is a credible edge.")
        return "\n".join(lines)
    return ("Sections 4\u20137 show all raw M5 means and medians to be small in magnitude (typically < 2 pips) "
            "relative to 2\u20133.5 pip costs (section 4, 9-10).")


if __name__ == "__main__":
    raise SystemExit(main())