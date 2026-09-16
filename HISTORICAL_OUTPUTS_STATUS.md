# Historical Outputs Status

**Created:** 2026-09-10 (Phase 0)

---

## Status of Previous Research Outputs

```
Historical Phase 5:
    INVALIDATED by Phase 6.5 audit

Historical Phase 6:
    INVALIDATED as formal evidence because holdout isolation was not respected

Current data:
    EXPLORATORY / NOT YET SUFFICIENT for definitive conclusions

Phase 0:
    IN PROGRESS
```

---

## Why Historical Outputs Are Invalidated

### Phase 5 (Strategy Benchmark)

**Reason:** The handoff document (`PROJECT_RESEARCH_HANDOFF.md`) contained fabricated performance numbers that did not match the actual source data (`outputs/benchmark/results.json`). Additionally, EURJPY results are meaningless due to incorrect pip scaling (pip=0.0001 used instead of 0.01).

**Action:** Do not use Phase 5 numbers from the handoff document. The raw `results.json` is the authoritative source, but even those EURJPY numbers are invalid.

### Phase 6 (Market Research)

**Reason:** Phase 6 studies were run on the FULL 90,000-bar dataset without respecting dev/val/holdout splits. The holdout period (last 20% of data) was included in the analysis, contaminating the holdout for all 28 hypotheses.

**Action:** Do not use Phase 6 findings as formal evidence. The behavioral patterns (reversal, mean reversion) may be real but are unvalidated and the holdout is compromised.

### Phase 1-4 (Original Research)

**Reason:** These were conducted on EURUSD only and used a broken spread feed (48.3% zero-spread bars). The findings are exploratory, not definitive.

**Action:** Treat as preliminary hypotheses requiring re-validation on clean multi-year data.

---

## What Remains Available

| Output | Status | Can Be Used For |
|--------|--------|-----------------|
| `outputs/benchmark/results.json` | Raw data available, EURJPY invalid | Understanding Phase 5 methodology (not conclusions) |
| `outputs/phase6/*/*.json` | Per-symbol data appears correct despite wrong headers | Understanding Phase 6 methodology (not conclusions) |
| `outputs/*/reports/data_validation_report.md` | Data quality audits are valid | Understanding current data limitations |
| `outputs/*/reports/data_split.json` | Split metadata is valid | Understanding previous split methodology |
| `MARKET_RESEARCH_REPORT.md` | Exploratory findings, not definitive | Identifying patterns for future investigation |

---

## What Must NOT Be Done With Historical Outputs

1. Do not present Phase 5/6 numbers as validated findings
2. Do not use compromised holdout as evidence of out-of-sample performance
3. Do not cherry-pick "good" results from invalidated studies
4. Do not delete historical outputs (they document the research process)
5. Do not overwrite with "corrected" numbers (that would be dishonest)

---

## When Historical Outputs Become Valid Again

Historical outputs can be considered exploratory evidence (not definitive) when:

1. Fresh multi-year data is obtained (3-5+ years)
2. Clean spread data replaces the broken feed
3. EURJPY pip scaling is fixed
4. New dev/val/holdout splits are established
5. Phase 6 studies are re-run on development data only
6. Results are validated on clean holdout

Until then, all previous research conclusions are **INVALIDATED as formal evidence**.

---

## Hygiene-Fence Notice (2026-09-13, Step 0)

- Interpreter baseline pinned to **Python 3.13** (`.python-version`). Bytecode
  (`__pycache__`) from both 3.13 and 3.14 runs was untracked from the index and is
  now ignored (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`) — it is caches, not
  evidence.
- Raw/intermediate Dukascopy artifacts (bid/ask chunk CSVs, `diag_seq/`, `poc*/`,
  `smoke_*/`, `temp_range_test/`) are now ignored; the canonical merged
  `data/<symbol>_m5.csv` files remain tracked evidence.
- `requirements.txt` now pins `matplotlib` and `pytest` (previously implied but
  unpinned). No existing package versions were changed.
- No historical outputs were deleted or rewritten.
