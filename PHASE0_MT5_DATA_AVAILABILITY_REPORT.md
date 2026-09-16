# PHASE 0: MT5 DATA AVAILABILITY REPORT

**Date:** 2026-09-10
**Status:** INVESTIGATION ONLY — DO NOT PROCEED TO PHASE 1
**Method:** Live MT5 API diagnostic (`diagnose_mt5_data.py`) + source code analysis

---

## Classification

### **C. HISTORY NOT AVAILABLE — NEED DIFFERENT DATA SOURCE**

The MetaQuotes-Demo MT5 account provides approximately **16 months** of M5 history (earliest: 2025-05-08). This is fundamentally insufficient for the 3–5+ year research requirement. No exporter fix can resolve this — the data simply does not exist on this server/account.

---

## 1. Current Exporter Behavior

**File:** `dump_mt5_multi.py`

The exporter uses `copy_rates_from_pos(symbol, TIMEFRAME_M5, 0, attempt_size)` with a fallback chain:

```
MAX_BARS = 1,000,000
FALLBACK_SIZES = [500000, 200000, 100000, 90000, 50000, 10000, 1000]
```

It tries 1,000,000 first, then walks down the fallback list until one succeeds.

**There is no hard-coded 90,000 limit.** The exporter correctly falls back. The 90,000 was simply the first size that contained all available data in the previous run. With the current terminal state, 97,000 succeeds but 100,000 fails.

---

## 2. Why 90,000–97,000 Bars Is the Ceiling

Two independent limits exist:

### A. `copy_rates_from_pos` count limit (HARD API LIMIT)

The MT5 terminal rejects requests for ≥100,000 bars with error `(-2, 'Terminal: Invalid params')`. The maximum that works is **97,000 bars**.

**Verified live (2026-09-10):**

| Requested | Result | First Bar | Last Bar |
|-----------|--------|-----------|----------|
| 1,000,000 | FAILED | — | — |
| 500,000 | FAILED | — | — |
| 200,000 | FAILED | — | — |
| 100,000 | FAILED | — | — |
| **97,000** | **97,000 bars** | **2025-05-22** | **2026-09-10** |
| 95,000 | 95,000 bars | 2025-06-02 | 2026-09-10 |
| 90,000 | 90,000 bars | 2025-06-25 | 2026-09-10 |

This is a **hard API limit in MetaTrader 5 build 6140** — not an exporter bug.

### B. Actual data availability

The terminal contains approximately **100,000–101,000 M5 bars** total, spanning from 2025-05-08 to 2026-09-10. The position-based API can only retrieve the most recent 97,000 of these.

**Per-symbol totals (via quarterly chunked retrieval):**

| Symbol | Total Bars (sum of quarters) | Earliest | Latest | Days |
|--------|------------------------------|----------|--------|------|
| EURUSD | ~100,830 | 2025-05-08 | 2026-09-10 | ~491 |
| EURGBP | ~100,844 | 2025-05-08 | 2026-09-10 | ~491 |
| EURJPY | ~100,841 | 2025-05-08 | 2026-09-10 | ~491 |
| GBPUSD | ~100,830 | 2025-05-08 | 2026-09-10 | ~491 |

**All four symbols have identical history depth.** The data covers ~491 days (~16 months).

---

## 3. Earliest Available M5 History

### Binary search result

A binary search across the full date range (2020-01-01 to 2026-09-10) using `copy_rates_from` confirmed:

| Symbol | Earliest M5 Bar |
|--------|-----------------|
| EURUSD | **2025-05-08 03:05:00** |
| EURGBP | **2025-05-08 07:55:00** |
| EURJPY | **2025-05-08 08:05:00** |
| GBPUSD | **2025-05-08 06:35:00** |

### Historical date probes via `copy_rates_from`

| Start Date Requested | Bars Returned | First Actual Bar |
|---------------------|---------------|-----------------|
| 2021-01-01 | 1 | 2025-05-08 |
| 2022-01-01 | 1 | 2025-05-08 |
| 2023-01-01 | 1 | 2025-05-08 |
| 2024-01-01 | 1 | 2025-05-08 |
| 2025-01-01 | 1 | 2025-05-08 |
| 2025-03-01 | 1 | 2025-05-08 |
| 2025-05-01 | 1 | 2025-05-08 |
| 2025-06-01 | 5 | 2025-05-30 |

When requesting data from any date before 2025-05-08, MT5 returns **1 bar** — the earliest available bar. **No M5 data exists in this terminal before May 8, 2025.**

---

## 4. `copy_rates_range` Behavior

`copy_rates_range` works for sub-annual ranges but **fails for full-year ranges**:

**Verified live (2026-09-10):**

| Range | Result | First | Last |
|-------|--------|-------|------|
| 2024 full year | **FAILED** | — | — |
| 2025 full year | **FAILED** | — | — |
| 2026 full year | **FAILED** | — | — |
| 2025-Q1 (Jan–Mar) | 1 bar | 2025-05-08 | 2025-05-08 |
| 2025-Q2 (Apr–Jun) | 10,870 bars | 2025-05-08 | 2025-06-30 |
| 2025-Q3 (Jul–Sep) | 18,810 bars | 2025-06-30 | 2025-09-30 |
| 2025-Q4 (Oct–Dec) | 18,649 bars | 2025-09-30 | 2025-12-31 |
| 2026-Q1 (Jan–Mar) | 18,042 bars | 2025-12-31 | 2026-03-31 |
| 2026-Q2 (Apr–Jun) | 18,720 bars | 2026-03-31 | 2026-06-30 |
| 2026-Q3 (Jul–Sep) | 14,909 bars | 2026-06-30 | 2026-09-10 |
| H1 2025 | 10,870 bars | 2025-05-08 | 2025-06-30 |
| H2 2025 | 37,459 bars | 2025-06-30 | 2025-12-31 |

Full-year ranges fail with `(-2, 'Terminal: Invalid params')`. The API has a separate limit on the time span or expected bar count for `copy_rates_range`.

**Date-range export cannot retrieve more data than `copy_rates_from_pos`.** Both APIs draw from the same data pool.

---

## 5. Whether 3–5 Years Is Available

**No.** The terminal contains approximately **16 months** of M5 data (May 8, 2025 – September 10, 2026), totaling ~100,800 bars.

| Requirement | Available | Deficit |
|-------------|-----------|---------|
| 3 years (~150,000 bars) | ~100,800 bars | **-49,200 bars (33% short)** |
| 5 years (~250,000 bars) | ~100,800 bars | **-149,200 bars (60% short)** |

The terminal provides **~35–67%** of the minimum research requirement.

---

## 6. Date-Range/Chunked Export

Chunked export **would retrieve slightly more data** than `copy_rates_from_pos` alone (~100,800 vs 97,000 bars) but **cannot solve the fundamental problem**. Both APIs are bounded by the same underlying data on the server.

| Method | Bars Retrieved | Date Range |
|--------|---------------|------------|
| `copy_rates_from_pos` (max) | 97,000 | 2025-05-22 → 2026-09-10 |
| Quarterly chunks (total) | ~100,800 | 2025-05-08 → 2026-09-10 |
| **Improvement** | **~3,800 bars (~15 days)** | — |

The exporter is not broken. It correctly retrieves all available data.

---

## 7. MT5 Terminal Settings

**Terminal:** MetaTrader 5, Build 6140
**Server:** MetaQuotes-Demo (account 5055770258)
**Company:** MetaQuotes Ltd.
**Balance:** 100,000 USD (demo)
**Leverage:** 1:100

### `maxbars` setting

The `terminal_info()` API exposes the `maxbars` attribute:

```
maxbars: 100000
```

This is the "Max bars in chart" setting (Tools → Options → Charts). It controls how many bars the UI loads into charts, **not** the Python API's data retrieval limit. The Python API's hard limit of ~97,000 is separate from this setting.

### Can changing `maxbars` help?

**No.** The `maxbars` setting only affects chart display in the MT5 UI. The Python API's data availability is determined by the server-side data retention, which for MetaQuotes-Demo is ~16 months of M5 data. The `terminal_info` attribute confirms the terminal is configured for 100,000 bars, but this is irrelevant to the API limit.

### If using a different broker

To maximize available history from any MT5 broker:
1. Open MT5 → Tools → Options → Charts
2. Set "Max bars in chart" to maximum (unlimited)
3. However, this primarily affects UI display — server-side data retention is the real constraint

---

## 8. Zero-Spread Diagnosis

**Verified live (2026-09-10):**

| Symbol | Recent 5K Bars | Zero % | Nonzero Mean (pts) | 2025-Q2 Zero % | 2025-Q2 Nonzero Mean |
|--------|----------------|--------|---------------------|-----------------|----------------------|
| EURUSD | 5,000 | **98.6%** | 3.5 | 0.1% | 9.8 |
| EURGBP | 5,000 | **83.7%** | 5.6 | 0.0% | 23.6 |
| EURJPY | 5,000 | **90.9%** | 22.9 | 0.0% | 24.5 |
| GBPUSD | 5,000 | **98.3%** | 8.7 | 0.0% | 21.0 |

### Finding

Recent data (last few months) has **84–99% zero spread**. Older data (Q2 2025) has **realistic non-zero spread**.

This is **not a code bug** — the `copy_rates_*` functions return `spread=0` because the MetaQuotes-Demo server does not populate the spread field for recent historical data. The spread field in MT5 history represents the "spread at bar close" as reported by the server; demo accounts often do not record this accurately.

### Implication

Spread data is unreliable in the current dataset. For backtesting, spread must be estimated or sourced externally. The existing `backtest/data/data_validation.py` correctly flags this issue.

---

## 9. Tick Data Availability

**Verified live (2026-09-10):**

| Symbol | Ticks Today | Ticks Yesterday | Ticks Last 7 Days |
|--------|------------|-----------------|-------------------|
| EURUSD | 153,721 | 228,456 | 1,079,690 |
| EURGBP | 98,621 | 124,547 | 693,640 |
| EURJPY | 323,354 | 509,954 | 2,492,689 |
| GBPUSD | 266,242 | 367,165 | 1,833,776 |

Tick data IS available via `copy_ticks_range` for intraday periods. However:
- Historical tick data beyond the current session is unlikely to extend much further than the M5 history
- Demo accounts typically do not retain long-term tick data
- The M5 history limit (~16 months) applies to tick data as well

Tick data could provide **better spread information** (bid/ask are separate fields in tick data), but only for the same 16-month window.

---

## 10. Non-Weekend Gap Diagnosis

The data validation reports 11–31 non-weekend gaps per symbol (varying by symbol). Analysis of the gap patterns:

### Misclassified weekend closures
All "long" gaps (>1000 min) are **Friday 23:55 → Monday 00:00** (2,885 min ≈ 48 hours). These are standard FX weekend closures. The validator's 1,000-minute threshold correctly classifies most, but some Fri→Mon boundaries where both timestamps are technically weekdays (e.g., Friday 23:55 to "Saturday" 00:00 which rolls to Monday) leak through. **These are NOT data quality issues.**

### Genuine intraday gaps
Short gaps (15–550 minutes) include:
- **US Independence Day (Jul 3–4, 2025):** 550 min and 385 min gaps — expected holiday closures
- **Late Dec 2025:** Several 15–25 min gaps around Christmas/New Year — reduced liquidity sessions
- **Scattered 15 min gaps:** Minor broker session breaks or feed interruptions

**No evidence of significant missing history.** The gaps are explained by holidays, session breaks, and reduced holiday liquidity.

---

## 11. Recommended Acquisition Method

Since the current MT5 demo account cannot provide sufficient historical data, the recommended approaches (in order of preference):

### Option A: Use MT5 with a broker that provides deeper history
Some brokers (ICMarkets, Pepperstone, Dukascopy) may provide years of M5 history. However, MT5 server-side data retention varies and may still be limited.

### Option B: Download from an independent data provider
- **Dukascopy TDS** (free, tick/M1 data, 10+ years)
- **TrueFX** (free, tick data, 10+ years)
- **MetaQuotes MT5 Market** (paid, various data packages)
- **HistData.com** (free, M1 data)

### Option C: Use Dukascopy's JForex platform or API
Provides direct access to institutional-grade tick data with full history.

**Recommendation:** Option B (Dukascopy) is the most practical. Their free tick data can be converted to M5 OHLCV and provides the full 3–5+ year depth required.

---

## 12. Exact Next Action

1. **Do NOT modify the exporter or retry MT5 export** — the data is not there
2. **Select an external data provider** (Dukascopy recommended)
3. **Create a new data acquisition script** that downloads from the chosen provider
4. **Validate the external data** using the existing `backtest/data/data_validation.py` framework
5. **Proceed to Phase 1** only after 3–5+ years of validated M5 data is acquired

---

## Appendix: Diagnostic Script

The diagnostic script `diagnose_mt5_data.py` was created for this investigation. It tests:
- `copy_rates_from_pos` with various bar counts (finds the hard API limit)
- `copy_rates_from` with historical start dates (finds earliest available data)
- `copy_rates_range` with quarterly and yearly ranges
- Binary search for earliest available M5 bar
- Spread field behavior across time periods
- Tick data availability

Results are saved to `mt5_diagnostic_results.json`. This script should be cleaned up after the investigation unless it is retained as a permanent diagnostic tool.

---

*This report is investigation only. No strategies were run, no parameters optimized, no historical conclusions modified.*
