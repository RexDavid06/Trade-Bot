# EDGE DISCOVERY PLAN — Market-Behavior Edition

Research only · DEV split only · 60/20/20 preserved · no strategy constructed ·
no backtest of a trading strategy · no parameter optimization · no ML · no live
execution · bot.py / V1 / V2 / Strategies 01–03 untouched · historical outputs
never overwritten.

This is the pre-registration document for the current discovery phase. It is
written BEFORE results are computed. Every hypothesis, its precise entry/exit
definition, its cost model, its sample floor and its failure criteria are fixed
here first; the results document (`EDGE_DISCOVERY_RESULTS.md`) will report what
was measured without changing any of these definitions.

---

## PART A — REPOSITORY AUDIT (answers the 8 required questions)

### A1. What instruments and timeframes are currently available?

**Instrument registry** (`backtest/instruments.py`): EURUSD, EURGBP, EURJPY,
GBPUSD. Each carries pip / point / digits / contract size / spread
interpretation.

**Data files actually present** (`data/*_m5.csv`), all Dukascopy M5 composite
feeds (bid OHLC + real observed `spread = round((ask_close-bid_close)/point)`):

| symbol | rows | date range | status |
|---|---|---|---|
| eurusd | 422,225 | 2021-01-03 .. 2026-09-09 | clean (0 dup ts; 99 zero-spread bars ~0.02%) |
| eurgbp | 425,477 | 2021-01-03 .. 2026-09-09 | clean (0 dup ts; 0 zero-spread bars) |
| gbpusd | 374,746 | 2021-01-03 .. 2026-09-09 | clean (0 dup ts; 0 zero-spread bars) |
| eurjpy | 90,000 | 2025-06-16 .. 2026-09-01 | **degraded** — 14-month window, ~46% zero-spread bars, feed artifact; EXCLUDED (issue A2 unresolved) |

**Timeframes.** Only M5 exists as raw CSV. M15 / H1 / H4 are built from the SAME
M5 source by UTC-anchored floor aggregation with no lookahead
(`phase5_research._aggregate`: first open / max high / min low / last close;
`spread` = spread of the last M5 bar in the window). No other timeframe data is
available locally.

### A2. What data ranges exist?

- Core clean pairs (EURUSD / EURGBP / GBPUSD): 2021-01-03 22:00 UTC →
  2026-09-09 23:55 UTC, ~5.7 years, M5.
- EURJPY: 2025-06-16 .. 2026-09-01, M5, degraded (excluded from this phase).
- MetaQuotes-Demo MT5 history was diagnosed in PHASE0 at ~16 months with an
  unreliable (~84–99% zero) spread field; it is not used as a research dataset.

### A3. Which datasets are DEV, VALIDATION, and HOLDOUT?

Chronological 60/20/20 fraction split per symbol, produced by
`backtest.data.research_split.make_research_split` and verified by
`validate_split_isolation`. Stored under `outputs/splits/<SYMBOL>/{assignments.csv, metadata.json}`.

| symbol | dev | val | holdout | dev window |
|---|---|---|---|---|
| EURUSD | 253,335 | 84,445 | 84,445 | .. 2025-07-24 |
| EURGBP | 255,286 | 85,096 | 85,095 | .. 2025-07-21 |
| GBPUSD | 224,848 | 74,949 | 74,949 | .. 2025-08-08 |

This phase reads **DEV rows only**. Validation is read **only** in the proposed
next step (if a candidate is reported, see STOP CONDITION in TASK.md); holdout
is never read.

### A4. What strategy/research interfaces already exist?

**Backtest/engine layer**
- `backtest.backtester.run_backtest(df, s_cfg, c_cfg)` + `Trade`, `Position`.
  Closed-candle/next-open execution (fixed); SL/TP intrabar conservative;
  per-symbol instruments; A5 balance-based sizing (default `fixed` unchanged).
- `backtest.config`: `StrategyConfig`, `CostConfig`, `PathConfig`.
- `backtest.run` CLI · `backtest.metrics.compute_metrics` ·
  `backtest.reporting` · `backtest.indicators.add_indicators`.
- Strategy definitions: `strategy.py` (V1 baseline), `strategy_v2.py` (V2
  trend+pullback), `backtest/strategies/strategy_0{1,2,3}_*.py`,
  `strategies/mean_reversion.py`, `strategies/breakout_fade.py`,
  `strategies/benchmark.py`, `spread_sensitivity.py`, `experiment.py`,
  `excursion.py`, `diagnostics.py`, `predictive*.py`, `validate*.py`.
- Research READ-ONLY helpers: `backtest.market_research/common.py`
  (`session_label`, `atr_regime`, `forward_return_matrix`, one-sample t-test /
  hit-rate z-test via numpy, `build_conditioned_table`), `_loader.py`
  (`load_m5`, `write_study`, `write_json`), `market_research/_atr`,
  `phase5_research._aggregate`.
- Research runners: `market_discovery.py` (Phase 1), `edge_research.py`
  (Phase 3), `multi_hour_research.py` (Phase 4), `phase5_research.py`
  (Phase 5 — written, not executed: no `PHASE_5_*.md` output exists),
  `phase6.py` (Phase 6 — **invalidated historically**: ran 7 studies on the
  FULL dataset with a symbol mislabelling bug; must not be emulated).

### A5. What metrics are already implemented?

`backtest.metrics.compute_metrics` implements: trade count, win/loss/BE counts,
win rate, gross profit/loss, profit factor, net profit, expectancy per trade
(money + pips), total return %, max drawdown ($ and %), longest streaks,
monthly table, long vs short table. Research layer (`common.py`) implements:
avg/median pips, hit%, t-stat/p, z-stat/p for sample size < SMALL_N flagging,
conditioned tables, long/short splits, regime/session conditioning. The
backtester records per-trade MAE/MFE and R-multiples used by `excursion.py`.

### A6. What costs and execution assumptions are implemented?

Three cost conventions in use (all documented):

1. **Research constant** (Phases 1/3/4): `round trip = 2 × median(dev M5 spread
   pips) + 1.7 pips` → EURUSD 2.30, EURGBP 3.50, GBPUSD 3.50.
2. **Research real-spread** (Phase 5 spec): `cost(i→j) = spread_pips[i] +
   spread_pips[j] + 1.0 pip slippage` (0.5/side per `CostConfig.slippage_pips`).
3. **Engine** (`CostConfig.shadow` in backtester): observed spread × point
   (× `spread_multiplier`), `slippage_pips = 0.5/side`, `commission_per_lot =
   $7` round-turn, `starting_balance = 10,000`, fixed lot 0.10 default,
   `conservative_intrabar=True`.

Execution convention everywhere: signal decided on the **closed** candle, entry
at the **next bar open** (A3 fixed), SL/TP intrabar conservative when present.
Phase 5 marks all MT5 broker symbol specs UNKNOWN (MinLot/lot step/commission
etc. not obtainable without connecting).

### A7. What known data/research limitations remain?

- EURJPY feed is degraded (A2 unresolved) → excluded from all experiments.
- `real_volume` is all zeros on every pair → volume-based behaviors are NOT
  TESTED.
- Spread is **Dukascopy observed bid/ask**, not the live broker feed; real
  broker spreads can differ (MT5 demo field is unreliable, PHASE0).
- Aggregated H1/H4 bars carry the last-M5-close spread (spread-at-close).
- Overlapping forward windows inflate effective n at long horizons (Phases 3–4);
  this phase therefore uses **non-overlapping event counting** for trade-level
  metrics while still evaluating all events for raw statistics.
- ATR-bar deferral is a known live-strategy issue; print-only order handling is
  a known live-execution limitation (neither blocks this DEV-only discovery).
- `PROJECT_RESEARCH_HANDOFF.md` and `PHASE6_5_RESEARCH_INTEGRITY_AUDIT.md` show
  the handoff document contains fabricated numbers; **decisions are based only
  on source files / raw output JSON**, not on handoff tables.

### A8. Which experiments have already been performed (do-not-duplicate list)?

| Phase | Module | Scope | Outcome (DEV) |
|---|---|---|---|
| Pre-1 | `run_all.py` studies on 90k EURUSD M5 (2025-06..2026-09) | momentum, trend persistence, mean reversion | M5 mean-reverting; not final data |
| 1 | `market_discovery.py` (7 studies) | 4 pairs, M5, H=1..80, sessions, vol regimes, pullbacks, breakout, range | trend cont. negative; fade-extreme positive (+0.2..+0.37 pips) but < costs (2.3–3.5) |
| 3 | `edge_research.py` | 4 pairs M5, H=5/20/80/240, momentum W=5/20/80, sessions, vol expand/contract, breakout | best movement-to-cost **0.66** (none ≥ 1.0); EURJPY excluded |
| 4 | `multi_hour_research.py` | 3 pairs, M5 1h..24h: reversal, persistence, session opens, vol expansion, 24h breakouts | best **0.734** (none ≥ 1.0) |
| 5 | `phase5_research.py` | M15/H1/H4 construction + real-spread re-check | module written; **no outputs in repo** (never executed) |
| 6 | `phase6.py` | 7 studies × 4 symbols on FULL data | historically invalidated (label bug, no split) |
| Strateg y | `strategies/benchmark.py` | V1, mean_reversion, breakout_fade × 4 pairs × dev/val/holdout | all negative; e.g. EURUSD dev V1 −62.9%, MR −67.1%, BF −21.9% |

Conclusions already established and therefore **not re-run** here: M5 trend
continuation rejected; breakout continuation rejected at M5 and 1h–24h;
session-open drift rejected; volatility expansion/contraction rejected as raw
behavior; fade-the-extreme is the only consistently positive raw M5 behavior but
is below costs on all three clean pairs.

---

## PART B — DESIGN PRINCIPLES (frozen before results)

1. **DEV only.** Every loader filters through `outputs/splits/<SYM>/assignments.csv`
   selecting `split == "dev"`; validation/holdout timestamps are never loaded
   (enforced by a test).
2. **No sweeps.** Each hypothesis is a single pre-registered rule with at most a
   small, economically separated horizon ladder (1–3 pre-chosen holds).
3. **No strategy construction.** Experiment outputs are behavioral measurements
   on DEV. No SL/TP tuning, no indicator parameter search, no portfolio logic.
4. **No machine learning.**
5. **Everything reproducible**: single module `backtest/market_research/
   edge_discovery.py`, single runner, JSON + MD outputs.
6. **Failure is a valid result.** Every hypothesis gets exactly one verdict:
   DISCOVERED / REJECTED / UNRESOLVED / NOT TESTED, with a reason.

### Trading semantics used for every experiment

- Decision information: **the close of bar t and strictly earlier bars only**.
  All conditions use causal rolling windows (min_periods = full window).
- Execution: enter at the **open of bar t+1**, exit at the **close of bar
  t+H** (fixed-horizon hold of H bars of the working timeframe). No stops are
  modelled — SL/TP values would be strategy parameters and are out of scope for
  behavior discovery.
- Cost model: `round_trip_pips = spread_pips[t+1] + spread_pips[t+H] + 1.0`
  (real observed spread at the entry and exit bars + 1.0 pip slippage, 0.5/side)
  — the Phase-5 `ratio_real` convention, kept for comparability.
- Net pips per event = `direction × (close[t+H] − open[t+1]) / pip − cost`.
- Sample floor per (experiment, symbol): **n ≥ 1000** events to report; a rule
  must also have **n ≥ 1000 across symbols** to be discussed at all.

### Pre-registered viability screen (fixed BEFORE results exist)

A rule is **VIABLE*** (a reported candidate) only if ALL hold:

1. `movement_to_cost = |mean raw pips| / mean round-trip cost ≥ 1.0` AND
   `|mean raw pips| ≥ 2.0` (identical to Phases 3/4/5 thresholds).
2. Net expectancy after the real-spread cost is positive, with one-sample
   t-test p < 0.05 (via `common.test_mean_nonzero`).
3. Positive mean net pips on **at least 2 of the 3** clean symbols.
4. Win rate is positive in **≥ 60% of calendar years** present, and no single
   year contributes > 50% of total net pips (stability across time).
5. No single 4-week window contributes > 40% of total net pips (no tiny-period
   dependence).
6. No lookahead (by construction; enforced by tests).
7. Economically interpretable rationale (stated per hypothesis).

Disqualifiers (REJECTED) that do NOT invalidate the experiment: n < 1000,
|mean| < 2.0 pips, movement-to-cost < 1.0, negative net expectancy, unstable
across years/symbols, no economic rationale.

---

## PART C — HYPOTHESES (A–J) AND PRE-REGISTERED EXPERIMENTS

### Common feature set (computed causally per working timeframe, per symbol)

Let `C, O, H, L` be close/open/high/low in price units, `pip` per instrument.
`ATR14` = market_research `_atr(H, L, C, 14)` (EWM alpha=1/14). `SMAk` = rolling
mean of closes with full window. `ATR-regime` = `atr_regime(ATR14, 50)` (33/67
percentiles, causal). `spread_pips = spread × point / pip`. Sessions via
`session_label(hour_utc)`.

The five hypotheses below are NEW. The remaining five (A, C, D, F, I) are
**already tested** by Phases 1/3/4 and are **NOT re-run** in this phase to avoid
duplication; their specs are recorded here for completeness and their prior
conclusions are carried forward as the verdict on this phase's report.

---

**HYPOTHESIS A — Trend continuation** — NOT RE-TESTED (Phase 1 `trend_persistence`,
Phase 3 momentum, Phase 4 multi-hour persistence).
Spec would be: prior-W move > median and hold H bars, same direction.
Carried verdict: REJECTED — continuation hit rates ~48–50%, forward means ≤ 0
after costs on M5 and 1h–24h; best momentum behavior only 0.35–0.66
movement-to-cost. Re-tested implicitly at higher TF by HYPOTHESIS H (alignment).

**HYPOTHESIS B — Trend pullbacks** — **NEW EXPERIMENT B-PB** (aligned,
two-timeframe pullback resumption).
- Working timeframe / hold: H1 bars; holds H = 12 and H = 24 (12h/24h).
- Entry (BUY only, same rule mirrored for SELL):
  1. H1 uptrend: `C_H1[t] > SMA24(C_H1)[t]`.
  2. Pullback within the last H1 bar: at least one M15 close inside bar t was
     `below SMA8(C_M15)` while M15 uptrend holds (`C_M15 > SMA24(C_M15)`).
  3. Resumption at decision time: the last M15 close of H1 bar t is `≥
     SMA8(C_M15)`.
  Direction: BUY. Symmetric mirror → SELL.
- Information available: closes of H1 bar t and all earlier bars; M15 closes up
  to the end of H1 bar t. Entry at open of H1 bar t+1.
- Failure: n < 1000 or screen 1–7 fail. Economic rationale: pullbacks in an
  established higher-TF trend are a classic continuation entry; H1 gives enough
  raw movement to plausibly clear costs (Phase 4 horizon ladder suggests the
  best raw ratios live at H1+).

**HYPOTHESIS C — Breakout continuation** — NOT RE-TESTED (Phases 3/4: 24h
channel and London-open overnight-range breaks; means negative after cost).
Spec would be: close beyond prior-k bar high/low, hold and continue.
Carried verdict: REJECTED on 1h–4h holds (means below cost). Partial re-check
indirectly inside HYPOTHESIS E (squeeze breakout uses a breakout entry).

**HYPOTHESIS D — Volatility expansion** — NOT RE-TESTED (Phases 3/4: entering
high ATR regime followed 2h/4h/8h; best 0.60 movement-to-cost).
Carried verdict: REJECTED as raw behavior (no directional follow-through).
Volatility is used as a **filter** in HYPOTHESIS J instead.

**HYPOTHESIS E — Volatility contraction followed by expansion** — **NEW
EXPERIMENT E-SQZ** (squeeze → breakout).
- Working timeframe / hold: H4 bars; holds H = 2 and H = 4 (8h/16h).
- Entry:
  1. Contraction: `ATR14_H4[t]` is in the LOW regime (`atr_regime` low) for the
     last K=4 consecutive H4 bars (16h squeezed).
  2. Expansion trigger: `C_H4[t]` breaks the max-high OR min-low of the prior
     K=4 H4 bars (excluding t), i.e. `C_H4[t] > max(H_H4[t-4:t])` →
     BUY-break, `C_H4[t] < min(L_H4[t-4:t])` → SELL-break.
  Direction: direction of the breakout.
- Information available: H4 bars up to and including t. Entry at open of t+1.
- Failure: n < 1000 or screen fail. Rationale: contracted volatility followed
  by a range breakout measures whether the "squeeze pop" directional move
  exists and survives cost; Phases 3/4 never combined contraction with a
  breakout entry, and H4 raw movement is largest in the ladder.

**HYPOTHESIS F — Mean reversion after extreme movement** — NOT RE-TESTED as a
standalone rule (Phase 1 = the strongest raw result, +0.2..+0.37 pips at H=20,
hit ~51–53%, but below the 2.3–3.5 pip costs). Re-tested inside HYPOTHESIS J
(regime-conditioned), which is the untested refinement.

**HYPOTHESIS G — Momentum following unusually large candles** — **NEW EXPERIMENT
G-CANDLE** (single-candle momentum; Phases 1/3 used window momentum, not
event candles).
- Working timeframe / hold: M15 bars; holds H = 4 and H = 12 (1h/3h).
- Entry: bar t has `|C_O|_body = |C_H4... |` i.e. `|C[t] − O[t]| ≥ 2.0 ×
  ATR14[t]` (an unusually large single-candle body). Direction = sign of the
  body (close > open → BUY, else SELL). Candle range condition (optional
  guard, pre-registered): exclude bars whose width `H[t]−L[t] > 5 × ATR14[t]`
  (data spikes).
- Information available: bar t and earlier. Entry at open of t+1.
- Failure: n < 1000 or screen fail. Rationale: large informational candles can
  be followed by short-term momentum; M15 gives enough events and the 1h/3h
  holds are cost-plausible on liquid majors.

**HYPOTHESIS H — Multi-timeframe directional alignment** — **NEW EXPERIMENT
H-ALIGN** (genuinely untested dimension).
- Working timeframe / hold: H4 bars; holds H = 2 and H = 6 (8h/24h).
- Entry: fast and slow frames agree —
  `sign(C_H1 − SMA8(C_H1)) == sign(C_H4 − SMA24(C_H4))` at the timestamp of the
  last H1 bar inside H4 bar t; both non-zero. Direction = that common sign.
- Information available: H1 closes up to the end of H4 bar t; H4 closes up to t.
  Entry at open of H4 bar t+1. (Alignment is constructed on bars built from the
  same M5 source — no extra data.)
- Failure: n < 1000 or screen fail. Rationale: confluence of a short and a long
  timeframe trend is a widely cited FX behavior; at H4 scale the raw movement is
  largest, giving the clearest cost-outcome test. Nothing in Phases 1/3/4
  measured cross-timeframe agreement.

**HYPOTHESIS I — Session / time-of-day effects** — NOT RE-TESTED (Phase 1
`sessions`, Phase 3 sessions, Phase 4 session opens: London/LondonNY/NewYork
drift below cost). Carried verdict: REJECTED as a standalone entry. Session is
used only as metadata in yearly/regime bucketing, not as an entry filter.

**HYPOTHESIS J — Regime-dependent behavior** — **NEW EXPERIMENT J-FADE-REGIME**
(mean reversion conditioned on volatility regime; the F × J refinement).
- Working timeframe / hold: H1 bars; holds H = 4 and H = 12 (4h/12h).
- Entry:
  1. Extreme deviation: `z[t] = (C[t] − SMA20(C)[t]) / ATR14[t]`. `z ≤ −1.0` →
     BUY (fade under), `z ≥ +1.0` → SELL (fade over).
  2. Regime gate: `ATR14[t]` in the LOW regime of `atr_regime(ATR14, 50)`.
- Information available: H1 bars up to t. Entry at open of t+1.
- Failure: n < 1000 or screen fail. Rationale: fading extremes should do better
  when volatility is low (range-bound microstructure); this tests whether the
  Phase-1 fade-the-extreme evidence strengthens enough to clear costs once the
  regime is restricted, without searching for the "best" regime threshold
  (0.33/0.67 is the frozen research convention).

---

## PART D — METRICS COMPUTED FOR EVERY EXPERIMENT

For every (experiment, symbol, hold) with n ≥ 1000 we report:

- number of trades (events), win rate, average win, average loss
- expectancy per trade (pips, net of cost), profit factor
- total net pips, total net (normalized $, $1/pip at 0.10 lot / $10 per
  pip-lot), gross profit/loss pips
- max drawdown (peak-to-trough on the sequential net-pips curve), trade
  duration (bars and hours), exposure (sum of holding bars / total bars)
- commission: 0 (no commission modelled in discovery; engine's $7/lot is an
  execution-assumption item, documented, not applied here)
- spread/slippage cost: per-trade mean and total (observed spread entry+exit +
  slip)
- yearly and monthly breakdown where n permits
- long vs short performance
- performance across volatility-regime buckets (low/normal/high ATR at entry)

Nothing is ranked by raw profit alone; the pre-registered screen (PART B) is the
only ranking.

---

## PART E — REPORT STRUCTURE (fixed)

`EDGE_DISCOVERY_RESULTS.md` must contain exactly these sections:

1. Method summary + integrity statements (DEV-only, no holdout read, files
   touched).
2. Pre-registered screen restated (so the verdicts are self-contained).
3. Per-experiment tables (metrics of PART D) for every rule that cleared n ≥
   1000 on at least one symbol.
4. Verdicts bucketed as:
   - **DISCOVERED** — rules clearing the full viability screen (report exact
     rule, DEV numbers, robustness notes, weaknesses, proposed next validation
     step; then STOP — do not optimize).
   - **REJECTED** — rules failing the screen, with the specific failing
     criterion.
   - **UNRESOLVED** — hypotheses that need more/better data (e.g., rely on the
     EURJPY clean history or broker-true specs).
   - **NOT TESTED** — anything intentionally excluded (EURJPY, volume,
     session-only entries, broker universe without local data).
5. Full machine-readable dump: `outputs/edge_discovery_results.json`.

---

## PART F — DELIVERABLES / EXECUTION ORDER

1. `EDGE_DISCOVERY_PLAN.md` (this file, written before results).
2. `backtest/market_research/edge_discovery.py` — reproducible runner.
3. `tests/test_edge_discovery.py` — split-isolation, causal-feature, next-open
   execution, cost accounting, metric coverage, no-lookahead.
4. Run on DEV for EURUSD / EURGBP / GBPUSD.
5. `EDGE_DISCOVERY_RESULTS.md` + `outputs/edge_discovery_results.json`.
6. Verify: no VALIDATION/HOLDOUT read, no strategy/backtester/bot.py change,
   full test suite still green.

STOP CONDITION (from TASK.md): if any rule clears the screen, do not optimize
it, do not re-test with different parameters, do not read holdout. Report it.