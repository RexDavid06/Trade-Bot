"""Phase 3F - Trend persistence: do trends (sustained directional streaks)
persist or reverse?

We define a trend by the sign of the last `TS` candles' net change AND by the
fraction of bars closing in that direction (strength). We measure forward
return after: a rising trend, a falling trend, and by trend STRENGTH buckets.
Also test the persistence of consecutive same-direction bars (streak length).

    python -m backtest.market_research.trend_persistence
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import HORIZONS, PIP, forward_return_matrix, to_markdown_table
from ._loader import load_m5, write_json, write_study

TREND_WINDOWS = [10, 20, 40, 80]
STRENGTH_BUCKETS = 5


def _discrete_move(close, wd):
    """Return array in {-1,0,1} for net move over window wd (past only)."""
    out = np.full(len(close), np.nan)
    out[wd:] = np.sign(close[wd:] - close[:-wd])
    return out


def run() -> dict:
    df = load_m5()
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Trend = net move sign over the trailing `TW` candles (causal). "
      "`up` = close now above close TW ago; `down` likewise. We report forward "
      "pips + hit rate conditioned on the trend sign. Persistence predicts "
      "positive forward after `up`; reversal predicts negative.")
    w("")

    for TW in TREND_WINDOWS:
        w(f"### Trend window = {TW}")
        w("")
        trend = _discrete_move(close, TW)
        valid = ~np.isnan(trend)
        rows = []
        for H in HORIZONS:
            for tname in ["down", "up"]:
                code = -1 if tname == "down" else 1
                m = valid & (trend == code)
                v = fwd_pips[H][m]
                v = v[np.isfinite(v)]
                if len(v) == 0:
                    continue
                rows.append({"H": H, "trend": tname, "n": int(len(v)),
                             "avg_pips": float(v.mean()),
                             "med_pips": float(np.median(v)),
                             "hit_pct": float((v > 0).mean() * 100)})
        w(to_markdown_table(pd.DataFrame(rows).set_index(["H", "trend"])))
        w("")

        # Streak-length persistence
        w("**Persistence by consecutive same-direction streak length:**")
        w("")
        signs = np.sign(close[1:] - close[:-1])
        signs = np.concatenate([[0], signs])  # bar i: direction vs bar i-1
        streak = np.zeros(n, dtype=int)
        for i in range(1, n):
            streak[i] = (streak[i - 1] + 1) if signs[i] == signs[i - 1] and signs[i] != 0 else 1
        buckets = {f"streak{k}": (streak == k) for k in range(3, 9)}
        srows = []
        for H in HORIZONS:
            for name, m in buckets.items():
                v = fwd_pips[H][m]
                v = v[np.isfinite(v)]
                if len(v) == 0:
                    continue
                srows.append({"H": H, "streak": name, "n": int(len(v)),
                              "avg_pips": float(v.mean()),
                              "hit_pct": float((v > 0).mean() * 100)})
        w(to_markdown_table(pd.DataFrame(srows).set_index(["H", "streak"])))
        w("")

        results[f"TW{TW}"] = {
            "up_bars_pct": float((valid & (trend == 1)).mean() * 100) if valid.any() else np.nan,
            "down_bars_pct": float((valid & (trend == -1)).mean() * 100) if valid.any() else np.nan,
        }

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trend persistence")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "trend_persistence.md", "TREND PERSISTENCE STUDY", df,
                result["md"], {"trend_windows": str(TREND_WINDOWS),
                               "forward_horizons": str(HORIZONS)})
    write_json(result["results"], out_dir / "trend_persistence_summary.json")
    print(f"Trend persistence study written to {out_dir / 'trend_persistence.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
