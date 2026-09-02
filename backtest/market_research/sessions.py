"""Phase 3E - Sessions: does forward return/hit-rate or volatility differ by
UTC session (Asian / London / London-NY / New York / OffHours)?

We use the simple UTC session model in common.py. We report forward pips,
directional hit rate and ATR-like volatility split by session, at several
horizons. A session where hit-rate is consistently != 50% could host an edge.

    python -m backtest.market_research.sessions
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import (
    HORIZONS,
    PIP,
    add_session,
    forward_return_matrix,
    to_markdown_table,
)
from ._loader import load_m5, write_json, write_study

SESSIONS = ["Asian", "London", "LondonNY", "NewYork", "OffHours"]


def run() -> dict:
    df = load_m5()
    close = df["close"].to_numpy(dtype=float)
    hour = pd.to_datetime(df["time"]).dt.hour.to_numpy()
    daynames = pd.to_datetime(df["time"]).dt.dayofweek  # Mon=0
    df_s = add_session(df)

    fwd = forward_return_matrix(close, HORIZONS)
    fwd_pips = {H: fh / PIP for H, fh in fwd.items()}

    results = {}
    body_lines = []
    w = body_lines.append

    w("## Interpretation")
    w("")
    w("Session is assigned from the bar's UTC hour. We report forward pips, "
      "hit rate and an average-absolute-move proxy per session. A session with "
      "hit rate consistently above/below 50% and non-trivial sample size is "
      "where a session-specific edge may exist; a session with large |move| "
      "but hit ~50% is high-noise/high-opportunity but not directional.")
    w("")

    for H in HORIZONS:
        w(f"### Horizon = {H}")
        w("")
        w("**Forward pips by session:**")
        w("")
        rows = []
        for s in SESSIONS:
            m = df_s["session"] == s
            v = fwd_pips[H][m]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            hit = (v > 0).mean() * 100
            avg_abs = np.abs(v).mean()
            rows.append({"session": s, "n": int(len(v)),
                         "avg_pips": float(v.mean()),
                         "med_pips": float(np.median(v)),
                         "hit_pct": float(hit),
                         "avg_abs_pips": float(avg_abs)})
        w(to_markdown_table(pd.DataFrame(rows).set_index("session")))
        w("")

    w("## Session frequency")
    w("")
    w("| session | bars | % |")
    w("|---|---|---|")
    n = len(df_s)
    for s in SESSIONS:
        k = int((df_s["session"] == s).sum())
        w(f"| {s} | {k} | {k / n * 100:.1f} |")
    w("")
    results["session_freq"] = {s: int((df_s["session"] == s).sum()) for s in SESSIONS}

    return {"md": "\n".join(body_lines), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Session behavior")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_dir = args.out if args.out is not None else Path("outputs") / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_m5()
    result = run()
    write_study(out_dir / "sessions.md", "SESSION STUDY", df, result["md"],
                {"sessions_utc": str(SESSIONS), "forward_horizons": str(HORIZONS)})
    write_json(result["results"], out_dir / "sessions_summary.json")
    print(f"Session study written to {out_dir / 'sessions.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
