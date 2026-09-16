# PHASE 0 — DATA & BACKTEST INTEGRITY REPORT

**Date:** 2026-09-10
**Status:** IN PROGRESS
**Objective:** Establish trustworthy market-data, instrument-configuration, execution-cost, backtesting, and research-split foundation

---

## 1. Objective

Phase 0 establishes the research infrastructure before any further edge research. This is NOT a strategy-development phase. The purpose is to make the research infrastructure trustworthy.

---

## 2. Previous Integrity Failures

| Failure | Impact | Fixed In Phase 0? |
|---------|--------|-------------------|
| Hardcoded pip=0.0001 for all symbols | EURJPY results meaningless (100x error) | YES — `instruments.py` |
| Phase 6 used full data | Holdout compromised for all 28 hypotheses | YES — `research_split.py` |
| Phase 5 handoff contained fabricated numbers | All Phase 5 conclusions invalid | DOCUMENTED — `HISTORICAL_OUTPUTS_STATUS.md` |
| 48.3% zero-spread bars on EURUSD | Backtest costs underestimated | DOCUMENTED — spread sensitivity framework |
| No tests for pip conversion | Regression risk | YES — `tests/test_instruments_and_backtest.py` |
| Phase 6 markdown reports wrong headers | Misleading metadata | DOCUMENTED — will be fixed in new reports |
| No spread sensitivity framework | Cannot assess cost robustness | YES — `spread_sensitivity.py` |
| No holdout protection | Easy to accidentally contaminate holdout | YES — `research_safety.py` |

---

## 3. Current Data Inventory

| Symbol | File | Bars | Period | Spread Quality |
|--------|------|------|--------|---------------|
| EURUSD | `data/eurusd_m5.csv` | 90,000 | Jun 2025 → Sep 2026 | POOR (48.3% zero-spread) |
| EURGBP | `data/eurgbp_m5.csv` | 90,000 | Jun 2025 → Sep 2026 | MODERATE (19.6% zero-spread) |
| EURJPY | `data/eurjpy_m5.csv` | 90,000 | Jun 2025 → Sep 2026 | MODERATE (27.0% zero-spread) |
| GBPUSD | `data/gbpusd_m5.csv` | 90,000 | Jun 2025 → Sep 2026 | MODERATE (24.6% zero-spread) |

**Total:** 360,000 bars across 4 symbols, ~15 months each.

**Classification:** EXPLORATORY DATA — NOT RESEARCH-GRADE

---

## 4. Instrument Configuration

**New file:** `backtest/instruments.py`

| Symbol | Pip | Point | Digits | Contract Size | Spread Interpretation |
|--------|-----|-------|--------|---------------|----------------------|
| EURUSD | 0.0001 | 0.00001 | 5 | 100,000 | points |
| EURGBP | 0.0001 | 0.00001 | 5 | 100,000 | points |
| EURJPY | **0.01** | **0.001** | **3** | 100,000 | points |
| GBPUSD | 0.0001 | 0.00001 | 5 | 100,000 | points |

**Key change:** EURJPY now uses correct pip=0.01 (was 0.0001). This is enforced by the test suite.

---

## 5. Pip/Point Conventions

**Before Phase 0:**
- `config.py` hardcoded `pip = 0.0001` and `point = 0.00001` for all symbols
- EURJPY calculations were 100x too large in "pip" terms
- No way to switch pip conventions per symbol

**After Phase 0:**
- `instruments.py` provides centralized, per-symbol pip/point configuration
- `get_instrument(symbol)` returns correct values for any supported symbol
- `price_to_pips()` and `pips_to_price()` handle conversions correctly
- Test suite prevents regression to hardcoded 0.0001

---

## 6. Data Validation Methodology

**Existing:** `backtest/data/data_validation.py` — validates structure, OHLC, gaps, spread

**Improved:** `backtest/data/validate_all.py` — runs validation on ALL symbols with instrument-specific checks

**Validation checks performed:**
- Required columns present
- Correct data types
- Chronological ordering
- Duplicate timestamps
- Missing bars / gaps
- OHLC validity (high >= low, close within range, etc.)
- Spread distribution (zero-spread percentage, median, extremes)
- Price range reasonableness per symbol

---

## 7. Spread-Quality Assessment

| Symbol | Zero-Spread % | Median Spread (pts) | Assessment |
|--------|--------------|-------------------|------------|
| EURUSD | 48.3% | 5.22 | POOR — feed artifact, not real zero-spread |
| EURGBP | 19.6% | 12.15 | MODERATE |
| EURJPY | 27.0% | 19.64 | MODERATE |
| GBPUSD | 24.6% | 8.73 | MODERATE |

**EURUSD critical issue:** 48.3% of bars have spread=0, uniformly across all weekdays. This is a feed artifact, not a real zero-spread market. The last 200 bars are all zero-spread (stale feed).

**Impact:** Backtests on zero-spread bars assume lower costs than realistic. This inflates returns (or understates losses).

**Recommendation:** Fresh multi-year data with clean spread column is required before live deployment decisions.

---

## 8. Backtester Execution Model

**Engine:** `backtest/backtester.py`

| Aspect | Implementation | Verified? |
|--------|---------------|-----------|
| Signal timing | Closed candle `i`, fill at open of `i+1` | YES ✅ |
| Entry price | `open[i+1]` | YES ✅ |
| Exit price | SL/TP against subsequent high/low | YES ✅ |
| Spread application | Once per trade, round-turn | YES ✅ |
| Slippage | 0.5 pips per side (configurable) | YES ✅ |
| Stop-loss | `entry ± 1.5 × ATR` | YES ✅ |
| Take-profit | `entry ± 3.0 × ATR` | YES ✅ |
| Position state | One position at a time | YES ✅ |
| Trade overlap | Prevented | YES ✅ |
| Look-ahead bias | None (causal signals) | YES ✅ |
| Intrabar rule | Conservative (SL first if both touch) | YES ✅ |

**New:** `_cost_price()` now supports `spread_multiplier`, `min_spread_pips`, and `extra_slippage_pips` for cost sensitivity analysis.

---

## 9. Cost Model

**Default costs (from `config.py`):**

| Cost Component | Value | Applied |
|---------------|-------|---------|
| Spread | Per-entry-candle `spread` column (points × point) | Round-turn |
| Slippage | 0.5 pips per side | Round-turn (1.0 pip total) |
| Commission | $7.00 per lot | Round-turn, USD |
| Lot size | 0.10 lots | Fixed |
| Starting balance | $10,000 | Fixed |

**New cost scenarios (from `spread_sensitivity.py`):**

| Scenario | Spread | Min Spread | Extra Slippage | Commission |
|----------|--------|-----------|----------------|------------|
| OBSERVED | 1× | 0 pips | 0 | $7 |
| STRESSED_2X | 2× | 0 pips | 0 | $7 |
| MINIMUM_1PIP | 0× | 1 pip | 0 | $7 |
| REALISTIC | 1× | 0.5 pips | 0.2 pips | $7 |
| HIGH_COST | 2× | 1 pip | 0.5 pips | $14 |

---

## 10. Research Split Methodology

**New file:** `backtest/data/research_split.py`

**Method:** Chronological fraction-based (60/20/20)

**Split rules:**
- Development (60%): Earliest data, may be used for hypothesis discovery
- Validation (20%): Middle data, may be used for configuration selection
- Holdout (20%): Latest data, MUST remain untouched until final confirmation

**Split isolation:**
- No overlap between splits
- Strict chronological ordering (dev < val < holdout)
- Metadata includes holdout protection warning
- Split assignments saved to CSV for reproducibility

---

## 11. Holdout Protection

**New file:** `backtest/research_safety.py`

**Safeguards implemented:**
1. `SplitGuard` — restricts which splits a research runner can access
2. `HoldoutGuard` — requires explicit reason to access holdout
3. `ResearchContext` — tracks split access history
4. `load_split_safe()` — validates split exists before loading
5. `validate_no_holdout_access()` — decorator that blocks holdout access

**Usage:**
```python
from backtest.research_safety import SplitGuard, HoldoutGuard

# Default: only dev split allowed
guard = SplitGuard(allowed_split="dev")
guard.require("dev")  # OK
guard.require("holdout")  # raises ValueError

# Holdout requires explicit access
holdout_guard = HoldoutGuard()
holdout_guard.request_access("Final validation")  # OK
holdout_guard.is_accessible()  # True
```

---

## 12. Tests Added

**New file:** `tests/test_instruments_and_backtest.py`

| Test Category | Count | Status |
|--------------|-------|--------|
| Pip value per symbol | 4 | PASS ✅ |
| Point value per symbol | 4 | PASS ✅ |
| Price-to-pip conversion | 2 | PASS ✅ |
| Pip-to-price conversion | 2 | PASS ✅ |
| Spread cost conversion | 2 | PASS ✅ |
| Instrument lookup | 2 | PASS ✅ |
| P&L calculation | 2 | PASS ✅ |
| Spread application | 1 | PASS ✅ |
| EURJPY regression | 1 | PASS ✅ |
| Slippage round-turn | 4 | PASS ✅ |
| **Total** | **24** | **ALL PASS** |

**Critical regression test:** `test_eurjpy_pip_is_not_0001` — fails if someone reintroduces hardcoded 0.0001 for EURJPY.

---

## 13. Remaining Data Requirements

| Requirement | Status | Priority |
|-------------|--------|----------|
| Multi-year data (3-5+ years) | NOT AVAILABLE — current data is ~15 months | HIGH |
| Clean spread column (no zero-spread artifacts) | NOT AVAILABLE — 48.3% zero-spread on EURUSD | HIGH |
| Realistic bid/ask spread history | NOT AVAILABLE — spread column is broker-specific | MEDIUM |
| Fresh MT5 export with correct pip scaling | AVAILABLE — can be done with `dump_mt5_multi.py` | ACTION REQUIRED |

**Data acquisition tooling created:** `dump_mt5_multi.py` exports all 4 symbols from MT5 with retry logic.

---

## 14. What Is Now Trustworthy

| Component | Trustworthy? | Notes |
|-----------|-------------|-------|
| Instrument configuration | YES | Pip/point values correct, tested |
| Pip conversion logic | YES | Tested for all 4 symbols |
| Backtester signal timing | YES | No look-ahead, causal signals |
| Backtester cost model | YES | Configurable, auditable |
| Spread sensitivity framework | YES | 5 scenarios available |
| Test suite | YES | 24 tests, all passing |
| Research split methodology | YES | Chronological, isolated |
| Holdout protection | YES | Explicit guards in place |

---

## 15. What Is Still Not Trustworthy

| Component | Trustworthy? | Why |
|-----------|-------------|-----|
| Current market data | NO | 15 months, broken spread feed |
| EURJPY Phase 5 results | NO | Old pip scaling still in results.json |
| Phase 6 findings | NO | Holdout compromised |
| Phase 5 conclusions | NO | Handoff numbers fabricated |
| Spread realism | NO | 48.3% zero-spread on EURUSD |
| Multi-regime validation | NO | Single market regime (Jun 2025 → Sep 2026) |

---

## 16. Explicit Recommendation for Phase 1

### BLOCKED — NEED FRESH DATA

**Reasoning:**

1. The current data is 15 months (one market regime) — insufficient for robust strategy validation
2. EURUSD has 48.3% zero-spread bars — backtest cost assumptions are unreliable
3. The holdout is compromised — no clean out-of-sample dataset exists
4. The backtester infrastructure is now trustworthy (tests pass, instrument config correct), but it needs clean multi-year data to produce meaningful results

**What must happen before Phase 1:**

1. Export fresh multi-year data (3-5+ years) using `dump_mt5_multi.py`
2. Validate new data with `python -m backtest.data.validate_all`
3. Create new research splits with `python -m backtest.data.research_split`
4. Verify clean spread column (no zero-spread artifacts)
5. Re-run Phase 5/6 on new data with proper split isolation

**The project is ready for fresh data. The infrastructure is in place.**

---

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `backtest/instruments.py` | CREATED | Centralized instrument configuration |
| `backtest/spread_sensitivity.py` | CREATED | Cost sensitivity framework |
| `backtest/research_safety.py` | CREATED | Holdout protection safeguards |
| `backtest/data/validate_all.py` | CREATED | Multi-symbol data validation |
| `backtest/data/research_split.py` | CREATED | Clean research splits with protection |
| `dump_mt5_multi.py` | CREATED | Multi-symbol MT5 data export |
| `tests/test_instruments_and_backtest.py` | CREATED | 24 tests for critical corrections |
| `HISTORICAL_OUTPUTS_STATUS.md` | CREATED | Status of previous outputs |
| `backtest/config.py` | MODIFIED | Added spread_multiplier, min_spread_pips, extra_slippage_pips |
| `backtest/backtester.py` | MODIFIED | Updated _cost_price() for sensitivity framework |

---

*Phase 0 establishes the foundation. Research integrity comes before strategy performance.*
