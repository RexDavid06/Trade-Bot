"""Phase 3G - Range / choppiness: does price tend to stay inside a range
(mean reversion) or trend after low intraday range (compression)?

We measure the recent range (high-low span fraction, or the ratio of recent
range to recent ATR) as a "range-tightness" / compression signal, then measure
forward pips + hit rate by compression bucket. Compression -> expansion is a
classic volatility-compression idea (coiling). We separate directionless
(|move|) from directional outlook.

    python -m backtest.market_research.range_behavior
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import (
    HORIZONS,
    PIP,
    build_conditioned_table,
    forward_return_matrix,
    to_markdown_table,
)
from ._loader import load_m5, write_json, write_study

RANGE_WINDOWS = [20, 40, 80]
# range index bucketed by quantile of (range/ATR) ratio -> compressed vs wide

ATR_PERIOD = 14


def _true_range(high, low, prev_close):
    return np.maximum(high - low, np.maximum(np.abs(high - prev_close),
                                             np.abs(low - prev_close)))


def _bucketize(v: np.ndarray, nb: int) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    out = np.full(len(v), -1, dtype=int)
    finite = np.isfinite(v)
    vals = v[finite]
    order = np.argsort(vals, kind="stable")
    nv = len(vals)
    edges = np.linspace(0, nv, nb + 1).astype(int)
    bucket = np.empty(nv, dtype=int)
    for b in range(nb):
        bucket[order[edges[b]:edges[b + 1]]] = b
    out[finite] = bucket
    return out


def run() -> dict:
    df = load_m5()
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    prev_close = np.concatenate([[np.nan], close[:-1]])
    atr = pd.Series(_true_range(high, low, prev_close)) \
        .ewm(alpha=1 / ATR_PERIOD, adjust=False, min_periods=ATR_PERIOD).mean().to_numpy()

    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}
    fwd_abs = {H: np.abs(fh) / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Range-index = `(rolling high-high - rolling low-low) / local ATR`, a "
      "measure of how wide recent price is relative to typical bar range. Low "
      "range-index = compression/coiling. Buckets are quintiles (Q1 = most "
      "compressed, Q5 = widest). We show forward |pips| (expansion) and "
      "directional hit rate. Compression -> big expansion but hit ~50% means "
      "a volatility trade, not a directional edge.")
    w("")

    for RW in RANGE_WINDOWS:
        w(f"### Range window = {RW}")
        w("")
        rng_hi = pd.Series(high).rolling(RW).max().to_numpy()
        rng_lo = pd.Series(low).rolling(RW).min().to_numpy()
        span = rng_hi - rng_lo
        ri = span / atr
        bucket = _bucketize(ri, 5)
        valid = bucket >= 0

        w("**Forward |pips| (expansion potential) by range-index quintile:**")
        w("")
        rows = []
        for H in HORIZONS:
            sub = fwd_abs[H][valid]
            bev = bucket[valid]
            mask = np.isfinite(sub)
            tbl = build_conditioned_table(sub[mask], np.sign(sub[mask] + 1e-12), bev[mask],
                                          [f"Q{i + 1}" for i in range(5)])
            for idx, r in tbl.iterrows():
                rows.append({"H": H, "range_q": idx, "n": r["n"],
                             "avg_abs_pips": r["avg_pips"],
                             "med_abs_pips": r["med_pips"]})
        w(to_markdown_table(pd.DataFrame(rows).set_index(["H", "range_q"])))
        w("")

        w("**Directional hit rate by range-index quintile (signed fwd pips):**")
        w("")
        rows = []
        for H in HORIZONS:
            sub = fwd_pips[H][valid]
            bev = bucket[valid]
            mask = np.isfinite(sub)
            tbl = build_conditioned_table(sub[mask], np.sign(sub[mask]), bev[mask],
                                          [f"Q{i + 1}" for i in range(5)])
            for idx, r in tbl.iterrows():
                rows.append({"H": H, "range_q": idx, "hit_pct": r["hit_pct"],
                             "avg_pips": r["avg_pips"]})
        w(to_markdown_table(pd.DataFrame(rows).set_index(["H", "range_q"])))
        w("")

        med_rc = float(np.nanmedian(ri[valid]))
        results[f"RW{RW}"] = {"median_range_index": med_rc}

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Range behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "range_behavior.md", "RANGE / CHOPPINESS STUDY", df,
                result["md"], {"range_windows": str(RANGE_WINDOWS),
                               "forward_horizons": str(HORIZONS)})
    write_json(result["results"], out_dir / "range_behavior_summary.json")
    print(f"Range behavior study written to {out_dir / 'range_behavior.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
