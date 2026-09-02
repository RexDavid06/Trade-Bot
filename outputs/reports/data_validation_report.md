# DATA VALIDATION REPORT

- Rows: `90000`
- First: `2025-06-16 23:30:00`
- Last: `2026-09-01 18:20:00`
- Date range (days): `441.78472222222223`
- Dominant bar (min): `5` (expected `5`); cadence match: `True`
- Time column sorted: `True`
- Duplicate timestamps: `0`
- Time not-a-date count: `0`
- Timezone: `UTC-naive (no tz info in file); treated as UTC server time`

## OHLC validity

- `ohlc_na`: `0`
- `high_lt_low`: `0`
- `neg_or_zero_ohlc`: `0`
- `close_outside_range`: `0`
- `open_outside_range`: `0`
- `flat_bars_hl_eq_0`: `38`
- `bars_gt_50x_median_range`: `0`
- median bar range: `0.00030`

## Gaps / missing

- gap_count: `96`
- weekend_gap_count: `65` (weekend closures are expected in FX)
- non_weekend_gap_count: `31` (these may indicate missing history/holidays)
- missing_bars_est (total): `37235`
- missing_bars_weekend_only_est: `36913`
- missing_bars_non_weekend_est: `322`
- largest_gap_minutes: `2945.0`

## Spread

- present: `True`
- `spread_na`: `0`
- `spread_positive_count`: `48549`
- `spread_zero_count`: `41451`
- `spread_negative_count`: `0`
- `spread_mean_points`: `5.415641928772993`
- `spread_min_points`: `1.0`
- `spread_max_points`: `176.0`
- `spread_zeros_at_tail`: `200`
- `spread_constant_everywhere`: `False`
- zero-spread by weekday (%):
  - Mon: 8760/18122 (48.3%)
  - Tue: 8468/18359 (46.1%)
  - Wed: 8205/18142 (45.2%)
  - Thu: 7843/17405 (45.1%)
  - Fri: 8175/17972 (45.5%)
  - Sat: 0/0 (-%)
  - Sun: 0/0 (-%)

## Volume

- tick_volume present: `True`; zero: `0`; sum: `31219120`
- real_volume present: `True`; zero: `90000`; sum: `0`

## Broker-specificity / data-quality flags

- spread is 0 for 41451 candles (46.06%).
- zero spread is NOT weekend-only: 46.1% of Mon-Fri candles also have spread=0 (feed artifact).
- real_volume is all zeros (typical MT5 demo/backtest feed).
- 96 time gaps detected (37235 missing bars estimated total; 31 non-weekend gaps / 322 non-weekend missing bars) - weekends/holidays and possibly missing history.
- 31 non-weekend gaps (322 bars) - check for missing trading days/history.
- last 200 candles all have spread=0 - feed may be stale near the end of the file.
- 38 bars with high==low.

(This module reports only; it never alters the dataset.)
