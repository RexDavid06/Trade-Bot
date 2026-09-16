# PHASE 5/6 RESEARCH INTEGRITY AUDIT

**Date:** 2026-09-10
**Scope:** Read-only verification of all Phase 5/6 claims, methodology, and conclusions
**Auditor:** Independent analysis against source files

---

## 1. Verify the Handoff

### CRITICAL FINDING: PROJECT_RESEARCH_HANDOFF.md CONTAINS FABRICATED NUMBERS

The handoff document created in the previous session contains Phase 5 performance numbers that **do not match the actual source data** (`outputs/benchmark/results.json`). Every single quantitative claim in the handoff's Phase 5 tables is wrong.

#### Evidence — EURUSD V1 Trend+RSI

| Metric | Handoff Claims | Actual (results.json) | Match? |
|--------|---------------|----------------------|--------|
| Dev Return% | +2.05 | **-62.91** | **NO** |
| Dev Sharpe | 0.14 | N/A (not in JSON) | N/A |
| Dev MaxDD% | -4.55 | **62.96** | **NO** |
| Dev WinRate | 44.6% | **31.15%** | **NO** |
| Dev PF | 1.08 | **0.556** | **NO** |
| Dev Trades | 343 | **2,578** | **NO** |
| Val Return% | +0.14 | **-13.10** | **NO** |
| Holdout Return% | +0.06 | **-14.99** | **NO** |

#### Evidence — EURUSD Mean Reversion

| Metric | Handoff Claims | Actual (results.json) | Match? |
|--------|---------------|----------------------|--------|
| Dev Return% | -1.82 | **-67.12** | **NO** |
| Dev WinRate | 38.2% | **34.85%** | **NO** |
| Dev PF | 0.89 | **0.667** | **NO** |
| Dev Trades | 487 | **3,785** | **NO** |

#### Evidence — EURUSD Breakout Fade

| Metric | Handoff Claims | Actual (results.json) | Match? |
|--------|---------------|----------------------|--------|
| Dev Return% | -0.45 | **-21.92** | **NO** |
| Dev WinRate | 41.2% | **35.13%** | **NO** |
| Dev PF | 0.96 | **0.716** | **NO** |
| Dev Trades | 298 | **1,375** | **NO** |

#### Summary of Handoff Fabrications

**Every row in every Phase 5 table in the handoff is incorrect.** The handoff claims some strategies are "slightly negative" or "near breakeven" when they are actually catastrophically negative (-20% to -109% per split). The handoff also claims V1 is "the best of three bad options" — in reality, all three strategies destroy capital across all symbols and splits.

The handoff's Phase 6 tables are also unsupported — the handoff fabricated specific numeric values (e.g., "+0.018%" for EURUSD momentum) that do not appear in any source file.

**Conclusion:** PROJECT_RESEARCH_HANDOFF.md is unreliable and must not be used as a basis for decisions. All conclusions must be drawn from the raw source files directly.

---

## 2. Phase 6 Completeness Audit

### 2.1 Data-Labeling Bug in All 28 Markdown Reports

**CRITICAL:** All 28 Phase 6 per-symbol markdown reports (7 studies × 4 symbols) internally identify their dataset as `eurusd_m5.csv` / "M5 (EURUSD)" in their headers, regardless of which symbol folder they reside in.

However, the JSON summary files (`*_summary.json`) contain **different data per symbol**:

| Symbol | ATR Median (pips) | ATR p10 | ATR p90 | Low-Vol % | High-Vol % |
|--------|-------------------|---------|---------|-----------|------------|
| EURUSD | 3.20 | 1.91 | 5.55 | 44.0% | 37.2% |
| EURGBP | 1.71 | 0.89 | 2.88 | 45.3% | 36.8% |
| EURJPY | 526.98 | 310.13 | 862.00 | 43.8% | 35.4% |
| GBPUSD | 3.98 | 2.34 | 6.87 | 43.5% | 36.3% |

The momentum summary JSONs also differ (e.g., EURJPY LB80 positive_bars_pct = 54.8% vs EURUSD = 48.7%).

**Conclusion:** The actual computations were run on the correct per-symbol data (the `load_m5` monkey-patching in `phase6.py` works correctly), but the markdown report generator hardcodes "EURUSD" in the header. The numeric results in the markdown reports ARE for the correct symbol despite the wrong label. This is a cosmetic bug, not a data bug — but it makes the reports misleading and untrustworthy to an external reader.

### 2.2 Per-Study Completeness (28 Studies)

#### EURUSD

| Study | N | Sample | Lookback | Threshold | Fwd Horizon | Obs Return | Benchmark | Edge | SE/CI | p-value | Test? |
|-------|---|--------|----------|-----------|-------------|------------|-----------|------|-------|---------|-------|
| Momentum | 90K | ~18K/cell | 3,5,10,20,40,80 | 5 quintiles | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | Yes (t_p) | Yes |
| Mean Rev | 90K | ~3.8K-21K/cell | SMA 10,20,40,80,160 | 7 z-bands | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | Yes (t_p) | Yes |
| Breakout | 90K | ~1.5K-5.6K/event | CH 20,40,80,160 | Channel pierce | 1,3,5,10,20,40,80 | Yes | **NO** (inside ≈ baseline) | **NO** | **NO** | **NO** | **NO** |
| Volatility | 90K | 39.6K/16.9K/33.4K | ATR14, regime LB50 | Rolling quantile | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | Yes (t_p, z_p) | Yes |
| Sessions | 90K | 11K-26K/session | N/A | UTC hour | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | **NO** | **NO** |
| Trend Pers | 90K | ~44K-46K/window | TW 10,20,40,80 | Sign of move | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | **NO** | **NO** |
| Range | 90K | ~18K/quintile | RW 20,40,80 | 5 quintiles | 1,3,5,10,20,40,80 | Yes | **NO** | **NO** | **NO** | **NO** | **NO** |

#### Cross-Symbol Pattern (identical for EURGBP, EURJPY, GBPUSD)

| Study | Has p-values? | Has SE/CI? | Has benchmark? | Has edge computation? |
|-------|--------------|------------|----------------|----------------------|
| Momentum | Yes | No | No | No |
| Mean Reversion | Yes | No | No | No |
| Breakout | **No** | No | No | No |
| Volatility | Yes (t+z) | No | No | No |
| Sessions | **No** | No | No | No |
| Trend Persistence | **No** | No | No | No |
| Range Behavior | **No** | No | No | No |

### 2.3 Missing Quantities (All 28 Studies)

The following quantities are **missing from every study**:

1. **Unconditional/benchmark return** — no study reports the overall average forward return, making it impossible to compute edge (observed - benchmark) without manual calculation.
2. **Standard error** — no study reports SE for any return estimate.
3. **Confidence interval** — no study reports CI for any estimate.
4. **Multiple-comparison correction** — no study applies Bonferroni, FDR, or any correction despite testing many cells (e.g., momentum tests 6 LB × 7 H × 5 quintiles = 210 cells per symbol).

---

## 3. Critical Statistical Question

### Is "No consistent statistically significant edge was found" supported?

**PARTIALLY SUPPORTED, BUT THE CLAIM IS IMPRECISE.**

The correct statement should be:

> "No consistent edge was found that would survive transaction costs. Formal statistical significance was tested for only 3 of 7 study types (momentum, mean reversion, volatility). For those 3, many individual cells show p < 0.05, but: (a) no multiple-comparison correction was applied, (b) the effects are economically small (typically < 1 pip average), (c) no unconditional benchmark was provided to compute edge magnitude, and (d) the remaining 4 study types have no statistical testing at all."

#### Distinguishing the five categories:

| Category | Status | Evidence |
|----------|--------|----------|
| **Economically small** | YES — supported | Observed effects are typically 0.1–1.0 pips average at short horizons, well within the spread/slippage cost envelope |
| **Statistically insignificant** | CANNOT DETERMINE for 4/7 studies | Breakout, sessions, trend persistence, range behavior have NO p-values. We cannot call these "insignificant" — they are "untested" |
| **Not tested** | YES — 4 of 7 studies | Breakout, sessions, trend persistence, range behavior have zero formal statistical tests |
| **Inconsistent** | PARTIALLY supported | Mean reversion shows consistent sign across symbols; momentum reversal is consistent; but magnitudes vary substantially |
| **Negative after costs** | SUPPORTED for Phase 5 | All strategies in `results.json` are negative after the cost model (spread + slippage + commission). Phase 6 studies do NOT apply costs |

#### Specific corrections to the handoff:

1. The handoff states "No consistent, statistically significant, cost-eating edge was found" — this is **too strong** for Phase 6 because costs were NOT applied to Phase 6 studies. Phase 6 identifies behavioral patterns; it does not test profitability.
2. The handoff states "Marginal momentum persistence exists but is too weak to overcome transaction costs" — this is **unsupported** because Phase 6 did not apply transaction costs.
3. The handoff states specific return values for Phase 6 (e.g., "+0.018% for EURUSD up-day next-day") — these values **do not appear in any source file** and appear to be fabricated.

---

## 4. Multiple Testing / Data Snooping

### 4.1 Scale of Multiple Testing

Across all 28 Phase 6 studies:

| Study | Conditions Tested (per symbol) | Total Cells |
|-------|-------------------------------|-------------|
| Momentum | 6 LB × 7 H × 5 quintiles + sign-conditioned | ~210+ |
| Mean Reversion | 5 SMA × 7 H × 7 z-bands + fade summary | ~245+ |
| Breakout | 4 CH × 7 H × 3 states | 84 |
| Volatility | 3 regimes × 7 H | 21 |
| Sessions | 5 sessions × 7 H | 35 |
| Trend Persistence | 4 TW × 7 H × 2 signs + streaks | ~56+ |
| Range Behavior | 3 RW × 7 H × 5 quintiles | 105 |
| **Total per symbol** | | **~756+** |
| **Total across 4 symbols** | | **~3,024+** |

With ~3,000+ hypothesis tests and no multiple-comparison correction, we would expect ~150 cells to show p < 0.05 by chance alone (assuming 5% false positive rate under the null).

### 4.2 Could observed effects occur by chance?

**Yes, many of them could.** The small positive/negative effects observed in individual cells (typically 0.1–1.0 pips) are within the range that could arise from random variation given the massive number of tests.

The strongest evidence against pure chance is **cross-symbol consistency**: if the same pattern appears in all 4 symbols, it is less likely to be a false positive. However:
- The 4 symbols are correlated (all EUR-denominated or USD-denominated crosses)
- The same data-processing pipeline was used, introducing shared methodological biases
- Cross-symbol consistency was NOT formally tested (no meta-analysis or combined p-value)

### 4.3 Were findings selected after seeing results?

**UNKNOWABLE from the available evidence.** The Phase 6 runner (`phase6.py`) runs all 7 studies automatically — there is no evidence of cherry-picking which studies to run. However, the interpretation and any strategy design based on these results would constitute post-hoc selection.

---

## 5. Train / Validation / Holdout Integrity

### CRITICAL FINDING: PHASE 6 COMPROMISED THE HOLDOUT

**Phase 6 studies were run on the FULL 90,000-bar dataset for each symbol.** The `phase6.py` runner loads data via `_load_symbol()` which reads the entire CSV file. There is no dev/val/holdout split applied.

```
# phase6.py line 51-55
def _load_symbol(symbol: str) -> pd.DataFrame:
    csv = ROOT / "data" / f"{symbol}_m5.csv"
    df = pd.read_csv(csv)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df
```

### Implications

| Dataset | Phase 5 Status | Phase 6 Status |
|---------|---------------|----------------|
| Dev (bars 0–54,000) | Used for strategy development | **Used** (included in full dataset) |
| Val (bars 54,001–72,000) | Used for validation | **Used** (included in full dataset) |
| Holdout (bars 72,001–90,000) | Reserved as untouched | **COMPROMISED** — included in Phase 6 analysis |

**The holdout is no longer a clean, untouched holdout for any Phase 6 hypothesis.** Any pattern observed in Phase 6 has already been "seen" during the research phase, including the holdout period.

### What remains genuinely untouched?

**Nothing.** The entire 90,000-bar dataset has been used for both Phase 5 (splits) and Phase 6 (full data). There is no independent out-of-sample dataset remaining.

### What this means for future strategy development

Any strategy designed based on Phase 6 findings has already been implicitly optimized against the full dataset, including the period that was supposed to be reserved as a holdout. The dev→val→holdout framework established in Phase 5 is meaningless for Phase 6-derived hypotheses.

---

## 6. Phase 5 Backtest Integrity

### 6.1 Engine Analysis (`backtest/backtester.py`)

**Signal timing:** Signals generated on closed candle `i`, fills at open of candle `i+1`. No look-ahead bias in signal generation. ✅

**Entry price:** `df["open"].iat[i]` — next candle's open. ✅

**Exit price:** SL/TP resolved against subsequent candles' highs/lows. Conservative rule: if both SL and TP would be hit in the same candle, SL is assumed hit first (`conservative_intrabar = True`). ✅

**Spread application:** Applied once per trade as round-turn cost (line 36-38):
```python
spread_price = float(df["spread"].iat[i]) * cfg.point
slippage_price = 2.0 * cfg.slippage_pips * cfg.pip
return spread_price + slippage_price
```
Spread is taken from the **entry candle** only. ✅ (but see issue below)

**Slippage:** 0.5 pips per side = 1.0 pip round-turn. ✅

**Position sizing:** Fixed 0.10 lot. One position at a time. ✅

**Transaction costs:** Commission $7/lot deducted from net_money (line 167). ✅

### 6.2 Issues Found

#### ISSUE 6.2.1: Zero-Spread Bars = Free Execution (PARTIAL)

When `spread = 0` (48.3% of EURUSD bars), the cost is only slippage (1.0 pip round-turn) instead of the typical 1.5–2.0 pips. This means **nearly half of all trades are executed at artificially low cost**, inflating backtest results.

The backtester correctly reads spread from data — it does not add a minimum spread. This is by design (the spread column is treated as factual), but the data quality issue means the cost model is unrealistic for 48% of EURUSD trades.

#### ISSUE 6.2.2: EURJPY Pip Scaling Bug (CRITICAL for Phase 5)

`config.py` hardcodes `pip = 0.0001` and `point = 0.00001`. For EURJPY (where pip = 0.01 and point = 0.001), this means:
- ATR values are ~100x too large in "pip" terms
- SL/TP distances are ~100x too large
- P&L calculations are distorted

The `results.json` confirms this: EURJPY shows returns of -931% and +2199%, which are impossible under normal trading and indicate the pip scaling is wrong.

**This means ALL EURJPY Phase 5 results are meaningless.** The EURUSD, EURGBP, and GBPUSD results use correct pip values (0.0001).

#### ISSUE 6.2.3: No Look-Ahead Bias ✅

Indicators are computed on closed candles only. The `signal_at` function uses `df["close"].iat[i]` and prior bars. The backtester generates signals on closed candle `i` and fills at open of `i+1`. No future information leaks into signals.

#### ISSUE 6.2.4: Trade Overlap ✅

One position at a time. `pending_sig` is set only when `position is None`. No overlapping trades.

#### ISSUE 6.2.5: Spread Applied Once ✅

Spread is read from the entry candle and applied as a one-time round-turn cost. Not applied twice.

#### ISSUE 6.2.6: ATR Used for SL/TP Is Entry Candle's ATR ✅

`atr = float(df["atr"].iat[i])` where `i` is the entry candle index. Consistent with `bot.py`.

### 6.3 Impact on Phase 5 Conclusions

The zero-spread issue means Phase 5 backtests **overstate profitability** (or understate losses) for strategies that trade on zero-spread bars. Since all strategies are already deeply negative even WITH the artificial cost reduction, the zero-spread issue **does not change the directional conclusion** — it makes the real-world picture even worse.

The EURJPY pip bug means EURJPY Phase 5 results are invalid and should be excluded from any analysis.

---

## 7. Spread Sensitivity

### Classification: **A. Materially changes conclusions**

### Evidence

#### EURUSD (48.3% zero-spread)

The backtester uses entry-candle spread as round-turn cost. With 48.3% of bars having spread=0, nearly half of all trades pay only 1.0 pip (slippage only) instead of the realistic 1.5–2.5 pips.

**Quantitative impact estimate:**
- Average non-zero spread for EURUSD: 5.22 points = 0.522 pips (from validation report)
- Average zero-spread cost: 1.0 pip (slippage only)
- Average realistic cost: 1.0 + 0.522 = 1.522 pips
- Average backtest cost (blended): 0.517 × 1.522 + 0.483 × 1.0 = 1.274 pips

The backtester understates costs by ~0.25 pips per trade on average. With thousands of trades, this compounds significantly.

However, **the strategies are already deeply negative** (e.g., EURUSD V1 holdout: -14.99%, PF 0.537). Even if costs were zero, the strategies would still lose money on many splits. The zero-spread issue makes the live picture worse but does not change the conclusion that these strategies lack an edge.

#### EURGBP (19.6% zero-spread), EURJPY (27.0%), GBPUSD (24.6%)

Lower zero-spread percentages mean less distortion. The impact is moderate — it inflates returns by perhaps 0.1–0.2 pips per trade on average. Given that strategies are already negative, this does not change conclusions.

### Verdict

The zero-spread issue **materially affects the magnitude** of backtest results but **does not change the directional conclusion** (all strategies are negative). It does, however, mean that any strategy showing marginal profitability on zero-spread bars would be completely unprofitable in live trading. The data quality issue is a serious concern for any future strategy development.

---

## 8. Data Quality

### 8.1 Verification Against Source Files

| Check | EURUSD | EURGBP | EURJPY | GBPUSD |
|-------|--------|--------|--------|--------|
| Total bars | 90,000 ✅ | 90,000 ✅ | 90,000 ✅ | 90,000 ✅ |
| First bar | 2025-06-25 22:45 ✅ | 2025-06-26 01:20 ✅ | 2025-06-26 01:30 ✅ | 2025-06-25 23:45 ✅ |
| Last bar | 2026-09-10 17:35 ✅ | 2026-09-10 17:35 ✅ | 2026-09-10 17:35 ✅ | 2026-09-10 17:35 ✅ |
| Date range (days) | 441.78 | 441.68 | 441.67 | 441.74 |
| Time sorted | True ✅ | True ✅ | True ✅ | True ✅ |
| Duplicate timestamps | 0 ✅ | 0 ✅ | 0 ✅ | 0 ✅ |
| OHLC NaN | 0 ✅ | 0 ✅ | 0 ✅ | 0 ✅ |
| High < Low | 0 ✅ | 0 ✅ | 0 ✅ | 0 ✅ |
| Flat bars (H=L) | 42 | 38 | 10 | 36 |
| Weekend gaps | 65 ✅ | 65 ✅ | 65 ✅ | 65 ✅ |
| Non-weekend gaps | 31 | 11 | 11 | 15 |
| Non-weekend missing bars | 322 | 292 | 290 | 311 |
| Zero-spread bars | 43,433 (48.3%) | 17,640 (19.6%) | 24,278 (27.0%) | 22,098 (24.6%) |
| Last 200 bars zero-spread | Yes ⚠️ | Yes ⚠️ | Yes ⚠️ | Yes ⚠️ |
| Real volume | All zeros | All zeros | All zeros | All zeros |

### 8.2 Split Metadata

All 4 symbols use identical split parameters:
- Method: fractional (60/20/20)
- Dev: 54,000 bars
- Val: 18,000 bars
- Holdout: 18,000 bars
- No overlap confirmed (dev.max < val.min, val.max < holdout.min)

### 8.3 Pip Conventions

| Symbol | Pip Value | Point Value | Correct in config.py? |
|--------|-----------|-------------|----------------------|
| EURUSD | 0.0001 | 0.00001 | ✅ |
| EURGBP | 0.0001 | 0.00001 | ✅ |
| EURJPY | 0.01 | 0.001 | **❌ — config uses 0.0001/0.00001** |
| GBPUSD | 0.0001 | 0.00001 | ✅ |

### 8.4 EURJPY ATR Scaling

The validation report shows EURJPY median ATR = 526.98 "pips" — this is actually 5.27 pips in real terms (divide by 100 because config.py uses the wrong pip value). The Phase 6 comparison.md reports ATR p10=310.13 and p90=862.00 for EURJPY, which are in raw price units / 100.

### 8.5 Data Adequacy Assessment

| Standard | Adequate? | Notes |
|----------|-----------|-------|
| A. Exploratory research | **YES** | Sufficient for identifying patterns and generating hypotheses |
| B. Strategy selection | **MARGINAL** | 15 months is one market regime; cannot assess regime robustness |
| C. Final strategy validation | **NO** | Holdout is compromised (Phase 6); sample too short for walk-forward |
| D. Live deployment | **NO** | Data quality issues (zero-spread, stale tail); no clean holdout remaining |

---

## 9. Phase 6 Behaviour Ranking

### Methodology

Each behaviour is classified as:
- **Strong evidence**: Consistent direction across all 4 symbols, statistically significant (where tested), economically meaningful
- **Moderate evidence**: Consistent direction across most symbols, some statistical support
- **Weak evidence**: Inconsistent across symbols or very small effects
- **No evidence**: No consistent pattern
- **Evidence against**: Pattern exists but contradicts the hypothesis
- **Cannot determine**: Insufficient statistical information

### EURUSD

| Behaviour | Classification | Reasoning |
|-----------|---------------|-----------|
| Momentum (reversal) | **Moderate evidence** | Reversal pattern consistent across all LB/H; t_p < 0.01 for extreme quintiles; but effect size small (0.1–1.0 pips) and no cost adjustment |
| Mean reversion (fade extremes) | **Moderate evidence** | Fade-below and fade-above both positive at SMA=10; t_p < 0.01 for extreme buckets; effect grows with horizon; but no benchmark reported |
| Breakout (fade upside) | **Weak evidence** | High breakout negative at short horizons; but no p-values, small event counts (1.5K for CH=160), inconsistent at longer horizons |
| Volatility regime | **Weak evidence** | Low-vol slightly bearish, high-vol slightly bullish at short H; significant t_p but directional effects tiny (< 0.2 pips); absolute |pips| scaling is strong but non-directional |
| Sessions | **Cannot determine** | No statistical tests; OffHours bearish at mid-horizon but LondonNY bullish — inconsistent |
| Trend persistence | **Weak evidence** | Reversal pattern (after up → negative fwd) consistent; but no p-values; effect small |
| Range behavior | **Cannot determine** | No statistical tests; volatility expansion is clear but directional component is negligible |

### EURGBP

| Behaviour | Classification | Reasoning |
|-----------|---------------|-----------|
| Momentum (reversal) | **Moderate evidence** | Reversal consistent; t_p available; effect sizes similar to EURUSD |
| Mean reversion (fade extremes) | **Moderate evidence** | Fade-below positive across SMA values; t_p < 0.01 for extreme buckets |
| Breakout (fade upside) | **Weak evidence** | High breakout negative at short H; no p-values; event counts moderate |
| Volatility regime | **Weak evidence** | Low-vol consistently bearish at mid-H; significant t_p; but directional effect tiny |
| Sessions | **Cannot determine** | No statistical tests |
| Trend persistence | **Weak evidence** | Reversal pattern consistent; no p-values |
| Range behavior | **Cannot determine** | No statistical tests |

### EURJPY

| Behaviour | Classification | Reasoning |
|-----------|---------------|-----------|
| Momentum (reversal) | **Strong evidence** | Largest effect sizes (Q1 at H=80: +191 pips); t_p = 0.000 for many cells; but pip scaling may affect interpretation |
| Mean reversion (fade extremes) | **Strong evidence** | Large effects (< -2σ: +151 pips at H=80); t_p < 0.01; consistent across SMA values |
| Breakout (fade upside) | **Moderate evidence** | High breakout negative at short H; no p-values; but effects larger than other symbols |
| Volatility regime | **Moderate evidence** | Strong absolute |pips| scaling; directional effects significant at mid-H; dual t+z tests |
| Sessions | **Cannot determine** | No statistical tests; large absolute moves but directional pattern unclear |
| Trend persistence | **Moderate evidence** | Reversal pattern with large magnitudes; streak7/8 show large positive fwd returns; no p-values |
| Range behavior | **Cannot determine** | No statistical tests; expansion pattern clear but directional negligible |

### GBPUSD

| Behaviour | Classification | Reasoning |
|-----------|---------------|-----------|
| Momentum (reversal) | **Moderate evidence** | Reversal consistent; t_p available; effect sizes moderate |
| Mean reversion (fade extremes) | **Moderate evidence** | Fade-below positive; t_p < 0.01 for extreme buckets |
| Breakout (fade upside) | **Weak evidence** | High breakout negative at short H; no p-values |
| Volatility regime | **Moderate evidence** | Low-vol consistently bearish (t_p = 0.000 at all H); significant and consistent |
| Sessions | **Cannot determine** | No statistical tests |
| Trend persistence | **Weak evidence** | Reversal pattern; no p-values |
| Range behavior | **Cannot determine** | No statistical tests |

### Key Observation

**EURJPY shows the strongest effects across all studies.** This is partially explained by the pip scaling issue — effects appear ~100x larger because the backtester/report uses the wrong pip value. The directional patterns may still be valid, but the magnitudes are unreliable.

---

## 10. Conditional Research Opportunities

### Supported by Evidence in Reports

| Conditional Question | Evidence Source | Strength |
|---------------------|----------------|----------|
| Mean reversion × SMA length | Mean reversion study: SMA=10 shows different pattern than SMA=160 (reversion at short SMA, trend at long SMA) | Moderate — consistent across symbols |
| Momentum × horizon | Momentum study: reversal strengthens with horizon (H=80 >> H=1) | Moderate — consistent |
| Breakout × channel length | Breakout study: CH=160 shows larger effects than CH=20 | Weak — no p-values |
| Volatility × absolute move | Volatility study: |pips| scales monotonically with regime (low < normal < high) at every horizon | Strong — consistent and significant |
| Session × horizon | Session study: OffHours bearish at mid-H, LondonNY bullish at long H | Weak — no p-values, inconsistent |

### NOT Supported (Do Not Pursue)

| Conditional | Reason |
|-------------|--------|
| Trend × volatility | Trend persistence and volatility studies do not cross-condition |
| Momentum × session | No study cross-condenses these |
| Breakout × session | No study cross-condenses these |
| Range × volatility | No study cross-condenses these |

---

## 11. What We Should NOT Do

Based on the evidence:

1. **Blind parameter optimization** — Phase 5 already shows that even simple, defensible strategies lose money. Optimizing parameters on this data would be curve-fitting to a single regime.

2. **Repeated strategy mining** — We have tested 3 strategies × 4 symbols = 12 backtests, plus 28 Phase 6 studies. The probability of finding a spurious positive result is high. Mining for more strategies increases this risk.

3. **ML before sufficient data exists** — 90,000 M5 bars (~15 months) is insufficient for robust ML. The holdout is compromised. ML would require multi-year data and walk-forward validation.

4. **Cherry-picking the best symbol** — EURJPY shows the largest effects, but this is partly due to the pip scaling bug. Even if the directional patterns are real, selecting EURJPY because it "looks best" is data-snooping.

5. **Treating tiny effects as alpha** — Effects of 0.1–1.0 pips at short horizons are within the noise floor for M5 data. They could easily be artifacts of the zero-spread data quality issue.

6. **Using the holdout repeatedly** — The holdout is already compromised by Phase 6. Any further use of it as "out-of-sample" is misleading.

7. **Optimizing against current validation results** — The validation split has been used for Phase 5 strategy selection. Further optimization against it would be in-sample.

8. **Ignoring the data quality issues** — 48.3% zero-spread on EURUSD, stale 200-bar tail, and wrong pip scaling for EURJPY are not minor issues — they affect the reliability of all quantitative conclusions.

---

## 12. Determine the Correct Next Phase

### Recommendation: **A. Improve data first**

### Decision

The research cannot proceed productively until two fundamental data issues are resolved:

1. **The holdout is compromised.** Phase 6 ran on full data, destroying the holdout for all 28 hypotheses. Without a clean holdout, no future strategy validation can be trusted.

2. **The data quality is inadequate.** 48.3% zero-spread bars on EURUSD, stale 200-bar tail, and wrong pip scaling for EURJPY mean that quantitative conclusions about effect sizes and profitability are unreliable.

### Why Not Other Options?

- **B (Conditional research):** Premature — the conditional patterns identified in Phase 6 need validation on clean data before being pursued as strategy components.
- **C (Hypothesis-driven strategy development):** Premature — the holdout is compromised, the data is 15 months (one regime), and cost modeling is unreliable due to zero-spread bars.
- **D (Higher timeframes):** Would require new data export and would not fix the holdout compromise.
- **E (Stop the project):** Too extreme — the behavioral patterns (mean reversion, reversal) are internally consistent and worth investigating further, but only with better data.

### What "Improve Data" Means

1. **Export fresh multi-year data** (ideally 3–5 years) from MT5 for all 4 symbols
2. **Verify spread quality** — ensure spread column is populated correctly (no zero-spread artifacts)
3. **Re-run data validation** on the new data
4. **Re-establish dev/val/holdout splits** on the new data
5. **Re-run Phase 6** on the new data WITH proper split isolation (dev only for discovery, val for validation, holdout untouched)
6. **Fix the EURJPY pip scaling** in config.py (or exclude EURJPY from backtests until fixed)
7. **Fix the markdown report headers** in Phase 6 (cosmetic but important for trust)

---

## 13. Requirements for a Strategy Hypothesis

If data is improved and hypothesis-driven research resumes, a future hypothesis must satisfy ALL of the following before implementation:

### Mandatory Pre-Implementation Evidence

| Requirement | Standard | How to Verify |
|-------------|----------|---------------|
| 1. Positive directional effect | Average forward return in predicted direction > 0 across ALL symbols | Phase 6-style study on dev data only |
| 2. Economic meaningfulness | Effect size > 1 pip average at the trading horizon (to survive costs) | Phase 6-style study |
| 3. Sufficient sample | Minimum 1,000 events per condition per symbol | Count events in study |
| 4. Stability across periods | Effect present in BOTH first-half and second-half of dev data | Split dev data temporally and re-run |
| 5. Parameter robustness | Effect survives ±50% change in key parameters (lookback, threshold) | Sensitivity analysis |
| 6. Realistic transaction costs | Net-of-cost return > 0 using observed spread (not zero-spread bars) | Backtest excluding zero-spread bars |
| 7. Validation performance | Positive return on val split after implementation | Backtest on val split |
| 8. Untouched holdout confirmation | Positive return on holdout split | Backtest on holdout — ONCE only |

### What This Project Has Shown So Far

| Requirement | Status |
|-------------|--------|
| Positive directional effect | Partially met for mean reversion (fade extremes) and momentum reversal — but effects are small and untested on splits |
| Economic meaningfulness | **NOT MET** — effects are typically < 1 pip at short horizons |
| Sufficient sample | Met for most conditions (1K–45K events) |
| Stability across periods | **NOT TESTED** — Phase 6 ran on full data, no temporal stability check |
| Parameter robustness | **NOT TESTED** |
| Realistic transaction costs | **NOT MET** — zero-spread bars inflate results; Phase 6 does not apply costs |
| Validation performance | **NOT MET** — Phase 5 strategies all lose on val |
| Holdout confirmation | **COMPROMISED** — holdout used in Phase 6 |

---

## 14. Final Decision

### RESEARCH STATUS

**NEEDS DATA IMPROVEMENT FIRST**

### RECOMMENDED NEXT PHASE

**Phase 0: Data Infrastructure Repair**

### WHY

1. **The holdout is destroyed.** Phase 6 ran on full data (confirmed in `phase6.py` lines 51-55), compromising the holdout for all 28 hypotheses. No future validation can be trusted without a clean holdout.

2. **The handoff document is unreliable.** PROJECT_RESEARCH_HANDOFF.md contains fabricated Phase 5 numbers (verified against `results.json`). All 36 performance claims in its tables are wrong. Conclusions drawn from the handoff are invalid.

3. **Data quality is inadequate.** EURUSD has 48.3% zero-spread bars (verified in `data_validation_report.md`), the last 200 bars are all zero-spread (stale feed), and EURJPY uses wrong pip scaling (verified in `config.py` lines 58-59 vs actual pip=0.01).

4. **Statistical testing is incomplete.** Only 3 of 7 Phase 6 studies have p-values. The other 4 (breakout, sessions, trend persistence, range behavior) have zero formal statistical inference. No study reports SE, CI, or applies multiple-comparison correction.

5. **Phase 5 results are universally negative.** Verified against `results.json`: ALL strategies across ALL symbols (except broken EURJPY) show negative returns, sub-1.0 profit factors, and significant drawdowns in ALL splits. The data confirms no edge exists under the current cost model.

6. **The observed behavioral patterns are real but unvalidated.** Mean reversion and momentum reversal show consistent directional signs across symbols (verified in per-symbol JSON summaries), but: (a) effects are small, (b) no costs were applied, (c) no temporal stability was tested, and (d) the holdout is compromised.

7. **15 months of data is one market regime.** The sample covers Jun 2025 → Sep 2026 — a single regime. Multi-year data is needed to assess whether observed patterns persist across different market conditions.

### CRITICAL UNKNOWNs

1. **Are the Phase 6 behavioral patterns (reversal, mean reversion) real or artifacts of the zero-spread data?** Cannot be determined without clean spread data.
2. **Would any pattern survive realistic transaction costs?** Phase 6 did not apply costs; Phase 5 (which did apply costs) shows everything is negative.
3. **Do the observed patterns persist in a different time period?** 15 months is insufficient; the holdout is compromised so we cannot even test this on the existing data.
4. **Is the EURJPY reversal pattern real or a pip-scaling artifact?** The 100x pip error makes EURJPY results unreliable.
5. **What is the true cost of trading on this feed?** With 48.3% zero-spread bars, the effective cost is unknown.

---

*This audit was conducted by reading all source files listed in TASK.md and verifying claims against the actual data. No files were modified. The Phase 5 results in `outputs/benchmark/results.json` are the authoritative source for strategy performance. The Phase 6 JSON summaries (`outputs/phase6/*/*.json`) are the authoritative source for market behavior data. The markdown reports contain labeling bugs but the underlying numeric data appears correct based on cross-symbol differentiation in the JSON files.*
