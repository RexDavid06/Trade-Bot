## Dataset (DEV only)

- **Symbol**: GBPUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-06-13 18:25:00
- **Dev candles**: 224,848
- **Validation meta**: {'dev': np.int64(224848), 'val': np.int64(74949), 'holdout': np.int64(74949)}

## Interpretation

A bar is a **high breakout** if its close pierces the highest high of the prior `CH` candles (excluding the current bar); **low breakout** if its close pierces the lowest low. Continuation predicts positive forward return after a high breakout; breakdown predicts negative return after a low breakout. Bucket = breakout state at entry.

### Channel = 20

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 13471 | 0.22 | 0.10 | 51.7 |
| 1 | inside | 197991 | -0.01 | 0.00 | 48.7 |
| 1 | high_breakout | 13365 | -0.13 | -0.20 | 46.2 |
| 3 | low_breakout | 13471 | 0.44 | 0.40 | 53.4 |
| 3 | inside | 197989 | -0.03 | 0.00 | 49.6 |
| 3 | high_breakout | 13365 | -0.19 | -0.30 | 46.4 |
| 5 | low_breakout | 13471 | 0.59 | 0.60 | 53.7 |
| 5 | inside | 197987 | -0.05 | 0.00 | 49.7 |
| 5 | high_breakout | 13365 | -0.27 | -0.40 | 46.6 |
| 10 | low_breakout | 13471 | 0.56 | 0.70 | 53.1 |
| 10 | inside | 197985 | -0.05 | 0.00 | 49.8 |
| 10 | high_breakout | 13362 | -0.50 | -0.50 | 47.2 |
| 20 | low_breakout | 13471 | 0.85 | 0.80 | 52.3 |
| 20 | inside | 197975 | -0.10 | 0.00 | 49.9 |
| 20 | high_breakout | 13362 | -0.71 | -0.70 | 47.3 |
| 40 | low_breakout | 13465 | 0.67 | 0.80 | 51.7 |
| 40 | inside | 197961 | -0.17 | 0.00 | 49.9 |
| 40 | high_breakout | 13362 | -0.86 | -0.60 | 48.5 |
| 80 | low_breakout | 13461 | 0.42 | 0.50 | 50.7 |
| 80 | inside | 197926 | -0.33 | 0.10 | 50.0 |
| 80 | high_breakout | 13361 | -1.05 | -0.80 | 48.7 |

High breakouts: `13366` bars, low breakouts: `13471` bars (~5.94% / 5.99% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 9202 | 0.24 | 0.20 | 51.6 |
| 1 | inside | 206407 | -0.01 | 0.00 | 48.7 |
| 1 | high_breakout | 9198 | -0.12 | -0.20 | 46.3 |
| 3 | low_breakout | 9202 | 0.48 | 0.50 | 53.9 |
| 3 | inside | 206405 | -0.03 | 0.00 | 49.6 |
| 3 | high_breakout | 9198 | -0.17 | -0.30 | 46.8 |
| 5 | low_breakout | 9202 | 0.62 | 0.80 | 54.3 |
| 5 | inside | 206403 | -0.04 | 0.00 | 49.7 |
| 5 | high_breakout | 9198 | -0.30 | -0.40 | 46.5 |
| 10 | low_breakout | 9202 | 0.69 | 0.90 | 53.6 |
| 10 | inside | 206398 | -0.05 | 0.00 | 49.8 |
| 10 | high_breakout | 9198 | -0.52 | -0.60 | 47.0 |
| 20 | low_breakout | 9202 | 1.09 | 0.90 | 52.5 |
| 20 | inside | 206388 | -0.11 | 0.00 | 49.9 |
| 20 | high_breakout | 9198 | -0.66 | -0.70 | 47.2 |
| 40 | low_breakout | 9196 | 1.02 | 1.10 | 52.1 |
| 40 | inside | 206374 | -0.20 | 0.00 | 49.9 |
| 40 | high_breakout | 9198 | -0.67 | -0.60 | 48.4 |
| 80 | low_breakout | 9193 | 1.24 | 1.40 | 51.8 |
| 80 | inside | 206338 | -0.39 | 0.00 | 49.9 |
| 80 | high_breakout | 9197 | -0.57 | -0.80 | 48.7 |

High breakouts: `9198` bars, low breakouts: `9202` bars (~4.09% / 4.09% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 6422 | 0.31 | 0.20 | 52.1 |
| 1 | inside | 211971 | -0.01 | 0.00 | 48.7 |
| 1 | high_breakout | 6374 | -0.16 | -0.20 | 45.5 |
| 3 | low_breakout | 6422 | 0.69 | 0.60 | 54.4 |
| 3 | inside | 211969 | -0.03 | 0.00 | 49.6 |
| 3 | high_breakout | 6374 | -0.20 | -0.35 | 46.3 |
| 5 | low_breakout | 6422 | 0.91 | 0.90 | 54.7 |
| 5 | inside | 211967 | -0.04 | 0.00 | 49.7 |
| 5 | high_breakout | 6374 | -0.29 | -0.60 | 46.0 |
| 10 | low_breakout | 6422 | 0.94 | 1.10 | 54.2 |
| 10 | inside | 211962 | -0.06 | 0.00 | 49.8 |
| 10 | high_breakout | 6374 | -0.50 | -0.70 | 46.5 |
| 20 | low_breakout | 6422 | 1.16 | 0.95 | 52.6 |
| 20 | inside | 211952 | -0.10 | 0.00 | 49.9 |
| 20 | high_breakout | 6374 | -0.74 | -0.80 | 46.8 |
| 40 | low_breakout | 6416 | 1.26 | 1.30 | 52.4 |
| 40 | inside | 211938 | -0.19 | 0.00 | 50.0 |
| 40 | high_breakout | 6374 | -0.93 | -0.90 | 47.9 |
| 80 | low_breakout | 6413 | 1.35 | 1.70 | 51.9 |
| 80 | inside | 211902 | -0.36 | 0.00 | 50.0 |
| 80 | high_breakout | 6373 | -0.81 | -1.20 | 48.3 |

High breakouts: `6374` bars, low breakouts: `6422` bars (~2.83% / 2.86% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 4481 | 0.30 | 0.20 | 51.6 |
| 1 | inside | 215774 | -0.01 | 0.00 | 48.7 |
| 1 | high_breakout | 4432 | -0.16 | -0.20 | 45.9 |
| 3 | low_breakout | 4481 | 0.71 | 0.70 | 54.4 |
| 3 | inside | 215772 | -0.02 | 0.00 | 49.6 |
| 3 | high_breakout | 4432 | -0.19 | -0.40 | 46.1 |
| 5 | low_breakout | 4481 | 1.02 | 1.00 | 54.9 |
| 5 | inside | 215770 | -0.04 | 0.00 | 49.7 |
| 5 | high_breakout | 4432 | -0.26 | -0.50 | 46.3 |
| 10 | low_breakout | 4481 | 1.00 | 1.20 | 54.2 |
| 10 | inside | 215765 | -0.06 | 0.00 | 49.8 |
| 10 | high_breakout | 4432 | -0.37 | -0.50 | 47.4 |
| 20 | low_breakout | 4481 | 1.22 | 1.00 | 52.8 |
| 20 | inside | 215755 | -0.10 | 0.00 | 49.9 |
| 20 | high_breakout | 4432 | -0.59 | -0.70 | 47.8 |
| 40 | low_breakout | 4475 | 1.10 | 1.60 | 52.6 |
| 40 | inside | 215741 | -0.17 | 0.00 | 49.9 |
| 40 | high_breakout | 4432 | -0.78 | -0.45 | 48.9 |
| 80 | low_breakout | 4472 | 1.58 | 2.20 | 52.7 |
| 80 | inside | 215705 | -0.33 | 0.00 | 50.0 |
| 80 | high_breakout | 4431 | -0.74 | -1.20 | 48.5 |

High breakouts: `4432` bars, low breakouts: `4481` bars (~1.97% / 1.99% of dataset).
