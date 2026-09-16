# DATA VALIDATION REPORT

- Rows: `374746`
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
- `high_lt_low`: `2`
- `neg_or_zero_ohlc`: `0`
- `close_outside_range`: `36`
- `open_outside_range`: `23`
- `flat_bars_hl_eq_0`: `449`
- `bars_gt_50x_median_range`: `2`
- median bar range: `0.00040`

## Gaps / missing

- gap_count: `494`
- weekend_gap_count: `414` (weekend closures are expected in FX)
- non_weekend_gap_count: `80` (these may indicate missing history/holidays)
- missing_bars_est (total): `222878`
- missing_bars_weekend_only_est: `222418`
- missing_bars_non_weekend_est: `460`
- largest_gap_minutes: `5765.0`

## Spread

- present: `True`
- `spread_na`: `0`
- `spread_positive_count`: `374746`
- `spread_zero_count`: `0`
- `spread_negative_count`: `0`
- `spread_mean_points`: `11.408834250398938`
- `spread_min_points`: `1.0`
- `spread_max_points`: `382.0`
- `spread_zeros_at_tail`: `0`
- `spread_constant_everywhere`: `False`
- zero-spread by weekday (%):
  - Mon: 0/74308 (0.0%)
  - Tue: 0/74553 (0.0%)
  - Wed: 0/74965 (0.0%)
  - Thu: 0/75849 (0.0%)
  - Fri: 0/66864 (0.0%)
  - Sat: 0/0 (-%)
  - Sun: 0/8207 (0.0%)

## Volume

- tick_volume present: `True`; zero: `0`; sum: `169040179105900`
- real_volume present: `True`; zero: `374746`; sum: `0`

## Broker-specificity / data-quality flags

- real_volume is all zeros (typical MT5 demo/backtest feed).
- 494 time gaps detected (222878 missing bars estimated total; 80 non-weekend gaps / 460 non-weekend missing bars) - weekends/holidays and possibly missing history.
- 80 non-weekend gaps (460 bars) - check for missing trading days/history.
- 449 bars with high==low.

(This module reports only; it never alters the dataset.)

## Instrument-specific validation

- **ISSUE**: Spread max 382 pts exceeds threshold 60 pts for GBPUSD
- **ISSUE**: Price range [1.0400, 1.4246] outside expected [1.1, 1.6]

