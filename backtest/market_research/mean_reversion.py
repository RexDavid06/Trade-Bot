"""Phase 3B - Mean reversion: does an over-extended move revert?

Condition on the distance of the current close from a trailing simple moving
average (z-score / number of ATRs from the mean) over several lookbacks, then
measure forward pips and hit rate. Fade (bet against) extreme deviations: a
positive forward return after an extreme BELOW-mean bar is reversion toward
the mean; hitting a short/long test separately.

Also reports a symmetric view: extreme UP deviation -> expected short profit.

    python -m backtest.market_research.mean_reversion
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import (
    HORIZONS,
    PIP,
    to_markdown_table,
)
from ._loader import load_m5, write_json, write_study

LOOKBACKS = [10, 20, 40, 80, 160]
# Distance buckets expressed in ATR multiples of the z-score from the SMA.
BUCKET_EDGES = [-np.inf, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, np.inf]
BUCKET_LABELS = ["<-2s", "-2..-1s", "-1..-0.5s", "-0.5..0.5s",
                 "0.5..1s", "1..2s", ">2s"]


def _bucket_dist(dist: np.ndarray) -> np.ndarray:
    """Bucket a standardized distance into integer bucket index from edges."""
    out = np.full(len(dist), -1, dtype=int)
    for i in range(len(BUCKET_EDGES) - 1):
        lo, hi = BUCKET_EDGES[i], BUCKET_EDGES[i + 1]
        if i == 0:
            m = dist <= hi
        elif i == len(BUCKET_EDGES) - 2:
            m = (dist > lo) & (dist <= hi)
        else:
            m = (dist > lo) & (dist <= hi)
        out[m] = i
    return out


def _std_recent(values: np.ndarray, lb: int) -> np.ndarray:
    """Rolling population std of the trailing `lb` values (past only)."""
    s = pd.Series(values)
    return s.rolling(lb, min_periods=lb).std(ddof=0).to_numpy()


def run() -> dict:
    df = load_m5()
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    from .common import forward_return_matrix
    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Distance = `(close[i] - SMA_lb[i-1]) / std_lb[i-1]` (z-score of the "
      "current close vs the trailing mean & dispersion, measured causally on "
      "past bars only). A strongly NEGATIVE bucket (e.g. `<-2s`) means price "
      "is unusually far below its recent mean; reversion predicts a forward "
      "RISE. A strongly POSITIVE bucket predicts a forward FALL. Long/short "
      "are analysed separately so the sign conventions are unambiguous.")
    w("")

    for LB in LOOKBACKS:
        w(f"### Lookback/SMA = {LB}")
        w("")
        sma = pd.Series(close).rolling(LB).mean().to_numpy()
        std = _std_recent(close, LB)
        dist = np.full(n, np.nan)
        ok = ~np.isnan(sma) & (std > 0)
        dist[ok] = (close[ok] - sma[ok]) / std[ok]
        bucket = _bucket_dist(dist)
        valid = bucket >= 0

        w("**Forward pips (long entry, i.e. fade below-mean / buy) by distance bucket:**")
        w("")
        from .common import build_conditioned_table
        rows = []
        for H in HORIZONS:
            sub = fwd_pips[H][valid]
            bev = bucket[valid]
            mask = np.isfinite(sub)
            tbl = build_conditioned_table(sub[mask], np.sign(sub[mask]), bev[mask],
                                          BUCKET_LABELS)
            for idx, r in tbl.iterrows():
                rows.append({"H": H, "dist": idx, "n": r["n"],
                             "avg_pips": r["avg_pips"], "med_pips": r["med_pips"],
                             "hit_pct": r["hit_pct"], "t_p": r["t_p"]})
        w(to_markdown_table(pd.DataFrame(rows).set_index(["H", "dist"])))
        w("")

        # Long/short punchline:
        # long book: go long at bar i, profit = close[i+H]-close[i]
        # short book: go short at bar i, profit = -(close[i+H]-close[i])
        w("**Reversion long/short summary (fade the extreme):**")
        w("")
        w("| H | fade_below (long) avg | fade_below hit% | fade_above (short) avg | fade_above hit% | n |")
        w("|---|---|---|---|---|---|")
        below = valid & (dist <= -1.0)
        above = valid & (dist >= 1.0)
        for H in HORIZONS:
            fh = fwd_pips[H]
            long_above = -fh[above]
            long_below = fh[below]
            rb = long_below[np.isfinite(long_below)]
            ra = long_above[np.isfinite(long_above)]
            w(f"| {H} | {rb.mean():.2f} | {(rb > 0).mean() * 100:.1f} | "
              f"{ra.mean():.2f} | {(ra > 0).mean() * 100:.1f} | "
              f"{int(np.isfinite(long_below).sum())}/{int(np.isfinite(long_above).sum())} |")
        w("")

        results[f"LB{LB}"] = {
            "dist_std": float(np.nanstd(dist)),
            "extreme_below_lt_neg1_pct": float((ok & (dist <= -1.0)).mean() * 100) if ok.any() else np.nan,
            "extreme_above_gt_1_pct": float((ok & (dist >= 1.0)).mean() * 100) if ok.any() else np.nan,
        }

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mean reversion behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "mean_reversion.md", "MEAN-REVERSION STUDY", df,
                result["md"], {"lookbacks/SMA": str(LOOKBACKS),
                               "forward_horizons": str(HORIZONS),
                               "buckets": str(BUCKET_LABELS)})
    write_json(result["results"], out_dir / "mean_reversion_summary.json")
    print(f"Mean-reversion study written to {out_dir / 'mean_reversion.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
