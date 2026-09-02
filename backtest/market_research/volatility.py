"""Phase 3D - Volatility: does current volatility predict future returns, and
into which regime do we get better forward expectancy?

We use ATR (average true range) both as a regime classifier (low/normal/high)
and as a normalized volatility forecast measure. Two questions:

  1. Forward return conditioned on volatility regime (is return/edge regime
     dependent?).
  2. Does realised absolute move correlate with forward direction? (i.e. does
     vol expansion forecast a directional move or just noise?)

    python -m backtest.market_research.volatility
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import (
    HORIZONS,
    PIP,
    atr_regime,
    build_conditioned_table,
    forward_return_matrix,
    to_markdown_table,
)
from ._loader import load_m5, write_json, write_study

ATR_PERIOD = 14
REGIME_ATR_LOOKBACK = 50


def _true_range(high, low, prev_close):
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close),
                                           np.abs(low - prev_close)))
    return tr


def run() -> dict:
    df = load_m5()
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    close = df["close"].to_numpy(dtype=float)
    n = len(close)

    prev_close = np.concatenate([[np.nan], close[:-1]])
    tr = _true_range(high, low, prev_close)
    atr = pd.Series(tr).ewm(alpha=1 / ATR_PERIOD, adjust=False, min_periods=ATR_PERIOD).mean().to_numpy()
    regime = atr_regime(atr, REGIME_ATR_LOOKBACK)

    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}
    fwd_abs_pips = {H: np.abs(fh) / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Regime is assigned causally from a rolling quantile of ATR "
      "(low/normal/high). We report forward pips and directional hit rate by "
      "regime. Low |avg| / hit ~ 50% in a regime means it is not "
      "directional; a regime where |forward| is large and hit rate is not "
      "~50% is where an edge could live. Also report absolute forward move "
      "(|pips|) per regime to see how much room there is to capture.")
    w("")

    for H in HORIZONS:
        w(f"### Horizon = {H}")
        w("")
        w("**Signed forward pips by volatility regime:**")
        w("")
        tbl = build_conditioned_table(fwd_pips[H], np.sign(fwd_pips[H]),
                                      regime)  # labels = actual regime values
        w(to_markdown_table(tbl))
        w("")
        w("**Absolute forward |pips| by regime (how far price actually moves):**")
        w("")
        abs_rows = []
        for rg in ["low", "normal", "high"]:
            m = regime == rg
            v = fwd_abs_pips[H][m]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            abs_rows.append({"regime": rg, "n": int(len(v)),
                             "avg_abs_pips": float(v.mean()),
                             "med_abs_pips": float(np.median(v))})
        w(to_markdown_table(pd.DataFrame(abs_rows).set_index("regime")))
        w("")

    # regime frequency
    from collections import Counter
    cnt = Counter(regime)
    w("## Regime frequency")
    w("")
    w("| regime | bars | % |")
    w("|---|---|---|")
    total = sum(cnt.values())
    for rg in ["low", "normal", "high"]:
        w(f"| {rg} | {cnt[rg]} | {cnt[rg] / total * 100:.1f} |")
    w("")
    results["regime_freq"] = {k: int(v) for k, v in cnt.items()}
    results["atr_median_pips"] = float(np.nanmedian(atr) / PIP)
    results["atr_p10_pips"] = float(np.nanpercentile(atr, 10) / PIP)
    results["atr_p90_pips"] = float(np.nanpercentile(atr, 90) / PIP)

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Volatility behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "volatility.md", "VOLATILITY STUDY", df, result["md"],
                {"atr_period": ATR_PERIOD, "regime_atr_lookback": REGIME_ATR_LOOKBACK,
                 "forward_horizons": str(HORIZONS)})
    write_json(result["results"], out_dir / "volatility_summary.json")
    print(f"Volatility study written to {out_dir / 'volatility.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
