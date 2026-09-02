"""Convenience runner: executes every market-research study and prints a
summary.  Flags each study's output path and any compute-time.

    python -m backtest.market_research.run_all
"""

from __future__ import annotations

import time

from ._loader import load_m5
from . import momentum, mean_reversion, breakout, volatility, sessions, trend_persistence, range_behavior  # noqa

MODULES = [
    momentum,
    mean_reversion,
    breakout,
    volatility,
    sessions,
    trend_persistence,
    range_behavior,
]


def main() -> int:
    df = load_m5()
    print(f"Dataset: {df['time'].min()} .. {df['time'].max()}  ({len(df):,} bars)\n")
    for mod in MODULES:
        t0 = time.time()
        name = mod.__name__.split(".")[-1]
        rc = mod.main([])
        print(f"  {name:18s}  {rc}  ({time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
