"""Phase 3C - Breakout: does price breaking a recent high/low continue?

Condition on where the current bar's close/high/low sits relative to the
trailing N-candle Donchian channel (rolling max high / min low). Classic
breakout idea: close above the prior N high -> continuation. We measure
forward pips + hit rate for bars that just broke out vs those that stayed
inside the recent range.

    python -m backtest.market_research.breakout
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import HORIZONS, PIP, forward_return_matrix, to_markdown_table
from ._loader import load_m5, write_json, write_study

CHANNELS = [20, 40, 80, 160]


def run() -> dict:
    df = load_m5()
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("A bar is a **high breakout** if its close pierces the highest high of "
      "the prior `CH` candles (excluding the current bar); **low breakout** if "
      "its close pierces the lowest low. Continuation predicts positive "
      "forward return after a high breakout; breakdown predicts negative "
      "return after a low breakout. Bucket = breakout state at entry.")
    w("")

    for CH in CHANNELS:
        w(f"### Channel = {CH}")
        w("")
        # causal channel: prior CH bars only
        prior_max_high = pd.Series(high).shift(1).rolling(CH).max().to_numpy()
        prior_min_low = pd.Series(low).shift(1).rolling(CH).min().to_numpy()
        state = np.full(n, -1, dtype=int)
        state[close > prior_max_high] = 2       # high breakout
        state[close < prior_min_low] = 0        # low breakout
        state[(close <= prior_max_high) & (close >= prior_min_low)] = 1  # inside
        valid = state >= 0

        rows = []
        for H in HORIZONS:
            sub = fwd_pips[H][valid]
            st = state[valid]
            mask = np.isfinite(sub)
            # only buckets that exist
            labels = [("low_breakout", 0), ("inside", 1), ("high_breakout", 2)]
            for name, code in labels:
                m = (st == code) & mask
                v = sub[m]
                if v.sum() == 0:
                    continue
                hit = (v > 0).mean() * 100
                rows.append({"H": H, "state": name, "n": int(m.sum()),
                             "avg_pips": float(v.mean()), "med_pips": float(np.median(v)),
                             "hit_pct": float(hit)})
        w(to_markdown_table(pd.DataFrame(rows).set_index(["H", "state"])))
        w("")

        # breakout frequency + continuation statistic
        nb = int((state == 2).sum())
        nbr = int((state == 0).sum())
        w(f"High breakouts: `{nb}` bars, low breakouts: `{nbr}` bars "
          f"(~{nb / n * 100:.2f}% / {nbr / n * 100:.2f}% of dataset).")
        w("")
        results[f"CH{CH}"] = {"high_breakout_bars": nb, "low_breakout_bars": nbr}

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Breakout behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "breakout.md", "BREAKOUT STUDY", df, result["md"],
                {"channels": str(CHANNELS), "forward_horizons": str(HORIZONS)})
    write_json(result["results"], out_dir / "breakout_summary.json")
    print(f"Breakout study written to {out_dir / 'breakout.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
