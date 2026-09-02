"""Phase 3/4 common research utilities.

Shared helpers for every market-behavior study (momentum, mean-reversion,
breakout, volatility, sessions, trend persistence, range/choppiness). Central
pieces:

  * forward_return_matrix - vectorized forward returns at multiple horizons.
  * window features - rolling/forward windows used across studies.
  * session_label - deterministic UTC session classification.
  * vol_regime - ATR-normalized volatility regime buckets.
  * stats: one-sample t-test (mean vs 0) and z-test (hit-rate vs 0.5), both
    implemented in numpy (no scipy dependency).
  * build_conditioned_table - standard report card: for each condition bucket,
    reports n, avg/median forward pips, directional hit rate, statistical
    significance, and (optionally) splits by direction and regime.

Reporting conventions (Phase 4): every table reports sample size, average /
median forward return, directional hit rate, distribution summary where
practical, breakdown by long/short direction, by volatility regime and by
session where applicable. Small samples (< SMALL_N) are auto-flagged and never
called an "edge" just because one subset is profitable.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Global research constants (pips normalisation for EURUSD).
PIP = 0.0001
HORIZONS = [1, 3, 5, 10, 20, 40, 80]

# Below this sample size we flag the bucket as unreliable.
SMALL_N = 30

# Minimum fraction (of the studied window) that must be "warm" before we trust
# a rolling feature; used to drop warm-up / partial windows.
MIN_WARM = 1.0


# ---------------------------------------------------------------------------
# Session classification (UTC)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Session:
    name: str
    start_hour: int
    end_hour: int


# Vanilla UTC definitions, deliberately simple and not hard-coded as "best".
SESSIONS_UTC = [
    Session("Asian", 0, 7),
    Session("London", 7, 12),
    Session("LondonNY", 12, 16),
    Session("NewYork", 16, 21),
    Session("OffHours", 21, 24),
]


def session_label(hour_utc: np.ndarray) -> np.ndarray:
    """Map hour-of-day (0-23, UTC) to a session name."""
    labels = np.empty(len(hour_utc), dtype=object)
    for s in SESSIONS_UTC:
        if s.start_hour < s.end_hour:
            m = (hour_utc >= s.start_hour) & (hour_utc < s.end_hour)
        else:
            m = (hour_utc >= s.start_hour) | (hour_utc < s.end_hour)
        labels[m] = s.name
    return labels


def add_session(df: pd.DataFrame, time_col: str = "time") -> pd.DataFrame:
    """Attach a 'session' column (UTC) to a copy of df."""
    out = df.copy()
    hour = pd.to_datetime(out[time_col]).dt.hour.to_numpy()
    out["session"] = session_label(hour).astype(str)
    return out


# ---------------------------------------------------------------------------
# Volatility regime
# ---------------------------------------------------------------------------

def atr_regime(atr: np.ndarray, atr_lookback: int = 50,
               quantile_lo: float = 0.33, quantile_hi: float = 0.67) -> np.ndarray:
    """Classify each bar into low/normal/high volatility regime.

    Uses a trailing rolling quantile of ATR so the labelling is causal (only
    past data).  Returns an object array of 'low'/'normal'/'high'.
    """
    n = len(atr)
    out = np.empty(n, dtype=object)
    out[:] = "normal"
    a = pd.Series(atr)
    rolling_lo = a.rolling(atr_lookback, min_periods=20).quantile(quantile_lo)
    rolling_hi = a.rolling(atr_lookback, min_periods=20).quantile(quantile_hi)
    lo = rolling_lo.to_numpy()
    hi = rolling_hi.to_numpy()
    for i in range(n):
        if np.isnan(lo[i]) or np.isnan(hi[i]) or hi[i] <= lo[i]:
            continue
        if atr[i] <= lo[i]:
            out[i] = "low"
        elif atr[i] >= hi[i]:
            out[i] = "high"
        else:
            out[i] = "normal"
    return out


# ---------------------------------------------------------------------------
# Vectorized forward-return matrix
# ---------------------------------------------------------------------------

def forward_return_matrix(close: np.ndarray, horizons: list[int] | tuple[int, ...]) -> dict[int, np.ndarray]:
    """Vectorized forward returns close[i] -> close[i+H] for each horizon.

    Returns {H: arr} where arr has NaN for bars whose forward window exceeds
    the series (those bars are simply invalid at that horizon).
    """
    n = len(close)
    out = {}
    for H in horizons:
        arr = np.full(n, np.nan)
        fwd = close[H:] - close[:-H] if H < n else np.array([])
        if len(fwd):
            arr[: len(fwd)] = fwd
        out[H] = arr
    return out


def test_mean_nonzero(x: np.ndarray) -> dict:
    """One-sample t-test of mean(x) != 0 (numpy, no scipy)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return {"n": n, "t": np.nan, "p": np.nan, "mean": np.nan, "se": np.nan}
    mean = float(x.mean())
    var = float(x.var(ddof=1))
    if var <= 0:
        se = 0.0
    else:
        se = float(np.sqrt(var / n))
    t = mean / se if se > 0 else 0.0
    # two-sided p from Student-t with n-1 df using the regularized incomplete
    # beta function (implemented in numpy-free way via scipy-like approx).
    p = _t_pvalue(t, n - 1)
    return {"n": n, "t": t, "p": p, "mean": mean, "se": se}


def _normal_tail(z: float) -> float:
    """Upper tail P(Z > z) of the standard normal, using math.erfc (robust)."""
    import math
    if z <= 0:
        return 0.5 * math.erfc(-z / math.sqrt(2.0))
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _t_pvalue(t: float, df: float) -> float:
    # Two-sided Student-t p-value, numpy-free and robust.
    df = float(df)
    if df < 1:
        return 1.0
    if df > 200:
        return 2.0 * _normal_tail(abs(t))
    import math
    C = math.gamma((df + 1.0) / 2.0) / (math.sqrt(df * math.pi) * math.gamma(df / 2.0))
    a = abs(float(t))
    upper = a + 30.0 * math.sqrt(max(df, 1.0))
    xs = np.linspace(a, upper, 40000)
    dens = C * (1.0 + (xs * xs) / df) ** (-(df + 1.0) / 2.0)
    tail = float(np.trapezoid(dens, xs))
    return min(2.0 * tail, 1.0)


def test_hitrate(p_hat: float, n: int) -> dict:
    """z-test that observed hit-rate != 0.5 (two-sided), numpy-only."""
    if n == 0:
        return {"n": 0, "z": np.nan, "p": np.nan, "p_hat": np.nan}
    se = np.sqrt(0.25 / n)  # var of a proportion under p=0.5
    z = (p_hat - 0.5) / se if se > 0 else 0.0
    p = 2.0 * _normal_tail(abs(z))
    return {"n": n, "z": z, "p": p, "p_hat": p_hat}


# ---------------------------------------------------------------------------
# Standard conditioned summary
# ---------------------------------------------------------------------------

def _summarize(move: np.ndarray, hit: np.ndarray, label: str) -> dict:
    """Build a one-row condition summary (pips)."""
    mv = move[np.isfinite(move)]
    n = len(mv)
    if n == 0:
        return {"group": label, "n": 0, "avg_pips": np.nan,
                "med_pips": np.nan, "hit_pct": np.nan, "t": np.nan,
                "t_p": np.nan, "z": np.nan, "p": np.nan, "small": True}
    avg = float(mv.mean())
    med = float(np.median(mv))
    h = hit[np.isfinite(move)]
    hitpct = float((h > 0).mean() * 100.0) if len(h) else np.nan
    ttest = test_mean_nonzero(mv)
    htest = test_hitrate(hitpct / 100.0, len(h)) if len(h) else {"p": np.nan, "z": np.nan}
    return {
        "group": label,
        "n": n,
        "avg_pips": avg,
        "med_pips": med,
        "hit_pct": hitpct,
        "t": ttest["t"],
        "t_p": ttest["p"],
        "z": htest["z"],
        "z_p": htest["p"],
        "small": n < SMALL_N,
    }


def build_conditioned_table(
    move: np.ndarray,
    hit: np.ndarray,
    condition_values: np.ndarray,
    condition_labels: list[str] | None = None,
) -> pd.DataFrame:
    """Summarize forward pips grouped by a categorical condition array.

    If `condition_labels` is given it should list labels aligned in the same
    order as the sorted unique condition_values (or exactly match each unique
    value). Otherwise unique values are used as labels directly.
    """
    cv = np.asarray(condition_values)
    unique = np.unique(cv).tolist()
    # map each unique value to a display label
    if condition_labels is not None:
        # If labels were passed, pair them with the sorted unique values if the
        # counts line up; otherwise assume they are the unique values already.
        if len(condition_labels) == len(unique):
            label_for = {u: str(l) for u, l in zip(unique, condition_labels)}
        else:
            label_for = {u: str(u) for u in unique}
    else:
        label_for = {u: str(u) for u in unique}

    rows = []
    for u in unique:
        if isinstance(u, float) and np.isnan(u):
            m = np.isnan(cv.astype(float)) if cv.dtype.kind == "f" else np.zeros(len(cv), dtype=bool)
        else:
            m = (cv == u)
        if int(m.sum()) == 0:
            continue
        rows.append(_summarize(move[m], hit[m], label_for[u]))
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame()
    return df.set_index("group")


def long_short_split(move_up: np.ndarray, move_down: np.ndarray) -> pd.DataFrame:
    """Combine a direction-agnostic study into long-only / short-only views.

    move_up[i] = expected signed forward return if we went LONG at bar i;
    move_down[i] = ... if we went SHORT at bar i (positive = profit).
    hit arrays are the same sign convention (positive => won).
    """
    rows = [
        _summarize(move_up, move_up, "long"),
        _summarize(move_down, move_down, "short"),
    ]
    return pd.DataFrame(rows).set_index("group")


def fmt_p(p: float) -> str:
    if p != p:
        return "-"
    return f"{p:.3f}"


def fmt_percent(x: float) -> str:
    if x != x:
        return "-"
    return f"{x:.1f}"


def to_markdown_table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_no data_"
    cols = list(df.columns)
    # Render index labels as a leading column (works for single or MultiIndex).
    index_levels = list(df.index.names) if isinstance(df.index, pd.MultiIndex) else [df.index.name]
    label_names = [("value" if n is None else str(n)) for n in index_levels]
    header = label_names + cols
    lines = ["| " + " | ".join(header) + " |",
             "|" + "---|" * len(header)]
    for idx, row in df.iterrows():
        if isinstance(idx, tuple):
            vals = [str(x) for x in idx]
        else:
            vals = [str(idx)]
        for c in cols:
            v = row[c]
            if isinstance(v, float) and v != v:
                vals.append("-")
            elif c in ("avg_pips", "med_pips"):
                vals.append(f"{v:.2f}" if v == v else "-")
            elif c in ("hit_pct",):
                vals.append(fmt_percent(v))
            elif c in ("t_p", "z_p"):
                vals.append(fmt_p(v))
            elif c == "t":
                vals.append(f"{v:.2f}" if v == v else "-")
            elif c == "z":
                vals.append(f"{v:.2f}" if v == v else "-")
            elif c == "n":
                vals.append(str(int(v)))
            elif isinstance(v, float):
                vals.append(f"{v:.2f}" if v == v else "-")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)
