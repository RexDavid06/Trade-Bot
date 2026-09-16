# BREAKOUT STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:30:00` .. `2026-09-10 17:35:00`
- **Candles**: `90,000`
- **Timeframe**: M5 (EURUSD)

## Configuration

- **channels**: `[20, 40, 80, 160]`
- **forward_horizons**: `[1, 3, 5, 10, 20, 40, 80]`

## Interpretation

A bar is a **high breakout** if its close pierces the highest high of the prior `CH` candles (excluding the current bar); **low breakout** if its close pierces the lowest low. Continuation predicts positive forward return after a high breakout; breakdown predicts negative return after a low breakout. Bucket = breakout state at entry.

### Channel = 20

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 4454 | 13.72 | 30.00 | 52.6 |
| 1 | inside | 79977 | 1.88 | 10.00 | 50.2 |
| 1 | high_breakout | 5548 | -20.75 | -10.00 | 47.0 |
| 3 | low_breakout | 4454 | 14.06 | 70.00 | 53.7 |
| 3 | inside | 79975 | 5.02 | 20.00 | 51.3 |
| 3 | high_breakout | 5548 | -31.58 | -30.00 | 47.0 |
| 5 | low_breakout | 4454 | 12.56 | 80.00 | 53.5 |
| 5 | inside | 79973 | 8.11 | 30.00 | 51.7 |
| 5 | high_breakout | 5548 | -40.09 | -30.00 | 47.5 |
| 10 | low_breakout | 4452 | 24.39 | 110.00 | 54.8 |
| 10 | inside | 79970 | 13.03 | 60.00 | 52.5 |
| 10 | high_breakout | 5548 | -32.49 | -15.00 | 49.1 |
| 20 | low_breakout | 4450 | 53.23 | 170.00 | 54.7 |
| 20 | inside | 79962 | 25.00 | 90.00 | 52.9 |
| 20 | high_breakout | 5548 | -49.44 | -10.00 | 49.6 |
| 40 | low_breakout | 4449 | 67.18 | 320.00 | 57.1 |
| 40 | inside | 79945 | 49.86 | 160.00 | 53.9 |
| 40 | high_breakout | 5546 | -58.67 | -5.00 | 49.8 |
| 80 | low_breakout | 4449 | 49.18 | 480.00 | 56.6 |
| 80 | inside | 79915 | 97.19 | 310.00 | 54.9 |
| 80 | high_breakout | 5536 | -18.26 | 230.00 | 53.3 |

High breakouts: `5548` bars, low breakouts: `4454` bars (~6.16% / 4.95% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2823 | 9.66 | 30.00 | 52.8 |
| 1 | inside | 83294 | 1.82 | 10.00 | 50.2 |
| 1 | high_breakout | 3842 | -20.91 | -10.00 | 47.0 |
| 3 | low_breakout | 2823 | 4.64 | 60.00 | 53.4 |
| 3 | inside | 83292 | 4.88 | 20.00 | 51.3 |
| 3 | high_breakout | 3842 | -32.39 | -30.00 | 46.5 |
| 5 | low_breakout | 2823 | 7.46 | 90.00 | 53.6 |
| 5 | inside | 83290 | 7.63 | 30.00 | 51.7 |
| 5 | high_breakout | 3842 | -43.36 | -30.00 | 47.2 |
| 10 | low_breakout | 2821 | 25.13 | 140.00 | 55.2 |
| 10 | inside | 83287 | 12.69 | 60.00 | 52.5 |
| 10 | high_breakout | 3842 | -39.70 | -20.00 | 48.9 |
| 20 | low_breakout | 2821 | 24.09 | 160.00 | 54.0 |
| 20 | inside | 83277 | 24.87 | 90.00 | 52.9 |
| 20 | high_breakout | 3842 | -48.63 | -30.00 | 48.8 |
| 40 | low_breakout | 2821 | 31.62 | 370.00 | 57.1 |
| 40 | inside | 83259 | 51.47 | 160.00 | 53.9 |
| 40 | high_breakout | 3840 | -112.15 | -40.00 | 49.1 |
| 80 | low_breakout | 2821 | 28.41 | 450.00 | 55.9 |
| 80 | inside | 83228 | 102.20 | 320.00 | 55.0 |
| 80 | high_breakout | 3831 | -159.05 | 130.00 | 51.9 |

High breakouts: `3842` bars, low breakouts: `2823` bars (~4.27% / 3.14% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1780 | 7.04 | 40.00 | 52.8 |
| 1 | inside | 85391 | 1.41 | 10.00 | 50.2 |
| 1 | high_breakout | 2748 | -12.52 | -10.00 | 47.6 |
| 3 | low_breakout | 1780 | 4.60 | 60.00 | 53.0 |
| 3 | inside | 85389 | 4.14 | 20.00 | 51.2 |
| 3 | high_breakout | 2748 | -24.71 | -30.00 | 47.2 |
| 5 | low_breakout | 1780 | -10.97 | 50.00 | 51.8 |
| 5 | inside | 85387 | 6.85 | 30.00 | 51.7 |
| 5 | high_breakout | 2748 | -27.58 | -30.00 | 47.6 |
| 10 | low_breakout | 1780 | 10.63 | 120.00 | 53.9 |
| 10 | inside | 85382 | 11.92 | 60.00 | 52.5 |
| 10 | high_breakout | 2748 | -20.97 | -5.00 | 49.5 |
| 20 | low_breakout | 1780 | -36.63 | 105.00 | 52.4 |
| 20 | inside | 85372 | 25.40 | 90.00 | 52.9 |
| 20 | high_breakout | 2748 | -37.53 | -40.00 | 48.9 |
| 40 | low_breakout | 1780 | -3.12 | 340.00 | 56.2 |
| 40 | inside | 85354 | 51.94 | 160.00 | 54.0 |
| 40 | high_breakout | 2746 | -119.30 | -60.00 | 48.5 |
| 80 | low_breakout | 1780 | 50.19 | 535.00 | 56.2 |
| 80 | inside | 85323 | 98.41 | 320.00 | 55.0 |
| 80 | high_breakout | 2737 | -137.57 | 70.00 | 50.9 |

High breakouts: `2748` bars, low breakouts: `1780` bars (~3.05% / 1.98% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1153 | 23.89 | 50.00 | 53.3 |
| 1 | inside | 86752 | 1.08 | 10.00 | 50.2 |
| 1 | high_breakout | 1934 | -10.84 | -10.00 | 47.3 |
| 3 | low_breakout | 1153 | 0.26 | 60.00 | 52.6 |
| 3 | inside | 86750 | 3.94 | 20.00 | 51.2 |
| 3 | high_breakout | 1934 | -20.65 | -20.00 | 48.3 |
| 5 | low_breakout | 1153 | -23.07 | 40.00 | 51.3 |
| 5 | inside | 86748 | 6.66 | 30.00 | 51.7 |
| 5 | high_breakout | 1934 | -25.62 | -30.00 | 47.3 |
| 10 | low_breakout | 1153 | -23.27 | 80.00 | 52.6 |
| 10 | inside | 86743 | 12.34 | 60.00 | 52.5 |
| 10 | high_breakout | 1934 | -21.00 | 0.00 | 49.9 |
| 20 | low_breakout | 1153 | -106.76 | 40.00 | 50.8 |
| 20 | inside | 86733 | 25.16 | 90.00 | 52.9 |
| 20 | high_breakout | 1934 | -27.80 | -35.00 | 49.1 |
| 40 | low_breakout | 1153 | -140.78 | 300.00 | 55.0 |
| 40 | inside | 86715 | 52.03 | 160.00 | 53.9 |
| 40 | high_breakout | 1932 | -163.25 | -95.00 | 48.0 |
| 80 | low_breakout | 1153 | -146.48 | 510.00 | 55.2 |
| 80 | inside | 86684 | 96.67 | 320.00 | 54.9 |
| 80 | high_breakout | 1923 | -130.04 | 130.00 | 51.9 |

High breakouts: `1934` bars, low breakouts: `1153` bars (~2.15% / 1.28% of dataset).

