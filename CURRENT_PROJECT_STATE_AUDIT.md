# CURRENT PROJECT STATE AUDIT

**Date:** 2026-09-23
**Type:** READ-ONLY forensic audit (no source, strategy, data, test, or bot changes; no backtests run; no MT5 orders; no holdout analysis)
**Repo:** `C:\Users\ADMIN\Documents\REX\BOT\Trade-Bot`
**Reference repo:** `C:\Users\ADMIN\Documents\REX\CLONED\algorithmic-tradingUR2023I` — exists; used only as background for `TRADING_REPO_COMPARISON.md`, not re-audited line-by-line here.

---

## 1. Executive summary

This repository is a **research-first MT5 EURUSD M5 bot** with a solid, mostly-correct bar-by-bar backtest engine, a large body of completed research, and a **frozen live bot** (`bot.py`). The dominant fact about the project right now is:

**No economically validated strategy exists. Every tested strategy and every cost-aware backtest in the repo is negative after costs. Historical Phase 5/6 conclusions are formally invalidated. The data foundation is mid-migration from a defective 15-month MT5 feed to multi-year Dukascopy bid/ask data (3 of 4 symbols done). The old holdout is compromised. A remediation plan exists and is partially executed (hygiene + A4 done; A5/A3 not done; A2 incomplete — EURJPY).**

Execution engineering is close to demo-ready but has a known live/backtest timing divergence (A3) that is documented and **not yet fixed**. The documented `venv/` is empty; tests currently pass only under system Python 3.14.7 (74 passed).

**State in one line:** *Execution is nearly demo-capable; strategy is not validated; research base is invalidated and mid-repair.*

---

## 2. Repository state

### 2.1 Top-level layout (current)

| Area | Location | Notes |
|------|----------|-------|
| Live bot | `bot.py` (150 lines) | EURUSD M5 EMA50/200 + RSI14 + ATR14, 1% risk, FOK |
| Backtest engine | `backtest/backtester.py`, `config.py`, `strategy.py`, `indicators.py`, `metrics.py`, `validate.py` | Closed-signal / next-open engine |
| V2 strategy | `backtest/strategy_v2.py`, `validate_v2.py`, `predictive_v2.py` | Frozen experimental |
| Strategy 01/02/03 | `backtest/strategies/strategy_0{1,2,3}_*.py` | Phase 2 historical experiments |
| Phase 5 candidates | `backtest/strategies/{mean_reversion,breakout_fade,benchmark}.py` | Benchmark runner |
| Research modules | `backtest/market_research/*` (discovery, edge, multi-hour, phase5_research, phase6, 7 studies) | Phases 1, 3, 4, 5, 6 |
| Data pipeline | `backtest/data/{dukascopy_acquire,data_split,research_split,data_validation,validate_all}.py` | Phase 0 / 0B |
| Holdout guards | `backtest/research_safety.py` | Defined; **not imported by any research module** |
| Data | `data/*.csv` | Mid-migration (see §9) |
| Outputs | `outputs/**` | Invalidated historical + new splits/validation |
| Tests | `tests/` (3 files) | 74 tests |
| Docs / reports | 20+ top-level `*.md` | See §8 |
| Dumps | `dump_mt5_data.py`, `dump_mt5_multi.py` | Read-only MT5 export helpers |
| Env | `.python-version` (3.13), `requirements.txt`, `venv/` | venv empty (pip only) |

No `README.md`. No CI config. No live-trading service/scheduler in-repo.

### 2.2 What is committed vs not

- **COMMITTED:** essentially the entire project (271 tracked files), latest commit `5ed2313 research pairs`.
- **UNCOMMITTED:** `TASK.md` only (`M TASK.md`, +458/−251 vs HEAD) — the current audit brief itself.
- **UNTRACKED:** `CURRENT_PROJECT_STATE_AUDIT.md` (this file). No other untracked files.
- Raw Dukascopy chunks / diag / poc / smoke dirs are **gitignored** (hygiene fence); canonical `data/*_m5.csv` are tracked.

---

## 3. Git state

| Item | Value |
|------|-------|
| Branch | `master` (up to date with `origin/master`) |
| Remote | `https://github.com/RexDavid06/Trade-Bot.git` |
| Stashes | none |
| Commits | 6 total |

| Commit | Message | Character |
|--------|---------|-----------|
| `1bcbe74` | initial commit | `.gitignore` + empty `bot.py` |
| `38eb89a` | requirements.txt | early `bot.py` + requirements |
| `6a8f0ad` | fix(bot): filling mode, safe lot, spread check | order-submit hardening |
| `a98314f` | research: add V2 trend pullback strategy and validation | engine, V1/V2, outputs, 90k EURUSD MT5 data |
| `d8ae50c` | saved error before agent failed | market_research suite, splits, data validation |
| `5ed2313` | research pairs | **huge**: Phase 0/0B/6.5 docs, strategies 01–03, benchmark, phase5/6, Dukascopy data, instruments, tests, research_safety, remediation plan |

**Intentional vs pre-existing:** all working-tree change is intentional (`TASK.md` brief). No stray modifications to code/data/tests.

---

## 4. Environment state

| Item | Finding | Classification |
|------|---------|----------------|
| `.python-version` | `3.13` | pinned |
| System `python` | **3.14.7** — has metatrader5 5.0.5640, pandas 3.0.1, numpy 2.4.3, ta 0.11.0, pytest 9.1.1, matplotlib 3.11.2 | matches `requirements.txt` versions |
| `venv/` | **exists but contains only `pip 26.2.1`** — no MetaTrader5/pandas/pytest | **INCONSISTENCY** — `BACKTEST.md` says run via `venv\Scripts\python.exe` |
| `requirements.txt` | metatrader5, numpy, pandas, dateutil, six, ta, tzdata, matplotlib, pytest | present |
| Test command | `python -m pytest tests` (system interpreter) | **74 passed** (last run 1.38s) |
| Same under venv | fails: `No module named pytest` | broken documented path |

**No packages were installed or upgraded during this audit.** Environment inconsistency is documented, not fixed.

---

## 5. Backtest engine audit

Source of truth: `backtest/backtester.py` + `config.py` + `strategy.py` + `indicators.py` + `validate.py`.

### 5.1 Mechanics (verified in code)

| Aspect | Behavior | Validity |
|--------|----------|----------|
| Signal timing | Generated on **closed** candle `i` (step 3 of loop), only when flat | OK — no lookahead in signal |
| Entry timing | **Open of candle `i+1`** (pending signal filled at next bar open) | OK |
| Candle timing | Indicators causal (`ta` on rows ≤ i); `validate.py` partial-recompute checks | OK |
| Exit timing | SL/TP walked on subsequent candles' high/low; optional `max_hold_bars` → close reason `HOLD`; end-of-data → `OPEN` | OK |
| Stop-loss | `entry ± atr_sl_mult × ATR` default 1.5 | see ATR timing issue below |
| Take-profit | default 3.0 × ATR | same |
| Intrabar both-touched | **Conservative: SL first** when `conservative_intrabar=True` (default) | OK — avoids optimistic bias |
| Spread | Entry-candle `spread × point × multiplier`, floored by `min_spread_pips` (default **0.0**) | Applied once round-turn |
| Slippage | 0.5 pip/side + optional extra → 1.0 pip round-turn default | OK |
| Commission | $7/lot round-turn, money only | OK |
| Position sizing | **Fixed 0.10 lot** in backtest; live uses ~1% balance / 1000 | **Mismatch (A5) — documented, not fixed** |
| Lot / risk sizing | Not SL-distance-aware in live either (`bot.py` `risk/1000`) | documented |
| Max holding | Optional via `max_hold_bars` (strategies 01/02 set 40/20) | OK |
| One-position rule | Yes; no queue while open (mirrors `position_exists()`) | OK |
| Result classification | **`classify_result(net_money)` → WIN/LOSS/BE** | **A4 RESOLVED** (was pips-based) |
| Metrics | `metrics.py` wins/PF/streaks from money labels | consistent post-A4 |
| Train/val/holdout | Engine is split-agnostic; **callers** choose loading | see §10 |
| `signal_fn` | Supported (`SignalFn`); V1 default `signal_at` | OK |
| Data loading | Callers read CSV; engine assumes indicator-augmented frame | OK |
| Timezone | Dukascopy → naive UTC; MT5-era files naive (treated UTC) | consistent within each generation |

### 5.2 Issue register (engine + research validity)

| # | Issue | Class | Evidence |
|---|-------|-------|----------|
| E1 | **SL/TP ATR uses entry candle `i` ATR at the open of `i`** (`atr = df["atr"].iat[i]`), which incorporates candle `i` high/low/close not known at the open. Signal candle ATR would be `i-1`. Mild lookahead in **risk geometry only** (not entry direction). Live bot currently uses forming-bar ATR too, but on a different bar than a fixed bot would after A3. | **CONFIRMED** (geometry lookahead); remediation defers alignment decision | `backtester.py:263`; `RESEARCH_REMEDIATION_PLAN.md` §1.3 |
| E2 | Cost spread taken from entry candle `spread` column; if that bar is zero-spread, cost understate | **CONFIRMED** historically on MT5 feed; **mitigated** for 3 symbols by Dukascopy (0% zeros); **still open** for EURJPY (27%) | validation reports; §9 |
| E3 | `min_spread_pips` default 0 → no floor; no runtime degeneracy guard | **CONFIRMED** open | `config.py:60`; remediation A2 |
| E4 | Fixed-lot money P&L vs live risk sizing | **CONFIRMED** open (A5) | `config.py` vs `bot.py:51-56` |
| E5 | Pips vs money win labels | **RESOLVED** | `classify_result`; `tests/test_result_classification.py` |
| E6 | Lookahead in signal path / `shift(-1)` / forming-candle in engine signals | **RESOLVED / not present** | engine loop; `validate.py`; no negative shifts in signal code |
| E7 | EURJPY pip/point wrong in `CostConfig` defaults when benchmark ran | **CONFIRMED** for old Phase 5 outputs; **partial fix** = `instruments.py` exists, but `benchmark.py` still constructs default `CostConfig()` (EURUSD pips) for all symbols | `benchmark.py:81`; `results.md` EURJPY −931%/+2199% |
| E8 | Overlapping trades | **RESOLVED** (engine design + tests) | one-position rule |
| E9 | Spread applied twice | **RESOLVED** (once round-turn) | `_cost_price` |

**Net:** engine is research-usable for 5-digit FX pairs on clean data; known open items are E1 (deferred), E3/E4 (planned), E7 if benchmark is ever re-run without per-symbol CostConfig.

---

## 6. Live / MT5 bot audit

Source: `bot.py` (only live execution module; dumps are export-only).

| Aspect | Finding |
|--------|---------|
| Broker connection | `mt5.initialize()` at import; no login/password in repo (terminal defaults). `.gitignore` has `meta logins.txt` |
| Account | Handoff cites MetaQuotes-Demo `5055770258` (docs only; not in code) |
| Symbol / TF | `EURUSD`, `TIMEFRAME_M5` |
| Candle retrieval | `copy_rates_from_pos(SYMBOL, TIMEFRAME, **0**, 500)` → **last row is the forming bar** |
| Signal timing | New-candle detector on `df.iloc[-1]['time']`, then signal on **that same forming row**; fill **immediately in-bar** |
| Indicators | EMA50, EMA200, RSI14, ATR14 via `ta` on the fetched window (includes forming bar) |
| Entry logic | BUY: EMA50>EMA200 and 40<RSI<55; SELL: EMA50<EMA200 and 45<RSI<60 (strict inequalities) |
| SL / TP | 1.5×ATR / 3.0×ATR from fill price, ATR = last row (forming) |
| Position sizing | `lot = max(round(balance * 0.01 / 1000, 2), 0.01)` — not SL-distance-aware |
| Risk | `RISK_PERCENT = 1` |
| Filling mode | `ORDER_FILLING_FOK` (commit `6a8f0ad`) |
| Order submission | `TRADE_ACTION_DEAL`, deviation 20, magic 999, comment `TREND_PULLBACK_BOT` |
| Error handling | Minimal: None-checks on rates/tick; `order_send` result printed only — **no retry, no retcode handling** |
| Duplicate positions | `position_exists()` blocks new entries while flat check fails |
| Logging | `print` only |
| Secrets | None in file |
| Trades live now? | No evidence it is running as a service; would only trade when executed manually |
| Safe on demo? | **Engineering: mostly** (FOK, spread gate <25 pts, min lot, one-position). **Scientifically: no** — A3 timing divergence + no validated edge |
| Live vs backtest gaps | **(a)** forming-candle signal + in-bar fill vs closed-candle + next-open; **(b)** ATR bar for SL/TP differs after A3 fix would be applied; **(c)** risk sizing vs fixed lot; **(d)** live spread gate vs backtest observed spread |

### Readiness label

**DEMO-READY BUT STRATEGY NOT READY** — more precisely:

- Execution code path exists and was hardened for filling mode (commit evidence).
- **Not verified in this audit** whether `mt5.initialize()` and `order_send` currently succeed (no connection attempted, per task rules).
- No in-repo proof of a successful historical fill (no trade logs); handoff claims prior demo deployment — **PLAUSIBLE, NOT PROVEN** from artifacts alone.
- A3 means any demo run would **not** reproduce the validated backtest semantics until fixed.

---

## 7. Strategy inventory

| ID / name | File | Rules (exact, condensed) | Instrument / TF | Status |
|-----------|------|--------------------------|-----------------|--------|
| **V1** | `backtest/strategy.py` (+ `bot.py`) | BUY iff EMA50>EMA200 and 40<RSI14<55; SELL iff EMA50<EMA200 and 45<RSI14<60; SL 1.5 ATR, TP 3 ATR; one position | EURUSD M5 (canonical); also run on 4 symbols in Phase 5 | **FROZEN.** Not validated. Full-data baseline: 4,109 trades, WR 31.6%, PF 0.57, **−93.1%** (`outputs/summary.json`, old 90k feed). Predictive: in-direction ≈48%, avg pips ≤0. Phase 5: negative all symbols/splits (except broken EURJPY). **Not suitable as a validated demo edge; it is the frozen live rule set.** |
| **V2** | `backtest/strategy_v2.py` | Trend both EMAs rising/falling + pullback ≥0.5 ATR into 0.25 ATR EMA50 zone + rejection candle + RSI cross 50; LOOKBACK=20 fixed | EURUSD M5 primarily | **FROZEN experimental.** 2,877 signals; predictive mostly worse than V1; handoff: “rejected in Phase 1–4”. Not deployed. |
| **Strategy 01** | `strategies/strategy_01_extreme_fade.py` | dist=(close−SMA20)/STD20; ≤−1 long / ≥+1 short; 1.0 ATR stop; hold 40; cost 2×spread+1.7 pips | EURUSD, EURGBP, GBPUSD M5 | **REJECTED / frozen historical.** Dev only. 78–80% exits are STOP; net −2.2 to −4.2 pips/trade; report: hypothesis not proven edge. |
| **Strategy 02** | `strategies/strategy_02_breakout_fade.py` | Close > prior 20-bar high → SELL fade; < prior 20-bar low → BUY; session hour UTC [7,16); hold 20; engine SL/TP | EURGBP, GBPUSD M5 | **REJECTED / frozen.** Dev only; pre-registered acceptance not met (report). |
| **Strategy 03** | `strategies/strategy_03_session_gated_mean_reversion.py` | Strategy 01 rules gated to London/LondonNY sessions | EURUSD, EURGBP, GBPUSD M5 | **REJECTED conditioning test.** Session gate adds pips vs S01 baseline but still fails cost. |
| **mean_reversion** (Ph5) | `strategies/mean_reversion.py` | BUY close < SMA10−1σ; SELL close > SMA10+1σ | 4 symbols × 3 splits | **REJECTED.** All non-broken cells negative (e.g. EURUSD dev −67.1%, PF 0.667). |
| **breakout_fade** (Ph5) | `strategies/breakout_fade.py` | Follow downside break of CH160−0.25 ATR; fade upside +0.25 ATR | 4 symbols × 3 splits | **REJECTED.** All non-broken cells negative (e.g. EURUSD dev −21.9%, PF 0.716). |
| **Phase 5 benchmark** | `strategies/benchmark.py` | Runs V1+MR+BF on dev/val/holdout | 4 symbols | Results **invalidated as conclusions** (handoff fabrication + EURJPY pip bug + zero-spread era). Raw `results.json` authoritative for what ran. |
| ema_sep experiment | `experiment.py` | Sweep `ema_sep_min` 0.00–0.50 | EURUSD | **FALSIFIED hypothesis** — no improvement (WR ~31.5%, PF ~0.56 flat). |
| Cloned-repo concepts | reference only | Keltner/Bollinger ideas | — | **Not implemented** (per comparison REJECT list; martingale etc. rejected). |

**Holding / costs:** per-strategy as above; engine defaults otherwise (spread+slip+$7, fixed 0.10 lot).  
**Validated / holdout-tested:** **none** under the current integrity rules. Old Phase 5 “holdout” numbers are invalidated and used a compromised-era pipeline.  
**Suitable for demo as an edge:** **none.** V1 is the only rule set wired to `bot.py` and may be demoed only as an **execution/pipeline test**, not as a validated strategy.

---

## 8. Research history

### 8.1 Documents present (authoritative vs not)

| Document | Role | Trust status |
|----------|------|--------------|
| `MARKET_BEHAVIOR_DISCOVERY.md` | Phase 1 discovery | Exploratory; naive trend/breakout continuation **rejected** |
| `STRATEGY_01/02/03_*.md` | Phase 2 | Accurate to code; all three non-viable |
| `PHASE_3_EDGE_RESEARCH.md` | Edge search on DEV | **Best movement-to-cost 0.66** (EURUSD session London H=80); nothing ≥1.0 |
| `PHASE_4_MULTI_HOUR_RESEARCH.md` | Multi-hour | **Best movement-to-cost 0.73** (EURUSD multi-hour reversal); still <1 |
| `PHASE_5_BROKER_DATA_AND_MARKET_EXPANSION.md` | — | **ABSENT** (TASK said “if it exists”). Related code: `phase5_research.py`; results: `outputs/benchmark/*` |
| `RESEARCH_REMEDIATION_PLAN.md` (2026-09-13) | A3/A4/A5/A2 plan | **Current governing plan**; sequence hygiene→A4→A5→A3→A2 |
| `TRADING_REPO_COMPARISON.md` | A1–A6 + vs cloned repo | Accurate issue framing |
| `BACKTEST.md` | Engine docs | Mostly current; venv instructions **stale** (venv empty); “Current result” stale vs new data |
| `TASK.md` | Prior briefs | Working copy modified (uncommitted) |
| `PROJECT_RESEARCH_HANDOFF.md` | Handoff | **UNRELIABLE — fabricated Phase 5/6 numbers** (proven by §6.5 audit vs `results.json`) |
| `PHASE6_5_RESEARCH_INTEGRITY_AUDIT.md` | Audit of Ph5/6 | **Authoritative critique**; matches code/data checks in this audit |
| `HISTORICAL_OUTPUTS_STATUS.md` | Invalidation registry | **Authoritative**; hygiene fence 2026-09-13 |
| `PHASE0_*` / `PHASE0B_*` | Data/integrity Phase 0 | Directionally right; **data inventory section stale** (still lists 90k×4; reality is 3 symbols migrated) |
| `MARKET_RESEARCH_REPORT.md` | Consolidated Ph1–4 | Exploratory |

### 8.2 Claims cross-checked

| Claim | Source | Verdict |
|-------|--------|---------|
| Phase 5 handoff numbers match `results.json` | handoff | **FALSE** — every audited row wrong (e.g. EURUSD V1 dev handoff +2.05% vs actual **−62.91%**) |
| All Phase 5 strategies negative after costs (non-EURJPY) | §6.5 + `results.md` | **TRUE** (verified tables) |
| EURJPY Phase 5 returns impossible | `results.md` | **TRUE** (−931% / +2199%) — pip scaling |
| Phase 6 ran on full data → holdout compromised | §6.5 `phase6.py:51-55` | **TRUE** |
| EURUSD 48.3% zero-spread on old feed | Ph5/6 docs | **TRUE for old 90k file**; **no longer true** for current `eurusd_m5.csv` (0.02%) |
| Current EURUSD data is 90k bars | `PHASE0_DATA_BACKTEST_INTEGRITY_REPORT` §3 | **OUTDATED** — file is 422,225 bars 2021–2026 |
| Handoff: commission $0 demo | handoff §4.1 | **FALSE vs code** — `CostConfig.commission_per_lot = 7.0` |
| Separation experiment falsified | `BACKTEST.md` | Consistent with `outputs/separation_experiment.md` |
| V1/V2/bot frozen | multiple | **TRUE** in policy; A3 plan explicitly contemplates minimal documented unfreeze of `bot.py` timing only |

---

## 9. Data audit

### 9.1 Canonical datasets (measured this session)

| File | Rows | Range | Zero-spread | Source generation | Split artifacts |
|------|------|-------|-------------|-------------------|-----------------|
| `data/eurusd_m5.csv` | **422,225** | 2021-01-03 → 2026-09-09 | **0.02%** | Dukascopy bid/ask merged | `outputs/splits/EURUSD` (422,225; holdout from 2025-07-24) **and** stale `outputs/eurusd/reports/*` (90k) |
| `data/eurgbp_m5.csv` | **425,477** | 2021-01-03 → 2026-09-09 | **0.0%** | Dukascopy | `outputs/splits/EURGBP` + stale 90k reports |
| `data/gbpusd_m5.csv` | **374,746** | 2021-01-03 → 2026-09-09 | **0.0%** | Dukascopy | `outputs/splits/GBPUSD` + stale 90k reports |
| `data/eurjpy_m5.csv` | **90,000** | 2025-06-26 → 2026-09-10 | **27.0%** | **OLD MT5** | `outputs/splits/EURJPY` (90k rows) |

Columns (all): `time, open, high, low, close, tick_volume, spread, real_volume`.  
Timezone: naive UTC. OHLC from bid; spread = round((ask−bid)/point) for Dukascopy (documented in `PHASE0B_ACQUISITION_FIX_REPORT.md`).

### 9.2 Known defects

| Dataset | Defects |
|---------|---------|
| EURUSD (new) | 29 negative spread values; 99 zero-spread bars (0.02%); 98 non-weekend gaps / ~759 missing bars; spread max 326 pts (flagged); 840 flat bars — see `outputs/eurusd/reports/data_validation_report.md` (report itself is current for row counts) |
| EURGBP / GBPUSD (new) | Same pipeline; 0% zero-spread; GBPUSD shorter than EURUSD/EURGBP (coverage difference — not investigated further) |
| EURJPY (old) | 27% zero-spread; 15-month single regime; **not migrated**; Phase 5 numbers invalid |
| Raw chunk tree | Many 0-byte CSVs under `data/` (ignored) — acquisition retries/rate limits documented |
| Broker-accurate bid/ask history | **Exists now for 3 symbols via Dukascopy** (not the user’s MT5 broker). MT5 multi-year export availability: see `PHASE0_MT5_DATA_AVAILABILITY_REPORT.md` (read-only probe; not re-verified live here). **EURJPY Dukascopy full history: NOT yet acquired.** |

### 9.3 DEV / VALIDATION / HOLDOUT labels

| System | Location | Basis | Used by |
|--------|----------|-------|---------|
| **NEW** research splits | `outputs/splits/<SYM>/assignments.csv` + `metadata.json` | 60/20/20 on **current** CSVs (EURJPY still on 90k) | `market_discovery`, `edge_research`, `multi_hour_research` (dev-only filters) |
| **OLD** Phase 5/6 splits | `outputs/<sym>/reports/data_split_assignments.csv` | 60/20/20 on **old 90k** | `benchmark.py` (all three splits); historical phase6 (actually ignored splits — full data) |

The two systems **disagree in time ranges** — do not mix them.

---

## 10. Validation / holdout protection audit

| Question | Answer |
|----------|--------|
| Has validation been read by research code? | **YES, intentionally** by `benchmark.py` (Phase 5 design: dev→val→holdout). Also any full-CSV tools (`run`, `validate`, `predictive`, `experiment`, standalone study modules) read **everything**. |
| Has holdout been read? | **YES — historically compromised.** Phase 6 `phase6.py` loads full CSVs (confirmed §6.5). Phase 5 benchmark also evaluated holdout (and those results are invalidated). |
| Is the 60/20/20 split intact as files? | **YES** for both artifact generations; chronological, no overlap (`validate_split_isolation` design; Ph5/6 audit confirmed old splits). |
| Were old conclusions based on leaked/compromised data? | **Phase 6: YES (holdout inside full-data studies). Phase 5: holdout was used as a test set inside an invalidated pipeline (fabricated handoff + pip bug + zero-spread costs).** |
| Historical vs current | **HISTORICAL ISSUE:** holdout contamination + bad costs + handoff fraud. **CURRENT STATE:** documented in `HISTORICAL_OUTPUTS_STATUS.md`; remediation creates a **fresh sealed holdout** on new data; **new holdout not yet fully established for all 4 symbols** (EURJPY still old file). |
| Is `research_safety.py` enforced? | **NO — dead guard.** Nothing imports `SplitGuard` / `HoldoutGuard` / `load_split_safe`. Protection is conventional, not mechanical. |

**Precision statement:** The old holdout is **not** a clean out-of-sample for any Phase 6-derived hypothesis. A new multi-year holdout exists in `outputs/splits/` for EURUSD/EURGBP/GBPUSD only and must remain untouched; it has **not** been used for new analysis in this audit.

---

## 11. Test audit

| Item | Finding |
|------|---------|
| Count | **74 passed** (`python -m pytest tests -q`, system 3.14.7, last run 1.38s) |
| Files | `test_result_classification.py`, `test_instruments_and_backtest.py`, `test_dukascopy_acquire.py` |
| Covered | money-based WIN/LOSS/BE; metrics consistency; pip/point per symbol (incl. EURJPY 0.01); spread-once; slippage round-turn; Dukascopy parse/normalize/chunk/resume/rate-limit |
| Lookahead protection | **Indirect only** — `backtest/validate.py` battery (not under pytest) checks indicator lookahead, next-open fills, no overlap, SL/TP first-touch, determinism |
| Forming-candle / A3 | **NOT covered** — no test that live helper ignores forming bar (helper does not exist yet) |
| Cost classification | **YES** (A4 tests, including pips-win/money-loss case) |
| Sizing | Pip conversion only; **no** live-vs-backtest lot sizing tests (A5 unimplemented) |
| Live/backtest parity | **NOT tested** |
| Engine SL/TP ATR-bar (E1) | **NOT tested** |
| Uncovered high-value areas | signal_fn contract fuzzing; split isolation as pytest; spread-degeneracy guard (does not exist); per-symbol CostConfig in benchmark; bot.py entirely untested |

Suite was run because it is side-effect-free; **no test or source was modified.**

---

## 12. Current evidence table

| Research area | Result (measurable) | Economic viability | Status |
|---------------|--------------------|--------------------|--------|
| M5 trend continuation | Hit 47.3–48.8%, negative on 4 pairs | None | **REJECTED** (discovery) |
| M5 reversal / extreme fade | Raw hit ~51–53% no stop; with 1 ATR stop 78–80% STOP exits, −2.2..−4.2 pips/trade | Negative after costs | **REJECTED** (S01) |
| M5 breakout | Continuation strongly negative; fade chosen instead | Weak raw | Continuation **REJECTED**; fade tested as S02 → **REJECTED** |
| Session behavior | Best M5 movement-to-cost **0.66** (EURUSD London H=80) | < 1.0 | Research finding only; gated S03 still fails cost |
| Strategy 01 | Dev-only; PF ~0.45 class; stop destroys reversion | Negative | **REJECTED / FROZEN** |
| Strategy 02 | Dev-only; acceptance test not met | Negative | **REJECTED / FROZEN** |
| Strategy 03 | Session gate improves vs S01, still below cost | Negative | **REJECTED** |
| Multi-hour directional | Best movement-to-cost **0.73** | < 1.0 | Research finding; no strategy built |
| Multi-hour reversal | 0.73 (top listed) | < 1.0 | Same |
| Session-open behavior | movement-to-cost 0.60 (London open 4h) | < 1.0 | Rejected as edge |
| Volatility behavior | movement-to-cost 0.60 expansion event | < 1.0 | Weak; no strategy |
| Breakout (24h) | 0.44–0.66 | < 1.0 | Rejected |
| V1 backtest (old full data) | 4,109 trades, WR 31.6%, PF 0.57, −93.1% | Catastrophically negative | FROZEN baseline, **not validated** |
| V1 predictive power | in-dir ≈48.2%, avg pips ≈0 or negative | None | No raw edge |
| V2 predictive power | 2,877 signals, mostly ≤ V1 | None | Rejected experimental |
| EMA separation filter | FALSIFIED (PF flat ~0.56) | None | Closed |
| Phase 5 V1/MR/BF × 4 symbols | All negative after costs (EURJPY invalid) | None | **REJECTED**; handoff numbers **FABRICATED** |
| Phase 6 behaviors (7×4) | Small effects 0.1–1.0 pips; **no costs applied**; holdout contaminated | Untested economically | **INVALIDATED as formal evidence**; exploratory patterns only (MR / momentum reversal signs consistent) |
| V1 trend pullback live bot | Same rules as V1 | Inherits V1 negativity | Frozen; demo = pipeline test only |

---

## 13. Confirmed facts

1. Engine signals on closed bars and fills next open; conservative SL-first; one position; costs once round-turn; deterministic; validated by `validate.py` + pytest.
2. A4 win/loss classification is money-based and tested (**74/74 pass**).
3. `instruments.py` defines correct EURJPY pip/point; Phase 5 benchmark outputs predate/ignore that for `CostConfig`.
4. Every cost-aware strategy result in-repo (non-broken symbols) is negative.
5. Phase 5 handoff quantitative claims are fabricated relative to `results.json`.
6. Phase 6 used full CSVs → old holdout compromised for those hypotheses.
7. `HISTORICAL_OUTPUTS_STATUS.md` formally invalidates Phase 5/6 as evidence.
8. Current EURUSD/EURGBP/GBPUSD CSVs are multi-year Dukascopy with ~0% zero-spread; EURJPY is still the old 90k MT5 file with 27% zero-spread.
9. Two split generations exist; they must not be mixed.
10. `bot.py` reads the forming candle (`start_pos=0`) and fills in-bar — diverges from the engine (A3), documented, **unfixed**.
11. `venv/` is empty; system Python runs the suite.
12. `research_safety.py` is unused by research entry points.
13. No strategy is holdout-clean and positive under current integrity rules.
14. Working tree: only `TASK.md` modified; no code/data/test dirt.

## 14. Plausible but not proven

- MT5 `initialize()` / `order_send` succeed today on the user’s terminal (code + package present; commit history implies past success; **not executed here**).
- Handoff claim of prior demo deployment.
- Phase 6 directional patterns (MR, momentum reversal) being “real” vs artifacts of costs/spread/multiple testing.
- GBPUSD shorter history being incomplete acquisition vs genuine feed coverage.
- Reference repo’s Keltner/Bollinger concepts being salvageable if rebuilt.

## 15. Unknown

- Whether a validated edge exists on any market/timeframe for this cost model.
- True live cost on the target broker (esp. spread distribution vs Dukascopy).
- Whether MT5 can export multi-year bid/ask for EURJPY faster than Dukascopy path.
- Whether the fresh `outputs/splits/` holdout has ever been touched by any process (no access log — guards unwired).
- Long-horizon regime robustness (single ~5.7-year window still one era structure; old data was 15 months).

## 16. Rejected approaches (do not resurrect)

| Rejected | Why |
|----------|-----|
| V1 as a *profitable* strategy claim | PF 0.57 / −93% full-data; Phase 5 negative everywhere |
| V2 trend-pullback as deployed edge | No predictive gain; rejected Ph1–4 |
| Strategies 01 / 02 / 03 | Stop/session variants fail cost on dev |
| Phase 5 mean_reversion & breakout_fade | Negative all valid cells |
| EMA-separation threshold tuning | Explicitly falsified |
| Naive M5 trend & breakout continuation | Discovery-rejected |
| Treating handoff Phase 5/6 tables as fact | Fabricated |
| Reusing old holdout as OOS after Phase 6 | Contaminated |
| EURJPY Phase 5 result mining | Pip bug |
| Parameter sweeps on rejected strategies | History + integrity rules |
| Martingale / cloned-repo lookahead patterns | Comparison REJECT list |

---

## 17. Current demo readiness

1. **Can the current code connect to MT5?**  
   **Code yes / session unverified.** `mt5.initialize()` present; `metatrader5` installed on system Python. No connection attempted in this audit.

2. **Can it submit an order?**  
   **Code yes** (`order_send` + FOK + deviation + magic). Runtime success **unverified now**.

3. **Has successful submission been demonstrated?**  
   **PLAUSIBLE, not proven in-repo** (fix commit `6a8f0ad`; handoff demo claim; no fill logs).

4. **Is the execution layer operational?**  
   **Operationally incomplete:** works as a script if the terminal is up, but A3 timing bug, print-only errors, no retcode handling, empty documented venv.

5. **Is the current trading strategy economically validated?**  
   **NO.**

6. **Is there a strategy suitable for demo?**  
   **No validated edge.** V1 (bot rules) is the only wired strategy and may be used **only** as an execution/observation vehicle on demo with understood negative prior evidence — not as a research success.

7. **Is the bot safe to run on a demo account?**  
   **Conditionally, engineering-safe** (min lot, spread filter, one position, FOK). **Not scientifically safe to interpret results as validation** until A3 is fixed and expectations are set to “pipeline test.”

8. **Exact pieces preventing starting demo trading today**  
   - **Engineering:** A3 closed-candle parity (and optional ATR-bar decision); restore runnable environment per `BACKTEST.md` (recreate venv **or** amend docs); confirm MT5 terminal/login; smoke `initialize` + `symbol_info` + `account_info` without orders.  
   - **Strategy:** absence of any economically validated signal (blocks *trusting* demo, not the act of sending a demo order).

9. **Strategy vs engineering split**  
   - **Strategy blockers:** no edge past cost; invalidated Phase 5/6; compromised old holdout; EURJPY data; need clean re-baseline.  
   - **Engineering blockers:** A3; empty venv; unused holdout guards; no order-result handling; E1 ATR alignment decision; A5 sizing parity (for money comparability).

---

## 18. Project blockers (identification only)

### STRATEGY BLOCKERS
1. No cost-surviving edge in any completed study or backtest.
2. V1 (the live rules) has strongly negative measured expectancy.
3. Phase 6 patterns are unvalidated and contaminated for OOS claims.

### DATA BLOCKERS
1. EURJPY still on defective 90k MT5 feed (27% zero-spread).
2. Fresh sealed 60/20/20 incomplete until EURJPY migrates + re-split.
3. Spread-degeneracy guard absent; negative spread values in EURUSD file.
4. Two conflicting split generations on disk.

### RESEARCH BLOCKERS
1. Old holdout unusable for Phase 6-derived ideas.
2. Handoff document must never be cited.
3. `research_safety.py` not wired — protection is honor-system.
4. Only 3/7 Phase 6 studies had any p-values; no multiple-testing correction.

### EXECUTION BLOCKERS
1. **A3** forming-candle / in-bar fill vs backtest semantics.
2. Order error handling is print-only.
3. Live/backtest sizing mismatch (A5).
4. No in-repo proof of current broker connectivity.

### ENVIRONMENT BLOCKERS
1. **Empty `venv/`** vs documented run path.
2. Interpreter drift: pin 3.13 vs running 3.14.7 (suite passes on 3.14.7).
3. Stale sections in `PHASE0_*` data inventory and `BACKTEST.md` venv notes.

---

## 19. The big question — shortest scientifically defensible path to MT5 DEMO trades

**Evidence-based answer:**  
**Execution is nearly ready; strategy is not.** The shortest defensible path is **not** another edge-search phase and **not** “tune V1.” It is a thin execution-readiness sequence followed by a demo run framed correctly as a **pipeline test of frozen V1**, while data remediation continues in parallel for future research:

1. **Close A3** (minimal documented `bot.py` timing fix + pure signal helper + repaint test) so live decisions match closed-candle backtest rules.  
2. **Restore the documented environment** (recreate `venv` from `requirements.txt` on 3.13 **or** officially document system 3.14) and re-run pytest + `backtest.validate`.  
3. **Read-only MT5 smoke** (`initialize`, symbol, tick, account — no orders), then a **single manual demo order** if and only if the user explicitly requests it (not part of this audit).  
4. **Run the bot on demo with V1 rules and tiny risk as an execution observability exercise** — explicitly **not** as an economically validated strategy (all repo evidence says V1 loses).  
5. **In parallel (does not block demo):** finish A2 EURJPY Dukascopy acquisition → `validate_all` → fresh four-symbol splits → seal new holdout → only then any new research.

Supported outcome labels from TASK: **“execution is ready but strategy is not”** (after A3 + env), with **data remediation required before any further validation claims.**

---

## 20. What not to do next

Supported by repo history:

1. Do not re-tune V1/V2/Strategy 01–03 or re-run `experiment.py` ladders looking for a winner.  
2. Do not run new M5 parameter searches on invalidated outputs.  
3. Do not use EURJPY Phase 5 numbers or the old EURJPY file for conclusions.  
4. Do not touch `outputs/splits/*` holdout segments or re-use the old Phase 6 holdout as OOS.  
5. Do not cite `PROJECT_RESEARCH_HANDOFF.md` performance tables.  
6. Do not build infrastructure/ML/new symbols before a cost-clearing hypothesis exists on clean dev data.  
7. Do not modify `bot.py` **except** the documented A3 timing unfreeze when that step is explicitly approved.  
8. Do not delete or “correct” invalidated outputs.  
9. Do not mix old 90k assignments with new multi-year CSVs.  
10. Do not treat Phase 6 p<0.05 cells as edge without costs, benchmarks, and multiple-testing control.  
11. Do not implement Phase 5/6 “next phases” as strategy code yet — remediation gates them.  
12. Do not place MT5 orders as part of “fixing” the repo.

---

## 21. ONE recommended next action

**Implement remediation step A3 only:** change `bot.py` to read completed candles (`copy_rates_from_pos(..., start_pos=1, ...)`), extract a pure `signal_from_candles(df)` helper that evaluates the last closed candle exactly like `backtest.strategy.signal_at`, and add the repaint/regression tests specified in `RESEARCH_REMEDIATION_PLAN.md` §1.4 — with a documented, rules-preserving unfreeze note. No parameter changes, no strategy changes, no orders.

*Why this one:* it is the smallest repo-identified change that makes any future demo run scientifically comparable to the validated backtest semantics; A4/hygiene are already done; A5 is money-labeling only; A2 is a long data job that does not block a demo pipeline test.

---

*End of audit. No source, strategy, bot, data, or test files were modified. No backtests, optimizations, holdout analyses, or MT5 orders were performed. This file (`CURRENT_PROJECT_STATE_AUDIT.md`) is the only artifact created.*
