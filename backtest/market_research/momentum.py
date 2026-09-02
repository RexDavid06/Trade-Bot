"""Phase 3A - Momentum: does recent directional movement predict continuation
or reversal?

For every bar, condition on the signed return over the trailing
`LOOKBACK`-candle window, then measure the forward return over horizons
H in {1,3,5,10,20,40,80}.  We report forward pips and directional hit rate for
each recent-move bucket, plus statistical significance.  This is a pure
price-based study (no EMA/RSI), independent of any strategy.

We look at both:
  * recent-move magnitude/quartile buckets (does strong up/down predict cont.)
  * a signed continuation coefficient (average forward move conditioned on the
    sign of the recent move).

    python -m backtest.market_research.momentum
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

LOOKBACKS = [3, 5, 10, 20, 40, 80]
MOMENTUM_BUCKETS = 5  # quintile buckets


def _bucketize(v: np.ndarray, nb: int) -> np.ndarray:
    """Bin a finite continuous array into nb equal-count buckets (rank-based).

    Wasted bars (first/last) are given NaN. Returns integer bucket 0..nb-1 for
    valid bars else -1.
    """
    v = np.asarray(v, dtype=float)
    n = len(v)
    out = np.full(n, -1, dtype=int)
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
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    fwd = forward_return_matrix(close, HORIZONS)  # close[i+H]-close[i]

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Recent move = `close[i] - close[i-LB]` (pips) over lookback `LB`. "
      "Forward move = `close[i+H]-close[i]` (pips). Buckets are quintiles of "
      "the recent move (1 = strongest DOWN, 5 = strongest UP). A positive "
      "average forward pip with hit rate > 50% after an UP bucket indicates "
      "**continuation**; a negative forward pip after an UP bucket indicates "
      "**reversal**. Rows are the forward horizon H.")
    w("")

    for LB in LOOKBACKS:
        recent = np.full(n, np.nan)
        if LB < n:
            recent = close[LB:] - close[:-LB]
            recent = np.concatenate([np.full(LB, np.nan), recent])

        bucket = _bucketize(recent, MOMENTUM_BUCKETS)
        valid_bucket = bucket >= 0  # exclude warm-up (NaN recent) bars
        # forward move in PIPs
        fwd_pips = {H: fwd_h / PIP for H, fwd_h in fwd.items()}

        w(f"### Lookback = {LB} candles")
        w("")
        w("Forward pips by recent-move quintile (bucket) at each horizon:")
        w("")
        rows = []
        for H in HORIZONS:
            tbl = build_conditioned_table(
                fwd_pips[H][valid_bucket], np.sign(fwd_pips[H][valid_bucket]),
                bucket[valid_bucket],
                [f"Q{i + 1}" for i in range(MOMENTUM_BUCKETS)],
            )
            for idx, r in tbl.iterrows():
                rows.append({
                    "H": H,
                    "recent_move_quintile": idx,
                    "n": r["n"],
                    "avg_pips": r["avg_pips"],
                    "med_pips": r["med_pips"],
                    "hit_pct": r["hit_pct"],
                    "t_p": r["t_p"],
                    "small": r["small"],
                })
        tbl_all = pd.DataFrame(rows)
        tbl_all = tbl_all.set_index(["H", "recent_move_quintile"])
        w(to_markdown_table(tbl_all))
        w("")

        # Continuation summary: average forward return conditioned on sign
        # of recent move (only include bars with valid recent move).
        valid = np.isfinite(recent)
        pos = valid & (recent > 0)
        neg = valid & (recent < 0)
        w(f"**Sign-conditioned continuation (LB={LB})**:")
        w("")
        w("| H | n_up | avg_fwd_after_up(pips) | hit_up% | n_dn | avg_fwd_after_dn(pips) | hit_dn% |")
        w("|---|---|---|---|---|---|---|")
        for H in HORIZONS:
            fh = fwd_pips[H]
            up_v = fh[pos]; dn_v = fh[neg]
            up_v = up_v[np.isfinite(up_v)]; dn_v = dn_v[np.isfinite(dn_v)]
            up_avg = up_v.mean() if len(up_v) else np.nan
            dn_avg = dn_v.mean() if len(dn_v) else np.nan
            up_hit = (up_v > 0).mean() * 100 if len(up_v) else np.nan
            dn_hit = (dn_v > 0).mean() * 100 if len(dn_v) else np.nan
            w(f"| {H} | {int(len(up_v))} | {up_avg:.2f} | {up_hit:.1f} | "
              f"{int(len(dn_v))} | {dn_avg:.2f} | {dn_hit:.1f} |")
        w("")

        results[f"LB{LB}"] = {
            "recent_move_pips_med": float(np.nanmedian(recent)),
            "positive_bars_pct": float((pos).mean() * 100) if valid.any() else np.nan,
        }

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Momentum market behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "momentum.md", "MOMENTUM STUDY", df, result["md"],
                {"recent_move_lookbacks": str(LOOKBACKS),
                 "forward_horizons": str(HORIZONS),
                 "buckets": MOMENTUM_BUCKETS})
    write_json(result["results"], out_dir / "momentum_summary.json")
    print(f"Momentum study written to {out_dir / 'momentum.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
