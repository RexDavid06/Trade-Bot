"""Clean chronological splits with holdout protection for multi-symbol research."""

from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .data_split import split_by_fraction

SUPPORTED_SYMBOLS = ["EURUSD", "EURGBP", "EURJPY", "GBPUSD"]


@dataclass
class ResearchSplit:
    symbol: str
    method: str
    fractions: dict
    counts: dict
    first: str
    last: str
    date_range_days: float
    run_id: str
    dataset_rows: int
    holdout_start: str
    holdout_end: str


def _csv_path(symbol: str, data_dir: Path) -> Path:
    return data_dir / f"{symbol.lower()}_m5.csv"


def make_research_split(
    symbol: str,
    data_dir: Path,
    out_dir: Path,
    dev_frac: float = 0.6,
    val_frac: float = 0.2,
    holdout_frac: float = 0.2,
) -> ResearchSplit:
    csv_path = _csv_path(symbol, data_dir)
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    total = len(df)
    fracs = {"dev": dev_frac, "val": val_frac, "holdout": holdout_frac}

    masks = split_by_fraction(df["time"], dev_frac, val_frac, holdout_frac)

    ts = df["time"]
    first_str = str(ts.min())
    last_str = str(ts.max())

    holdout_mask = masks["holdout"]
    holdout_start = str(ts[holdout_mask].min())
    holdout_end = str(ts[holdout_mask].max())

    counts = {k: int(m.sum()) for k, m in masks.items()}

    meta = {
        "symbol": symbol,
        "method": "fraction",
        "fractions": fracs,
        "counts": counts,
        "first": first_str,
        "last": last_str,
        "date_range_days": float((ts.max() - ts.min()).total_seconds() / 86400.0),
        "run_id": uuid.uuid4().hex[:12],
        "dataset_rows": total,
        "holdout_start": holdout_start,
        "holdout_end": holdout_end,
        "holdout_protection": (
            "WARNING: The holdout set must NOT be used for feature selection, "
            "hyperparameter tuning, or any model development. It exists solely "
            "for final unbiased performance estimation."
        ),
    }

    split_out = out_dir / "splits" / symbol
    split_out.mkdir(parents=True, exist_ok=True)

    assignments = df[["time"]].copy()
    assignments["split"] = "?"
    for k, m in masks.items():
        assignments.loc[m, "split"] = k
    assignments_path = split_out / "assignments.csv"
    assignments.to_csv(assignments_path, index=False)

    with open(split_out / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    return ResearchSplit(
        symbol=symbol,
        method="fraction",
        fractions=fracs,
        counts=counts,
        first=first_str,
        last=last_str,
        date_range_days=meta["date_range_days"],
        run_id=meta["run_id"],
        dataset_rows=total,
        holdout_start=holdout_start,
        holdout_end=holdout_end,
    )


def validate_split_isolation(assignments_path: Path) -> dict:
    df = pd.read_csv(assignments_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    splits = df["split"].unique().tolist()
    expected = {"dev", "val", "holdout"}
    missing = expected - set(splits)
    unexpected = set(splits) - expected

    overlap_counts = {}
    for s in splits:
        count = (df["split"] == s).sum()
        overlap_counts[s] = count

    dev_end = df.loc[df["split"] == "dev", "time"].max() if "dev" in splits else pd.NaT
    val_start = df.loc[df["split"] == "val", "time"].min() if "val" in splits else pd.NaT
    val_end = df.loc[df["split"] == "val", "time"].max() if "val" in splits else pd.NaT
    hold_start = df.loc[df["split"] == "holdout", "time"].min() if "holdout" in splits else pd.NaT
    hold_end = df.loc[df["split"] == "holdout", "time"].max() if "holdout" in splits else pd.NaT

    chronological_ok = True
    violations = []
    if pd.notna(dev_end) and pd.notna(val_start) and dev_end > val_start:
        chronological_ok = False
        violations.append(f"dev ends {dev_end} > val starts {val_start}")
    if pd.notna(val_end) and pd.notna(hold_start) and val_end > hold_start:
        chronological_ok = False
        violations.append(f"val ends {val_end} > holdout starts {hold_start}")

    total_rows = len(df)
    overlap_detected = False
    for col in ["dev", "val", "holdout"]:
        if col in splits:
            mask = df["split"] == col
            other_mask = df["split"] != col
            if (mask & other_mask).any():
                overlap_detected = True
                violations.append(f"row overlap detected involving '{col}'")

    results = {
        "valid": bool(
            not missing
            and not unexpected
            and not overlap_detected
            and chronological_ok
            and len(violations) == 0
        ),
        "total_rows": total_rows,
        "splits_found": sorted(splits),
        "counts": overlap_counts,
        "chronological_order_ok": chronological_ok,
        "violations": violations,
        "missing_splits": sorted(missing) if missing else [],
        "unexpected_splits": sorted(unexpected) if unexpected else [],
        "boundaries": {
            "dev_max": str(dev_end) if pd.notna(dev_end) else None,
            "val_min": str(val_start) if pd.notna(val_start) else None,
            "val_max": str(val_end) if pd.notna(val_end) else None,
            "holdout_min": str(hold_start) if pd.notna(hold_start) else None,
            "holdout_max": str(hold_end) if pd.notna(hold_end) else None,
        },
    }
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Multi-symbol research splits with holdout protection")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory containing symbol CSVs")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for splits")
    parser.add_argument("--dev", type=float, default=0.6)
    parser.add_argument("--val", type=float, default=0.2)
    parser.add_argument("--holdout", type=float, default=0.2)
    args = parser.parse_args(argv)

    results: list[ResearchSplit] = []
    for sym in SUPPORTED_SYMBOLS:
        csv = _csv_path(sym, args.data_dir)
        if not csv.exists():
            print(f"  SKIP  {sym}: {csv} not found")
            continue
        rs = make_research_split(sym, args.data_dir, args.out_dir, args.dev, args.val, args.holdout)
        results.append(rs)
        print(f"  OK    {sym}: {rs.dataset_rows} rows, "
              f"dev={rs.counts['dev']} val={rs.counts['val']} holdout={rs.counts['holdout']}")

    print("\n--- Validation ---")
    for rs in results:
        assignments_path = args.out_dir / "splits" / rs.symbol / "assignments.csv"
        vr = validate_split_isolation(assignments_path)
        status = "PASS" if vr["valid"] else "FAIL"
        print(f"  {status}  {rs.symbol}: {vr['counts']}")
        if vr["violations"]:
            for v in vr["violations"]:
                print(f"        -> {v}")

    print(f"\n--- Summary Table ---")
    print(f"{'Symbol':<10} {'Rows':>8} {'Dev':>8} {'Val':>8} {'Hold':>8} {'Days':>8} {'RunID':<14}")
    print("-" * 70)
    for rs in results:
        print(f"{rs.symbol:<10} {rs.dataset_rows:>8} {rs.counts['dev']:>8} "
              f"{rs.counts['val']:>8} {rs.counts['holdout']:>8} "
              f"{rs.date_range_days:>8.1f} {rs.run_id:<14}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
