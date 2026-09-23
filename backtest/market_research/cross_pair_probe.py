"""Cross-pair relative-strength probe — pre-registered divergence test (RESEARCH ONLY).

FROZEN BEFORE RESULTS.  Rationale from RESEARCH_STATE_AUDIT.md section 12: cross-pair
relative strength / divergence is the genuinely untested, data-complete dimension.
All single-instrument shape tests (trend, pullback, squeeze, momentum, alignment,
fade, gaps, structure) have failed the screen on DEV; this is the last honest stone.

Rule (defined here, not tuned):
  instrument  : EURGBP (the triangle leg that isolates EUR strength vs the USD pair)
  signal      : rel(t) = log-return of EURUSD over the last N=20 H1 bars
                          - log-return of GBPUSD over the last N=20 H1 bars
                z(t)     = ( rel(t) - trailing_mean ) / trailing_std   (trailing W=60 bars, closed at t)
                trade when |z(t)| >= k=0.5 ; direction = sign(z(t))
                (EUR strong vs GBP -> EURGBP rises; EUR weak -> EURGBP falls)
  execution   : entry at open of bar t+1, exit at close of bar t+H, H in {12, 24}
  hypothesis  : relative-strength continuation (cross-sectional momentum)

Integrity: DEV rows only, all three legs synchronized on the UTC hour index
(inner join on timestamp); no lookahead (only closed-bar data up to t); real
observed EURGBP spreads + 1.0 pip slippage; EURJPY excluded; no strategy or
backtester file changed.  Only the EURGBP tradeable leg is evaluated.

Usage:
    python -m backtest.market_research.cross_pair_probe
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_parent = Path(__file__).resolve().parent.parent  # backtest/
_root = _parent.parent
import sys

sys.path.insert(0, str(_root))

from backtest.config import PathConfig
from backtest.instruments import get_instrument
from backtest.market_research.edge_discovery import SYMBOLS, SLIP_TOTAL_PIPS, bucket, classify, experiment_metrics

N_BARS = 20
MOM_WIN = 60
K_Z = 0.5
HOLDS = [12, 24]
WEIGHTS = {"EURUSD": 1.0, "GBPUSD": -1.0}
TRADE_SYM = "EURGBP"

REPORT_PATH = "CROSS_PAIR_PROBE_RESULTS.md"


def main() -> int:
    pcfg = PathConfig()
    x = pd.read_csv(pcfg.base_dir / "data" / "eurgbp_m5.csv")
    x["time"] = pd.to_datetime(x["time"])
    xdev = x.iloc[pd.read_csv(pcfg.output_dir / "splits" / "EURGBP" / "assignments.csv")["split"].to_numpy() == "dev"].reset_index(drop=True)
    leg: dict[str, pd.DataFrame] = {}
    for sym in ["EURUSD", "GBPUSD"]:
        df = pd.read_csv(pcfg.base_dir / "data" / f"{sym.lower()}_m5.csv")
        df["time"] = pd.to_datetime(df["time"])
        dev = df.iloc[pd.read_csv(pcfg.output_dir / "splits" / sym / "assignments.csv")["split"].to_numpy() == "dev"].reset_index(drop=True)
        dev["bucket"] = dev["time"].dt.floor("1h")
        leg[sym] = dev.groupby("bucket", as_index=False).agg(
            close=("close", "last"), time=("time", "last"))

    xdev["bucket"] = xdev["time"].dt.floor("1h")
    xh = xdev.groupby("bucket", as_index=False).agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), spread=("spread", "last"), time=("time", "last"))

    aligned = xh
    for sym in ["EURUSD", "GBPUSD"]:
        l = leg[sym][["bucket", "close"]].rename(columns={"close": f"{sym}_close"})
        aligned = aligned.merge(l, on="bucket", how="inner")
    aligned = aligned.dropna(subset=[c for c in aligned if c not in ("bucket", "time")]).reset_index(drop=True)

    t = aligned["time"].to_numpy()
    c_e = aligned["EURUSD_close"].to_numpy(float)
    c_g = aligned["GBPUSD_close"].to_numpy(float)
    o = aligned["open"].to_numpy(float)
    cl = aligned["close"].to_numpy(float)
    spd = (aligned["spread"].to_numpy(float) * get_instrument(TRADE_SYM).point) / get_instrument(TRADE_SYM).pip
    n = len(aligned)

    lb = np.log(c_e) - np.log(c_g)
    rlr = np.full(n, np.nan)
    rlr[N_BARS:] = lb[N_BARS:] - lb[:-N_BARS]
    z = np.full(n, np.nan)
    s = pd.Series(rlr).rolling(MOM_WIN, min_periods=MOM_WIN)
    mu, sd = s.mean().to_numpy(), s.std(ddof=0).to_numpy()
    ok = sd > 0
    z[ok] = (rlr[ok] - mu[ok]) / sd[ok]
    sig = (np.abs(z) >= K_Z) & np.isfinite(z)
    direction = np.sign(z)
    pip = get_instrument(TRADE_SYM).pip

    events: list[dict] = []
    for idx in np.nonzero(sig)[0]:
        entry_i, exit_i = idx + 1, idx + HOLDS[0]
        if exit_i >= n:
            continue
        entry, exit_px = o[entry_i], cl[exit_i]
        if not (np.isfinite(entry) and np.isfinite(exit_px) and np.isfinite(spd[entry_i]) and np.isfinite(spd[exit_i])):
            continue
        d = direction[idx]
        gross = d * (exit_px - entry) / pip
        cost = spd[entry_i] + spd[exit_i] + SLIP_TOTAL_PIPS
        events.append({
            "entry_time": str(t[entry_i]), "exit_time": str(t[exit_i]),
            "direction": "BUY" if d > 0 else "SELL",
            "gross_pips": float(gross), "cost_pips": float(cost), "net_pips": float(gross - cost),
            "duration_bars": int(HOLDS[0]), "duration_hours": float(HOLDS[0]), "entry_regime": "normal",
            "entry_year": int(pd.Timestamp(t[entry_i]).year), "entry_month": str(pd.Timestamp(t[entry_i]).to_period("M")),
        })

    ns = type("F", (), {})()
    ns.symbol, ns.tf, ns.bars_min, ns.pip, ns.n = TRADE_SYM, "H1", 60, pip, n
    m: dict[str, Any] = experiment_metrics(events, ns)
    pos = sum(1 for _ in [0]) if m.get("total_net_pips", 0.0) > 0 and m.get("n", 0) >= 1000 else 0
    cv = classify(m, pos)
    m["verdict"] = cv["verdict"]
    m["reason"] = cv["reason"]
    m["bucket"] = bucket(cv["verdict"], cv["reason"])

    lines: list[str] = []
    A = lines.append
    A("# CROSS-PAIR PROBE RESULTS — EURUSD/GBPUSD divergence traded on EURGBP (research only)\n")
    A("\nPre-registered rule frozen before running (see module). DEV rows only; three legs synchronized on the "
      "UTC hour index (inner join); signal uses closed bars only up to t; entry open[t+1], exit close[t+H]; "
      "real observed EURGBP spread + 1.0 pip slippage; EURJPY excluded. Verdict judged on the FROZEN "
      "momentum rule only.\n")
    A("\n## Result (H=" + str(HOLDS[0]) + ")\n")
    A("\n| metric | value |")
    A("|---|---|")
    for k in ("n", "win_rate", "expectancy_net_pips", "mean_raw_pips", "avg_win_pips", "avg_loss_pips",
              "profit_factor", "movement_to_cost", "total_cost_pips", "total_net_pips", "max_drawdown_pips",
              "years_positive_share", "max_year_share", "t_test", "verdict", "reason", "bucket"):
        A(f"| {k} | {m.get(k)} |")
    A("\n## Screen pass check\n")
    A("\n- n >= 1000: " + str(m.get("n", 0) >= 1000))
    A("- movement-to-cost >= 1.0 and |raw| >= 2.0: " + str(m.get("movement_to_cost", 0.0)))
    A("- t p < 0.05 and net > 0: " + str((m.get("t_test") or {}).get("p")))
    A("- exit reasons never applied; fixed horizon only.\n")

    out = {"meta": {"rule": {"instrument": TRADE_SYM, "N": N_BARS, "window": MOM_WIN, "k": K_Z,
                             "holds": HOLDS, "signal": "z of (logRetEURUSD - logRetGBPUSD)",
                             "hypothesis": "relative-strength continuation"},
                    "data": "dev split of clean Dukascopy M5", "cost_model": "real spread + 1.0 pip slip"},
           "result": m}
    with open(_root / REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(pcfg.output_dir / "cross_pair_probe_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Report written to {_root / REPORT_PATH}")
    print(f"Dump: {pcfg.output_dir / 'cross_pair_probe_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())