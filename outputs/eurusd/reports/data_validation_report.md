# DATA VALIDATION REPORT

- Rows: `422225`
- First: `2021-01-03 22:00:00`
- Last: `2026-09-09 23:55:00`
- Date range (days): `2075.0798611111113`
- Dominant bar (min): `5` (expected `5`); cadence match: `True`
- Time column sorted: `True`
- Duplicate timestamps: `0`
- Time not-a-date count: `0`
- Timezone: `UTC-naive (no tz info in file); treated as UTC server time`

## OHLC validity

- `ohlc_na`: `0`
- `high_lt_low`: `0`
- `neg_or_zero_ohlc`: `0`
- `close_outside_range`: `36`
- `open_outside_range`: `30`
- `flat_bars_hl_eq_0`: `840`
- `bars_gt_50x_median_range`: `0`
- median bar range: `0.00029`

## Gaps / missing

- gap_count: `404`
- weekend_gap_count: `306` (weekend closures are expected in FX)
- non_weekend_gap_count: `98` (these may indicate missing history/holidays)
- missing_bars_est (total): `175399`
- missing_bars_weekend_only_est: `174640`
- missing_bars_non_weekend_est: `759`
- largest_gap_minutes: `4325.0`

## Spread

- present: `True`
- `spread_na`: `0`
- `spread_positive_count`: `422097`
- `spread_zero_count`: `99`
- `spread_negative_count`: `29`
- `spread_mean_points`: `4.637358237561508`
- `spread_min_points`: `1.0`
- `spread_max_points`: `326.0`
- `spread_zeros_at_tail`: `0`
- `spread_constant_everywhere`: `False`
- zero-spread by weekday (%):
  - Mon: 0/84506 (0.0%)
  - Tue: 0/84919 (0.0%)
  - Wed: 0/84169 (0.0%)
  - Thu: 99/84484 (0.1%)
  - Fri: 0/74773 (0.0%)
  - Sat: 0/0 (-%)
  - Sun: 0/9374 (0.0%)

## Volume

- tick_volume present: `True`; zero: `0`; sum: `318174873974000`
- real_volume present: `True`; zero: `422225`; sum: `0`

## Broker-specificity / data-quality flags

- spread is 0 for 99 candles (0.02%).
- spread has 29 negative values.
- real_volume is all zeros (typical MT5 demo/backtest feed).
- 404 time gaps detected (175399 missing bars estimated total; 98 non-weekend gaps / 759 non-weekend missing bars) - weekends/holidays and possibly missing history.
- 98 non-weekend gaps (759 bars) - check for missing trading days/history.
- 840 bars with high==low.

(This module reports only; it never alters the dataset.)

## Instrument-specific validation

- **ISSUE**: Spread max 326 pts exceeds threshold 50 pts for EURUSD

