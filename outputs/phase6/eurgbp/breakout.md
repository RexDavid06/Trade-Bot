# BREAKOUT STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:20:00` .. `2026-09-10 17:35:00`
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
| 1 | low_breakout | 4861 | 0.22 | 0.20 | 54.2 |
| 1 | inside | 80621 | -0.00 | 0.00 | 47.1 |
| 1 | high_breakout | 4497 | -0.17 | -0.10 | 43.1 |
| 3 | low_breakout | 4861 | 0.24 | 0.20 | 53.8 |
| 3 | inside | 80620 | 0.00 | 0.00 | 48.5 |
| 3 | high_breakout | 4496 | -0.23 | -0.20 | 43.1 |
| 5 | low_breakout | 4861 | 0.25 | 0.20 | 53.2 |
| 5 | inside | 80618 | -0.00 | 0.00 | 48.6 |
| 5 | high_breakout | 4496 | -0.18 | -0.30 | 43.6 |
| 10 | low_breakout | 4861 | 0.19 | 0.10 | 51.2 |
| 10 | inside | 80614 | 0.00 | 0.00 | 48.8 |
| 10 | high_breakout | 4495 | -0.14 | -0.40 | 44.2 |
| 20 | low_breakout | 4861 | 0.54 | 0.40 | 53.3 |
| 20 | inside | 80604 | -0.01 | 0.00 | 49.7 |
| 20 | high_breakout | 4495 | -0.19 | -0.40 | 45.4 |
| 40 | low_breakout | 4861 | 0.70 | 0.70 | 54.5 |
| 40 | inside | 80587 | 0.00 | 0.00 | 49.9 |
| 40 | high_breakout | 4492 | -0.30 | -0.60 | 44.7 |
| 80 | low_breakout | 4860 | 0.57 | 0.80 | 53.8 |
| 80 | inside | 80551 | 0.04 | 0.10 | 50.4 |
| 80 | high_breakout | 4489 | -0.14 | -0.60 | 46.3 |

High breakouts: `4497` bars, low breakouts: `4861` bars (~5.00% / 5.40% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 3283 | 0.27 | 0.20 | 54.8 |
| 1 | inside | 83586 | -0.00 | 0.00 | 47.2 |
| 1 | high_breakout | 3090 | -0.17 | -0.10 | 43.5 |
| 3 | low_breakout | 3283 | 0.31 | 0.30 | 55.0 |
| 3 | inside | 83585 | -0.00 | 0.00 | 48.5 |
| 3 | high_breakout | 3089 | -0.22 | -0.20 | 43.5 |
| 5 | low_breakout | 3283 | 0.32 | 0.30 | 54.0 |
| 5 | inside | 83583 | -0.00 | 0.00 | 48.5 |
| 5 | high_breakout | 3089 | -0.15 | -0.30 | 43.7 |
| 10 | low_breakout | 3283 | 0.29 | 0.20 | 52.2 |
| 10 | inside | 83579 | -0.00 | 0.00 | 48.7 |
| 10 | high_breakout | 3088 | -0.09 | -0.40 | 44.5 |
| 20 | low_breakout | 3283 | 0.67 | 0.60 | 54.3 |
| 20 | inside | 83569 | -0.01 | 0.00 | 49.6 |
| 20 | high_breakout | 3088 | -0.07 | -0.40 | 45.9 |
| 40 | low_breakout | 3283 | 0.75 | 0.90 | 55.7 |
| 40 | inside | 83552 | 0.01 | 0.00 | 49.9 |
| 40 | high_breakout | 3085 | -0.30 | -0.70 | 44.0 |
| 80 | low_breakout | 3283 | 0.42 | 0.80 | 53.9 |
| 80 | inside | 83514 | 0.04 | 0.10 | 50.4 |
| 80 | high_breakout | 3083 | 0.01 | -0.70 | 45.9 |

High breakouts: `3090` bars, low breakouts: `3283` bars (~3.43% / 3.65% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2098 | 0.26 | 0.20 | 54.8 |
| 1 | inside | 85662 | -0.00 | 0.00 | 47.2 |
| 1 | high_breakout | 2159 | -0.15 | -0.10 | 43.9 |
| 3 | low_breakout | 2098 | 0.32 | 0.30 | 54.4 |
| 3 | inside | 85661 | -0.00 | 0.00 | 48.5 |
| 3 | high_breakout | 2158 | -0.20 | -0.30 | 43.8 |
| 5 | low_breakout | 2098 | 0.34 | 0.30 | 53.9 |
| 5 | inside | 85659 | -0.00 | 0.00 | 48.6 |
| 5 | high_breakout | 2158 | -0.06 | -0.20 | 44.5 |
| 10 | low_breakout | 2098 | 0.23 | 0.20 | 51.7 |
| 10 | inside | 85655 | 0.00 | 0.00 | 48.7 |
| 10 | high_breakout | 2157 | 0.05 | -0.30 | 45.5 |
| 20 | low_breakout | 2098 | 0.44 | 0.60 | 53.9 |
| 20 | inside | 85645 | 0.01 | 0.00 | 49.7 |
| 20 | high_breakout | 2157 | -0.03 | -0.60 | 45.2 |
| 40 | low_breakout | 2098 | 0.39 | 0.90 | 55.1 |
| 40 | inside | 85628 | 0.04 | 0.00 | 49.9 |
| 40 | high_breakout | 2154 | -0.60 | -0.90 | 43.5 |
| 80 | low_breakout | 2098 | 0.10 | 0.90 | 54.3 |
| 80 | inside | 85590 | 0.06 | 0.10 | 50.4 |
| 80 | high_breakout | 2152 | -0.17 | -0.90 | 45.3 |

High breakouts: `2159` bars, low breakouts: `2098` bars (~2.40% / 2.33% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1189 | 0.26 | 0.20 | 54.8 |
| 1 | inside | 87132 | -0.00 | 0.00 | 47.2 |
| 1 | high_breakout | 1518 | -0.10 | -0.10 | 45.5 |
| 3 | low_breakout | 1189 | 0.35 | 0.30 | 54.7 |
| 3 | inside | 87131 | -0.00 | 0.00 | 48.5 |
| 3 | high_breakout | 1517 | -0.13 | -0.20 | 46.0 |
| 5 | low_breakout | 1189 | 0.46 | 0.50 | 55.5 |
| 5 | inside | 87129 | -0.00 | 0.00 | 48.5 |
| 5 | high_breakout | 1517 | 0.07 | -0.20 | 46.7 |
| 10 | low_breakout | 1189 | 0.38 | 0.30 | 52.2 |
| 10 | inside | 87125 | -0.00 | 0.00 | 48.7 |
| 10 | high_breakout | 1516 | 0.28 | -0.15 | 47.8 |
| 20 | low_breakout | 1189 | 0.56 | 0.70 | 55.2 |
| 20 | inside | 87115 | 0.01 | 0.00 | 49.6 |
| 20 | high_breakout | 1516 | -0.01 | -0.55 | 46.1 |
| 40 | low_breakout | 1189 | 0.65 | 1.10 | 55.7 |
| 40 | inside | 87098 | 0.03 | 0.00 | 49.9 |
| 40 | high_breakout | 1513 | -0.69 | -1.00 | 43.7 |
| 80 | low_breakout | 1189 | 0.47 | 1.40 | 56.3 |
| 80 | inside | 87059 | 0.05 | 0.10 | 50.4 |
| 80 | high_breakout | 1512 | -0.04 | -0.90 | 46.0 |

High breakouts: `1518` bars, low breakouts: `1189` bars (~1.69% / 1.32% of dataset).

