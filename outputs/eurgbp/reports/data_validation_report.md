# DATA VALIDATION REPORT

- Rows: `425477`
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
- `close_outside_range`: `17`
- `open_outside_range`: `24`
- `flat_bars_hl_eq_0`: `286`
- `bars_gt_50x_median_range`: `3`
- median bar range: `0.00019`

## Gaps / missing

- gap_count: `432`
- weekend_gap_count: `298` (weekend closures are expected in FX)
- non_weekend_gap_count: `134` (these may indicate missing history/holidays)
- missing_bars_est (total): `172147`
- missing_bars_weekend_only_est: `171459`
- missing_bars_non_weekend_est: `688`
- largest_gap_minutes: `4325.0`

## Spread

- present: `True`
- `spread_na`: `0`
- `spread_positive_count`: `425477`
- `spread_zero_count`: `0`
- `spread_negative_count`: `0`
- `spread_mean_points`: `11.683588067040052`
- `spread_min_points`: `1.0`
- `spread_max_points`: `350.0`
- `spread_zeros_at_tail`: `0`
- `spread_constant_everywhere`: `False`
- zero-spread by weekday (%):
  - Mon: 0/85067 (0.0%)
  - Tue: 0/85486 (0.0%)
  - Wed: 0/85031 (0.0%)
  - Thu: 0/84777 (0.0%)
  - Fri: 0/75792 (0.0%)
  - Sat: 0/0 (-%)
  - Sun: 0/9324 (0.0%)

## Volume

- tick_volume present: `True`; zero: `0`; sum: `178848501370000`
- real_volume present: `True`; zero: `425477`; sum: `0`

## Broker-specificity / data-quality flags

- real_volume is all zeros (typical MT5 demo/backtest feed).
- 432 time gaps detected (172147 missing bars estimated total; 134 non-weekend gaps / 688 non-weekend missing bars) - weekends/holidays and possibly missing history.
- 134 non-weekend gaps (688 bars) - check for missing trading days/history.
- 286 bars with high==low.

(This module reports only; it never alters the dataset.)

## Instrument-specific validation

- **ISSUE**: Spread max 350 pts exceeds threshold 70 pts for EURGBP

