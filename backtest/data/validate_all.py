"""Run data validation across all supported symbols and produce a comparison summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .data_validation import validate_data, _flag_broker_specificity, _report_md
from ..instruments import get_instrument
from ..config import PathConfig

SYMBOLS = ["EURUSD", "EURGBP", "EURJPY", "GBPUSD"]

PRICE_RANGES: dict[str, tuple[float, float]] = {
    "EURUSD": (0.90, 1.30),
    "EURGBP": (0.70, 1.10),
    "EURJPY": (100.0, 220.0),
    "GBPUSD": (1.10, 1.60),
}

MAX_SPREAD_POINTS: dict[str, float] = {
    "EURUSD": 50.0,
    "EURGBP": 70.0,
    "EURJPY": 70.0,
    "GBPUSD": 60.0,
}


def validate_symbol(df: pd.DataFrame, symbol: str, data_dir: Path) -> dict:
    instrument = get_instrument(symbol)
    result = validate_data(df, symbol, "M5", 5)

    issues: list[str] = []

    sp_col = None
    for c in df.columns:
        if str(c).strip().lower() == "spread":
            sp_col = c
            break

    if sp_col is not None:
        sp = df[sp_col].to_numpy(dtype=float)
        nonzero = sp[sp > 0]
        if len(nonzero) > 0:
            mean_sp = float(nonzero.mean())
            max_sp = float(nonzero.max())
            max_allowed = MAX_SPREAD_POINTS.get(symbol, 100.0)
            if max_sp > max_allowed:
                issues.append(
                    f"Spread max {max_sp:.0f} pts exceeds threshold {max_allowed:.0f} pts for {symbol}"
                )
            if mean_sp <= 0:
                issues.append(f"Mean spread is non-positive ({mean_sp:.2f})")
    else:
        issues.append("No spread column found")

    close_col = None
    for c in df.columns:
        if str(c).strip().lower() == "close":
            close_col = c
            break

    if close_col is not None:
        prices = df[close_col].dropna().to_numpy(dtype=float)
        if len(prices) > 0:
            lo, hi = PRICE_RANGES.get(symbol, (0.0, 999999.0))
            p_min, p_max = float(prices.min()), float(prices.max())
            if p_min < lo or p_max > hi:
                issues.append(
                    f"Price range [{p_min:.4f}, {p_max:.4f}] outside expected [{lo}, {hi}]"
                )

    result["instrument_issues"] = issues
    result["instrument"] = {
        "symbol": instrument.symbol,
        "pip": instrument.pip,
        "point": instrument.point,
        "price_digits": instrument.price_digits,
    }
    return result


def _is_critical(result: dict) -> bool:
    if "error" in result:
        return True
    if result.get("ohlc_na", 0) > 0:
        return True
    if result.get("high_lt_low", 0) > 0:
        return True
    if result.get("non_weekend_gap_count", 0) > 100:
        return True
    if len(result.get("instrument_issues", [])) > 0:
        return True
    return False


def _symbol_summary_row(symbol: str, result: dict) -> dict:
    return {
        "symbol": symbol,
        "rows": result.get("total_rows", 0),
        "first": result.get("first_timestamp", "?"),
        "last": result.get("last_timestamp", "?"),
        "days": result.get("date_range_days", 0),
        "gaps": result.get("gap_count", 0),
        "non_wknd_gaps": result.get("non_weekend_gap_count", 0),
        "missing_bars": result.get("missing_bars_est", 0),
        "spread_mean": result.get("spread_mean_points", 0),
        "spread_max": result.get("spread_max_points", 0),
        "dups": result.get("duplicate_timestamps", 0),
        "flags": len(_flag_broker_specificity(result)),
        "instrument_issues": len(result.get("instrument_issues", [])),
        "critical": _is_critical(result),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate data for all symbols")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing {symbol}_m5.csv files",
    )
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_dir = args.data_dir if args.data_dir is not None else pcfg.base_dir / "data"

    if not data_dir.exists():
        sys.stderr.write(f"Data directory not found: {data_dir}\n")
        return 1

    all_results: dict[str, dict] = {}
    all_summaries: list[dict] = []

    for symbol in SYMBOLS:
        csv_path = data_dir / f"{symbol.lower()}_m5.csv"
        print(f"\n{'='*60}")
        print(f"  Validating {symbol} ({csv_path.name})")
        print(f"{'='*60}")

        if not csv_path.exists():
            print(f"  SKIP: file not found at {csv_path}")
            all_results[symbol] = {"error": f"file not found: {csv_path}"}
            all_summaries.append(_symbol_summary_row(symbol, all_results[symbol]))
            continue

        df = pd.read_csv(csv_path)
        result = validate_symbol(df, symbol, data_dir)
        all_results[symbol] = result

        out_dir = pcfg.base_dir / "outputs" / symbol / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)

        md_path = out_dir / "data_validation_report.md"
        json_path = out_dir / "data_validation.json"

        md_content = _report_md(result)
        inst_issues = result.get("instrument_issues", [])
        if inst_issues:
            md_content += "\n## Instrument-specific validation\n\n"
            for issue in inst_issues:
                md_content += f"- **ISSUE**: {issue}\n"
            md_content += "\n"

        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(md_content)
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)

        print(f"  Reports written to {out_dir}")
        flags = _flag_broker_specificity(result)
        for f in flags:
            print(f"  FLAG: {f}")
        for issue in inst_issues:
            print(f"  INSTRUMENT ISSUE: {issue}")

        all_summaries.append(_symbol_summary_row(symbol, result))

    print(f"\n\n{'='*80}")
    print("  SUMMARY TABLE")
    print(f"{'='*80}")
    header = (
        f"{'Symbol':<8} {'Rows':>8} {'Days':>6} {'Gaps':>6} "
        f"{'Non-Wknd':>9} {'Spd Mean':>9} {'Spd Max':>8} "
        f"{'Flags':>5} {'Issues':>7} {'Critical':>8}"
    )
    print(header)
    print("-" * len(header))
    critical_symbols: list[str] = []
    for row in all_summaries:
        crit_mark = " ***" if row["critical"] else ""
        print(
            f"{row['symbol']:<8} {row['rows']:>8} {row['days']:>6.1f} "
            f"{row['gaps']:>6} {row['non_wknd_gaps']:>9} "
            f"{row['spread_mean']:>9.1f} {row['spread_max']:>8.0f} "
            f"{row['flags']:>5} {row['instrument_issues']:>7}{crit_mark}"
        )
        if row["critical"]:
            critical_symbols.append(row["symbol"])

    print(f"\n{'='*80}")
    if critical_symbols:
        print(f"  CRITICAL ISSUES FOUND in: {', '.join(critical_symbols)}")
    else:
        print("  All symbols passed validation with no critical issues.")
    print(f"{'='*80}\n")

    return 1 if critical_symbols else 0


if __name__ == "__main__":
    raise SystemExit(main())
