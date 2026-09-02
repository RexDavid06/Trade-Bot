# BREAKOUT STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-16 23:30:00` .. `2026-09-01 18:20:00`
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
| 1 | low_breakout | 4896 | 0.20 | 0.20 | 52.1 |
| 1 | inside | 80035 | -0.01 | 0.00 | 48.5 |
| 1 | high_breakout | 5048 | -0.09 | -0.10 | 46.1 |
| 3 | low_breakout | 4896 | 0.27 | 0.20 | 51.8 |
| 3 | inside | 80033 | 0.00 | 0.00 | 49.2 |
| 3 | high_breakout | 5048 | -0.26 | -0.30 | 44.7 |
| 5 | low_breakout | 4896 | 0.33 | 0.30 | 52.0 |
| 5 | inside | 80031 | -0.00 | 0.00 | 49.3 |
| 5 | high_breakout | 5048 | -0.27 | -0.40 | 45.3 |
| 10 | low_breakout | 4896 | 0.45 | 0.40 | 52.5 |
| 10 | inside | 80026 | -0.00 | 0.00 | 49.4 |
| 10 | high_breakout | 5048 | -0.31 | -0.50 | 46.0 |
| 20 | low_breakout | 4896 | 0.72 | 0.70 | 52.8 |
| 20 | inside | 80018 | -0.01 | -0.10 | 49.3 |
| 20 | high_breakout | 5046 | -0.34 | -0.40 | 47.7 |
| 40 | low_breakout | 4895 | 0.74 | 0.60 | 51.6 |
| 40 | inside | 80002 | 0.00 | -0.10 | 49.4 |
| 40 | high_breakout | 5043 | -0.45 | -0.60 | 47.8 |
| 80 | low_breakout | 4894 | 1.00 | 0.70 | 51.7 |
| 80 | inside | 79964 | 0.02 | -0.50 | 48.8 |
| 80 | high_breakout | 5042 | -0.58 | -1.00 | 47.5 |

High breakouts: `5048` bars, low breakouts: `4897` bars (~5.61% / 5.44% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 3353 | 0.21 | 0.20 | 53.3 |
| 1 | inside | 83133 | -0.00 | 0.00 | 48.5 |
| 1 | high_breakout | 3473 | -0.09 | -0.10 | 46.4 |
| 3 | low_breakout | 3353 | 0.24 | 0.30 | 53.0 |
| 3 | inside | 83131 | 0.01 | 0.00 | 49.1 |
| 3 | high_breakout | 3473 | -0.33 | -0.40 | 44.0 |
| 5 | low_breakout | 3353 | 0.24 | 0.30 | 52.9 |
| 5 | inside | 83129 | 0.01 | 0.00 | 49.3 |
| 5 | high_breakout | 3473 | -0.33 | -0.60 | 44.3 |
| 10 | low_breakout | 3353 | 0.42 | 0.60 | 53.6 |
| 10 | inside | 83124 | 0.00 | 0.00 | 49.3 |
| 10 | high_breakout | 3473 | -0.36 | -0.60 | 46.0 |
| 20 | low_breakout | 3353 | 0.78 | 1.00 | 53.9 |
| 20 | inside | 83116 | -0.01 | -0.10 | 49.3 |
| 20 | high_breakout | 3471 | -0.31 | -0.40 | 47.6 |
| 40 | low_breakout | 3352 | 0.90 | 0.80 | 52.4 |
| 40 | inside | 83100 | 0.00 | -0.10 | 49.4 |
| 40 | high_breakout | 3468 | -0.46 | -0.55 | 47.9 |
| 80 | low_breakout | 3352 | 1.32 | 0.80 | 51.8 |
| 80 | inside | 83060 | 0.00 | -0.50 | 48.8 |
| 80 | high_breakout | 3468 | -0.45 | -0.90 | 47.7 |

High breakouts: `3473` bars, low breakouts: `3353` bars (~3.86% / 3.73% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2247 | 0.23 | 0.20 | 53.2 |
| 1 | inside | 85296 | -0.00 | 0.00 | 48.5 |
| 1 | high_breakout | 2376 | -0.14 | -0.10 | 46.3 |
| 3 | low_breakout | 2247 | 0.24 | 0.30 | 53.1 |
| 3 | inside | 85294 | 0.01 | 0.00 | 49.1 |
| 3 | high_breakout | 2376 | -0.42 | -0.50 | 43.5 |
| 5 | low_breakout | 2247 | 0.25 | 0.40 | 53.4 |
| 5 | inside | 85292 | 0.01 | 0.00 | 49.3 |
| 5 | high_breakout | 2376 | -0.39 | -0.70 | 44.2 |
| 10 | low_breakout | 2247 | 0.55 | 0.80 | 54.8 |
| 10 | inside | 85287 | -0.00 | 0.00 | 49.3 |
| 10 | high_breakout | 2376 | -0.35 | -0.60 | 45.7 |
| 20 | low_breakout | 2247 | 0.97 | 1.10 | 54.7 |
| 20 | inside | 85279 | -0.01 | -0.10 | 49.3 |
| 20 | high_breakout | 2374 | -0.40 | -0.60 | 47.1 |
| 40 | low_breakout | 2247 | 1.39 | 1.20 | 53.4 |
| 40 | inside | 85259 | -0.02 | -0.10 | 49.4 |
| 40 | high_breakout | 2374 | -0.07 | -0.70 | 47.6 |
| 80 | low_breakout | 2247 | 1.71 | 1.20 | 53.0 |
| 80 | inside | 85219 | -0.01 | -0.50 | 48.7 |
| 80 | high_breakout | 2374 | -0.08 | -1.00 | 47.7 |

High breakouts: `2376` bars, low breakouts: `2247` bars (~2.64% / 2.50% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1541 | 0.19 | 0.20 | 51.7 |
| 1 | inside | 86730 | -0.00 | 0.00 | 48.6 |
| 1 | high_breakout | 1568 | -0.14 | -0.20 | 46.4 |
| 3 | low_breakout | 1541 | 0.23 | 0.20 | 52.7 |
| 3 | inside | 86728 | 0.01 | 0.00 | 49.1 |
| 3 | high_breakout | 1568 | -0.51 | -0.70 | 43.2 |
| 5 | low_breakout | 1541 | 0.32 | 0.40 | 53.3 |
| 5 | inside | 86726 | 0.00 | 0.00 | 49.3 |
| 5 | high_breakout | 1568 | -0.43 | -0.75 | 44.1 |
| 10 | low_breakout | 1541 | 0.67 | 1.00 | 54.9 |
| 10 | inside | 86721 | -0.00 | 0.00 | 49.3 |
| 10 | high_breakout | 1568 | -0.18 | -0.60 | 46.5 |
| 20 | low_breakout | 1541 | 1.65 | 2.00 | 57.4 |
| 20 | inside | 86711 | -0.02 | -0.10 | 49.2 |
| 20 | high_breakout | 1568 | -0.16 | -0.60 | 47.4 |
| 40 | low_breakout | 1541 | 2.30 | 2.30 | 55.6 |
| 40 | inside | 86691 | -0.03 | -0.10 | 49.4 |
| 40 | high_breakout | 1568 | 0.29 | -1.00 | 46.7 |
| 80 | low_breakout | 1541 | 2.73 | 2.10 | 55.2 |
| 80 | inside | 86651 | -0.02 | -0.50 | 48.7 |
| 80 | high_breakout | 1568 | 0.90 | -0.70 | 48.6 |

High breakouts: `1568` bars, low breakouts: `1541` bars (~1.74% / 1.71% of dataset).

