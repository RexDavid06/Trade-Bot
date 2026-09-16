# BREAKOUT STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 22:45:00` .. `2026-09-10 17:35:00`
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
| 1 | low_breakout | 4900 | 0.19 | 0.20 | 52.1 |
| 1 | inside | 80058 | -0.01 | 0.00 | 48.5 |
| 1 | high_breakout | 5021 | -0.09 | -0.10 | 46.1 |
| 3 | low_breakout | 4900 | 0.25 | 0.20 | 51.5 |
| 3 | inside | 80057 | 0.00 | 0.00 | 49.2 |
| 3 | high_breakout | 5020 | -0.28 | -0.30 | 44.6 |
| 5 | low_breakout | 4900 | 0.31 | 0.20 | 51.8 |
| 5 | inside | 80056 | -0.00 | 0.00 | 49.3 |
| 5 | high_breakout | 5019 | -0.30 | -0.40 | 45.1 |
| 10 | low_breakout | 4900 | 0.40 | 0.40 | 52.3 |
| 10 | inside | 80051 | -0.01 | 0.00 | 49.3 |
| 10 | high_breakout | 5019 | -0.35 | -0.50 | 45.8 |
| 20 | low_breakout | 4900 | 0.71 | 0.70 | 52.7 |
| 20 | inside | 80041 | -0.03 | -0.10 | 49.2 |
| 20 | high_breakout | 5019 | -0.38 | -0.40 | 47.5 |
| 40 | low_breakout | 4896 | 0.78 | 0.60 | 51.8 |
| 40 | inside | 80025 | -0.04 | -0.10 | 49.3 |
| 40 | high_breakout | 5019 | -0.56 | -0.70 | 47.2 |
| 80 | low_breakout | 4892 | 0.97 | 0.80 | 52.0 |
| 80 | inside | 79989 | -0.07 | -0.50 | 48.6 |
| 80 | high_breakout | 5019 | -0.75 | -1.20 | 47.3 |

High breakouts: `5022` bars, low breakouts: `4900` bars (~5.58% / 5.44% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 3357 | 0.20 | 0.20 | 53.3 |
| 1 | inside | 83158 | -0.00 | 0.00 | 48.5 |
| 1 | high_breakout | 3444 | -0.09 | -0.10 | 46.3 |
| 3 | low_breakout | 3357 | 0.23 | 0.30 | 52.7 |
| 3 | inside | 83156 | 0.00 | 0.00 | 49.1 |
| 3 | high_breakout | 3444 | -0.34 | -0.50 | 43.8 |
| 5 | low_breakout | 3357 | 0.24 | 0.30 | 52.9 |
| 5 | inside | 83154 | 0.00 | 0.00 | 49.3 |
| 5 | high_breakout | 3444 | -0.35 | -0.60 | 44.1 |
| 10 | low_breakout | 3357 | 0.38 | 0.60 | 53.5 |
| 10 | inside | 83149 | -0.00 | 0.00 | 49.3 |
| 10 | high_breakout | 3444 | -0.42 | -0.60 | 45.8 |
| 20 | low_breakout | 3357 | 0.78 | 0.90 | 53.8 |
| 20 | inside | 83139 | -0.03 | -0.10 | 49.2 |
| 20 | high_breakout | 3444 | -0.38 | -0.50 | 47.4 |
| 40 | low_breakout | 3353 | 0.88 | 0.80 | 52.4 |
| 40 | inside | 83123 | -0.04 | -0.10 | 49.3 |
| 40 | high_breakout | 3444 | -0.61 | -0.80 | 47.2 |
| 80 | low_breakout | 3349 | 1.27 | 0.90 | 52.0 |
| 80 | inside | 83087 | -0.08 | -0.50 | 48.6 |
| 80 | high_breakout | 3444 | -0.66 | -1.05 | 47.3 |

High breakouts: `3444` bars, low breakouts: `3357` bars (~3.83% / 3.73% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2247 | 0.22 | 0.20 | 53.1 |
| 1 | inside | 85338 | -0.00 | 0.00 | 48.5 |
| 1 | high_breakout | 2334 | -0.14 | -0.10 | 46.3 |
| 3 | low_breakout | 2247 | 0.21 | 0.30 | 52.9 |
| 3 | inside | 85336 | 0.00 | 0.00 | 49.1 |
| 3 | high_breakout | 2334 | -0.41 | -0.50 | 43.3 |
| 5 | low_breakout | 2247 | 0.24 | 0.40 | 53.4 |
| 5 | inside | 85334 | 0.00 | 0.00 | 49.2 |
| 5 | high_breakout | 2334 | -0.39 | -0.70 | 44.0 |
| 10 | low_breakout | 2247 | 0.49 | 0.80 | 54.7 |
| 10 | inside | 85329 | -0.01 | 0.00 | 49.2 |
| 10 | high_breakout | 2334 | -0.40 | -0.60 | 45.6 |
| 20 | low_breakout | 2247 | 0.90 | 1.10 | 54.3 |
| 20 | inside | 85319 | -0.03 | -0.10 | 49.2 |
| 20 | high_breakout | 2334 | -0.45 | -0.60 | 47.0 |
| 40 | low_breakout | 2243 | 1.30 | 1.10 | 53.1 |
| 40 | inside | 85303 | -0.06 | -0.10 | 49.3 |
| 40 | high_breakout | 2334 | -0.21 | -1.00 | 46.8 |
| 80 | low_breakout | 2239 | 1.67 | 1.30 | 53.3 |
| 80 | inside | 85267 | -0.10 | -0.50 | 48.6 |
| 80 | high_breakout | 2334 | -0.35 | -1.20 | 47.3 |

High breakouts: `2334` bars, low breakouts: `2247` bars (~2.59% / 2.50% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1545 | 0.18 | 0.20 | 51.7 |
| 1 | inside | 86768 | -0.00 | 0.00 | 48.5 |
| 1 | high_breakout | 1526 | -0.15 | -0.20 | 46.2 |
| 3 | low_breakout | 1545 | 0.21 | 0.20 | 52.4 |
| 3 | inside | 86766 | 0.00 | 0.00 | 49.1 |
| 3 | high_breakout | 1526 | -0.52 | -0.70 | 42.9 |
| 5 | low_breakout | 1545 | 0.30 | 0.40 | 53.4 |
| 5 | inside | 86764 | -0.00 | 0.00 | 49.2 |
| 5 | high_breakout | 1526 | -0.44 | -0.80 | 43.6 |
| 10 | low_breakout | 1545 | 0.61 | 1.00 | 54.7 |
| 10 | inside | 86759 | -0.02 | 0.00 | 49.2 |
| 10 | high_breakout | 1526 | -0.22 | -0.60 | 46.3 |
| 20 | low_breakout | 1545 | 1.57 | 2.00 | 57.0 |
| 20 | inside | 86749 | -0.05 | -0.10 | 49.2 |
| 20 | high_breakout | 1526 | -0.15 | -0.60 | 47.4 |
| 40 | low_breakout | 1541 | 2.24 | 2.10 | 55.2 |
| 40 | inside | 86733 | -0.09 | -0.20 | 49.2 |
| 40 | high_breakout | 1526 | 0.15 | -1.15 | 45.9 |
| 80 | low_breakout | 1539 | 2.95 | 2.30 | 55.7 |
| 80 | inside | 86695 | -0.14 | -0.60 | 48.6 |
| 80 | high_breakout | 1526 | 0.53 | -0.90 | 48.0 |

High breakouts: `1526` bars, low breakouts: `1545` bars (~1.70% / 1.72% of dataset).

