"""Phase 6 — Multi-market research runner.

Runs all 7 market-behavior studies on every available symbol, producing
per-symbol reports in outputs/phase6/<symbol>/ and a cross-market comparison.

Usage:
    python -m backtest.market_research.phase6

Outputs:
    outputs/phase6/<symbol>/*.md + *_summary.json  (per-symbol)
    outputs/phase6/comparison.md                    (cross-market)
    outputs/phase6/comparison.json                  (machine-readable)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import numpy as np

# Ensure the backtest package is importable
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backtest.market_research import (
    momentum, mean_reversion, breakout, volatility,
    sessions, trend_persistence, range_behavior,
)
from backtest.market_research._loader import load_m5

MODULES = [
    ("momentum",           momentum),
    ("mean_reversion",     mean_reversion),
    ("breakout",           breakout),
    ("volatility",         volatility),
    ("sessions",           sessions),
    ("trend_persistence",  trend_persistence),
    ("range_behavior",     range_behavior),
]

SYMBOLS = ["eurusd", "eurgbp", "eurjpy", "gbpusd"]
OUT_BASE = ROOT / "outputs" / "phase6"


def _load_symbol(symbol: str) -> pd.DataFrame:
    csv = ROOT / "data" / f"{symbol}_m5.csv"
    df = pd.read_csv(csv)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df


def _run_symbol(symbol: str) -> dict:
    """Run all 7 studies for one symbol by monkey-patching load_m5."""
    df = _load_symbol(symbol)
    out_dir = OUT_BASE / symbol
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  {symbol.upper()}: {len(df):,} bars, {df['time'].min()} .. {df['time'].max()}")

    # Monkey-patch load_m5 to return this symbol's data
    original_load = load_m5

    def _patched_load():
        return df.copy()

    results = {}
    with patch("backtest.market_research._loader.load_m5", side_effect=_patched_load):
        # Also patch in each module's namespace where they import it
        patches = []
        for mod_name, mod in MODULES:
            if hasattr(mod, "load_m5"):
                patches.append(patch.object(mod, "load_m5", _patched_load))

        for p in patches:
            p.start()

        for study_name, mod in MODULES:
            t0 = time.time()
            try:
                rc = mod.main(["--out", str(out_dir)])
                elapsed = time.time() - t0
                results[study_name] = {"status": "ok", "time_s": round(elapsed, 1)}
                print(f"    {study_name:20s}  ok  ({elapsed:.1f}s)")
            except Exception as e:
                results[study_name] = {"status": "error", "error": str(e)}
                print(f"    {study_name:20s}  ERROR: {e}")

        for p in patches:
            p.stop()

    return {
        "bars": len(df),
        "first": str(df["time"].min()),
        "last": str(df["time"].max()),
        "studies": results,
    }


def _extract_mr_findings(symbol: str) -> dict:
    """Extract mean-reversion fade-extreme results for a symbol."""
    fpath = OUT_BASE / symbol / "mean_reversion_summary.json"
    if not fpath.exists():
        return {}
    with open(fpath) as f:
        data = json.load(f)
    # The JSON has LB10..LB160 keys with dist stats
    return data


def _extract_mom_findings(symbol: str) -> dict:
    """Extract momentum findings."""
    fpath = OUT_BASE / symbol / "momentum_summary.json"
    if not fpath.exists():
        return {}
    with open(fpath) as f:
        return json.load(f)


def _extract_vol_findings(symbol: str) -> dict:
    """Extract volatility findings."""
    fpath = OUT_BASE / symbol / "volatility_summary.json"
    if not fpath.exists():
        return {}
    with open(fpath) as f:
        return json.load(f)


def _build_comparison(symbols: list[str]) -> str:
    L = ["# Phase 6 — Multi-Market Research Comparison\n"]
    L.append(f"**Symbols**: {', '.join(s.upper() for s in symbols)}")
    L.append("**Timeframe**: M5")
    L.append("**Studies**: momentum, mean-reversion, breakout, volatility, sessions, trend-persistence, range-behavior\n")

    # --- Mean Reversion ---
    L.append("## 1. Mean Reversion — Cross-Market\n")
    L.append("Fade extreme distance from trailing mean.  Positive forward returns after extreme moves = reversion.\n")
    L.append("| Symbol | LB | dist_std | below -1σ % | above +1σ % |")
    L.append("|--------|-----|----------|-------------|-------------|")
    for sym in symbols:
        mr = _extract_mr_findings(sym)
        for lb_key in ["LB10", "LB40", "LB160"]:
            if lb_key in mr:
                d = mr[lb_key]
                ds = d.get("dist_std", "?")
                bl = d.get("extreme_below_lt_neg1_pct", "?")
                ba = d.get("extreme_above_gt_1_pct", "?")
                try:
                    ds = f"{float(ds):.3f}"
                except (TypeError, ValueError):
                    pass
                try:
                    bl = f"{float(bl):.1f}"
                except (TypeError, ValueError):
                    pass
                try:
                    ba = f"{float(ba):.1f}"
                except (TypeError, ValueError):
                    pass
                L.append(f"| {sym.upper()} | {lb_key} | {ds} | {bl} | {ba} |")
    L.append("")

    # --- Momentum ---
    L.append("## 2. Momentum / Trend Persistence — Cross-Market\n")
    L.append("| Symbol | Key finding |")
    L.append("|--------|------------|")
    for sym in symbols:
        mom = _extract_mom_findings(sym)
        # Look for sign-conditioned continuation data
        if "sign_conditioned" in mom:
            sc = mom["sign_conditioned"]
            LB = list(sc.keys())[0] if sc else None
            if LB:
                after_up = sc[LB].get("avg_fwd_after_up", "?")
                after_dn = sc[LB].get("avg_fwd_after_dn", "?")
                L.append(f"| {sym.upper()} | after_up={after_up}, after_dn={after_dn} pips (LB={LB}) |")
            else:
                L.append(f"| {sym.upper()} | (data available in per-symbol report) |")
        else:
            L.append(f"| {sym.upper()} | (see per-symbol report) |")
    L.append("")

    # --- Volatility ---
    L.append("## 3. Volatility Regimes — Cross-Market\n")
    L.append("| Symbol | Low % | Normal % | High % | Median ATR (pips) | ATR p10 | ATR p90 |")
    L.append("|--------|-------|----------|--------|-------------------|---------|---------|")
    for sym in symbols:
        vol = _extract_vol_findings(sym)
        rd = vol.get("regime_distribution", {})

        def _f(v, fmt=".1f"):
            try:
                return f"{float(v):{fmt}}"
            except (TypeError, ValueError):
                return str(v)

        L.append(f"| {sym.upper()} | "
                 f"{_f(rd.get('low', '?'))}% | {_f(rd.get('normal', '?'))}% | {_f(rd.get('high', '?'))}% | "
                 f"{_f(vol.get('median_atr_pips', '?'), '.2f')} | "
                 f"{_f(vol.get('atr_p10_pips', '?'), '.2f')} | {_f(vol.get('atr_p90_pips', '?'), '.2f')} |")
    L.append("")

    # --- Conclusions ---
    L.append("## 4. Cross-Market Conclusions\n")
    L.append("### Patterns consistent across all 4 symbols:")
    L.append("- _To be filled after reviewing individual reports_\n")
    L.append("### Symbol-specific differences:")
    L.append("- _To be filled after reviewing individual reports_\n")
    L.append("### Strategy design implications:")
    L.append("- Any mean-reversion strategy should be validated on all 4 symbols.\n")
    L.append("---\n")
    L.append("*Auto-generated. Verify against individual study reports in outputs/phase6/<symbol>/.*\n")

    return "\n".join(L)


def main() -> int:
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    print("Phase 6 — Multi-Market Research")
    print("=" * 60)

    all_results = {}
    for sym in SYMBOLS:
        all_results[sym] = _run_symbol(sym)

    # Build comparison
    print(f"\n{'='*60}")
    print("Building cross-market comparison...")
    comp_md = _build_comparison(SYMBOLS)
    comp_path = OUT_BASE / "comparison.md"
    with open(comp_path, "w", encoding="utf-8") as f:
        f.write(comp_md)
    print(f"  {comp_path}")

    comp_json = OUT_BASE / "comparison.json"
    with open(comp_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"  {comp_json}")

    print("\nPhase 6 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
