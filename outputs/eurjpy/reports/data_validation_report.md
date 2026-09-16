# DATA VALIDATION REPORT

- Rows: `90000`
- First: `2025-06-26 03:00:00`
- Last: `2026-09-10 19:05:00`
- Date range (days): `441.6701388888889`
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
- `flat_bars_hl_eq_0`: `10`
- `bars_gt_50x_median_range`: `0`
- median bar range: `0.04700`

## Gaps / missing

- gap_count: `76`
- weekend_gap_count: `65` (weekend closures are expected in FX)
- non_weekend_gap_count: `11` (these may indicate missing history/holidays)
- missing_bars_est (total): `37202`
- missing_bars_weekend_only_est: `36912`
- missing_bars_non_weekend_est: `290`
- largest_gap_minutes: `2945.0`

## Spread

- present: `True`
- `spread_na`: `0`
- `spread_positive_count`: `65704`
- `spread_zero_count`: `24296`
- `spread_negative_count`: `0`
- `spread_mean_points`: `19.63572994033849`
- `spread_min_points`: `1.0`
- `spread_max_points`: `445.0`
- `spread_zeros_at_tail`: `199`
- `spread_constant_everywhere`: `False`
- zero-spread by weekday (%):
  - Mon: 4929/18136 (27.2%)
  - Tue: 4859/18143 (26.8%)
  - Wed: 5050/18144 (27.8%)
  - Thu: 4803/17602 (27.3%)
  - Fri: 4655/17975 (25.9%)
  - Sat: 0/0 (-%)
  - Sun: 0/0 (-%)

## Volume

- tick_volume present: `True`; zero: `0`; sum: `37545355`
- real_volume present: `True`; zero: `90000`; sum: `0`

## Broker-specificity / data-quality flags

- spread is 0 for 24296 candles (27.00%).
- zero spread is NOT weekend-only: 27.0% of Mon-Fri candles also have spread=0 (feed artifact).
- real_volume is all zeros (typical MT5 demo/backtest feed).
- 76 time gaps detected (37202 missing bars estimated total; 11 non-weekend gaps / 290 non-weekend missing bars) - weekends/holidays and possibly missing history.
- 11 non-weekend gaps (290 bars) - check for missing trading days/history.
- 10 bars with high==low.

(This module reports only; it never alters the dataset.)

## Instrument-specific validation

- **ISSUE**: Spread max 445 pts exceeds threshold 70 pts for EURJPY

