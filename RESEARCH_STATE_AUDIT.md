# Research State Audit

**Date:** 2026-09-23
**Scope:** Read-only reconstruction of the trading-research state of this repository. No code, data, strategy, or parameter changes were made. No backtests were run. No validation/holdout data was read. All conclusions are traced to source code and machine-readable outputs; `PROJECT_RESEARCH_HANDOFF.md` is treated as **unreliable** (proven fabricated — see §10).

---

## 1. Executive Summary

The repository has performed **six numbered research phases plus the new pre-registered EDGE DISCOVERY round**. The consistent, data-backed conclusion across every phase is:

> **No market behavior has yet produced raw forward movement large enough to clear observed spread + slippage costs on the clean 5-year DEV data of any of the three clean pairs (EURUSD / EURGBP / GBPUSD).**

- Best movement-to-cost ever recorded: **0.734** (EURUSD, multi-hour mean reversion after an 8h up-move, `outputs/multi_hour_research.json`) and **0.660** (EURUSD session behavior, `outputs/edge_research.json`). The tradeable threshold is ≥ 1.0; nothing has reached it.
- All full strategies (V1, V2, Strategies 01–03, Phase-5 MR/BF) are **negative after costs** on DEV and are frozen/rejected.
- The latest pre-registered round (EDGE DISCOVERY) tested 5 hypotheses × 2 horizons × 3 symbols on M15/H1/H4. **None cleared the pre-registered screen.** One rule (GBPUSD fade-extremes-gated-to-low-ATR, H1, 12h hold) reached movement-to-cost 1.17 with +0.61 pips net but failed significance (t = 0.67, p = 0.50) and concentration tests → REJECTED.
- Two hypotheses are **UNRESOLVED** purely from low event counts (squeeze-breakout max n = 388; large-candle momentum max n = 921, both below the pre-registered n ≥ 1000), not from evidence of edge.
- Research pipeline is now **hygienic**: DEV-only loading, closed-candle signals, next-open fills, real observed spreads, pre-registration, and a 124-test regression suite. Historical phases 5/6 are **invalidated** (see §10).
- The behavioral map (§4, §8) shows the genuinely untested frontier: **market-structure behavior** (swing structure, break/reject of structure, failed breakouts, rejection/wick candles), **calendar microstructure** (day-of-week, session transitions, overnight/weekend gaps), **volatility-regime dynamics as an event** (persistence, shocks), **gap/spread-shock context**, and — the single largest gap — **cross-pair / relative-strength behavior across the EURUSD/EURGBP/GBPUSD triangle**.

**Readiness for demo:** execution pipeline is engineering-ready; **no strategy is evidence-backed for trading**. Demo may run V1 only as an execution test, never as a validated edge.

---

## 2. Repository Evidence

Files inspected and what each contributed:

| File | Contribution |
|---|---|
| `TASK.md` | Brief governing this audit (read-only, pre-registration, DEV-only, stop-condition). |
| `EDGE_DISCOVERY_PLAN.md` | The latest pre-registered experiment definitions, viability screen, integrity rules. |
| `EDGE_DISCOVERY_RESULTS.md` + `outputs/edge_discovery_results.json` | Verdicts for B-PB, E-SQZ, G-CANDLE, H-ALIGN, J-FADE-REGIME. |
| `backtest/market_research/market_discovery.py` | Phase 1 raw directional power (7 studies × 4 pairs, M5). |
| `backtest/market_research/edge_research.py` | Phase 3 edge search (183 behaviors) → `outputs/edge_research.json`. |
| `backtest/market_research/multi_hour_research.py` | Phase 4 multi-hour (84 behaviors) → `outputs/multi_hour_research.json`. |
| `backtest/market_research/phase5_research.py` | Phase 5 code (never executed — no output artifacts exist). |
| `backtest/market_research/phase6.py` | Phase 6 studies (ran on full data; invalidated, `phase6.py:50-55`). |
| `backtest/market_research/edge_discovery.py` | The current reproducible experiment runner + screen + report writer. |
| `backtest/market_research/common.py` | ATR regime, session labels, `test_mean_nonzero` used consistently. |
| `backtest/strategies/strategy_01/02/03_*.py` | Phase 2 strategy implementations (S01 fade, S02 breakout-fade, S03 session-gated fade). |
| `backtest/strategies/{mean_reversion,breakout_fade,benchmark}.py` | Phase 5 benchmark candidates + `outputs/benchmark/results.json`. |
| `backtest/strategy.py`, `strategy_v2.py` | V1 and V2 signal definitions. |
| `backtest/backtester.py`, `config.py`, `metrics.py`, `instruments.py` | Engine mechanics, cost model, fixed/risk-fraction sizing, per-symbol pip/point. |
| `data/*_m5.csv` + `outputs/splits/*/metadata.json` | Canonical data (3 clean pairs) and official 60/20/20 split boundaries. |
| `outputs/<sym>/reports/data_validation_report.md` | Measured defect stats (zero-spread, gaps, flat bars). |
| `CURRENT_PROJECT_STATE_AUDIT.md` | The engine/issue register (E1–E9), strategy inventory, data audit, evidence table. |
| `PRE_DEMO_REMEDIATION_REPORT.md`, `RESEARCH_REMEDIATION_PLAN.md`, `TRADING_REPO_COMPARISON.md` | Recent engineering remediation (A3 closed-candle timing, A5 sizing parity, venv hygiene). |
| `PHASE6_5_RESEARCH_INTEGRITY_AUDIT.md`, `HISTORICAL_OUTPUTS_STATUS.md` | Authoritative critiques/invalidation registry of phases 5–6. |
| `MARKET_BEHAVIOR_DISCOVERY.md`, `MARKET_RESEARCH_REPORT.md`, `BACKTEST.md` | Phase 1 report + consolidated Ph1–4 + engine docs. |
| `PROJECT_RESEARCH_HANDOFF.md` | **UNRELIABLE** — fabricated Phase 5/6 numbers; used only to flag. |
| `tests/*` | 124 passing regression tests (closed-candle, sizing parity, edge-discovery integrity). |

---

## 3. Chronological Experiment History

All meaningful experiments, oldest → newest. Split discipline and cost model are noted per row; "cost model" names: **E** = engine spread + 0.5 pip/side + $7/lot; **RS** = observed entry+exit spread + slippage; **M+1.7** = 2×median spread + 1.7 pips; **C** = flat-cost constant.

| # | Phase | Experiment | Behavior | TF | Horizons | Symbols | Type | Split | Cost | Result | Classification | Reason | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Pre-1 | 7-study research (old 90k MT5 EURUSD) | assorted (MR, momentum, session…) | M5 | 5–80 bar | EURUSD | event/continuous | none (old data) | C | M5 mean-reverting tendency | INVALID | old 90k degraded feed replaced | `backtest/market_research/run_all.py` |
| 2 | 0/0B | Data acquisition + integrity audits | — | M5 | — | all | — | — | — | clean 3-pair Dukascopy composites | DONE | — | `PHASE0*`, `PHASE0B*` |
| 3 | 1 | Raw directional power (7 studies) | trend, breakout, fade, mean-rev, momentum, session, vol-regime | M5 | 5/20/40/80 | EURUSD/EURGBP/GBPUSD/JPY | event | DEV (old) | RS | naive trend/breakout → negative; fade-the-extreme → positive raw but < cost | REJECTED (except fade=UNRESOLVED cost) | not an edge after costs | `market_discovery.py`, `MARKET_BEHAVIOR_DISCOVERY.md` |
| 4 | 2 | Strategy 01 extreme fade | mean reversion (dist from SMA20) | M5 | 40-bar hold + 1 ATR stop | 3 clean | signal-gated | DEV (old) | 2×spread+1.7 | net −2.2..−4.2 pips/trade | REJECTED | costs exceed fade mean | `strategy_01_extreme_fade.py`, report |
| 5 | 2 | Strategy 02 breakout fade (London session) | breakout fade | M5 | 20-bar hold, engine SL/TP | EURGBP/GBPUSD | signal-gated | DEV (old) | E | negative; acceptance not met | REJECTED | — | `strategy_02_breakout_fade.py` |
| 6 | 2 | Strategy 03 session-gated fade | mean reversion + session | M5 | 40-bar hold + 1 ATR stop | 3 clean | signal-gated | DEV (old) | 2×spread+1.7 | gate adds +93.6k pips vs S01 but still < cost | REJECTED | conditioning helps; not enough | `strategy_03_*.py` |
| 7 | — | EMA-separation filter experiment | trend filter | M5 | engine | EURUSD | filter | full (old) | E | flat WR ~31.5% / PF ~0.56 | REJECTED | hypothesis falsified | `experiment.py`, `BACKTEST.md` |
| 8 | 3 | Edge search (183 behaviors) | 8 behavior families on DEV | M5 | 5/20/80/120/240 bar | 3 clean | event | DEV (new data) | RS | best movement-to-cost **0.66** (EURUSD session, H=80) | REJECTED | none ≥ 1.0 | `edge_research.py`, `outputs/edge_research.json` |
| 9 | 4 | Multi-hour research (84 behaviors) | reversal, breakout_24h, session windows, vol-expansion | H1/H4 | 1–24h | EURUSD/EURGBP/GBPUSD | event | DEV | RS | best **0.734** (EURUSD 8h reversal) | REJECTED | none ≥ 1.0 | `multi_hour_research.py`, `outputs/multi_hour_research.json` |
| 10 | 5 | Broker-data + benchmark (V1/MR/BF × 4 symbols × 3 splits) | continuation / MR / breakout-fade | M5 | engine SL/TP | 4 incl. EURJPY | strategy | dev/val/holdout | E(typo) | all clean-pair cells negative; EURJPY impossible (+2199%/−931%) | **INVALIDATED** | split-assignment bug + EURJPY pip bug + fabrications | `strategies/benchmark.py`, `outputs/benchmark/results.json`, `PHASE6_5_*` |
| 11 | 5 | `phase5_research.py` market-expansion study | would add broker/session behaviors | M5–H4 | — | 3 clean | event | DEV | RS | **never executed** — no output artifacts | NOT TESTED | code exists; no outputs in repo | `phase5_research.py` (absent `PHASE_5_*` / `outputs/phase_5_market_research.json`) |
| 12 | 6 | 7 studies × 4 symbols (retest after data migration) | assorted | M5 | — | 4 | event | **full data** | RS | dumped per study | **INVALIDATED** | full-data read → holdout destroyed (`phase6.py:50-55`) | `phase6.py`, `outputs/phase6/*` |
| 13 | EDG | **B-PB** aligned two-TF pullback resumption | trend pullback (H1 trend + M15) | H1 + M15 | 12/24h | 3 clean | event | DEV | RS (+1 pip) | m2c 0.12–0.39, all INSUFF | REJECTED | movement << cost | `edge_discovery.py:222-247` |
| 14 | EDG | **E-SQZ** low-ATR squeeze → breakout | vol contraction + expansion | H4 | 8/16h | 3 clean | event | DEV | RS (+1 pip) | m2c 0.37–2.78 but max n = 388 | UNRESOLVED | n < 1000 (event too rare) | `edge_discovery.py:250-269` |
| 15 | EDG | **G-CANDLE** large-body candle momentum | candle/event momentum | M15 | 1/3h | 3 clean | event | DEV | RS (+1 pip) | max n = 921 | UNRESOLVED | n < 1000 | `edge_discovery.py:272-282` |
| 16 | EDG | **H-ALIGN** H1/H4 trend-sign confluence | multi-TF alignment | H4 + H1 | 8/24h | 3 clean | event | DEV | RS (+1 pip) | m2c 0.26–0.95, INSUFF/BORDER | REJECTED | movement << cost | `edge_discovery.py:285-306` |
| 17 | EDG | **J-FADE-REGIME** fade extremes in low-ATR regime | regime-conditioned mean reversion | H1 | 4/12h | 3 clean | event | DEV | RS (+1 pip) | GBPUSD H=12: raw +4.14, **net +0.61**, m2c 1.17, p=0.50; others INSUFF/BORDER | REJECTED | not significant; year/window concentration | `edge_discovery.py:309-321` |

**Not-a-believer check (TASK."do not infer different because differently named"):** V1 trend+RSI vs Phase-3 momentum vs B-PB/H-ALIGN are different rule families of the **same underlying "trend continuation" dimension**; S01/S03/J are different gates over the **same "fade price extremes" dimension**; S02/BF/E-SQZ are three formulations of **breakout** (fade, channel-follow, squeeze-continuation). These are treated as one dimension each in §4/§5.

---

## 4. Behavioral Dimension Matrix

| Dimension | Tested? | Exhausted? | Status | Evidence |
| --- | --- | --- | --- | --- |
| Trend continuation (indicator-based) | Yes (V1, V2, Ph1/3 momentum, B-PB, H-ALIGN) | Effectively (5+ formulations, all negative) | TESTED-BUT-NOT-EXHAUSTED | V1 −93%, B-PB m2c ≤ 0.39, H-ALIGN m2c ≤ 0.95 |
| Trend pullback/resumption | Yes (V2 M5; B-PB H1/M15) | Effectively (2 formulations, both negative) | TESTED-BUT-NOT-EXHAUSTED | V2 rejected; B-PB INSUFF |
| Trend reversal / exhaustion | No | — | **UNTESTED** | no structural-exhaustion test in repo (only price-extreme fade, different mechanism) |
| Trend acceleration/deceleration | No | — | **UNTESTED** | no slope-of-slope study |
| Multi-TF trend alignment | Yes (H-ALIGN) | No (1 formulation only) | TESTED-BUT-NOT-EXHAUSTED | H-ALIGN INSUFF/BORDER |
| Multi-TF disagreement / transition | No | — | **UNTESTED** | only *agreement* tested |
| Unconditional mean reversion | Yes (Ph1 fade, Ph3 mean_revision, Ph4 8h reversal best 0.734, S01, Ph5 MR) | Yes (many formulations, consistently < 1.0) | **EXHAUSTED** | best ever 0.734 < 1.0 |
| Extreme-price fade | Yes (S01, S03, Ph1, J-FADE-REGIME) | Effectively (4 gates, all negative) | TESTED-BUT-NOT-EXHAUSTED | J GBPUSD m2c 1.17 but p=0.50 |
| Regime/vol-conditioned mean reversion | Yes (J-FADE-REGIME low-ATR gate only) | No (one gate tested) | TESTED-BUT-NOT-EXHAUSTED | J rejected; other gates untested |
| Distance-from-equilibrium | Yes (S01/S03 dist-SMA20) | Effectively | TESTED-BUT-NOT-EXHAUSTED | negative after costs |
| Short-term momentum (window) | Yes (Ph1/3 momentum) | Effectively | TESTED-BUT-NOT-EXHAUSTED | weak/negative |
| Large-candle continuation | Yes (G-CANDLE) | No (1 formulation) | **UNRESOLVED** | n max 921 < 1000 |
| Breakout continuation | Yes (Ph4 breakout_24h best 0.66; E-SQZ; Ph3 breakout) | No (3 formulations; E-SQZ under-powered) | TESTED-BUT-NOT-EXHAUSTED | best 0.66 < 1.0 |
| Volatility contraction / expansion | Yes (E-SQZ, Ph3/4 vol tables) | No | TESTED-BUT-NOT-EXHAUSTED (E-SQZ UNRESOLVED) | vol best 0.60; E-SQZ n<1000 |
| Volatility-regime **persistence / shock / mean-reversion** (as a tradable event) | No | — | **UNTESTED** | ATR regime used only as a *gate* |
| Swing highs/lows (pivot structure) | No | — | **UNTESTED** | no swing-point code anywhere |
| Break of structure / failed breakout | No | — | **UNTESTED** | only window-channel breaks (S02/BF/E) |
| Range-boundary rejection (inside range) | No | — | **UNTESTED** | only *outside*-break fades tested |
| Support/resistance behavior | No | — | **UNTESTED** | — |
| Rejection / wick behavior (pin bars, body/wick) | No | — | **UNTESTED** | G-CANDLE used *body size*, not wick rejection |
| Hour-of-day / session (static) | Yes (Ph3 session best 0.66; S02/S03 gates; Ph4 session windows) | Effectively at M5 | TESTED-BUT-NOT-EXHAUSTED | best 0.66 < 1.0 |
| Session **transitions** / overlap phase | No | — | **UNTESTED** | sessions only used as static membership |
| Day-of-week | No | — | **UNTESTED** | — |
| Overnight behavior / large gap | No | — | **UNTESTED** | weekend/overnight gaps exist in data, unused |
| Weekend effects | No | — | **UNTESTED** | — |
| Month/quarter effects | No | — | **UNTESTED** | — |
| Cross-TF: lower-TF impulse in higher-TF range | No | — | **UNTESTED** | range frame + fast impulse never combined |
| Cross-TF: higher-TF trend + lower-TF reversal | No | — | **UNTESTED** | only same-direction tested |
| Cross-pair relative strength / divergence | No | — | **UNTESTED (largest gap)** | zero cross-pair research modules; 3 clean synchronized pairs available |
| Cross-pair lead/lag, confirmation | No | — | **UNTESTED** | — |
| News / economic events | No | — | **INVALID/UNAVAILABLE** | no news data; external data acquisition forbidden |
| Large-gap / spread-shock context | No | — | **UNTESTED** | real observed `spread` column unused as an event |
| Unusual consecutive returns / runs | Partially (Ph1 momentum/persistence) | — | TESTED-BUT-NOT-EXHAUSTED | run-length formalization untested |
| Regime transitions (as context) | No | — | **UNTESTED** | — |

---

## 5. Redundant / Overlapping Research

| Overlap group | Members | Shared underlying dimension | Genuinely different axis | New information if re-tested? |
| --- | --- | --- | --- | --- |
| Fade-the-extreme family | S01 (M5), S03 (M5+session), J-FADE-REGIME (H1+low-ATR), Ph1 fade-the-extreme | Mean reversion at price extremes | Gating dimension (none / session / ATR-regime), timeframe | **Low** — the core mechanism is tested 4×; only genuinely *new* gates (structure, calendar) add information |
| Breakout family | S02 (fade, session), BF (channel-follow), E-SQZ (squeeze-continuation), Ph4 breakout_24h, Ph3 breakout | Price breaks a recent range | Fade vs follow vs squeeze timing, horizon | **Low-Med** — E-SQZ was under-powered (n<1000), the only open case |
| Trend-continuation family | V1 (EMA+RSI), V2 (pullback), B-PB, H-ALIGN | Follow an established trend | Indicator vs price vs multi-TF definition | **Low** — 5 formulations all negative |
| Momentum family | Ph1/3 momentum (window), G-CANDLE (event) | Continuation after directional impulse | Window vs single-candle event | **Low** (G-CANDLE n<1000, but event formulation is the new axis) |
| Squeeze vs volatility expansion | E-SQZ, Ph3/4 vol tables | Volatility dynamics | Contraction+breakout vs bare expansion | **Med** (E-SQZ unresolved by count, not by result) |
| Session studies | Ph3 session (best 0.66), S02/S03 gates, Ph4 session windows | Time-of-day conditioning | Static membership vs transitions | **Low** for static; **Med** for the untested *transitional* sub-dimension |
| Multi-TF | H-ALIGN (agreement), B-PB (pullback) | Cross-timeframe information | Same-direction only | **Med** for untested *disagreement/transition* variants |

**Bottom line:** the unconditional mean-reversion and standard trend/momentum families are close to exhausted. Re-testing them should require a genuinely different conditioning dimension, not a parameter tweak.

---

## 6. Confirmed Rejections

Do not revisit unless a genuinely new hypothesis is introduced:

1. **Standard EMA/RSI trend continuation (V1)** — −93.1% full-data, negative on every clean pair/split in Phase 5; frozen as the live-exercise rule only.
2. **V2 trend-pullback** — predictive power ≤ V1; "rejected in Phases 1–4".
3. **Unconditional extreme-price fade (S01, S03)** — negative after costs on all 3 pairs; session gate improves but does not clear cost.
4. **Breakout-fade, channel-based (S02, Phase-5 BF)** — negative after costs; pre-registered acceptance not met.
5. **Phase-5 mean-reversion candidate (MR)** — negative on all non-broken cells.
6. **EMA-separation filter** — falsified (flat WR/PF).
7. **Indicator-based trend/momentum edge search (Ph3/4)** — best 0.66/0.734; nothing ≥ 1.0.
8. **B-PB, H-ALIGN, J-FADE-REGIME** — rejected by the pre-registered screen.
9. **Phase 5/6 results as evidence** — invalidated entirely (see §10); raw `results.json` only documents what ran.

---

## 7. Unresolved Experiments

Per rule, these are **not** silently upgraded:

| Experiment | Why unresolved | What would resolve it |
| --- | --- | --- |
| **E-SQZ** (squeeze→breakout, H4) | Max n = 388 (range: 358–388) across holds/symbols; pre-registered n ≥ 1000 not reached. Direction is a *data-limitation* result, not an edge result. (Note GBPUSD H4 m2c = 2.02–2.78 but n = 359 — interesting but statistically starved.) | Clean history ≥ 2× longer, or a permissive-but-still-causal squeeze definition that reaches n ≥ 1000 (must be re-pre-registered) |
| **G-CANDLE** (large-candle momentum, M15) | Max n = 921 (< 1000) | Longer M15 history, or a looser pre-registered "large-candle" definition |
| **Unconditional fade-the-extreme** (from Phase 1) | Positive raw means at M5 but below the cost threshold with the then-unavailable clean spread data | Re-measure on the clean 3-pair DEV with the RS cost model (a *measurement*, not an edge claim) |

---

## 8. Untested Behavioral Dimensions

Genuinely untested families (see §4 matrix for the full list and evidence):

1. **Market structure / price structure** — swing highs/lows, break of structure, failed breakout, range-boundary rejection, support/resistance, **rejection/wick candles** (body/wick-length structure). The repo has used indicator windows (EMA/SMA/ATR/channel) but **never geometric price structure**.
2. **Cross-pair / relative behavior** — relative strength between EURUSD and GBPUSD (i.e., implicit EURGBP cross), correlated-pair divergence, cross-pair confirmation. Nothing in the repo reads more than one symbol per experiment.
3. **Calendar microstructure** — day-of-week, session **transitions**, overlap-phase dynamics, weekend effects, month/quarter effects.
4. **Overnight / gap behavior** — size of the weekly/overnight period open gap vs. post-gap continuation/reversal.
5. **Volatility-regime dynamics as an event** — regime persistence (does a low/high ATR regime continue?), volatility shocks (single-bar ATR jumps), volatility-of-volatility.
6. **Gap / spread-shock context** — using the real observed `spread` column as an event context (spread expansion into decision points).
7. **Trend exhaustion / acceleration** and **multi-TF disagreement** (higher-TF trend vs. lower-TF reversal; lower-TF impulse inside higher-TF range).
8. **News / fundamentals** — unavailable (see §9); classified INVALID, not merely untested.

---

## 9. Data Feasibility

Current DEV dataset (3 clean pairs) capability for each untested dimension:

| Dimension | Date range/symbols | Granularity | Spread data | Event count outlook | Feasible on current DEV? |
| --- | --- | --- | --- | --- | --- |
| Market structure (wick/rejection, BoS, failed breakout, swing points) | 2021-01-03→2026-09-09, 3 pairs | M5 → any TF | yes (real) | abundant (thousands of candles per TF) | **Yes** — fully causal at H1/H4; M5 events frequent |
| Cross-pair relative behavior | 3 pairs, synchronized minutes | M5 → H1 compatible | yes | hundreds of daily H1 bars × <5.7y | **Yes** — requires closed-candle cross-pair synchronization (both symbols' closed bar at the same UTC wall-time); no new data |
| Calendar microstructure (day-of-week, transitions) | full 5.7y | M5→H4 | yes | high | **Yes** | 
| Overnight/weekend gap behavior | full 5.7y (weekend gaps present) | M5 open | yes | ~296 weeks → ~300 gap events | **Borderline** event count; ~300–600 events is testable but below the 1000 comfort level for the existing screen |
| Volatility-regime dynamics | full | H1/H4 | yes | ATR regimes persist for long stretches → continuous-style condition, high n | **Yes** |
| Spread-shock context | full, real spread | M5 | yes (this is the point) | high | **Yes** — spread is a free, real, unused column |
| Trend acceleration/exhaustion, multi-TF disagreement | full | H1/H4 | yes | enough | **Yes** |
| News / fundamentals | none locally; external acquisition prohibited | — | — | — | **No — INVALID** under current rules |

Notes: EURJPY excluded (27% zero-spread, 14 months, single regime, old feed). `real_volume` is all zeros — **volume research is INVALID** until real volume exists. H4 aggregation is valid (UTC floor, no lookahead, verified by tests).

---

## 10. Research-Integrity Findings

Findings from code + endpoints, each with evidence. None were modified.

| ID | Finding | Severity | Evidence |
| --- | --- | --- | --- |
| J1 | **`PROJECT_RESEARCH_HANDOFF.md` is fabricated.** Phase-5 tables have a Sharpe column `outputs/benchmark/results.json` does not even contain; every audited claim differs from actuals (e.g., EURUSD V1 dev " +2.05%" vs actual **−62.91%**; "343 trades" vs 2,578). No Phase-5 artifact exists to corroborate (`outputs/phase_5_market_research.json` and `PHASE_5_*` are absent). | HIGH — treat handoff as untrustworthy | `PHASE6_5_RESEARCH_INTEGRITY_AUDIT.md`; benchmark JSON absent outputs |
| J2 | **Phase 6 read full data** — `phase6.py:50-55` loads entire CSVs with no split filter → validation/holdout rows were consumed; the holdout is destroyed for all 28 hypotheses. | HIGH | `phase6.py` |
| J3 | **`predictive.py:249-255`, `predictive_v2.py:296-304`** read the full data file (no DEV filter) — any predictive-power claim leaks holdout-window rows. | HIGH (if results relied on) | `predictive*.py` |
| J4 | **Benchmark split bug:** `benchmark.py` consumes stale 90,000-row report files (`outputs/<sym>/reports/data_split_assignments.csv`) instead of `outputs/splits/<SYM>/assignments.csv`, so the Phase-5 benchmark "dev/val/holdout" windows were the *first* 90k rows (early-2021), not the official splits. | HIGH | `benchmark.py` vs splits metadata |
| J5 | **EURJPY scaling bug:** benchmark constructs a single `CostConfig()` (EURUSD pip=0.0001/point=1e-5) for every symbol, ignoring `instruments.py` (EURJPY pip=0.01/point=0.001) → EURJPY dev V1 "−931%", MR "+2199%" are 100× artifacts. | HIGH (invalidates those cells) | `benchmark.py:81`, `instruments.py` |
| J6 | **A3 closed-candle timing divergence** — live `bot.py` previously signaled on the forming candle and filled in-bar. Fixed to closed-candle/next-open in the uncommitted remediation. | RESOLVED | `PRE_DEMO_REMEDIATION_REPORT.md` |
| J7 | **E1 mild geometry lookahead (open):** SL/TP ATR taken from the *entry* bar `i` at its open (`backtester.py:263`), incorporating bar `i` high/low/close — affects risk geometry only, not entry direction. Deferred. | LOW-OPEN | `backtester.py`, state-audit E1 |
| J8 | **Cost conventions are three, not one** (engine; real-spread+slip; flat). Each module declares its own; any comparison of numbers across modules without restating cost model is apples-to-oranges. | MED | config vs S01/S03 vs edge_discovery |
| J9 | **Multiple-testing exposure** — Ph3 (183) and Ph4 (84) scanned many behaviors; "best of" values (0.66/0.734) are optimism-inflated. Mitigated going forward by pre-registration + fixed screen. | MED | edge_research/multi_hour JSONs |
| J10 | **Stale 90k artifacts remain** under `outputs/*/reports/` and can be misread as canonical splits; canonical source is `outputs/splits/<SYM>/assignments.csv`. | MED | splits vs reports tree |
| J11 | EURJPY (27–46% zero-spread, old feed) must stay excluded; `real_volume` all zeros → volume metrics must not be used. | MED | data audits |

---

## 11. Research Frontier

Remaining conceptual directions (no parameters, no code). For each: hypothesis, novelty, required data, event-count concern, leakage risk, pre-registration cleanliness.

1. **Market-structure rejection / failed-break behavior**
   - Hypothesis: after a price break of a geometrically-defined swing extreme or range, the *failure of that break to sustain* (reclaim/reject within a structure window) carries directional information.
   - Novelty: only indicator-over-window breaks were tested; geometric structure and *failure* of breaks are untested.
   - Data: current 3-pair DEV; M5→H1/H4.
   - Event count: high (H1 breaks are frequent); feasibility good.
   - Leakage risk: break/failure windows must be trailing (closed candles only); no next-bar silhouette.
   - Pre-registration: clean — all structure windows can be frozen.
2. **Cross-pair relative-strength / divergence (EURUSD vs GBPUSD, EURGBP cross)**
   - Hypothesis: relative divergence between the two USD pairs (i.e., EURGBP is the synthesized gauge) conditions the direction of either leg.
   - Novelty: **nothing in the repo reads two symbols together**; this is a genuinely different information source.
   - Data: current 3 pairs (synchronizable on closed M5/H1 bars); no new data.
   - Event count: H1/day-level, hundreds of episodes over 5.7y; acceptable.
   - Leakage risk: must align only *closed* bars on the same UTC wall-time for both legs (no future bar from either symbol).
   - Pre-registration: clean.
3. **Calendar microstructure — session transitions and day-of-week**
   - Novelty: only static session *membership* was tested; *transitions* (e.g., London close → New York open) and weekday effects are untested.
   - Data: current; event count high. Leakage: none beyond closed-candle discipline. Pre-registration: clean.
4. **Overnight/weekend gap behavior**
   - Hypothesis: does the magnitude of the market-open gap predict short-horizon gap-fill vs gap-continuation?
   - Data: current; ~296 weekly opens plus daily overnight opens. Event count borderline for the n≥1000 screen (can raise to hour-of-day aggregations).
   - Leakage risk: re-open bar must be excluded from any feature; cleanly pre-registrable.
5. **Volatility-regime dynamics as an event (persistence, shocks, vol-of-vol)**
   - Novelty: ATR regime was only a *gate* (J). Volatility’s own persistence/mean-reversion is untested as a tradable condition.
   - Data: current; high event count; leakage low; pre-registration clean.
6. **Trend exhaustion / acceleration and multi-TF disagreement**
   - Novelty: only agreement was tested (H-ALIGN); the *disagreement* and *exhaustion* cases are untested.

---

## 12. Recommended NEXT AUDIT/RESEARCH TASK

*(One conceptual task, no strategy, no parameters — per instructions.)*

> **Investigate whether cross-pair relative-strength / divergence behavior exists between the EURUSD, GBPUSD, and EURGBP legs at the H1 timeframe, under a pre-registered closed-candle synchronized condition — i.e., whether the relative performance of one leg against the cross-gauge carries directional information that single-symbol behavior does not.**

**Why it is genuinely different from everything already tested** (§4/§5/§8 evidence):
- Every prior experiment is **single-symbol-unilateral**: signal + forward return on one pair in isolation. V1/V2, S01–S03, Ph1/3/4, and EDGE DISCOVERY never join two symbols.
- The dataset *already includes* three clean, synchronized pairs for 5.7 years with real spreads — the one case where an untested dimension is also data-complete (no acquisition, no volume, no EURJPY dependencies).
- It does not re-test mean reversion, momentum, or trend on a price series; it tests a **relational** property (co-movement, divergence, relative strength) that cannot be observed from any single time series, so the "same-idea-wrapped-differently" objection to redundant research does not apply.
- It is directly usable in a EURUSD-only live bot as a *confirmation/context* filter, so a result transfers to the deployed instrument without retrading a basket.

*Named equally strong but not selected as THE next task:* price-structure rejection/failed-breakout behavior (§11.1) and overnight-gap behavior (§11.4) are both feasible, cleanly pre-registrable, and genuinely untested; they can be sequenced after the cross-pair question.

---

## 13. Explicit Stop Condition

**No strategy shall be implemented or promoted — including for MT5 demo — until a future pre-registered DEV experiment clears the existing viability screen** (n ≥ 1000; movement-to-cost ≥ 1.0 with |raw mean| ≥ 2 pips; net significantly positive, t p < 0.05; positive on ≥ 2 of 3 symbols; ≥ 60% of years positive; no single year > 50% or 4-week window > 40% of total net). No such result currently exists in the repository, so the stop condition remains in force. As of this audit the only allowed demo usage of V1 is as an **execution/pipeline test**, not as a validated edge.