# RESEARCH REMEDIATION PLAN

**Created:** 2026-09-13
**Status:** PLAN ONLY — no files were modified, no optimization was run, no new strategy was introduced, the holdout was not accessed, and no historical evidence was deleted or overwritten.

Purpose: a controlled plan that fixes the known integrity/safety issues (A3, A4, A5, A2, minor hygiene) **before** any future controlled strategy research. It is grounded in the current implementation, not in the previously-invalidated handoff numbers.

Source documents read and relied upon:
- `TRADING_REPO_COMPARISON.md` (phases 3–4 define A1–A6)
- `PROJECT_RESEARCH_HANDOFF.md`, `PHASE6_5_RESEARCH_INTEGRITY_AUDIT.md`, `PHASE0_DATA_BACKTEST_INTEGRITY_REPORT.md`, `PHASE0_MT5_DATA_AVAILABILITY_REPORT.md`, `PHASE0B_EXTERNAL_DATA_SOURCE_REPORT.md`, `PHASE0B_ACQUISITION_FIX_REPORT.md`, `PHASE0B_SYMBOL_ACQUISITION_REPORT.md`, `HISTORICAL_OUTPUTS_STATUS.md`
- `bot.py`, `backtest/backtester.py`, `backtest/config.py`, `backtest/metrics.py`, `backtest/strategy.py`, `backtest/strategy_v2.py`, `backtest/instruments.py`, `backtest/run.py`, `backtest/reporting.py`, `backtest/validate.py`, `backtest/indicators.py`, `backtest/spread_sensitivity.py`, `backtest/research_safety.py`, `backtest/data/{data_split,research_split,data_validation,validate_all,dukascopy_acquire}.py`, `tests/*.py`
- Repo hygiene state: `.gitignore`, `requirements.txt`, `BACKTEST.md`, `git status`, current interpreter.

---

## 0. Global constraints (invariants for every step below)

| Constraint | Meaning |
|---|---|
| No new strategy | Do not implement Keltner/Bollinger/any candidate yet. |
| No optimization | No parameter search, no `ema_sep_min` change, no sweep. |
| Holdout untouched | None of the fixes below reads, trains on, or evaluates the holdout. New splits created in A2 produce a *fresh* holdout that remains sealed. |
| Frozen semantics preserved | V1/V2 strategy **rules** (`strategy.py`, `strategy_v2.py`) are never altered. Only `bot.py` candle-index semantics (A3) and engine/config/metrics support code change, each with an explicit decision point. |
| No deletion of evidence | Invalidated outputs stay on disk; their status is already documented in `HISTORICAL_OUTPUTS_STATUS.md`. Do not overwrite them with "corrected" numbers. |
| Determinism | Every fix must keep the engine deterministic and covered by `backtest/validate.py` + pytest. |

---

## 1. Issue A3 — live bot may evaluate the forming candle while the backtester uses closed-candle signals

### 1.1 Current implementation (inspection)

- `bot.py:31` — `rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)`. With `start_pos = 0`, MT5 returns the series whose **last** element is the **currently forming bar** (the MT5 data series is indexed from the current bar backward; position 0 = current/forming bar).
- `bot.py:110-114` — the bot keys on `candle_time = df.iloc[-1]['time']` changing.
- `bot.py:124` — `last = df.iloc[-1]`; `bot.py:124-128` reads `ema50/ema200/rsi/atr` from that row; `bot.py:135-140` emits the signal and `bot.py:137/140` fills **immediately** inside the forming bar.
  → The signal is evaluated on an **incomplete** candle and the fill is intra-bar.
- `backtester.py:290-291` — signal is generated only on **closed** candle `i` (`signal_at(df, i, s_cfg)`); `backtester.py:246` fills at the **open of candle `i+1`**; indicators depend only on rows `[0..i]` (`indicators.py:20-27`, `validate.py` look-ahead checks).
  → The backtest rules are closed-candle + next-open; the live bot is forming-candle + immediate fill.
- Secondary off-by-one: for SL/TP placement the engine uses the **fill candle's** ATR (`backtester.py:247` `atr = float(df["atr"].iat[i])`), whereas `bot.py` uses the ATR of `df.iloc[-1]` — which, once the bot is fixed to the last *closed* candle, is the **signal** candle (bar `i-1`). Today these are different bars.

### 1.2 Exact problem

Live execution does not reproduce the validated backtest rules: (a) the signal can "repaint" as the forming bar's `close` evolves, so the live evaluation is not the deterministic closed-candle reproduction the engine validates; (b) live fills occur inside the bar rather than at the next open; (c) SL/TP geometry anchors on a different ATR bar. Reported live-vs-backtest performance is therefore not comparable.

### 1.3 Smallest safe architectural fix

- **Lift the `bot.py` freeze for this one, semantics-preserving change** (document the decision in the plan/commit message; the strategy *rules* are unchanged).
- `bot.py:31` — request completed bars only: `copy_rates_from_pos(SYMBOL, TIMEFRAME, 1, 500)` (position 1 = the last **completed** candle), so `df.iloc[-1]` is the last closed candle. Keep the `candle_time` change-detector and the `position_exists()` / `spread_ok()` guards unchanged.
- Extract a pure, testable helper (e.g. `signal_from_candles(df) -> (direction | None, atr, candle_index)`) that evaluates the **last closed candle** exactly like `signal_at`; have `bot.py` call it. The helper must only touch `df.iloc[-2]`-equivalent data (last completed row) and never `iloc[-1]` for signal inputs — this is the regression guard.
- Add a safety check that buffers ≥ 2 bars and asserts the last two rows' times differ as expected before acting (recommended; prevents acting on a feed that returns only one bar).
- **Decision item (deferred, documented):** whether to align `backtester.py:247` to use the **signal candle** (bar `i-1`) ATR for SL/TP, so the engine reproduces the fixed bot exactly. This is a *separate, engine-impacting* change (see §5: frozen-baseline note) and is NOT part of the minimal A3 step.

### 1.4 Tests to add

- `signal_from_candles(df) == signal_at(df, len(df) - 1)` for synthetic and real data (equal once the bot reads completed bars).
- Regression: a synthetic "forming bar" appended to `df` must **not** change the helper's output (no repaint) — the helper provably ignores `iloc[-1]`.
- Edge: insufficient history (`len(df) < 2`, warm-up NaN) → returns `None`, no fallback to the forming bar.
- Parity spot-check (replay, no MT5): for a recorded candle window, live helper signal + fill-price mapping == engine output for the same window (extend `backtest/validate.py` conceptually, added as a pure test).

### 1.5 Existing outputs invalidated

- **Backtest outputs: none changed** (engine untouched in the minimal fix).
- Live-trading logs/hypotheticals (none in repo) would become the first *comparable* artifacts after the fix.
- Nothing historical is rewritten; `BACKTEST.md` "Current result" is already stale w.r.t. the new data regardless (see A2).

### 1.6 Frozen V1/V2 impact

- None to `strategy.py` / `strategy_v2.py` — rules unchanged. `bot.py` changes are execution-timing only. If the deferred ATR-bar alignment (§1.3 decision) is later adopted, V1/V2 engine geometry changes → that becomes a separate re-baseline decision, not part of this step.

### 1.7 Holdout impact

- None. This fix touches live signal timing only; no split data is read.

---

## 2. Issue A4 — win/loss classification uses `net_pips` while financial metrics use `net_money`

### 2.1 Current implementation (inspection)

- `backtester.py:170-175` — `result` (`"WIN"/"LOSS"/"BE"`) is set from **`net_pips`** only.
- `backtester.py:166-168` — `net_money = gross_money − cost_price·notional − commission_per_lot·lot_size`. **Commission is money-only** and is *not* part of `net_pips` (`cost_pips` = spread + slippage only, `backtester.py:163`).
- Quantitatively: at 0.10 lot, EURUSD pip value = 0.10 × 100,000 × 0.0001 = $1; commission $7 ≈ **7 pips**. Any trade with `0 < net_pips < ~7` is labelled `"WIN"` but is a **money-loser** (net_money < 0).
- `metrics.py:20-24` builds `win_count/loss_count` from `t.result` (pips-based); `metrics.py:26-29` computes `gross_profit/gross_loss` and `profit_factor` from **`net_money` sign**; `metrics.py:31,65` mix the two. So `win_rate` vs `profit_factor` disagree structurally. `streaks` (`metrics.py:43-53`) and `build_monthly_table` (`metrics.py:104-115`) use the pips-based `result`, while `build_direction_table` (`metrics.py:120-126`) counts wins by `money > 0` — three different win definitions in one report.
- Downstream consumers of `t.result`: `diagnostics.py:36,222-235`, `excursion.py:43-113`, `experiment.py:37-40`.

### 2.2 Exact problem

The "win" label is defined on a quantity (`net_pips`) that excludes the commission that `net_money` includes. Financial classification (`money sign`) and P&L metrics therefore disagree on the same trades; win rate, streaks, monthly and directional wins, and profit-factor buckets are not mutually reconcilable, and the discrepancy is material (≈multi-pip band, see §2.1).

### 2.3 Smallest safe architectural fix

- Introduce one classifier, e.g. `classify_result(net_money: float) -> "WIN" | "LOSS" | "BE"` (net_money is the financial truth; it already includes spread/slippage/commission).
- Use it **both** in `backtester._finalize` (`backtester.py:170-175`) **and** in `metrics.py` (wins/losses, streaks) so there is a single definition. Keep `net_pips` as reported data (it is still a useful, competitor-neutral quantity) but never as the *label*.
- `build_direction_table` (`metrics.py:120-126`) and `build_monthly_table` (`metrics.py:104-115`) then agree by construction.
- No engine or strategy change: entry/fill/exit geometry is untouched; this is labelling + aggregation only.

### 2.4 Tests to add

- Unit: crafted `Trade` with `net_pips > 0` but `net_money < 0` (e.g. +3 pips, high commission) → `result == "LOSS"`; symmetric case → `"WIN"`; exact zero → `"BE"`.
- Consistency: `compute_metrics` → `winning_trades == (net_money > 0).sum()`, `losing_trades == (net_money < 0).sum()`; `sum(monthly.wins) == metrics["winning_trades"]`; `build_direction_table` win count matches money-sign count for each direction; streaks consistent with the same labels.
- Regression: `backtest/validate.py` battery still passes (determinism etc. unchanged).

### 2.5 Existing outputs invalidated

- All artifacts that report win rate / win count / streaks / monthly / directional wins and were derived from pips-based labels. In-repo such files (e.g. `outputs/benchmark/results.json`, `outputs/phase6/*`, old `outputs/*/reports`) are **already invalidated** by `HISTORICAL_OUTPUTS_STATUS.md` → no additional evidentiary loss.
- After the fix, *future* reports show slightly lower win rates (the 0–7 pip winners move to LOSS), but profit factor / expectancy / net P&L are unchanged (they already used money). The divergence disappears.

### 2.6 Frozen V1/V2 impact

- None. Signal rules untouched; only per-trade *result labels* and their aggregation change. V1/V2 trade *sets* and pips/money P&L are identical.

### 2.7 Holdout impact

- None. Metric computation is split-agnostic and never reads split data itself.

---

## 3. Issue A5 — fixed-lot backtesting differs from nominal live risk sizing

### 3.1 Current implementation (inspection)

- `config.py:52` — `CostConfig.lot_size = 0.10`, applied to every trade in `backtester.py:166` `notional = c_cfg.lot_size * c_cfg.base_contract`.
- `bot.py:51-56` — live sizing: `lot = max(round(balance × 0.01 / 1000, 2), 0.01)` → 1% of balance treated as if the stop were a fixed 100 pips. **Not SL-distance-aware** and **balance-dependent**.
- `config.py:45-48` documents that money P&L is a synthetic fixed-lot book and doesn't replicate live sizing.
- `spread_sensitivity.py:108-141` already builds `CostConfig` per scenario including `lot_size`, confirming sizing is a *config* concern.

### 3.2 Exact problem

Dollar P&L from the backtest is a synthetic book at fixed 0.10 lot; the live account uses nominal-1%-balance sizing that re-scales with equity. Any claim about dollar transferability between the two is not supported. (This does not affect pips/R-multiple metrics, which are sizing-independent.)

### 3.3 Smallest safe architectural fix

- Add **additive, default-preserving** sizing modes to `CostConfig` (backtest-only; `bot.py` untouched):
  - `lot_size_mode: str = "fixed"` (default — reproduces today exactly), plus `risk_percent: float = 1.0`, `min_lot: float = 0.01`, `lot_round: float = 0.01`, `assumed_sl_pips_for_lot: float = 100.0`.
  - `lot_size_mode = "risk_fraction"` implements the bot formula `lot = max(round(balance × risk_percent / 100 / assumed_sl_pips_for_lot, 2), min_lot)` evaluated **per trade** using the running live balance (the same `balance` the engine already tracks, `backtester.py:236,284`).
- The engine computes `notional` per trade from this resolved lot (`backtester.py:166`), keeping `sl/tp` geometry and signals identical — only money P&L scales.
- Document the now-verified live equivalent: with $10k start and default params, `risk_fraction` reproduces 0.10 lot at the first trade, then diverges as equity moves.

### 3.4 Tests to add

- Unit: `lot_for_balance(10000, ...) == 0.10`; floor at 0.01 for tiny balances; rounding to 0.01; risk-percent scaling.
- Engine: for identical signal windows, `fixed` and `risk_fraction` produce **exactly identical** trade lists (entry/exit/result/pips) and differ only in `net_money`/balances; monotonicity (profit raises next lot).
- Determinism: two runs of `risk_fraction` identical.

### 3.5 Existing outputs invalidated

- **None under the default** (`fixed`). Reports produced with `risk_fraction` are new artifacts and must live in separate output paths (e.g. `outputs/<symbol>/risk_sized/`) so they are not confused with the fixed-lot book.

### 3.6 Frozen V1/V2 impact

- None. This is a cost-model/sizing concern; signals and geometry are unaffected. `strategy.py`/`strategy_v2.py` are not touched.

### 3.7 Holdout impact

- None.

---

## 4. Issue A2 — historical zero/sparse spread data

### 4.1 Current implementation (inspection)

- The dataset is mid-migration. Current `data/`:
  - `eurusd_m5.csv` (422,225 bars), `eurgbp_m5.csv` (425,477 bars), `gbpusd_m5.csv` (374,746 bars) are **Dukascopy-derived** with **0.0% zero-spread** (spread = observed `(ask_close − bid_close)/point`).
  - `eurjpy_m5.csv` is still the **old MT5 file** (90,000 bars, Jun 2025–Sep 2026, 27% zero-spread) — the full Dukascopy EURJPY history download is scheduled but not yet run (`PHASE0B_SYMBOL_ACQUISITION_REPORT.md §9-10`).
- Cost model: `backtester.py:36-39` — `spread = max(observed·multiplier, min_spread_pips·pip)`; default `min_spread_pips = 0.0` (`config.py:60`). Historically 48.3% zero-spread EURUSD meant ~half of trades paid only slippage+commission.
- `data_validation.py:176-212` detects zero-spread and flags it; `validate_all.py:26-31,88-99` treats spread-related instrument issues as **critical**.
- `spread_sensitivity.py:62-105` provides OBSERVED/2×/min/REALISTIC/HIGH cost scenarios for robustness checks.

### 4.2 Exact problem

On the old MT5 feed the per-bar spread column understated costs (zeros = free execution). That feed is being retired, but (a) **EURJPY is not yet migrated**, (b) there is **no guard** that a backtest refuses to run on degenerately-zero-spread data (the floor is config-only and off by default), and (c) no fresh dev/val/holdout splits exist for the new multi-year files yet (`outputs/splits/` does not exist).

### 4.3 Smallest safe architectural fix

- **Data task (longest lead time, gated):** complete the EURJPY Dukascopy full run (resumable; `python -m backtest.data.dukascopy_acquire --symbol EURJPY --from 2021-01-01 --to 2026-09-10 --chunk-days 7 --out-dir data`), then run `python -m backtest.data.validate_all --data-dir data` and require **zero critical flags** (spread 0% across all four symbols) before any research.
- **Code hardening (small):** a pre-backtest **spread-degeneracy guard** in the engine entry path (or `run.py`/`validate.py`): if a loaded frame has zero-spread ratio above a documented threshold (e.g. >1%) **and** `min_spread_pips == 0.0`, refuse with a clear message pointing to `spread_sensitivity.py` scenarios / the floor — rather than silently running on free execution.
- Keep `min_spread_pips` as an explicit *scenario* knob (do not change the 0.0 default, because that would silently alter every backtest); require authors to pick a scenario (OBSERVED/REALISTIC/...) for any conclusion, as `spread_sensitivity.py` already intends.
- Re-establish fresh 60/20/20 splits with `backtest.data.research_split` on the completed four-symbol set; record provenance (dukascopy-node version, download ranges) in the split manifests for reproducibility.

### 4.4 Tests to add

- Data: integration check that all four `data/*_m5.csv` have `spread_zero_count == 0` after the EURJPY run (enforced in CI-style validation gate).
- Code: guard unit test — a frame with >1% zero-spread and no floor raises; with a floor set, it runs; ≤ threshold runs.
- Split: fresh `validate_split_isolation` passes for all symbols (existing function, new artifacts).
- Cost robustness: `spread_sensitivity` runs on the clean multi-year data and reports all 5 scenarios (framework exists — execution task, not new code).

### 4.5 Existing outputs invalidated

- Everything derived from the old MT5-era data becomes non-reproducible once files are replaced: per-symbol `outputs/<symbol>/reports/*` (old 90k basis), `outputs/benchmark/*`, `outputs/phase6/*`, `outputs/market_research/*`. These are **already invalidated** (`HISTORICAL_OUTPUTS_STATUS.md`); they remain as evidence but must not be cited as results.
- The **old EURJPY file is replaced** — its diagnostic value is preserved in git history; do not delete it mid-migration.

### 4.6 Frozen V1/V2 impact

- None to code. Their *reported results* will be re-baselined on clean data (fresh runs, same frozen rules) — this is a data requirement, not a strategy change.

### 4.7 Holdout impact

- The old holdout artifacts are compromised (Phase 6). A2 **creates brand-new splits**; the new holdout (202x–latest ~20%) remains **sealed** and is not evaluated in this or any remediation step.

---

## 5. Minor hygiene

### 5.1 Inspection

- `.gitignore` contains only `venv` and `meta logins.txt`. The tree is cluttered with untracked artifacts: `backtest/**/__pycache__/` (*.cpython-314.pyc), `.pytest_cache/`, throwaway `data/diag_seq/`, `data/poc*/`, `data/smoke_*/`, `data/temp_range_test/`, several **0-byte** Dukascopy chunk CSVs (e.g. `data/eurgbp-m5-ask-2021-01-01-2021-01-07.csv`, `data/eurjpy-m5-ask-2021-01-14-2021-01-21.csv`, `data/eurgbp-m5-bid-2021-01-01-2026-09-10.csv`).
- `git status` shows `data/eurusd_m5.csv` tracked-and-modified (canonical data is git-tracked) while `eurgbp/eurjpy/gbpusd_m5.csv` are untracked — **inconsistent tracking policy** for the same class of file.
- Python: active interpreter is **3.14.7** (`python`), 3.13 is also installed; `BACKTEST.md:8-10` documents a `venv/` with 3.13 and "matplotlib (already installed)" — **no `venv/` exists** and **matplotlib is absent from `requirements.txt`** (which pins numpy/pandas/ta/metatrader5/dateutil/six/tzdata).
- Stale generated outputs remain tracked because `.gitignore` doesn't cover them.

### 5.2 Exact problem

Repository noise (caches, diag artifacts, 0-byte files, undifferentiated tracking of canonical CSVs) makes diffs and releases hard to review; documented interpreter/venv state contradicts reality (3.13 vs 3.14; no venv; matplotlib unlisted), risking silent environment drift and reproducibility loss.

### 5.3 Smallest safe fix

- Expand `.gitignore`: `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `data/diag_seq/`, `data/poc*/`, `data/smoke_*/`, `data/temp_range_test/`, 0-byte/raw Dukascopy chunk CSVs (`data/*-m5-*-*.csv`), and a documented decision on canonical CSVs (recommend: **track** the canonical `data/{symbol}_m5.csv` as versioned evidence — they are the research dataset — and ignore all raw/intermediate artifacts).
- Never delete invalidated outputs; only *ignore* generated artifacts going forward.
- Pin the environment: add `.python-version` (3.13) and/or a documented Python version in `BACKTEST.md`; add `matplotlib` (and anything else imported, e.g. `pytest`) to `requirements.txt`; note that `bot.py`'s `MetaTrader5` wheel must match the chosen interpreter.
- Record in `HISTORICAL_OUTPUTS_STATUS.md` (append, don't rewrite) which outputs are now stale under the new data and that the interpreter baseline moved to 3.13.

### 5.4 Tests

- None behavioral. Verification = `python -m pytest tests` green under the pinned interpreter, and `git status` clean of cache/artifact noise.

### 5.5 Existing outputs invalidated

- None (no numeric meaning changes). Only git/ignored-file bookkeeping and requirements metadata change.

### 5.6 Frozen strategies / holdout

- Unaffected.

---

## 6. Ordered implementation sequence (safest first)

Hairstanding principle: each step preserves the default behavior of everything before it, is test-covered, and leaves the holdout sealed.

| # | Step | Risk / blast radius | Why this order |
|---|---|---|---|
| 0 | **Hygiene fence** (expand `.gitignore`, pin interpreter to 3.13, add `matplotlib`/`pytest` to requirements, document venv re-creation, ignore diag/0-byte/cache artifacts) | Zero behavioral risk; repo-policy only | Touches nothing numeric; makes every later output change visible in git. Do in parallel at any time. |
| 1 | **A4 — single win/loss classifier on `net_money`** (+ consistency tests) | Contained: `backtester._finalize`, `metrics.py`; no engine, data, strategy, or holdout contact; historical metrics already invalidated | **Safest substantive issue to fix first**: pure local consistency change, deterministic, fully unit-testable, and the outputs it affects are already-invalidated win-rate figures. |
| 2 | **A5 — additive `risk_fraction` sizing mode** (default `fixed` unchanged, separate output paths) | Additive, default-preserving; touches cost model via per-trade lot resolution | Self-contained config change with an untouched default; only new-money outputs appear. |
| 3 | **A3 — live/backtest candle-timing parity** (bot reads `copy_rates_from_pos(…, 1, …)`, pure `signal_from_candles` helper + repaint regression test) | Requires a **documented, minimal unfreeze** of `bot.py`; strategy rules unchanged; engine untouched in the minimal step | Live-layer correctness matters most for any future research→live step, but it touches a frozen file → ranked after the code-only fixes. The engine ATR-bar decision (§1.3) is deliberately **deferred** and gated behind a frozen-baseline re-validation. |
| 4 | **A2 — complete EURJPY Dukascopy acquisition, spread-degeneracy guard, fresh runs + new sealed splits** | Data-heavy, long run; the only step that replaces datasets and re-creates splits | Highest cost and the only step that re-establishes the research foundation (fresh splits, clean spread, new holdout) → last, gated on validation (`validate_all` all-clear). |

### Elaboration of the answer "safest issue to fix first"

**A4 (win/loss classification consistency) is the safest issue to fix first.** It is the only one that is (a) purely code-local (one classifier reused in `backtester` + `metrics`), (b) fully unit-testable without data/MetaTrader dependencies, (c) orthogonal to the engine's entry/fill/exit geometry and to both frozen strategies, (d) incapable of touching the holdout, and (e) whose only "downside" — a drift in future win-rate figures — concerns outputs that `HISTORICAL_OUTPUTS_STATUS.md` has already invalidated. Its fix additionally removes a real, quantifiable inconsistency (commission ≈ 7 pips at 0.10 lot means the pips-vs-money label disagreement is material, §2.1).

---

*End of plan. No repository files were modified during its production; only this document was created.*