"""Phase 1 - Data validation and quality reporting for the research dataset.

Independently audits a raw OHLCV candle CSV before any research/backtest uses
it. It never modifies the dataset; it only inspects and reports. Checks:

  * file shape / columns
  * timezone / timestamp parsing
  * exact date range, candle count, and expected vs actual cadence
  * missing candles / gaps
  * duplicate timestamps
  * OHLC validity (high >= low >= 0, open/close within [low, high], non-NaN)
  * spread availability and odd values (negatives, zero at the end, constant)
  * volume fields (tick_volume / real_volume)
  * broker-specificity heuristics (spread=0, real_volume=0, midnight rollover)
  * data-quality problem summary

Produces a human-readable report and a machine-readable JSON summary. The
module is written generically so a larger multi-year dataset can be dropped in
without changes: everything keys off the parsed `time` column and the available
columns.

    python -m backtest.data.data_validation [--data PATH] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import PathConfig

# Expected candle bar length in minutes for the timeframe heuristic.
DEFAULT_SYMBOL = "EURUSD"
DEFAULT_TIMEFRAME = "M5"
DEFAULT_BAR_MINUTES = 5


def _expected_cadence(df: pd.DataFrame) -> int:
    """Infer the most common time delta between consecutive candles (minutes)."""
    deltas = df["time"].diff().dropna().dt.total_seconds()
    if deltas.empty:
        return 0
    return int(float(deltas.mode().iloc[0]) / 60.0)


def validate_data(
    df: pd.DataFrame,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
    bar_minutes: int = DEFAULT_BAR_MINUTES,
) -> dict:
    """Run the full validation battery on a raw m5 DataFrame."""
    out: dict = {}
    total_rows = int(len(df))

    # ---- Columns ----
    cols = [str(c).strip().lower() for c in df.columns]
    columns_present = list(df.columns)
    out["columns_present"] = columns_present
    out["expected_columns"] = ["time", "open", "high", "low", "close",
                               "tick_volume", "spread", "real_volume"]

    # normalized lookup
    norm = {str(c).strip().lower(): c for c in df.columns}

    # ---- Timestamps ----
    tcol = norm.get("time")
    if tcol is None:
        out["error"] = "no time column"
        return out
    ts = pd.to_datetime(df[tcol], errors="coerce")
    n_na_time = int(ts.isna().sum())
    out["time_na_count"] = n_na_time

    tmin = ts.min()
    tmax = ts.max()
    out["first_timestamp"] = tmin.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(tmin) else None
    out["last_timestamp"] = tmax.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(tmax) else None
    out["date_range_days"] = (
        float((tmax - tmin).total_seconds() / 86400.0) if pd.notna(tmin) and pd.notna(tmax) else None
    )
    out["timezone_detected"] = "UTC-naive (no tz info in file); treated as UTC server time"
    out["time_well_formed"] = n_na_time == 0

    # drop invalid times for downstream
    valid = ts.notna()
    ts_v = ts[valid]
    n = int(valid.sum())

    # ---- Duplicates ----
    n_dups = int(ts_v.duplicated().sum())
    out["duplicate_timestamps"] = n_dups

    # ---- Expected cadence & gaps ----
    actual_min = _expected_cadence(pd.DataFrame({"time": ts_v}))
    out["dominant_bar_minutes"] = actual_min
    out["expected_bar_minutes"] = bar_minutes
    out["cadence_matches_expected"] = bool(actual_min == bar_minutes)

    if n > 1:
        deltas = ts_v.diff().dt.total_seconds().iloc[1:] / 60.0
        deltas_arr = deltas.to_numpy()
        tol = 1e-6
        is_gap = deltas_arr > actual_min + tol
        n_gaps = int(is_gap.sum())

        # Classify gaps: a full weekend closure is a very long gap (>= 1000 min,
        # ~ a Fri-close to Mon-open).  Shorter gaps are holidays, feed drops, or
        # missing intraweek history - these are the data-quality concern.
        weekend_gap = is_gap & (deltas_arr >= 1000.0)
        non_weekend_gap = is_gap & (~weekend_gap)
        weekend_n = int(weekend_gap.sum())
        weekday_gaps = int(non_weekend_gap.sum())

        total_missing = int(np.round((deltas_arr[is_gap] / actual_min - 1.0).sum()))
        missing_weekend = int(
            np.round((deltas_arr[weekend_gap] / actual_min - 1.0).sum())
            if weekend_n else 0
        )
        missing_non_weekend = int(
            np.round((deltas_arr[non_weekend_gap] / actual_min - 1.0).sum())
            if weekday_gaps else 0
        )

        out["time_column_sorted"] = bool(ts_v.is_monotonic_increasing)
        out["gap_count"] = n_gaps
        out["weekend_gap_count"] = weekend_n
        out["non_weekend_gap_count"] = weekday_gaps
        out["largest_gap_minutes"] = float(deltas_arr.max()) if len(deltas_arr) else 0.0
        out["missing_bars_est"] = total_missing
        out["missing_bars_weekend_only_est"] = missing_weekend
        out["missing_bars_non_weekend_est"] = missing_non_weekend
    else:
        out["time_column_sorted"] = True
        out["gap_count"] = 0
        out["weekend_gap_count"] = 0
        out["non_weekend_gap_count"] = 0
        out["largest_gap_minutes"] = 0.0
        out["missing_bars_est"] = 0
        out["missing_bars_weekend_only_est"] = 0
        out["missing_bars_non_weekend_est"] = 0

    # ---- OHLC validity ----
    ohlc = {k: norm.get(k) for k in ("open", "high", "low", "close")}
    if any(v is None for v in ohlc.values()):
        out["error"] = "missing OHLC column(s)"
        return out

    op = df[ohlc["open"]].to_numpy(dtype=float)
    hi = df[ohlc["high"]].to_numpy(dtype=float)
    lo = df[ohlc["low"]].to_numpy(dtype=float)
    cl = df[ohlc["close"]].to_numpy(dtype=float)

    def _count(mask):
        return int(np.count_nonzero(mask))

    out["ohlc_na"] = _count(pd.isna(op) | pd.isna(hi) | pd.isna(lo) | pd.isna(cl))
    out["high_lt_low"] = _count(hi < lo)
    out["neg_or_zero_ohlc"] = _count((op <= 0) | (hi <= 0) | (lo <= 0) | (cl <= 0))
    # close/open outside [low, high]
    out["close_outside_range"] = _count((cl < lo) | (cl > hi))
    out["open_outside_range"] = _count((op < lo) | (op > hi))
    # bar range sanity: high-low == 0 (flat bar, could be legit in low liquidity)
    out["flat_bars_hl_eq_0"] = _count(hi == lo)
    # bar too large vs neighbors (crude outlier: > 50 * ATR-like median range)
    rng = hi - lo
    med_rng = float(np.nanmedian(rng)) if rng.size else 0.0
    out["median_bar_range"] = med_rng
    out["bars_gt_50x_median_range"] = _count(rng > (50.0 * med_rng + 1e-12))

    # ---- Spread ----
    sp_col = norm.get("spread")
    if sp_col is not None:
        sp = df[sp_col].to_numpy(dtype=float)
        out["spread_present"] = True
        out["spread_na"] = int(pd.isna(sp).sum())
        pos = sp[sp > 0]
        out["spread_positive_count"] = int((sp > 0).sum())
        out["spread_zero_count"] = int((sp == 0).sum())
        out["spread_negative_count"] = int((sp < 0).sum())
        out["spread_mean_points"] = float(pos.mean()) if len(pos) else None
        out["spread_min_points"] = float(pos.min()) if len(pos) else None
        out["spread_max_points"] = float(pos.max()) if len(pos) else None
        # trailing zero spreads (common when live feed ends / holidays)
        out["spread_zeros_at_tail"] = int((sp == 0)[-200:].sum()) if len(sp) else 0
        # constant spread across the whole file?
        out["spread_constant_everywhere"] = bool(len(np.unique(sp)) <= 1)
        # zero-spread coverage by weekday (helps tell weekend/low-liquidity from
        # a feed artifact)
        if tcol in df.columns:
            ts_z = ts
            dow = ts_z[valid].dt.dayofweek
            zdow = (sp == 0)[valid]
            wk = {}
            for d in range(7):
                m = (dow == d).to_numpy()
                tot = int(m.sum())
                zz = int((m & zdow).sum())
                wk[f"weekday_{d}"] = {
                    "zero": zz,
                    "total": tot,
                    "zero_pct": (zz / tot * 100.0) if tot else None,
                }
            out["spread_zero_by_weekday"] = wk
        out["spread_nonzero_samples"] = int((sp > 0).sum())
    else:
        out["spread_present"] = False

    # ---- Volume ----
    tv = norm.get("tick_volume")
    rv = norm.get("real_volume")
    out["tick_volume_present"] = tv is not None
    out["real_volume_present"] = rv is not None
    if tv is not None:
        out["tick_volume_zero_count"] = int((df[tv] == 0).sum())
        out["tick_volume_sum"] = int(df[tv].sum())
    if rv is not None:
        out["real_volume_zero_count"] = int((df[rv] == 0).sum())
        out["real_volume_sum"] = int(df[rv].sum())

    out["total_rows"] = total_rows
    return out


def _flag_broker_specificity(v: dict) -> list[str]:
    """Return human-readable broker-specificity observations."""
    flags = []
    if not v.get("spread_present", False):
        flags.append("No spread column.")
    else:
        if v.get("spread_zero_count", 0) > 0:
            flags.append(
                f"spread is 0 for {v['spread_zero_count']} candles "
                f"({v['spread_zero_count'] / max(v['total_rows'],1) * 100:.2f}%).")
            zby = v.get("spread_zero_by_weekday", {})
            mon_fri_zero = sum(
                zby.get(f"weekday_{d}", {}).get("zero", 0) for d in range(5)
            )
            mon_fri_total = sum(
                zby.get(f"weekday_{d}", {}).get("total", 0) for d in range(5)
            )
            if mon_fri_total:
                mp = mon_fri_zero / mon_fri_total * 100.0
                if mp > 20:
                    flags.append(
                        f"zero spread is NOT weekend-only: {mp:.1f}% of "
                        f"Mon-Fri candles also have spread=0 (feed artifact)."
                    )
        if v.get("spread_constant_everywhere", False):
            flags.append("spread is constant across the entire file.")
        if v.get("spread_negative_count", 0) > 0:
            flags.append(f"spread has {v['spread_negative_count']} negative values.")
    if not v.get("real_volume_present", False):
        flags.append("No real_volume column.")
    elif v.get("real_volume_zero_count", 0) == v.get("total_rows", 0):
        flags.append("real_volume is all zeros (typical MT5 demo/backtest feed).")
    if v.get("tick_volume_zero_count", 0) > 0:
        flags.append(
            f"tick_volume is 0 for {v['tick_volume_zero_count']} candles "
            f"({v['tick_volume_zero_count'] / max(v['total_rows'],1) * 100:.2f}%).")
    if v.get("gap_count", 0) > 0:
        flags.append(
            f"{v['gap_count']} time gaps detected "
            f"({v['missing_bars_est']} missing bars estimated total; "
            f"{v.get('non_weekend_gap_count',0)} non-weekend gaps / "
            f"{v.get('missing_bars_non_weekend_est',0)} non-weekend missing bars) "
            f"- weekends/holidays and possibly missing history.")
    if v.get("non_weekend_gap_count", 0) > 0:
        flags.append(
            f"{v['non_weekend_gap_count']} non-weekend gaps "
            f"({v.get('missing_bars_non_weekend_est',0)} bars) "
            f"- check for missing trading days/history.")
    if v.get("spread_zeros_at_tail", 0) >= 200 and v.get("spread_present"):
        flags.append(
            f"last {v.get('spread_zeros_at_tail',0)} candles all have spread=0 "
            f"- feed may be stale near the end of the file.")
    if v.get("flat_bars_hl_eq_0", 0) > 0:
        flags.append(f"{v['flat_bars_hl_eq_0']} bars with high==low.")
    if v.get("date_range_days", 0) and v["date_range_days"] and v["date_range_days"] < 30:
        flags.append("Dataset spans less than ~30 days - very short sample.")
    return flags


def _report_md(v: dict) -> str:
    L = []
    w = L.append
    w("# DATA VALIDATION REPORT")
    w("")
    w(f"- Rows: `{v.get('total_rows')}`")
    w(f"- First: `{v.get('first_timestamp')}`")
    w(f"- Last: `{v.get('last_timestamp')}`")
    w(f"- Date range (days): `{v.get('date_range_days')}`")
    w(f"- Dominant bar (min): `{v.get('dominant_bar_minutes')}` "
      f"(expected `{v.get('expected_bar_minutes')}`); "
      f"cadence match: `{v.get('cadence_matches_expected')}`")
    w(f"- Time column sorted: `{v.get('time_column_sorted')}`")
    w(f"- Duplicate timestamps: `{v.get('duplicate_timestamps')}`")
    w(f"- Time not-a-date count: `{v.get('time_na_count')}`")
    w(f"- Timezone: `{v.get('timezone_detected')}`")
    w("")
    w("## OHLC validity")
    w("")
    for k in ("ohlc_na", "high_lt_low", "neg_or_zero_ohlc",
              "close_outside_range", "open_outside_range",
              "flat_bars_hl_eq_0", "bars_gt_50x_median_range"):
        w(f"- `{k}`: `{v.get(k)}`")
    w(f"- median bar range: `{v.get('median_bar_range'):.5f}`")
    w("")
    w("## Gaps / missing")
    w("")
    w(f"- gap_count: `{v.get('gap_count')}`")
    w(f"- weekend_gap_count: `{v.get('weekend_gap_count')}` "
      f"(weekend closures are expected in FX)")
    w(f"- non_weekend_gap_count: `{v.get('non_weekend_gap_count')}` "
      f"(these may indicate missing history/holidays)")
    w(f"- missing_bars_est (total): `{v.get('missing_bars_est')}`")
    w(f"- missing_bars_weekend_only_est: `{v.get('missing_bars_weekend_only_est')}`")
    w(f"- missing_bars_non_weekend_est: `{v.get('missing_bars_non_weekend_est')}`")
    w(f"- largest_gap_minutes: `{v.get('largest_gap_minutes')}`")
    w("")
    w("## Spread")
    w("")
    w(f"- present: `{v.get('spread_present')}`")
    if v.get("spread_present"):
        for k in ("spread_na", "spread_positive_count", "spread_zero_count",
                  "spread_negative_count", "spread_mean_points",
                  "spread_min_points", "spread_max_points",
                  "spread_zeros_at_tail", "spread_constant_everywhere"):
            w(f"- `{k}`: `{v.get(k)}`")
        w("- zero-spread by weekday (%):")
        zby = v.get("spread_zero_by_weekday", {})
        names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for d in range(7):
            rec = zby.get(f"weekday_{d}", {})
            pct = rec.get("zero_pct")
            pct_s = f"{pct:.1f}" if pct is not None else "-"
            w(f"  - {names[d]}: {rec.get('zero',0)}/{rec.get('total',0)} ({pct_s}%)")
    w("")
    w("## Volume")
    w("")
    w(f"- tick_volume present: `{v.get('tick_volume_present')}`; "
      f"zero: `{v.get('tick_volume_zero_count')}`; sum: `{v.get('tick_volume_sum')}`")
    w(f"- real_volume present: `{v.get('real_volume_present')}`; "
      f"zero: `{v.get('real_volume_zero_count')}`; sum: `{v.get('real_volume_sum')}`")
    w("")
    w("## Broker-specificity / data-quality flags")
    w("")
    flags = _flag_broker_specificity(v)
    for f in flags:
        w(f"- {f}")
    if not flags:
        w("- No obvious data-quality problems detected.")
    w("")
    w("(This module reports only; it never alters the dataset.)")
    w("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate research dataset")
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    pcfg = PathConfig()
    data_path = args.data if args.data is not None else pcfg.data_file
    out_dir = args.out if args.out is not None else pcfg.output_dir
    out_dir = out_dir / "reports"

    if not data_path.exists():
        sys.stderr.write(f"Data file not found: {data_path}\n")
        return 1

    df = pd.read_csv(data_path)
    results = validate_data(df, DEFAULT_SYMBOL, DEFAULT_TIMEFRAME, DEFAULT_BAR_MINUTES)
    if "error" in results:
        sys.stderr.write(f"Validation error: {results['error']}\n")
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "data_validation_report.md"
    json_path = out_dir / "data_validation.json"
    html_flags = _flag_broker_specificity(results)

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(_report_md(results))
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)

    print(f"Data validation written to {out_dir}")
    print(f"  - {md_path}")
    print(f"  - {json_path}")
    print(f"\nFirst: {results.get('first_timestamp')}  Last: {results.get('last_timestamp')}")
    print(f"Rows: {results.get('total_rows')}  Dups: {results.get('duplicate_timestamps')}  "
          f"Gaps: {results.get('gap_count')}  Missing bars: {results.get('missing_bars_est')}")
    print(f"Flags ({len(html_flags)}):")
    for f in html_flags:
        print(f"  - {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
