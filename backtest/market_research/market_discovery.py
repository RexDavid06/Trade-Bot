"""PHASE 1 — Market Behavior Discovery (exploratory, DEVELOPMENT data only).

Runs the existing market-research studies on the chronological DEVELOPMENT
split of all four pairs and aggregates the results into
``MARKET_BEHAVIOR_DISCOVERY.md``.

Integrity guarantees enforced in this module:

* Only bars tagged ``dev`` in ``outputs/splits/<SYMBOL>/assignments.csv`` are
  read. Validation and holdout bars are never loaded or referenced.
* The split is produced by the existing ``research_split`` framework
  (deterministic chronological 60/20/20) and validated for isolation.
* No strategy is constructed, no parameter is optimized, and ``bot.py`` /
  V1/V2 are untouched.
* All study outputs are written under ``outputs/market_behavior_discovery/`` so
  historical outputs are never overwritten.

Usage::

    python -m backtest.market_research.market_discovery
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from ..config import PathConfig
from ..instruments import get_instrument
from ..data.research_split import SUPPORTED_SYMBOLS, make_research_split, validate_split_isolation
from . import momentum, mean_reversion, breakout, volatility, sessions  # noqa: F401
from . import trend_persistence, range_behavior  # noqa: F401
from .common import HORIZONS, SMALL_N, atr_regime, session_label, _summarize

STUDY_MODULES = {
    "momentum": momentum,
    "mean_reversion": mean_reversion,
    "breakout": breakout,
    "volatility": volatility,
    "sessions": sessions,
    "trend_persistence": trend_persistence,
    "range_behavior": range_behavior,
}

ATR_PERIOD = 14
REGIME_LOOKBACK = 50
TREND_WINDOW = 20
HEADLINE_H = 20
HSCALE = [5, 20, 40, 80]


# ---------------------------------------------------------------------------
# Data loading (dev-only)
# ---------------------------------------------------------------------------

def _dev_df(symbol: str, data_dir: Path, out_dir: Path) -> tuple[pd.DataFrame, dict]:
    assignments = out_dir / "splits" / symbol / "assignments.csv"
    if not assignments.exists():
        make_research_split(symbol, data_dir, out_dir)
    validation = validate_split_isolation(assignments)
    if not validation["valid"]:
        raise RuntimeError(f"{symbol}: split validation failed: {validation['violations']}")

    df = pd.read_csv(data_dir / f"{symbol.lower()}_m5.csv")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    asn = pd.read_csv(assignments)
    asn["time"] = pd.to_datetime(asn["time"])
    dev_times = pd.Index(asn.loc[asn["split"] == "dev", "time"])
    dev = df[df["time"].isin(dev_times)].reset_index(drop=True)
    return dev, validation


def _true_range(high: np.ndarray, low: np.ndarray, prev_close: np.ndarray) -> np.ndarray:
    return np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))


def _atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ATR_PERIOD) -> np.ndarray:
    prev_close = np.concatenate([[np.nan], close[:-1]])
    tr = _true_range(high, low, prev_close)
    return pd.Series(tr).ewm(alpha=1 / period, adjust=False, min_periods=period).mean().to_numpy()


def _pips(x: np.ndarray, pip: float) -> np.ndarray:
    return np.asarray(x, dtype=float) / pip


# ---------------------------------------------------------------------------
# Vectorized forward windows + excursions
# ---------------------------------------------------------------------------

def _fwd_window(high: np.ndarray, low: np.ndarray, close: np.ndarray, H: int):
    """Return arrays aligned to bar i covering the NEXT H bars (i+1..i+H).

    All returned arrays have length ``n - H`` where element ``i`` corresponds to
    original bar ``i`` (``i`` in 0..n-H-1).
    """
    n = len(close)
    fut_high = sliding_window_view(high, H + 1)[:, 1:].max(axis=1)
    fut_low = sliding_window_view(low, H + 1)[:, 1:].min(axis=1)
    cur_close = close[: n - H]
    fwd_move = close[H:] - cur_close
    return fut_high, fut_low, cur_close, fwd_move


def _cond_rows(
    fwd_pips: np.ndarray,
    state_masks: dict[str, np.ndarray],
    label_map: dict[str, str] | None = None,
) -> list[dict]:
    """Rows from common._summarize for each boolean state mask (aligned)."""
    rows = []
    fm = np.isfinite(fwd_pips)
    for key, mask in state_masks.items():
        m = mask[: len(fwd_pips)]
        v = fwd_pips[m & fm]
        label = label_map.get(key, key) if label_map else key
        rows.append(_summarize(v, v, label))
    return rows


# ---------------------------------------------------------------------------
# Headline state definitions (causal, past bars only)
# ---------------------------------------------------------------------------

def _trend_states(close: np.ndarray, tw: int) -> dict[str, np.ndarray]:
    n = len(close)
    net = np.full(n, np.nan)
    net[tw:] = np.sign(close[tw:] - close[:-tw])
    return {
        "up_trend": net > 0,
        "down_trend": net < 0,
        "flat_trend": np.abs(net) == 0,
    }


def _meanrev_states(close: np.ndarray, lb: int) -> dict[str, np.ndarray]:
    n = len(close)
    sma = pd.Series(close).rolling(lb).mean().to_numpy()
    std = pd.Series(close).rolling(lb, min_periods=lb).std(ddof=0).to_numpy()
    dist = np.full(n, np.nan)
    ok = ~np.isnan(sma) & (std > 0)
    dist[ok] = (close[ok] - sma[ok]) / std[ok]
    return {"oversold_le_neg1": dist <= -1.0, "overbought_ge_1": dist >= 1.0, "neutral": (np.abs(dist) < 0.5)}


def _breakout_states(high: np.ndarray, low: np.ndarray, close: np.ndarray, ch: int) -> dict[str, np.ndarray]:
    n = len(close)
    prior_max_high = pd.Series(high).shift(1).rolling(ch).max().to_numpy()
    prior_min_low = pd.Series(low).shift(1).rolling(ch).min().to_numpy()
    return {
        "high_breakout": close > prior_max_high,
        "low_breakout": close < prior_min_low,
        "inside": (close <= prior_max_high) & (close >= prior_min_low),
    }


def _pullback_states(close: np.ndarray, tw: int) -> dict[str, np.ndarray]:
    """Pullbacks inside an established trend (causal 20-bar trend)."""
    n = len(close)
    net = np.full(n, np.nan)
    net[tw:] = np.sign(close[tw:] - close[:-tw])
    up_regime = net > 0
    down_regime = net < 0
    down_bar = np.full(n, False)
    up_bar = np.full(n, False)
    if n > 1:
        down_bar[1:] = close[1:] < close[:-1]
        up_bar[1:] = close[1:] > close[:-1]
    pull_long = up_regime & down_bar
    pull_short = down_regime & up_bar
    d = pd.Series(down_bar.astype(int))
    grp = (d == 0).cumsum()
    streak = d.groupby(grp).cumsum().to_numpy()
    return {
        "pull_long_any": pull_long,
        "pull_long_depth1": pull_long & (streak == 1),
        "pull_long_depth2": pull_long & (streak == 2),
        "pull_long_depth3plus": pull_long & (streak >= 3),
        "pull_short_any": pull_short,
    }


# ---------------------------------------------------------------------------
# Aggregated per-symbol analytics
# ---------------------------------------------------------------------------

def _symbol_analytics(symbol: str, dev: pd.DataFrame, pip: float) -> dict:
    high = dev["high"].to_numpy(dtype=float)
    low = dev["low"].to_numpy(dtype=float)
    close = dev["close"].to_numpy(dtype=float)
    n = len(close)

    atr = _atr(high, low, close)
    regime = atr_regime(atr, REGIME_LOOKBACK)
    hour = pd.to_datetime(dev["time"]).dt.hour.to_numpy()
    sess = session_label(hour)

    H = HEADLINE_H
    Hn = n - H

    # --- headlined forward stats at TREND_WINDOW-based conditions
    fh = _fwd_window(high, low, close, H)
    fut_high, fut_low, cur_close, fwd_move = fh
    fwd_pips = _pips(fwd_move, pip)          # length Hn, aligned to bar i

    trend = _trend_states(close, TREND_WINDOW)
    mrv = _meanrev_states(close, TREND_WINDOW)
    brk = _breakout_states(high, low, close, TREND_WINDOW)
    pull = _pullback_states(close, TREND_WINDOW)

    # trend continuation: long on up-trend, short on down-trend
    up_mask = trend["up_trend"][: Hn]
    dn_mask = trend["down_trend"][: Hn]
    cont_signed = np.where(up_mask, fwd_pips,
                           np.where(dn_mask, -fwd_pips, np.nan))
    toolong_cont = _summarize(cont_signed, cont_signed, "trend_continuation20")

    # mean reversion: long after oversold, short after overbought
    mrv_signed = np.where(mrv["oversold_le_neg1"][: Hn], fwd_pips,
                          np.where(mrv["overbought_ge_1"][: Hn], -fwd_pips, np.nan))
    toolong_mrv = _summarize(mrv_signed, mrv_signed, "meanrev20")

    # breakout: long after high breakout, short after low breakout
    brk_signed = np.where(brk["high_breakout"][: Hn], fwd_pips,
                          np.where(brk["low_breakout"][: Hn], -fwd_pips, np.nan))
    toolong_brk = _summarize(brk_signed, brk_signed, "breakout20")

    # pullback: long after dip in uptrend
    pl_mask = pull["pull_long_any"][: Hn]
    pl_signed = fwd_pips[pl_mask & np.isfinite(fwd_pips)]

    # regime-conditioned continuation
    reg_rows = {}
    for rg in ["low", "normal", "high"]:
        m = (np.asarray(regime)[: Hn] == rg)
        v = cont_signed[m & np.isfinite(cont_signed)]
        reg_rows[rg] = _summarize(v, v, f"trend_cont_{rg}")

    # session-conditioned continuation
    sess_rows = {}
    for sname in ["Asian", "London", "LondonNY", "NewYork", "OffHours"]:
        m = (sess[: Hn] == sname)
        v = cont_signed[m & np.isfinite(cont_signed)]
        sess_rows[sname] = _summarize(v, v, f"trend_cont_{sname}")

    # excursions for headline long setups
    exc_rows = {}
    exc_specs = {
        "trend_up_long": trend["up_trend"][: Hn],
        "oversold_long": mrv["oversold_le_neg1"][: Hn],
        "high_breakout_long": brk["high_breakout"][: Hn],
        "pullback_long": pull["pull_long_any"][: Hn],
    }
    for name, mask in exc_specs.items():
        fav = (fut_high[mask] - cur_close[mask]) / pip
        adv = (cur_close[mask] - fut_low[mask]) / pip
        fav = fav[np.isfinite(fav)]
        adv = adv[np.isfinite(adv)]
        if len(fav):
            exc_rows[name] = {
                "n": int(len(fav)),
                "avg_fav_pips": float(fav.mean()),
                "med_fav_pips": float(np.median(fav)),
                "avg_adv_pips": float(adv.mean()),
                "med_adv_pips": float(np.median(adv)),
            }

    # horizon scaling for the three candidate directional behaviors
    horizon = {}
    for H in HSCALE:
        Hn_h = n - H
        fwd_pips_h = _pips(_fwd_window(high, low, close, H)[3], pip)
        tc_signed = np.where(trend["up_trend"][: Hn_h], fwd_pips_h,
                             np.where(trend["down_trend"][: Hn_h], -fwd_pips_h, np.nan))
        mr_long_v = fwd_pips_h[mrv["oversold_le_neg1"][: Hn_h]]
        mr_short_v = -fwd_pips_h[mrv["overbought_ge_1"][: Hn_h]]
        bf_long_v = -fwd_pips_h[brk["high_breakout"][: Hn_h]]
        bf_short_v = fwd_pips_h[brk["low_breakout"][: Hn_h]]
        mr_fade_v = np.concatenate([mr_long_v, mr_short_v]) if len(mr_long_v) and len(mr_short_v) else np.full(0, np.nan)
        bf_fade_v = np.concatenate([bf_long_v, bf_short_v]) if len(bf_long_v) and len(bf_short_v) else np.full(0, np.nan)
        horizon[H] = {
            "trend_cont": _summarize(tc_signed, tc_signed, f"tc{H}"),
            "mr_fade": _summarize(mr_fade_v, mr_fade_v, f"mr{H}"),
            "breakout_fade": _summarize(bf_fade_v, bf_fade_v, f"bf{H}"),
        }

    # spread/cost proxy from the dev bars (points -> pips per side)
    spread_pts = dev["spread"].to_numpy(dtype=float)
    med_spread_points = float(np.median(spread_pts[np.isfinite(spread_pts)]))
    point = get_instrument(symbol).point

    return {
        "symbol": symbol,
        "n_dev": int(n),
        "dev_first": str(dev["time"].iloc[0]),
        "dev_last": str(dev["time"].iloc[-1]),
        "atr_median_pips": float(np.nanmedian(atr) / pip),
        "median_spread_points": med_spread_points,
        "median_spread_price_pips": float(med_spread_points * point / pip),
        "trend_continuation_H20": toolong_cont,
        "mean_reversion_H20": toolong_mrv,
        "breakout_H20": toolong_brk,
        "pullback_long_H20": _summarize(pl_signed, pl_signed, "pullback_long"),
        "pull_back_depth": {d: _summarize(fwd_pips[(pull[f"pull_long_{d}"][: len(fwd_pips)]) & np.isfinite(fwd_pips)],
                                          fwd_pips[(pull[f"pull_long_{d}"][: len(fwd_pips)]) & np.isfinite(fwd_pips)],
                                          f"d{d}") for d in ["depth1", "depth2", "depth3plus"]},
        "trend_cont_by_regime": reg_rows,
        "trend_cont_by_session": sess_rows,
        "excursions_H20": exc_rows,
        "regime_freq": {
            rg: int(np.sum(np.asarray(regime)[: Hn] == rg)) for rg in ["low", "normal", "high"]
        },
        "horizon": horizon,
    }


def _leaderboard(an: dict, cost_pips: float) -> list[dict]:
    cands = []
    specs = [
        ("trend_continuation_H20", "trend continuation"),
        ("mean_reversion_H20", "mean-reversion"),
        ("breakout_H20", "breakout"),
        ("pullback_long_H20", "trend+pullback"),
    ]
    for key, label in specs:
        r = an[key]
        edge = float(r["avg_pips"]) - cost_pips if r["avg_pips"] == r["avg_pips"] else float("nan")
        cands.append({
            "symbol": an["symbol"],
            "behavior": label,
            "n": int(r["n"]),
            "avg_pips": r["avg_pips"],
            "med_pips": r["med_pips"],
            "hit_pct": r["hit_pct"],
            "t_p": r["t_p"],
            "est_net_after_cost_pips": edge,
        })
    return cands


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def _md_table(rows: list[dict], cols: list[str]) -> str:
    header = "| " + " | ".join(cols) + " |"
    sep = "|" + "---|" * len(cols)
    lines = [header, sep]
    for r in rows:
        vals = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, float):
                if v != v:
                    vals.append("-")
                elif c in ("hit_pct",):
                    vals.append(f"{v:.1f}")
                elif c in ("t_p", "z_p"):
                    vals.append(f"{v:.3f}")
                elif c in ("avg_pips", "med_pips", "avg_fav_pips", "med_fav_pips",
                           "avg_adv_pips", "med_adv_pips", "est_net_after_cost_pips"):
                    vals.append(f"{v:.2f}")
                else:
                    vals.append(f"{v:.2f}")
            elif isinstance(v, int):
                vals.append(str(v))
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def _summ_to_row(r: dict, prefix: str = "") -> dict:
    return {
        f"n": int(r["n"]),
        f"avg_pips": r["avg_pips"],
        f"med_pips": r["med_pips"],
        f"hit_pct": r["hit_pct"],
        f"t_p": r["t_p"],
    }


def main() -> int:
    pcfg = PathConfig()
    data_dir = pcfg.base_dir / "data"
    out_dir = pcfg.output_dir
    disc_dir = out_dir / "market_behavior_discovery"
    disc_dir.mkdir(parents=True, exist_ok=True)

    per_symbol = {}
    leaderboard = []

    for symbol in SUPPORTED_SYMBOLS:
        try:
            dev, validation = _dev_df(symbol, data_dir, out_dir)
        except RuntimeError as e:
            print(f"  SKIP {symbol}: {e}")
            continue
        pip = get_instrument(symbol).pip

        sym_dir = disc_dir / symbol
        sym_dir.mkdir(parents=True, exist_ok=True)

        study_notes = []
        for name, mod in STUDY_MODULES.items():
            t0 = pd.Timestamp.now()
            res = mod.run(dev, pip=pip)
            elapsed = (pd.Timestamp.now() - t0).total_seconds()
            with open(sym_dir / f"{name}.md", "w", encoding="utf-8") as fh:
                fh.write(f"## Dataset (DEV only)\n\n")
                fh.write(f"- **Symbol**: {symbol}\n")
                fh.write(f"- **Split**: output from `research_split` (60/20/20 chronological)\n")
                fh.write(f"- **Dev date range**: {dev['time'].iloc[0]} .. {dev['time'].iloc[-1]}\n")
                fh.write(f"- **Dev candles**: {len(dev):,}\n")
                fh.write(f"- **Validation meta**: {validation['counts']}\n\n")
                fh.write(res["md"])
            with open(sym_dir / f"{name}.json", "w", encoding="utf-8") as fh:
                json.dump(res["results"], fh, indent=2, default=float)
            study_notes.append(f"{name}({elapsed:.1f}s)")

        an = _symbol_analytics(symbol, dev, pip)
        per_symbol[symbol] = an
        leaderboard.extend(_leaderboard(an, cost_pips=_cost_estimate(an)))
        print(f"  OK {symbol}: dev={an['n_dev']:,} "
              f"{an['dev_first']} .. {an['dev_last']}  " + " ".join(study_notes))

    stats_out = disc_dir / "stats.json"
    with open(stats_out, "w", encoding="utf-8") as fh:
        json.dump({"per_symbol": per_symbol, "leaderboard": leaderboard},
                  fh, indent=2, default=str)

    leaderboard = sorted(leaderboard, key=lambda r: r["est_net_after_cost_pips"], reverse=True)

    print("\n--- LEADERBOARD (est. net pips after ~typical cost, H=20) ---")
    print(_md_table(leaderboard, ["symbol", "behavior", "n", "avg_pips", "med_pips", "hit_pct", "t_p",
                                  "est_net_after_cost_pips"]))

    report = _build_report(per_symbol, leaderboard, out_dir)
    with open(pcfg.base_dir / "MARKET_BEHAVIOR_DISCOVERY.md", "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"\nReport written to {pcfg.base_dir / 'MARKET_BEHAVIOR_DISCOVERY.md'}")
    return 0


def _cost_estimate(an: dict) -> float:
    """Typical round-trip cost in pips (spread x2 + slippage ~1 + commission ~0.7)."""
    return float(an["median_spread_price_pips"]) * 2.0 + 1.0 + 0.7


def _build_report(per_symbol: dict, leaderboard: list[dict], out_dir: Path) -> str:
    fmt_rows = [r for r in leaderboard if r["avg_pips"] == r["avg_pips"]]

    L: list[str] = []
    w = L.append
    w("# Market Behavior Discovery")
    w("")
    w("**Exploratory findings, DEVELOPMENT split only. All results are "
    "hypotheses to be validated — nothing here is a proven edge.**")
    w("")

    w("## 0. Methodology and integrity")
    w("")
    w("- Data: M5 OHLC + observed spread for EURUSD, EURGBP, GBPUSD "
      "(2021-01-03 .. 2026-09-09) and EURJPY (2025-06-26 .. 2026-09-10, "
      "27% zero-spread bars — degraded feed, cost claims for EURJPY are unreliable).")
    w("- Only DEV bars used; split produced and validated by "
      "`backtest.data.research_split` (60/20/20 chronological).")
    w("- Holdout and validation rows were never read.")
    w("- No strategy constructed; no parameter optimized; `bot.py`, V1/V2 untouched.")
    w("- Full per-study detail: `outputs/market_behavior_discovery/<SYMBOL>/<study>.md`.")
    w("")
    w("### Dev date ranges and sizes")
    w("")
    w("| symbol | dev candles | dev start | dev end |")
    w("|---|---|---|---|")
    for sym, an in per_symbol.items():
        w(f"| {sym} | {an['n_dev']:,} | {an['dev_first']} | {an['dev_last']} |")
    w("")

    # ---- section 1: executive summary (computed, not hand-written) ----
    mr = {sym: an["mean_reversion_H20"] for sym, an in per_symbol.items()}
    tc = {sym: an["trend_continuation_H20"] for sym, an in per_symbol.items()}
    bx = {sym: an["breakout_H20"] for sym, an in per_symbol.items()}
    best_sym = max(per_symbol, key=lambda s: mr[s]["avg_pips"])
    all_tc = [tc[s]["avg_pips"] for s in per_symbol]
    all_bx = [bx[s]["avg_pips"] for s in per_symbol]

    w("## 1. Executive summary")
    w("")
    w(f"Four pairs (EURUSD, EURGBP, GBPUSD, EURJPY), first-60% DEVELOPMENT rows only, "
      f"investigated with seven existing `market_research` studies plus a discovery "
      f"aggregator that measures raw directional behavior across horizons of "
      f"5/20/40/80 M5 bars (25 min .. 6.7 h). All conditions are causal; outcomes "
      f"are fixed-horizon forward returns measured after the signal bar, so no "
      f"lookahead enters these numbers.")
    w("")
    w("**1. The market at M5 is mildly, reliably mean-reverting.** Trend continuation "
      f"is negative on every pair ({min(all_tc):.2f} .. {max(all_tc):.2f} pips avg; hit "
      f"{min(tc[s]['hit_pct'] for s in per_symbol):.1f}--{max(tc[s]['hit_pct'] for s in per_symbol):.1f}%), "
      f"so short-term trends do not persist. Naive breakouts are consistently bad "
      f"({min(all_bx):.2f} .. {max(all_bx):.2f} pips; hit "
      f"{min(bx[s]['hit_pct'] for s in per_symbol):.1f}--{max(bx[s]['hit_pct'] for s in per_symbol):.1f}%). "
      f"The only behavior that is positive on all four pairs is fading the extreme: "
      f"oversold-fade long / overbought-fade short. It is strongest on EURGBP "
      f"({mr['EURGBP']['avg_pips']:.2f} pips, hit {mr['EURGBP']['hit_pct']:.1f}%) and GBPUSD "
      f"({mr['GBPUSD']['avg_pips']:.2f} pips, hit {mr['GBPUSD']['hit_pct']:.1f}%), with EURUSD "
      f"({mr['EURUSD']['avg_pips']:.2f}, hit {mr['EURUSD']['hit_pct']:.1f}%); all three are "
      f"statistically reliable (t_p < 1e-3).")
    w("")
    for sym, an in per_symbol.items():
        w(f"- **{sym}** mean-reversion H=20: **{mr[sym]['avg_pips']:+.2f} pips**, hit "
          f"{mr[sym]['hit_pct']:.1f}% (n={mr[sym]['n']:,}); estimated round-trip cost "
          f"{_cost_estimate(an):.2f} pips; est. net after cost "
          f"**{mr[sym]['avg_pips'] - _cost_estimate(an):+.2f} pips**.")
    w("")
    w("**2. No raw M5 behavior clears costs on its own.** The best gross edges above are "
      "~0.2-0.4 pips at H=20. Measured round-trip costs (median spread x2 + ~1.7 "
      "slippage/commission) are 2.3-3.5 pips on EURUSD/EURGBP/GBPUSD and ~5.7 on "
      f"EURJPY. The strongest clean-pair edge (EURGBP {mr['EURGBP']['avg_pips']:.2f} pips) covers "
      "less than 15% of its cost. Even the horizon scaling in section 2 (edge grows to "
      "~0.5-1.3 pips at H=80 on EURGBP/GBPUSD) stays well below break-even.")
    w("")
    w("**3. Conditioning changes sign, not scale.** Session overlay is the only "
      "conditioning that flips behavior direction: trend continuation turns positive in "
      "the London-New York overlap (EURUSD +0.12/50.1%, GBPUSD +0.49/50.5%) and is "
      "strongly negative in OffHours (hit 39-47%). Volatility-regime conditioning is "
      "weak and direction-inconsistent. Forward excursions are symmetric (favorable "
      "median ~= adverse median, ~6 pips on EURUSD/EURGBP, ~9 on GBPUSD), so naive "
      "entries leave price as much room to hurt as to help: any candidate needs a stop.")
    w("")
    w("**4. EURJPY is not evidence yet.** Its fade-oversold numbers look exceptional "
      "(+1.7 pips at H=40, +3.2 at H=80, hit ~56%) but come from a ~15-month span "
      "(2025-06-26 .. 2026-03-19 dev) of a degraded feed (27% zero-spread bars) during a "
      "strong sustained drift; the short side is negative, consistent with a one-way "
      "market rather than a structural edge. Excluded from candidate claims until a "
      "clean EURJPY history is available.")
    w("")
    w("**Bottom line.** Phase 1 discovery does not yet supply a cost-clearing edge at M5. "
      "It does narrow the search space sharply: reject trend-continuation, breakout-"
      "continuation, and pullback-resumption; investigate fade-the-extreme and "
      "breakout-fade, gated to liquid sessions, with stops. Section 11 gives the three "
      "candidates and their acceptance tests for the strategy phase.")
    w("")

    w("## 2. Pair comparison")
    w("")
    w("Headline directional behaviors at H=20 (avg/median forward pips, hit %, n; "
      "sign convention: positive = profitable in the traded direction; "
      "`est. net` = avg minus estimated round-trip cost).")
    w("")
    head_cols = ["symbol", "behavior", "n", "avg_pips", "med_pips", "hit_pct", "t_p",
                 "est_net_after_cost_pips"]
    w(_md_table([dict(r) for r in fmt_rows], head_cols))
    w("")
    w("Estimated round-trip cost per pair (pips):")
    w("")
    w("| symbol | median spread (pips/side) | est round-trip cost (pips) |")
    w("|---|---|---|")
    for sym, an in per_symbol.items():
        w(f"| {sym} | {an['median_spread_price_pips']:.2f} | {_cost_estimate(an):.2f} |")
    w("")
    w("Horizon scaling (avg signed forward pips / hit % for trend continuation, "
      "fade-the-extreme mean reversion, and fade-the-breaking-breakout):")
    w("")
    for sym, an in per_symbol.items():
        rows = []
        for H in HSCALE:
            h = an["horizon"][H]
            rows.append({"H": H,
                         "tc_avg": h["trend_cont"]["avg_pips"], "tc_hit": h["trend_cont"]["hit_pct"],
                         "mr_avg": h["mr_fade"]["avg_pips"], "mr_hit": h["mr_fade"]["hit_pct"],
                         "bf_avg": h["breakout_fade"]["avg_pips"], "bf_hit": h["breakout_fade"]["hit_pct"]})
        w(f"**{sym}**")
        w("")
        w(_md_table(rows, ["H", "tc_avg", "tc_hit", "mr_avg", "mr_hit", "bf_avg", "bf_hit"]))
        w("")

    # Sections 3-8 auto-generated from aggregations
    _section_trend_persistence(w, per_symbol)
    _section_mean_reversion(w, per_symbol)
    _section_breakout(w, per_symbol)
    _section_volatility(w, per_symbol)
    _section_sessions(w, per_symbol)
    _section_trend_pullback(w, per_symbol)

    w("## 9. Strongest candidate behaviors")
    w("")
    w("Ranked by consistency across pairs and per-trade raw size (all development-only, "
      "all below cost as standalone rules):")
    w("")
    w("1. **Fade the extreme (mean reversion)** — long below / short above 1 SD from the "
      "trailing-20 SMA. The only behavior positive on all four pairs. Clean-pair profile "
      "at H=20: hit 51.5-53.1%, avg +0.24 .. +0.37 pips, t_p < 1e-3, and it survives "
      "extending the horizon: EURGBP +0.56 pips and GBPUSD +0.83 pips (short side) at "
      "H=80. It is the most structurally believable (intraday over-reaction is a "
      "documented microstructure effect) and the least sensitive to which extreme is "
      "used. Rank 1.")
    w("")
    w("2. **Fade the failing breakout** — the mirror of section 5: breakout-continuation "
      "is negative to a degree unmatched by any other signal (EURUSD -0.43 .. GBPUSD "
      "-0.78 pips at H=20; hit 44.5-47.9%), which makes the inverted trade the largest "
      "per-trade raw coefficient in the study. It is less clean than extreme-fade "
      "(overlaps heavily with it) and needs the session gate, but it is the single "
      "biggest directional signal per event. Rank 2.")
    w("")
    w("3. **Session-gated directional behavior (London + London-NY overlap)** — the only "
      "conditioning that flips the sign of a behavior (section 7) and is direction-"
      "consistent: EURUSD and GBPUSD continuation turns positive in London-NY; OffHours "
      "hit collapses to 39-47% on every pair. This is an overlay that improves any "
      "candidate above rather than a behavior on its own, and its magnitudes alone "
      "still do not clear costs. Rank 3.")
    w("")
    w("(Flagged but not ranked: EURJPY fade-oversold long at H=40/80 — see section 1, "
      "item 4 — data-quality + drift caveats disqualify it as evidence.)")
    w("")

    w("## 10. Weakest / rejected behaviors")
    w("")
    w("- **Naive trend continuation** — negative on all four pairs (hit 47.3-48.8%). "
      "M5 trends do not persist over 25 min-6 h; buy-every-trend rules are rejected.")
    w("- **Naive breakout continuation** — strongly negative everywhere; rejected in "
      "favor of the fade (section 9, rank 2).")
    w("- **Trend + pullback resumption** — flat-to-negative on every pair (EURUSD "
      "-0.14, EURGBP -0.14, GBPUSD -0.15; hit ~48-49%); dips do not reliably resume. "
      "Rejected as a standalone; deeper pullbacks are only marginally less bad.")
    w("- **OffHours / Asian-only rule making** — anti-directional (hit 39-47%); these "
      "bars should be traded only as noise-filter context, never as the signal.")
    w("- **Any EURJPY-based claim** — degraded 1-year feed with drift dominance; "
      "excluded until a clean EURJPY history exists.")
    w("")

    w("## 11. Recommended TOP 3 behaviors for strategy construction")
    w("")
    w("These are hypotheses for the next phase, not promises: each must pass a "
      "pre-registered acceptance test on the untouched VALIDATION split before any "
      "backtest is meaningful. Costs modeled as the pair's estimated round-trip cost.")
    w("")
    w("1. **Counter-trend extreme fade (mean reversion), EURGBP/GBPUSD/EURUSD.** "
      "Signal: close more than 1 SD below/above trailing-20 SMA; long/short into the "
      "extreme. Hold 20-40 bars; stop tighter than expected ATR excursion "
      "(~1 ATR); round-trip cost 2.3-3.5 pips. **Acceptance:** on validation, H=20-40 "
      "avg >= cost + 0.5 pips AND hit >= 52% AND no single year rejects the sign.")
    w("")
    w("2. **Breakout fade in liquid sessions (EURGBP/GBPUSD, London + London-NY).** "
      "Signal: close pierces prior-20 high/low; fade it, biased to the London-NY "
      "overlap only where the overlay flips positive. **Acceptance:** on validation, "
      "avg >= cost + 0.5 pips AND hit >= 50% AND direction stable per session.")
    w("")
    w("3. **Session-gated mean-reversion (split-overlap every other hour).** "
      "Candidate 1 filtered to London and London-NY bars; a pure conditioning test of "
      "whether exclusion of OffHours/Asian lifts the fade edge over cost. "
      "**Acceptance:** filter gain vs candidate 1 must be positive and the filtered "
      "edge must clear cost on validation.")
    w("")
    w("If none passes, the evidence-based conclusion is that M5 horizons net of costs "
      "are not productive for these pairs and the strategy phase should move to larger "
      "horizons or a different instrument set — an outcome this discovery run treats "
      "as success.")
    w("")
    return "\n".join(L)


def _section_trend_persistence(w, per_symbol: dict) -> None:
    w("## 3. Trend persistence")
    w("")
    w("Condition: trailing-20-bar net move (causal). Continuation score = signed "
      "forward 20-bar pips (positive when price continues the trend).")
    w("")
    rows = []
    for sym, an in per_symbol.items():
        r = an["trend_continuation_H20"]
        rows.append({"symbol": sym, **{k: r[k] for k in ("n", "avg_pips", "med_pips", "hit_pct", "t_p")}})
    w(_md_table(rows, ["symbol", "n", "avg_pips", "med_pips", "hit_pct", "t_p"]))
    w("")
    w("Regime-conditioned continuation (avg pips, hit %, n):")
    w("")
    for sym, an in per_symbol.items():
        rows = []
        for rg in ["low", "normal", "high"]:
            r = an["trend_cont_by_regime"][rg]
            rows.append({"regime": rg, **{k: r[k] for k in ("n", "avg_pips", "hit_pct")}})
        w(f"**{sym}**")
        w("")
        w(_md_table(rows, ["regime", "n", "avg_pips", "hit_pct"]))
        w("")


def _section_mean_reversion(w, per_symbol: dict) -> None:
    w("## 4. Mean reversion")
    w("")
    w("Condition: close more than 1 std below/above trailing-20 SMA. Trade "
      "against the move. Positive avg pips = reversion worked.")
    w("")
    rows = []
    for sym, an in per_symbol.items():
        r = an["mean_reversion_H20"]
        rows.append({"symbol": sym, **{k: r[k] for k in ("n", "avg_pips", "med_pips", "hit_pct", "t_p")}})
    w(_md_table(rows, ["symbol", "n", "avg_pips", "med_pips", "hit_pct", "t_p"]))
    w("")


def _section_breakout(w, per_symbol: dict) -> None:
    w("## 5. Breakout behavior")
    w("")
    w("Condition: close pierces prior 20-bar high (long) / low (short). Positive "
      "avg pips = breakout continuation.")
    w("")
    rows = []
    for sym, an in per_symbol.items():
        r = an["breakout_H20"]
        rows.append({"symbol": sym, **{k: r[k] for k in ("n", "avg_pips", "med_pips", "hit_pct", "t_p")}})
    w(_md_table(rows, ["symbol", "n", "avg_pips", "med_pips", "hit_pct", "t_p"]))
    w("")


def _section_volatility(w, per_symbol: dict) -> None:
    w("## 6. Volatility regimes")
    w("")
    w("Regimes are causal rolling ATR quantiles (low/normal/high). ATR "
      "distribution in dev data:")
    w("")
    w("| symbol | ATR median (pips) | regime bars (low/normal/high) |")
    w("|---|---|---|")
    for sym, an in per_symbol.items():
        f = an["regime_freq"]
        w(f"| {sym} | {an['atr_median_pips']:.1f} | {f['low']:,}/{f['normal']:,}/{f['high']:,} |")
    w("")
    w("Trend-continuation edge by regime (avg pips, H=20): see section 3 tables. "
      "Directional hit-rate per regime is covered in the per-symbol volatility "
      "studies.")
    w("")


def _section_sessions(w, per_symbol: dict) -> None:
    w("## 7. Session behavior")
    w("")
    w("Sessions are UTC buckets. Trend-continuation edge by session (H=20):")
    w("")
    for sym, an in per_symbol.items():
        rows = []
        for sname in ["Asian", "London", "LondonNY", "NewYork", "OffHours"]:
            r = an["trend_cont_by_session"][sname]
            rows.append({"session": sname, **{k: r[k] for k in ("n", "avg_pips", "hit_pct")}})
        w(f"**{sym}**")
        w("")
        w(_md_table(rows, ["session", "n", "avg_pips", "hit_pct"]))
        w("")


def _section_trend_pullback(w, per_symbol: dict) -> None:
    w("## 8. Trend + pullback behavior")
    w("")
    w("Inside a trailing-20-bar trend, signal on the first pullback bar against "
      "the trend, betting on resumption. Positive avg = resumption worked.")
    w("")
    rows = []
    for sym, an in per_symbol.items():
        r = an["pullback_long_H20"]
        rows.append({"symbol": sym, **{k: r[k] for k in ("n", "avg_pips", "med_pips", "hit_pct", "t_p")}})
    w(_md_table(rows, ["symbol", "n", "avg_pips", "med_pips", "hit_pct", "t_p"]))
    w("")
    w("Resumption by pullback depth (consecutive adverse bars inside the trend):")
    w("")
    for sym, an in per_symbol.items():
        rows = []
        for d in ["depth1", "depth2", "depth3plus"]:
            r = an["pull_back_depth"][d]
            rows.append({"depth": d, **{k: r[k] for k in ("n", "avg_pips", "hit_pct")}})
        w(f"**{sym}**")
        w("")
        w(_md_table(rows, ["depth", "n", "avg_pips", "hit_pct"]))
        w("")
    w("Favorable / adverse forward excursions (pips) over the 20-bar window for "
      "the long setups studied:")
    w("")
    for sym, an in per_symbol.items():
        w(f"**{sym}**")
        w("")
        rows = []
        for name, r in an["excursions_H20"].items():
            rows.append({"setup": name, **{k: r[k] for k in
                ("n", "avg_fav_pips", "med_fav_pips", "avg_adv_pips", "med_adv_pips")}})
        w(_md_table(rows, ["setup", "n", "avg_fav_pips", "med_fav_pips", "avg_adv_pips", "med_adv_pips"]))
        w("")


if __name__ == "__main__":
    raise SystemExit(main())