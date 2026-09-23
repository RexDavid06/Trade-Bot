# PRE-DEMO REMEDIATION REPORT

**Date:** 2026-09-23
**Type:** Engineering remediation only (per `TASK.md`). No strategy created, no optimization, no market research, no MT5 connection/orders, no EURJPY changes, no validation/holdout touched, no historical reports deleted.
**Scope:** A3 (live candle timing), A5 (sizing parity), Python environment, regression tests.

---

## 1. A3 — live candle timing (before/after)

**Before**
- `bot.py:31`: `copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)` — with `start_pos = 0` the **last row was the currently-forming candle**.
- `bot.py:124-128`: signal inputs (`ema50/ema200/rsi/atr`) and `bot.py:135-140` signal decision + fill were computed on `df.iloc[-1]` (**forming** candle), i.e. the signal could repaint as the forming bar evolved, and live decisions were **not** comparable to the backtest engine, which signs only closed candles and fills next-open.

**After**
- **Pure helper `bot.signal_from_candles(df)`** evaluates V1 rules **exclusively on `df.iloc[-2]` — the last COMPLETED candle** (never `df.iloc[-1]`). Returns `(BUY|SELL|None, atr)` where `atr` is the closed candle's ATR (used for SL/TP distances).
- `bot.check_signal()` now calls the helper; the new-candle detector (`candle_time` from `df.iloc[-1]`) and the `position_exists()` / `spread_ok()` guards are unchanged.
- MT5 connection + `while` loop moved into `bot.main()` (guarded by `if __name__ == "__main__"`), so importing `bot` for tests does **not** connect to MT5 and cannot place orders.
- Strategy rules are byte-for-byte the same: BUY iff `ema50 > ema200` and `40 < rsi < 55`; SELL iff `ema50 < ema200` and `45 < rsi < 60`.
- **No parameter changes**: EMA50/200, RSI14, ATR14, 1% risk, SL/TP multiples unchanged.

**Regression tests (new, `tests/test_closed_candle_signal.py`)**
- forming candle (last row) mutated → signal unchanged (no repaint);
- last closed candle mutated → signal changes accordingly;
- candle ordering correct (forming row in SELL zone cannot override a BUY closed candle);
- insufficient history (`None` / single row) and `NaN` warm-up → `(None, None)`;
- parity: `signal_from_candles(df) == strategy.signal_at(df, len(df)-2)`.

---

## 2. A5 — sizing parity (before/after)

**Before**
- Backtest: `CostConfig.lot_size = 0.10` fixed for every trade (`backtester._finalize`).
- Live (`bot.py:77-82`): `lot = max(round(balance * 0.01 / 1000, 2), 0.01)` — 1% of balance with a nominal 100-pip SL at $10/pip/lot (= divisor 1000), balance-dependent, **not SL-distance-aware**.
- No explicit, shared sizing model; dollar P&L between backtest and live were not transferable.

**After — additive, default-preserving sizing model**
- `CostConfig` gains: `lot_size_mode` ("fixed" default | "risk_fraction"), `risk_percent` (1.0), `assumed_sl_pips_for_lot` (100.0), `pip_value_per_lot` (10.0), `min_lot` (0.01), `lot_round` (0.01), `maximum_lot` (100.0).
- **`lot_for_balance(balance, cfg)`** centralizes the formula. `"fixed"` returns `cfg.lot_size` unchanged → **every existing frozen backtest reproduces identically**. `"risk_fraction"` computes `lot = balance * (risk_percent/100) / (assumed_sl_pips_for_lot * pip_value_per_lot)` then `round` to `lot_round`, floor at `min_lot`, cap at `maximum_lot`. With defaults this is exactly `bot.py`'s `max(round(balance * 0.01 / 1000, 2), 0.01)` → 0.10 lots at $10k.
- Engine: the lot is resolved **per trade from the running balance** at entry (`backtester.run_backtest`), stored on the position, and used for `net_money`/commission in `_finalize`. Signal, entry/exit geometry and pips are untouched.
- **Documented sizing model**
  - Backtest sizing (default `fixed`): constant 0.10 lots.
  - Live sizing (`bot.py`): `risk = balance × 1%`; `lot = risk / 1000`; normalized `round(x, 2)`, floor 0.01; no cap in bot.py.
  - `risk_fraction` backtest mode = same formula via explicit parameters (matches live at start, diverges as equity moves).
  - Risk calc: `balance × risk_percent/100`; equivalent assumed SL distance = `assumed_sl_pips_for_lot` pips; money risked/lot = `assumed_sl_pips_for_lot × pip_value_per_lot` = $1000.
  - Broker min lot: 0.01. Lot step: 0.01. Max lot: `maximum_lot` (bot.py: none; config default 100.0 safety cap).
- `Trade.lot` added to the dataclass and `to_dict()` for transparency.

**Regression tests (new, `tests/test_sizing_parity.py`)**
- `lot_for_balance`: fixed unchanged; risk_fraction reproduces bot formula at $10k (0.10); balance scaling; min-lot floor; max-lot cap; 0.01-step rounding; risk-percent scaling.
- Engine parity: `fixed` vs `risk_fraction` produce identical trade lists (entry/exit/times/direction/result/reason/pips) differing only in lot/money; `risk_fraction` deterministic (two runs identical); first lot equals 0.10; equity grows on a winning streak and end balance = start + Σnet.

---

## 3. Python environment (before/after)

| Item | Before | After |
|------|--------|-------|
| `.python-version` | 3.13 | 3.13 (unchanged) |
| System Python | 3.14.7 (deps present) | 3.14.7 (untouched) |
| `venv/` | **existed but contained only `pip`** | **fully populated** from `requirements.txt` |
| `venv\Scripts\python.exe --version` | Python 3.13.15 | **Python 3.13.15** |
| venv packages | pip 26.2.1 only | metatrader5 5.0.5640, numpy 2.4.3, pandas 3.0.1, ta 0.11.0, matplotlib 3.11.2, pytest 9.1.1, dateutil, six, tzdata, plus pytest deps |
| Install method | — | `venv\Scripts\python.exe -m pip install -r requirements.txt` (no global installs, no version changes) |
| Tests | passed only under system Python | **passed under venv 3.13** |

No global packages were installed or upgraded; no dependency versions were modified.

---

## 4. Tests (before/after)

| | Before | After |
|---|--------|-------|
| Test files | 3 | **5** (added `test_closed_candle_signal.py`, `test_sizing_parity.py`) |
| Count (system Python) | 74 passed | **96 passed** |
| Count (venv 3.13) | not runnable (`No module named pytest`) | **96 passed** |
| Command | `venv\Scripts\python.exe -m pytest tests -q` | same |

Final test count: **96 passed** under `venv\Scripts\python.exe -m pytest tests -q`.

---

## 5. Files changed

| File | Change |
|------|--------|
| `bot.py` | A3: pure `signal_from_candles()` on last closed candle; MT5 connect/loop under `main()`; `check_signal()` uses the helper. Rules/params unchanged. |
| `backtest/config.py` | A5: sizing fields on `CostConfig` + `lot_for_balance()` helper. |
| `backtest/backtester.py` | A5: per-trade lot resolution from running balance; `Trade.lot`; `_finalize` uses position lot for money/commission. Default `fixed` reproduces prior behavior. |
| `tests/test_closed_candle_signal.py` | NEW: A3 regression tests (forming/closed/ordering/parity). |
| `tests/test_sizing_parity.py` | NEW: A5 sizing tests (unit + engine parity/determinism). |

Not modified: `TASK.md` (pre-existing working-tree change), strategy files, `eurjpy_m5.csv`, `outputs/**`, historical reports, `.gitignore`, `requirements.txt`, `.python-version`. `CURRENT_PROJECT_STATE_AUDIT.md` remains untracked (unchanged).

---

## 6. Strategy behavior confirmation

- V1 rules in `bot.py` (BUY/SELL conditions, EMA/RSI/ATR periods, risky 1%, SL/TP multiples, one-position rule, spread gate) are **unchanged**.
- The backtest `strategy.signal_at` and `backtest.config.StrategyConfig` are **untouched**. V1/V2, Strategies 01–03 untouched.
- Engine signals still on closed candles with next-open fills; `signal_from_candles` was proven equal to `signal_at` on the same closed candle (parity test).
- No parameter optimization of any kind was performed.

---

## 7. Validation / holdout untouched

- No code reads `outputs/splits/*` or old Phase 5/6 holdout artifacts.
- `research_safety.py`, `phase6.py`, `phase5_research.py`, `edge_research.py`, `multi_hour_research.py`, `market_discovery.py` **not modified, not run**.
- Historical outputs and reports left exactly as-is (no deletion, no "repair").
- EURJPY dataset **not regenerated**; A2 stays **unresolved** (documented as open below).

---

## 8. Remaining blockers

**Execution layer**
- A3 fixed, but the engine's ATR-bar decision (§1.3 / E1 in the audit: engine uses fill-candle ATR for SL/TP vs live uses closed-candle ATR) is **deferred** by design — documented, not part of this task.
- `bot.py` order-result handling is still print-only (no retry/retcode handling) — unchanged, not in scope.
- No in-repo proof of current MT5 broker connectivity (remediation deliberately does not connect).

**Data / research**
- **A2 incomplete:** `eurjpy_m5.csv` is still the old 90k MT5 file (27% zero-spread, 2025-06-26→2026-09-10). **Unresolved** per TASK 4.
- Fresh sealed 60/20/20 splits exist for EURUSD/EURGBP/GBPUSD; EURJPY missing until migrated.
- No cost-surviving strategy exists; V1 remains negative after costs (unchanged — not part of engineering remediation).

**Environment**
- None remaining for the documented run path: venv is populated and the suite passes under 3.13.

---

## 9. Is the execution layer technically ready for a future demo strategy?

**Engineering: YES** — with confirmed conditions:
- Live signal timing now matches backtest closed-candle semantics (A3), protected by regression tests.
- Sizing is explicit and consistent between backtest (`fixed` default) and live (`risk_fraction` mode) with a documented, tested mapping.
- The documented Python environment is restored: `venv\Scripts\python.exe` = 3.13.15, full deps, **96/96 tests pass under the venv**.
- Limitations that remain are documented and non-blocking for a **pipeline/execution demo only**: print-only order-result handling, deferred ATR-bar alignment, and untested live broker connectivity (deliberately not exercised here).

**Scientific readiness: NO** — there is still **no economically validated strategy**; V1's measured expectancy is negative. A future demo run may be used strictly as an **execution observability test of the frozen V1 rules**, never as evidence of a profitable edge. This does not block the execution layer itself.

---

*End of remediation. Only `bot.py`, `backtest/config.py`, `backtest/backtester.py`, and the two new test files were modified; `PRE_DEMO_REMEDIATION_REPORT.md` is the final deliverable. No MT5 connection, no orders, no optimization, no new strategy, no holdout/validation access.*