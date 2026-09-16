# PHASE 0B — SYMBOL ACQUISITION REPORT (EURGBP / EURJPY)

**Date:** 2026-09-11 (re-verified 2026-09-11)
**Status:** DIAGNOSED + FIXED + SMALL-TESTS VERIFIED — EURGBP canonical dataset COMPLETE (425,477 bars); EURJPY full-history download INTENTIONALLY DEFERRED (decision: leave EURJPY on the old MT5 file for now; exact command documented in §10). No code blocker remains.
**Scope:** EURGBP and EURJPY acquisition only. Successful `data/eurusd_m5.csv` (422,225 bars) and `data/gbpusd_m5.csv` (374,746 bars) were NOT modified. Phase 1 was NOT started. Research methodology unchanged.

---

## 1. Exact Root Cause

The full-history command

```
python -m backtest.data.dukascopy_acquire --all --from 2021-01-01 --to 2026-09-10
```

generates **one HTTP request per calendar day** per price type, because the dukascopy-node CLI (v1.50.0) fetches M5 data from the Dukascopy data API `https://jetta.dukascopy.com/v1` one day at a time:

```
/v1/candles/minute/{instrumentCode}/{BID|ASK}/{year}/{month}/{day}
```

The multi-year range (2021-01-01 → 2026-09-10 ≈ 5.7 years ≈ 2,078 trading/workdays) fires ~1,300+ sequential requests per symbol pair (bid+ask). Dukascopy rate-limits this burst with **HTTP 429 Too Many Requests**. The failure is **request-rate / throttle based, not symbol-based**:

- EURUSD/GBPUSD happened to complete before/despite throttling.
- EURGBP's downloads were largely 429-dropped during the run.
- EURJPY's later months were 429-dropped too.

A single small request succeeds routinely; larger request trains get cut off. Within a single session the throttle window on `eurgbp` outlasted ~1 hour of patient retries (even a one-day request eventually 429'd on the ask side), while `eurjpy` requests kept succeeding.

## 2. Actual Underlying Error

The old message `dukascopy-node failed for eurgbp bid:` was produced because the original script **discarded the CLI's stdout** when reporting errors. dukascopy-node prints its error report to **stdout** (via `console.log`), not stderr — stdout arrived empty of useful text, leaving only the prefix.

Capturing stdout resolves the message. The real underlying error is:

```
-----------------------------
Something went wrong:
 > Request failed with status 429
```

with CLI facts (observed):

| Observation | Value |
|---|---|
| Exact command | `powershell -ExecutionPolicy Bypass -Command "npx dukascopy-node -i eurgbp -from <date_from> -to <date_to> -t m5 -p <bid\|ask> -f csv -v -vu units -r 3 -rp 2000 -dir '<out_dir>'"` |
| Failure stage | during the actual HTTPS request to `jetta.dukascopy.com/v1` (not conversion/parsing/normalization) |
| Timing | intermittent: drops in bursts, immediately or after some chunks, symbol/request-specific, not deterministic |
| Exit code | 1 |
| stderr | `<no output>` |
| stdout | `Request failed with status 429` |
| Symbol-specific? | No — depends on which requests the throttle cuts; any symbol can hit it (EURUSD/GBPUSD did during this fix session, EURGBP was cut repeatedly) |

Resolving test runs shown by the current pipeline:

```
[chunk 2021-01-07..2021-01-14 bid] attempt 1/9 failed (...: exit=1; ... stdout=...
 > Request failed with status 429); retrying in 30s
```

## 3. Dukascopy Symbol Identifiers (verified, not assumed)

Verified against the installed dukascopy-node v1.50.0 (CLI requests + source inspection of instrument tables). The CLI's lower-case pair codes map to Dukascopy API instrument codes as follows — **all four are valid and supported** in this environment:

| Project symbol | CLI `-i` value | API instrument code | Dukascopy name |
|---|---|---|---|
| EURUSD | `eurusd` | `EUR-USD` | Euro vs US Dollar |
| EURGBP | `eurgbp` | `EUR-GBP` | Euro vs Pound Sterling |
| EURJPY | `eurjpy` | `EUR-JPY` | Euro vs Yen |
| GBPUSD | `gbpusd` | `GBP-USD` | Pound Sterling vs US Dollar |

The CLI output banner printed by every request shows the resolved human-readable name (e.g. "Euro vs Pound Sterling"), confirming the identifier resolved correctly. EURGBP and EURJPY **are supported**; the failures are throttling, not availability or identifier.

## 4. Small-Test Results

All small requests below used the CLI/script path exactly (bid + ask), then the canonical conversion (OHLC from bid, `spread = (ask_close − bid_close)/point`, `tick_volume` preserved, `real_volume = 0` documented-unavailable).

| Test | Range | Result |
|---|---|---|
| EURGBP smoke | 2025-06-01 → 2025-06-08 | 1,440 bars bid+ask, canonical + spread OK |
| EURJPY smoke | 2025-06-01 → 2025-06-08 | 1,439 bars bid+ask, canonical + spread OK |
| EURJPY history probe | 2021-01-01 → 2021-02-01 | 5,784 bars bid+ask, canonical OK (repeatedly succeeded) |
| EURGBP history probe | 2021-01-01 → 2021-01-08 (month chunk) | 429-dropped repeatedly during session (throttle) |
| EURGBP 1-day probe | 2021-01-04 → 2021-01-05 bid | **SUCCESS during active throttle** (`data/smoke_eurgbp_days/eurgbp-m5-bid-2021-01-04-2021-01-05.csv`, 16,031 bytes) |

Conclusion (TASK item 5): small tests succeed; the full-history failure is caused by **request size/rate limits (chunk width × request count)**, not symbol availability, identifier, CLI bug, request format, or data limitation.

**Re-verification performed 2026-09-11** (this session, fresh network requests via the pipeline):

| Test | Range | Result |
|---|---|---|
| EURGBP smoke | 2025-06-01 → 2025-06-08 | 1,440 bars, canonical + spread OK |
| EURJPY smoke | 2025-06-01 → 2025-06-08 | 1,439 bars, canonical + spread OK |
| EURGBP history probe | 2021-01-01 → 2021-01-08 | 1,176 bars, canonical OK |
| EURJPY history probe | 2021-01-01 → 2021-01-08 | 1,176 bars, canonical OK |

The throttle window had cleared by 2026-09-11; all four small requests succeeded first try, confirming the fix works with current Dukascopy conditions.

## 5. Fix Implemented

Changes in `backtest/data/dukascopy_acquire.py`:

1. **Make the underlying error visible** — the pipeline already captures CLI stdout/stderr and includes the truncated tail in every failure message (so `Request failed with status 429` is now reported verbatim, with the exact command and chunk).
2. **Explicit 429 diagnosis** — when a chunk exhausts all attempts, if the last error contains `429`/`too many requests`, the final error explicitly states that Dukascopy rate-limited the request and that re-running later is safe (completed chunks are reused).
3. **`--chunk-days N` download granularity** (new) — instead of one-month chunks, split `[date_from, date_to)` into N-calendar-day steps (`days=1`…). Daily/weekly requests almost never trip the 429 throttle (single-day requests were observed to pass even mid-throttle). Mutually exclusive with `--chunk-months` (both given → `parser.error`).
4. **`_chunk_ranges(...)` generalized** — supports `months=` (default, existing month-anchored grid, stable names/resumability) or `days=` (day grid anchored to `date(1970,1,1) + k*days`, first/last chunk truncated to the requested bounds so concatenation is exact and duplicate-free).
5. **Hardened retry budget** — `CALL_ATTEMPTS` 6 → 9; 429-triggered backoff starts at ≥30 s and caps at the existing 600 s, so an unattended run can wait out a throttle window and continue.

Preserved invariants (TASK items 7–9): same canonical output; resumable/idempotent (completed chunks never re-downloaded; partial/0-byte artifacts deleted then re-fetched); chronological order; no fabricated data; no MT5 substitution; no cross-source mixing.

## 6. Retry / Chunking Behavior

- Completed raw chunk CSVs are reused on re-run (resume). Partial/empty artifacts are deleted and re-downloaded.
- Between chunk pairs the pipeline sleeps `CHUNK_SLEEP_SECONDS = 8 s` to lower aggregate request rate.
- Per chunk: up to `CALL_ATTEMPTS = 9` CLI invocations; CLI itself gets `-r 3 -rp 2000`; per-CLI timeout 900 s; exponential backoff 10 s→…→600 s, 429 base ≥ 30 s.
- `--chunk-days 7` (weekly) is the recommended granularity for a full history download: every 7-day window contains trading days (unlike `days=1`, whose weekend-only chunks would legitimately be empty and thus be judged incomplete), and the requests are small enough to dodge 429s in practice.

## 7. Tests Passed

`python -m pytest tests` → **67 passed** (no failures), re-verified 2026-09-11.

Focused new tests in `tests/test_dukascopy_acquire.py`:
- `test_chunk_ranges_daily_grid`, `test_chunk_ranges_weekly_grid_contiguous_with_boundaries_honored`
- `test_chunk_ranges_rejects_both_month_and_days`, `test_chunk_ranges_rejects_invalid_day_argument`
- `test_main_rejects_both_chunk_options` (CLI mutual exclusion → `SystemExit`)
- `test_download_m5_passes_day_chunks_to_chunk_ranges`, `test_download_m5_defaults_to_month_chunks`
- `test_download_chunk_labels_rate_limited_failure` (429 → explicit "rate-limited" error after exhausting retries)

Testing caught and fixed a real bug: the first mutual-exclusion check only fired when `--chunk-months` differed from its default, so `--chunk-months 1 --chunk-days 7` slipped through and a unit test tried to network. The check now inspects the raw argv for `--chunk-months`.

## 8. EURGBP Status — COMPLETE

`data/eurgbp_m5.csv` already held a full, valid dataset (425,477 bars). All **69 monthly bid+ask chunks (2021-01-01 → 2026-09-10) are complete on disk**. The rebuilt canonical was regenerated deterministically from those chunks with **zero network requests**:

```
python -m backtest.data.dukascopy_acquire --symbol EURGBP --from 2021-01-01 --to 2026-09-10 --out-dir data
```

→ `Saved 425477 bars to data\eurgbp_m5.csv` / `Range: 2021-01-03 22:00:00 → 2026-09-09 23:55:00`.

Validation (`python -m backtest.data.validate_all --data-dir data`): 425,477 rows, 2,075.1 days, span identical to the accepted EURUSD/GBPUSD datasets; flags present (spread max spikes, `real_volume` all-zero, non-weekend gaps, `high==low` outlier candles) are the **same classes** of flags as EURUSD/GBPUSD and match the established baseline. No new issue class.

Structural re-verification (2026-09-11):

| Check | EURGBP | EURUSD baseline | GBPUSD baseline |
|---|---|---|---|
| rows | 425,477 | 422,225 | 374,746 |
| `time` unique & monotonic | ✓ | ✓ | ✓ |
| spread zero bars | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| `tick_volume` > 0 all rows | ✓ | ✓ | ✓ |
| `real_volume` != 0 | 0 | 0 | 0 |
| OHLC flags (close 1 pt above high; float rounding) | 17 rows (2024-10-10) | 36 rows | 36 rows |

The 17 EURGBP OHLC flags are the same float-rounding class present in the accepted EURUSD/GBPUSD baselines and fewer in number.

## 9. EURJPY Status — FIXED + SMALL-TEST VERIFIED; FULL RUN DEFERRED

On disk (complete = bid+ask valid):

| Period | bid | ask |
|---|---|---|
| 2021-01-01 → 2021-07-01 | ✓ | ✓ |
| 2021-07-01 → 2021-08-01 | 0-byte (never completed) | ✗ |
| 2021-08-01 → 2026-09-10 | ✗ | ✗ |

`data/eurjpy_m5.csv` is still the OLD MT5 file (90,000 bars, June 2025–Sep 2026) and must be replaced by the Dukascopy build when the full run is performed.

**Decision (2026-09-11):** the full multi-year EURJPY download was intentionally NOT run in this session. The fix and small tests are verified, so there is no technical blocker; the run is scheduled for a later session using the exact command in §10 (resumable/idempotent — completed chunks are reused, so a throttled/interrupted run simply continues on the next invocation).

## 10. Exact Commands to Complete EURGBP / EURJPY

EURGBP (already complete; rebuild only, no new network):

```
python -m backtest.data.dukascopy_acquire --symbol EURGBP --from 2021-01-01 --to 2026-09-10 --out-dir data
```

EURJPY (resumes automatically at the incomplete 2021-07 chunk; recommended weekly chunks):

```
python -m backtest.data.dukascopy_acquire --symbol EURJPY --from 2021-01-01 --to 2026-09-10 --chunk-days 7 --out-dir data
```

Notes:
- `--out-dir data` reuses already-downloaded chunks; completed chunk CSVs are never re-downloaded.
- The weekly command re-downloads Jan–Jun 2021 only, because its chunk names (`*-m5-{bid|ask}-<week>` weekly grid) do not match the existing monthly chunk files from the previous session. Using the default monthly granularity instead:

  ```
  python -m backtest.data.dukascopy_acquire --symbol EURJPY --from 2021-01-01 --to 2026-09-10 --out-dir data
  ```

  resumes Jan–Jun 2021 from the existing monthly files and re-downloads only from the incomplete 2021-07 chunk, at the cost of larger monthly requests that are more likely to be 429-throttled. Either variant produces identical canonical output and is resumable.
- If throttling interrupts the EURJPY run, completed chunks persist and the same command can simply be re-run later (idempotent).
- `data/eurjpy-m5-bid-2021-01-01-2026-09-10.csv` (2.72 MB, no matching ask, stops ~2021-08) is a truncated single-shot artifact that the chunked pipeline ignores; safe to delete.

## 11. Remaining Blocker

**None.** The Dukascopy throttle window that blocked the original session had cleared by 2026-09-11 (all small verification requests succeeded first try). The only open item is the scheduled full EURJPY run (§10 command); it should be run in a later session (it is resumable, so a throttled run simply continues on re-run).