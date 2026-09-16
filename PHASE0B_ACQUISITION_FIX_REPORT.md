# PHASE 0B — DUKASCOPY ACQUISITION FIX REPORT

**Date:** 2026-09-10
**Status:** FIXED — SMOKE TEST PASSED (full 2021–2026 download NOT run; see §8)
**Scope:** Acquisition/normalization pipeline only. Research methodology, backtester, strategies, Phase 1, and dataset validation criteria were NOT changed.

---

## 1. Root Cause of `KeyError: 'tick_volume'`

The full acquisition command

```
python -m backtest.data.dukascopy_acquire --all --from 2021-01-01 --to 2026-09-10
```

failed immediately on EURUSD with `FAILED: 'tick_volume'`.

The old `backtest/data/dukascopy_acquire.py` constructed the canonical output by reading the raw Dukascopy CSV column `tick_volume`:

```python
"tick_volume": bid_df["tick_volume"].values   # KeyError
```

but the raw dukascopy-node CSV names that column **`volume`**, not `tick_volume`. There was no parsing/adapter layer — the code tried to consume raw Dukascopy fields as if they were already in the canonical schema. This is a pure column-name/schema mismatch. It is NOT a data-quality problem with Dukascopy (which was already classified as the accepted primary source in Phase 0B), so the source remains accepted.

## 2. Actual Dukascopy Raw Schema

Established by running the CLI on EURUSD (Jun 1–8 2025) and inspecting the downloaded CSV directly — no field names guessed.

CLI used (bid example):

```
npx dukascopy-node -i eurusd -from 2025-06-01 -to 2025-06-08 -t m5 -p bid -f csv -v -vu units -dir '<dir>'
```

| Field | Type | Meaning |
|-------|------|---------|
| `timestamp` | int64 | Unix epoch, **milliseconds, UTC** |
| `open` | float64 | bar open (bid if `-p bid`, ask if `-p ask`) |
| `high` | float64 | bar high |
| `low` | float64 | bar low |
| `close` | float64 | bar close |
| `volume` | int64 | aggregated **tick volume** for the bar (in units) |

Observed values (EURUSD M5, 1 week): volume min 3,600,000, max 3,216,620,000, mean ≈ 497,896,340, **zero-count = 0** → volume is meaningful tick data, not a dummy.

Key facts:
- **Bid/ask**: separate CSV per price type (`-p bid` / `-p ask`) with the same 6 columns.
- **Spread**: NOT provided directly by Dukascopy — must be computed from `ask_close − bid_close`.
- **Volume**: real tick-volume field exists (units), which maps to `tick_volume`.
- **Real volume**: not available from Dukascopy.

## 3. Canonical Schema Mapping

Project canonical schema (must match legacy MT5 CSV layout used by validator/backtester):

| Canonical column | Source / derivation |
|------------------|---------------------|
| `time` | `timestamp` (ms UTC) → naive-UTC `datetime64[ns]` |
| `open` | bid `open` |
| `high` | bid `high` |
| `low` | bid `low` |
| `close` | bid `close` |
| `tick_volume` | Dukascopy **`volume`** (renamed, integer units preserved) |
| `spread` | `round((ask_close − bid_close) / instrument.point)` as int points |
| `real_volume` | `0` — see §4 |

Bid/ask are aligned on the common `time` index (intersection of timestamps, duplicates dropped, then sorted). OHLC is taken from the bid side (the backtester treats prices as bid).

## 4. Unavailable Volume Representation

- `tick_volume`: **real, observed** Dukascopy aggregated tick volume (in units). Mapped from the raw `volume` column — not fabricated.
- `real_volume`: **unavailable** from Dukascopy → set to `0` and documented as unavailable/not observed. The `0` is a documented convention required because the canonical schema has the column; it does not claim a real volume of zero was measured.

No volume data is manufactured.

## 5. Spread Calculation

```
observed spread (points) = round((ask_close − bid_close) / instrument.point)
```

Per-symbol point (from `backtest/instruments.py`): EURUSD/EURGBP/GBPUSD 0.00001, EURJPY 0.001.

Smoke-test EURUSD (1 week): spread min 1, mean 6.4, p99 ≈ 39.6, max 79, **zero-spread bars = 0 (0.00%)** — contrast with the MT5-era feed (48.3% zero-spread on EURUSD).

Spread is preserved exactly as observed; it is not created or zeroed.

## 6. Timezone Handling

- Raw `timestamp` is int64 Unix ms **UTC** (verified: 1748811600000 → `2025-06-01 21:00:00` UTC).
- Converted with `pd.to_datetime(timestamp, unit="ms", utc=True).dt.tz_localize(None)` → **naive UTC** `datetime64[ns]`, matching the existing canonical/MT5 files (no tz-aware datetimes in the dataset).
- Unit tests assert naive-UTC (no tzinfo) and exact wall-clock conversion.

## 7. Tests Performed

New `tests/test_dukascopy_acquire.py` (22 cases), all synthetic (no network), covering:

| Category | Cases |
|----------|-------|
| Raw-schema parsing (`read_dukascopy_csv`) | column mapping, ms→naive-UTC time, missing column raises, missing file raises |
| Canonical normalization | output columns/order, bid/ask alignment, bid-side OHLC |
| Bid/ask spread calculation | all 4 symbols by point size (EURUSD 8, EURGBP 10, EURJPY 2, GBPUSD 6 pts) |
| Volume handling | `tick_volume` preserved >0; `real_volume` all zero (available = None) |
| Edge cases | empty frames raise, no timestamp overlap raises, duplicate timestamps deduped |
| All four instruments | e2e CSV→canonical for EURUSD, EURGBP, EURJPY, GBPUSD |

**Result:**

```
tests/test_dukascopy_acquire.py ... 22 passed
tests/ (full suite)            ... 46 passed
```

(The focused tests initially detected the raw-vs-parsed interface mismatch; test helpers were aligned to the adapter's documented two-stage interface: `read_dukascopy_csv` → `dukascopy_to_canonical`.)

## 8. Smoke-Test Result (one week EURUSD)

Command (previously failing):

```
python -m backtest.data.dukascopy_acquire --symbol EURUSD --from 2025-06-01 --to 2025-06-08 --out-dir data
```

Result: **SUCCESS**

```
Downloading EURUSD from Dukascopy (2025-06-01 to 2025-06-08)...
  Saved 1440 bars to data\eurusd_m5.csv
  Range: 2025-06-01 21:00:00 to 2025-06-06 20:55:00
  Columns: ['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
```

Output verification:

| Check | Result |
|-------|--------|
| Column order | exactly `CANONICAL_COLUMNS` ✓ |
| `time` | naive UTC, monotonic ✓ |
| dtypes | time=datetime64, OHLC=float64, tick_volume/spread/real_volume=int64 ✓ |
| bars | 1440 over 4 trading days (gaps = only weekends) ✓ |
| `tick_volume` ≤ 0 | 0 bars ✓ |
| `spread` == 0 | 0 bars (0.00%) ✓ |
| `real_volume` != 0 | 0 bars (documented as unavailable) ✓ |

Validator run on smoke output (`python -m backtest.data.validate_all --data-dir data`):

- EURUSD flags: only `real_volume all zeros` (expected, documented) and `short <30-day sample` (expected: smoke test is 1 week). No duplicate/gap/OHLC issues, no zero-spread.
- **Finding (flagged, NOT a criterion change):** EURUSD `Spread max 79 pts exceeds threshold 50 pts`. This is 7/1440 bars (0.49%); it is the actual observed ask−bid spread (the same 79-pt max appeared in the Phase 0B cross-source analysis). Per scope, validation criteria were not changed. The validator reports instrument_issue for EURUSD; EURGBP/EURJPY/GBPUSD rows in the same run were the still-pending MT5-era files (not Dukascopy smoke data), so their flags are out of scope here.

## 9. Exact Command for the Full 2021–2026 Acquisition

```
python -m backtest.data.dukascopy_acquire --all --from 2021-01-01 --to 2026-09-10
```

Notes for the full run:
- Runs bid+ask weekly CLI downloads for all 4 symbols and writes canonical CSVs to `data/{symbol}_m5.csv` inside `--out-dir data`.
- Raw weekly bid/ask CSVs are also left in the output dir (they are the CLI's download artifacts; `{symbol}_m5.csv` is the canonical result). ~5.6 years × 52 weeks × 4 symbols ≈ 1,140+ bid/ask pairs ≈ 2,300+ CLI calls.
- Estimated runtime is ~30 min to a couple of hours depending on npx startup overhead per call (observed ~0.6–0.8 s network per week; `npx` wrapper adds per-invocation startup). Run in a terminal that stays open; per-symbol failures are reported and do not abort other symbols.
- Requires Node.js 18+ and network access to Dukascopy (uses `npx dukascopy-node`, auto-provisioned).

**Per TASK.md item 12: the full multi-year download was intentionally NOT performed in this task.** The smoke test passed and the acquisition code is verified; the full run is the next step.

## 10. Files Changed

| File | Action |
|------|--------|
| `backtest/data/dukascopy_acquire.py` | REWRITTEN — clean adapter: `read_dukascopy_csv` (raw→parsed), `dukascopy_to_canonical` (parsed→canonical), `download_m5`, CLI `main` with per-symbol failure reporting |
| `tests/test_dukascopy_acquire.py` | CREATED — 22 tests for parsing/normalization/spread/volume/instruments/timezone |

Temporary raw diagnostic files under `data/raw_diag/` and in `data/` were removed after inspection. `data/eurusd_m5.csv` now holds the Dukascopy smoke-test canonical output (previous MT5-era version is preserved in git history).

## 11. Remaining Blocker

None for acquisition. Next sequential step is the full four-symbol 2021–2026 download (§9), followed by `validate_all` and fresh research splits — all after/outside this fix.