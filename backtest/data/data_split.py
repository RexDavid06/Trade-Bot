"""Phase 2 - Reproducible chronological data split (development / validation /
final holdout).

Time-series data is NEVER randomly shuffled. The split is strictly
chronological: the earliest portion becomes DEVELOPMENT, the middle portion
VALIDATION, and the latest portion FINAL HOLDOUT. Parameters discovered /
tuned on DEVELOPMENT may be evaluated on VALIDATION; FINAL HOLDOUT must remain
untouched until the very end.

The split is configured by either:
  * fractions  (dev_frac, val_frac, holdout_frac summing to ~1), or
  * explicit cutoff timestamps.

Design / reproducibility:
  * The split is a pure function of the time column (seeded by nothing - it is
    fully deterministic given the inputs), so it is reproducible on any machine.
  * It writes a JSON manifest recording the dataset, date range, cutoffs,
    fractions, candle counts and a run identifier so every research run can be
    traced.
  * It supports saving an 'assignments.csv' (time, split) once so downstream
    analyses can filter by split without recomputing boundaries.

    python -m backtest.data.data_split [--data PATH] [--out DIR]
                                       [--dev FRAC] [--val FRAC] [--holdout FRAC]
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

import pandas as pd

from ..config import PathConfig

DEFAULT_SPLITS = {"dev": 0.60, "val": 0.20, "holdout": 0.20}


def split_by_fraction(
    ts: pd.Series,
    dev_frac: float,
    val_frac: float,
    holdout_frac: float,
) -> dict:
    """Return {'dev','val','holdout'} boolean masks given time fractions.

    Fractions are applied to the COUNT of valid, sorted rows (chronological).
    Guarantees exclusive, exhaustive, ordered coverage.
    """
    total = float(len(ts))
    dev_end = int(round(total * dev_frac))
    val_end = int(round(total * (dev_frac + val_frac)))

    dev = pd.Series(False, index=ts.index)
    val = pd.Series(False, index=ts.index)
    hold = pd.Series(False, index=ts.index)

    pos = ts.reset_index(drop=True).index.to_numpy()
    dev_idx = pos[:dev_end]
    val_idx = pos[dev_end:val_end]
    hold_idx = pos[val_end:]
    dev.iloc[dev_idx] = True
    val.iloc[val_idx] = True
    hold.iloc[hold_idx] = True
    return {"dev": dev.to_numpy(), "val": val.to_numpy(), "holdout": hold.to_numpy()}


def split_by_timestamps(df: pd.DataFrame, cutoffs: dict) -> dict:
    """Return masks for a dict of {'name': cutoff_timestamp} boundaries.

    Each entry i defines a half-open interval [cutoff_i, cutoff_{i+1}). The
    keys are used as split names.
    """
    ts = pd.to_datetime(df["time"])
    names = list(cutoffs.keys())
    out = {}
    sorted_names = sorted(names)
    for k in names:
        out[k] = pd.Series(False, index=df.index)
    idx = df.index.to_numpy()
    for j, k in enumerate(sorted_names):
        lo = pd.to_datetime(cutoffs[k])
        hi = pd.to_datetime(cutoffs[sorted_names[j + 1]]) if j + 1 < len(sorted_names) else None
        m = ts >= lo
        if hi is not None:
            m &= ts < hi
        out[k].iloc[idx[m.to_numpy()]] = True
        out[k] = out[k].to_numpy()
    return out


def make_split(
    df: pd.DataFrame,
    method: str,
    dev_frac: float,
    val_frac: float,
    holdout_frac: float,
    cutoffs: dict | None = None,
) -> dict:
    """High-level: produce {'dev','val','holdout'} masks and a metadata dict.

    `method` in {'fraction','timestamp'}.
    """
    ts = pd.to_datetime(df["time"])
    ts_s = ts.sort_values()
    if method == "timestamp":
        masks = split_by_timestamps(df, cutoffs or {})
    else:
        masks = split_by_fraction(ts_s, dev_frac, val_frac, holdout_frac)

    meta = {
        "method": method,
        "fractions": {"dev": dev_frac, "val": val_frac, "holdout": holdout_frac},
        "cutoffs": cutoffs,
        "first": str(ts.min()),
        "last": str(ts.max()),
        "counts": {k: int(m.sum()) for k, m in masks.items()},
        "date_range_days": float((ts.max() - ts.min()).total_seconds() / 86400.0),
        "run_id": uuid.uuid4().hex[:12],
        "dataset_rows": int(len(df)),
    }
    return {"masks": masks, "meta": meta}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chronological dataset split")
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dev", type=float, default=DEFAULT_SPLITS["dev"])
    parser.add_argument("--val", type=float, default=DEFAULT_SPLITS["val"])
    parser.add_argument("--holdout", type=float, default=DEFAULT_SPLITS["holdout"])
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    out_dir = out_dir / "reports"

    if not data_path.exists():
        sys.stderr.write(f"Data file not found: {data_path}\n")
        return 1

    df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])

    s = args.dev + args.val + args.holdout
    if abs(s - 1.0) > 1e-6:
        # allow non-total fractions but warn
        print(f"Note: fractions sum to {s:.3f}, not 1.0 (uneven coverage).")

    result = make_split(df, "fraction", args.dev, args.val, args.holdout)
    masks = result["masks"]
    meta = result["meta"]

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = out_dir / "data_split.json"
    with open(manifest, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    assignments = df[["time"]].copy()
    assignments["split"] = "?"
    for k, m in masks.items():
        assignments.loc[m, "split"] = k
    assignments.to_csv(out_dir / "data_split_assignments.csv", index=False)

    print(f"Data split written to {out_dir}")
    print(f"  - {manifest}")
    print(f"  - data_split_assignments.csv")
    print(f"Dataset: {meta['first']} .. {meta['last']}  "
          f"({meta['date_range_days']:.1f} days, {meta['dataset_rows']} rows)")
    for k in ("dev", "val", "holdout"):
        print(f"  {k:8s}: {meta['counts'][k]} candles ({meta['counts'][k]/meta['dataset_rows']*100:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
