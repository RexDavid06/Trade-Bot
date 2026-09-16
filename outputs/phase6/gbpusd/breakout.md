# BREAKOUT STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 23:45:00` .. `2026-09-10 17:35:00`
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
| 1 | low_breakout | 5252 | 0.15 | 0.10 | 51.0 |
| 1 | inside | 79695 | -0.00 | 0.00 | 48.7 |
| 1 | high_breakout | 5032 | -0.16 | -0.20 | 45.2 |
| 3 | low_breakout | 5252 | 0.16 | 0.20 | 52.0 |
| 3 | inside | 79693 | 0.01 | 0.00 | 49.4 |
| 3 | high_breakout | 5032 | -0.35 | -0.40 | 45.6 |
| 5 | low_breakout | 5252 | 0.26 | 0.30 | 52.4 |
| 5 | inside | 79692 | -0.00 | 0.00 | 49.4 |
| 5 | high_breakout | 5031 | -0.36 | -0.30 | 46.9 |
| 10 | low_breakout | 5252 | 0.24 | 0.50 | 52.2 |
| 10 | inside | 79687 | -0.00 | 0.00 | 49.5 |
| 10 | high_breakout | 5031 | -0.50 | -0.40 | 47.4 |
| 20 | low_breakout | 5252 | 0.85 | 0.90 | 53.1 |
| 20 | inside | 79677 | -0.06 | -0.10 | 49.3 |
| 20 | high_breakout | 5031 | -0.56 | -0.90 | 46.7 |
| 40 | low_breakout | 5246 | 1.12 | 1.10 | 53.0 |
| 40 | inside | 79663 | -0.11 | -0.10 | 49.6 |
| 40 | high_breakout | 5031 | -0.66 | -0.50 | 48.4 |
| 80 | low_breakout | 5241 | 1.00 | 1.40 | 52.4 |
| 80 | inside | 79628 | -0.20 | -0.20 | 49.5 |
| 80 | high_breakout | 5031 | -0.37 | -0.20 | 49.6 |

High breakouts: `5032` bars, low breakouts: `5252` bars (~5.59% / 5.84% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 3544 | 0.16 | 0.20 | 51.3 |
| 1 | inside | 82998 | -0.00 | 0.00 | 48.7 |
| 1 | high_breakout | 3417 | -0.17 | -0.20 | 44.8 |
| 3 | low_breakout | 3544 | 0.24 | 0.30 | 52.6 |
| 3 | inside | 82996 | 0.00 | 0.00 | 49.4 |
| 3 | high_breakout | 3417 | -0.49 | -0.60 | 44.5 |
| 5 | low_breakout | 3544 | 0.39 | 0.50 | 53.2 |
| 5 | inside | 82994 | -0.00 | 0.00 | 49.4 |
| 5 | high_breakout | 3417 | -0.56 | -0.50 | 45.7 |
| 10 | low_breakout | 3544 | 0.34 | 0.60 | 52.8 |
| 10 | inside | 82989 | -0.01 | 0.00 | 49.5 |
| 10 | high_breakout | 3417 | -0.72 | -0.50 | 47.0 |
| 20 | low_breakout | 3544 | 1.02 | 0.95 | 53.1 |
| 20 | inside | 82979 | -0.05 | -0.10 | 49.4 |
| 20 | high_breakout | 3417 | -0.90 | -1.30 | 45.8 |
| 40 | low_breakout | 3538 | 1.07 | 1.10 | 52.8 |
| 40 | inside | 82965 | -0.10 | -0.10 | 49.7 |
| 40 | high_breakout | 3417 | -0.70 | -0.70 | 47.8 |
| 80 | low_breakout | 3533 | 1.37 | 1.40 | 52.5 |
| 80 | inside | 82930 | -0.21 | -0.20 | 49.5 |
| 80 | high_breakout | 3417 | -0.11 | 0.00 | 49.9 |

High breakouts: `3417` bars, low breakouts: `3544` bars (~3.80% / 3.94% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2392 | 0.12 | 0.10 | 51.0 |
| 1 | inside | 85204 | -0.00 | 0.00 | 48.6 |
| 1 | high_breakout | 2323 | -0.19 | -0.30 | 45.0 |
| 3 | low_breakout | 2392 | 0.14 | 0.30 | 52.3 |
| 3 | inside | 85202 | 0.01 | 0.00 | 49.4 |
| 3 | high_breakout | 2323 | -0.58 | -0.60 | 44.3 |
| 5 | low_breakout | 2392 | 0.19 | 0.40 | 52.8 |
| 5 | inside | 85200 | 0.00 | 0.00 | 49.4 |
| 5 | high_breakout | 2323 | -0.74 | -0.70 | 45.0 |
| 10 | low_breakout | 2392 | 0.01 | 0.40 | 51.9 |
| 10 | inside | 85195 | -0.00 | 0.00 | 49.5 |
| 10 | high_breakout | 2323 | -0.75 | -0.50 | 47.5 |
| 20 | low_breakout | 2392 | 0.63 | 0.45 | 51.6 |
| 20 | inside | 85185 | -0.04 | -0.10 | 49.4 |
| 20 | high_breakout | 2323 | -0.82 | -1.30 | 46.1 |
| 40 | low_breakout | 2386 | 1.08 | 1.10 | 52.6 |
| 40 | inside | 85171 | -0.10 | 0.00 | 49.7 |
| 40 | high_breakout | 2323 | -0.57 | -0.80 | 47.7 |
| 80 | low_breakout | 2382 | 1.33 | 1.20 | 51.9 |
| 80 | inside | 85135 | -0.22 | -0.20 | 49.6 |
| 80 | high_breakout | 2323 | 0.13 | 0.30 | 50.5 |

High breakouts: `2323` bars, low breakouts: `2392` bars (~2.58% / 2.66% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1699 | 0.06 | 0.00 | 50.0 |
| 1 | inside | 86536 | -0.00 | 0.00 | 48.6 |
| 1 | high_breakout | 1604 | -0.17 | -0.20 | 46.3 |
| 3 | low_breakout | 1699 | 0.11 | 0.30 | 52.0 |
| 3 | inside | 86534 | 0.00 | 0.00 | 49.3 |
| 3 | high_breakout | 1604 | -0.57 | -0.70 | 44.1 |
| 5 | low_breakout | 1699 | 0.19 | 0.50 | 52.9 |
| 5 | inside | 86532 | -0.00 | 0.00 | 49.4 |
| 5 | high_breakout | 1604 | -0.66 | -0.80 | 45.4 |
| 10 | low_breakout | 1699 | 0.04 | 0.80 | 52.7 |
| 10 | inside | 86527 | -0.02 | 0.00 | 49.5 |
| 10 | high_breakout | 1604 | -0.49 | -0.30 | 48.3 |
| 20 | low_breakout | 1699 | 1.17 | 1.20 | 53.6 |
| 20 | inside | 86517 | -0.07 | -0.10 | 49.4 |
| 20 | high_breakout | 1604 | -0.38 | -1.30 | 46.7 |
| 40 | low_breakout | 1693 | 1.64 | 1.10 | 52.5 |
| 40 | inside | 86503 | -0.14 | -0.10 | 49.7 |
| 40 | high_breakout | 1604 | 0.65 | -0.10 | 49.7 |
| 80 | low_breakout | 1690 | 1.61 | 1.25 | 52.0 |
| 80 | inside | 86466 | -0.23 | -0.20 | 49.6 |
| 80 | high_breakout | 1604 | 0.87 | 0.60 | 50.8 |

High breakouts: `1604` bars, low breakouts: `1699` bars (~1.78% / 1.89% of dataset).

