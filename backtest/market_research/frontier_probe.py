"""Frontier probe — pre-registered tests of genuinely untested behaviors (RESEARCH ONLY).

Two hypotheses defined here BEFORE results, on DEV rows only, with real observed
spreads + 1.0 pip slippage, using the edge_discovery execution/metrics/classify
conventions.  EURJPY excluded.  Nothing is optimized; verdicts come from the
pre-registered screen.

  G-DAYGAP  : M5 gap behavior — a bar whose previous M5 bar is missing
              (weekday session re-open, overnight, or data break).  Direction =
              sign of the open-to-previous-close gap (continuation hypothesis).
              Holds 6 / 24 M5 bars (30 min / 2h).

  P-WICK    : H1 long-wick rejection candles (price structure).  A bar whose
              rejection wick >= 0.5 * range with a small body closes against the
              wick direction -> fade the wick.  Holds 2 / 6 H1 bars (2h / 6h).

Usage:
    python -m backtest.market_research.frontier_probe
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent
import sys

sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.market_research.edge_discovery import (
    Frame,
    SYMBOLS,
    TF_MIN,
    bucket,
    classify,
    experiment_metrics,
    simulate,
)

REPORT_PATH = "FRONTIER_PROBE_RESULTS.md"
WICK_RATIO = 0.5
BODY_RATIO = 0.4
GAP_MIN_MINUTES = 5.1


def _exp_g_daygap(frame: Frame) -> tuple[np.ndarray, np.ndarray]:
    n = frame.n
    mask = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=float)
    delta = np.full(n, np.inf, dtype=float)
    if n > 1:
        delta[1:] = (frame.ts[1:] - frame.ts[:-1]).astype("timedelta64[m]").astype(float)
    for i in range(1, n):
        if not np.isfinite(delta[i]) or delta[i] <= GAP_MIN_MINUTES:
            continue
        oc = frame.open[i] - frame.close[i - 1]
        if not np.isfinite(oc) or oc == 0.0:
            continue
        mask[i] = True
        direction[i] = 1.0 if oc > 0 else -1.0
    return mask, direction


def _exp_p_wick(frame: Frame) -> tuple[np.ndarray, np.ndarray]:
    n = frame.n
    rng = frame.high - frame.low
    body = frame.close - frame.open
    bull = (frame.open - frame.low >= WICK_RATIO * rng) & (np.abs(body) <= BODY_RATIO * rng) & (body >= 0)
    bear = (frame.high - frame.close >= WICK_RATIO * rng) & (np.abs(body) <= BODY_RATIO * rng) & (body <= 0)
    bull &= rng > 0
    bear &= rng > 0
    direction = np.zeros(n, dtype=float)
    direction[bull] = 1.0
    direction[bear] = -1.0
    return (bull | bear), direction


EXPERIMENTS: list[dict[str, Any]] = [
    {
        "id": "G-DAYGAP",
        "name": "overnight/weekend gap continuation",
        "hypothesis": "I - event/context (large gaps)",
        "tf": "M5",
        "holds": [6, 24],
        "rationale": "Gap behavior is explicitly untested in the audit; direction = gap sign.",
    },
    {
        "id": "P-WICK",
        "name": "H1 long-wick rejection candles",
        "hypothesis": "E - market structure (rejection/wick)",
        "tf": "H1",
        "holds": [2, 6],
        "rationale": "Price-structure rejection behavior has never been tested in any phase.",
    },
]


def main() -> int:
    pcfg = PathConfig()
    results: dict[str, dict] = {}
    for exp in EXPERIMENTS:
        eid = exp["id"]
        results[eid] = {"experiment": exp, "symbols": {}}
        for sym in SYMBOLS:
            results[eid]["symbols"][sym] = {"mask_sum": 0, "holds": {}}
            frame = None
            if exp["tf"] == "M5":
                frame = Frame(sym, "M5", pcfg)
            elif exp["tf"] == "H1":
                frame = Frame(sym, "H1", pcfg)
            else:
                raise ValueError(exp["tf"])
            if eid == "G-DAYGAP":
                mask, direction = _exp_g_daygap(frame)
            elif eid == "P-WICK":
                mask, direction = _exp_p_wick(frame)
            else:
                raise ValueError(eid)
            results[eid]["symbols"][sym]["mask_sum"] = int(mask.sum())
            for H in exp["holds"]:
                events = simulate(frame, mask, direction, H)
                results[eid]["symbols"][sym]["holds"][str(H)] = experiment_metrics(events, frame)

    for eid, r in results.items():
        for H in r["experiment"]["holds"]:
            pos = sum(1 for sym in SYMBOLS
                      if r["symbols"][sym]["holds"][str(H)].get("total_net_pips", 0.0) > 0
                      and r["symbols"][sym]["holds"][str(H)].get("n", 0) >= 1000)
            for sym in SYMBOLS:
                single = r["symbols"][sym]["holds"][str(H)]
                single["_pos_symbols"] = pos
                single["verdict"] = classify(single, pos)["verdict"]
                single["reason"] = classify(single, pos)["reason"]
                single["bucket"] = bucket(single["verdict"], single["reason"])

    lines: list[str] = []
    A = lines.append
    A("# FRONTIER PROBE RESULTS — pre-registered untested behaviors on DEV (research only)\n")
    A("\nDefinitions frozen before running (see module). DEV rows only, EURUSD/EURGBP/GBPUSD, "
      "EURJPY excluded. Cost = entry + exit observed spread + 1.0 pip slippage. Screen: n >= 1000, "
      "movement-to-cost >= 1.0 with |raw mean| >= 2 pips, t p < 0.05, >= 2/3 symbols positive, "
      ">= 60% years positive, no year > 50% / window > 40% of net.\n")
    A("\n## Verdicts\n")
    A("\n| experiment | sym | hold | n | raw | net_exp | m2c | win% | PF | verdict | bucket |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for eid, r in results.items():
        exp = r["experiment"]
        for H in exp["holds"]:
            for sym in SYMBOLS:
                m = r["symbols"][sym]["holds"][str(H)]
                A(f"| {eid} | {sym} | H={H} | {m.get('n',0):,} | {m.get('mean_raw_pips',0.0):+.2f} | "
                  f"{m.get('expectancy_net_pips',0.0):+.3f} | {m.get('movement_to_cost',0.0):.2f} | "
                  f"{m.get('win_rate',0.0)*100:.1f} | {m.get('profit_factor',0.0):.3f} | "
                  f"{m['verdict']} | {m['bucket']} |")
    A("\n## Full metrics\n")
    for eid, r in results.items():
        for H in r["experiment"]["holds"]:
            for sym in SYMBOLS:
                m = r["symbols"][sym]["holds"][str(H)]
                A(f"\n### {eid} / {sym} / H={H}\n")
                A("| metric | value |\n|---|---|")
                for k, v in sorted(m.items()):
                    if not isinstance(v, (dict, list)):
                        A(f"| {k} | {v} |")
    out = {"meta": {"phase": "frontier_probe", "data": "dev split clean Dukascopy M5",
                    "cost_model": "entry+exit observed spread + 1.0 pip slippage",
                    "screen": "edge_discovery pre-registered screen", "excluded": {"EURJPY": "degraded"}},
           "results": results}
    with open(_root / REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(pcfg.output_dir / "frontier_probe_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Report written to {_root / REPORT_PATH}")
    print(f"Probe dump: {pcfg.output_dir / 'frontier_probe_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())