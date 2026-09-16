## Dataset (DEV only)

- **Symbol**: EURUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-29 08:00:00
- **Dev candles**: 253,335
- **Validation meta**: {'dev': np.int64(253335), 'val': np.int64(84445), 'holdout': np.int64(84445)}

## Interpretation

A bar is a **high breakout** if its close pierces the highest high of the prior `CH` candles (excluding the current bar); **low breakout** if its close pierces the lowest low. Continuation predicts positive forward return after a high breakout; breakdown predicts negative return after a low breakout. Bucket = breakout state at entry.

### Channel = 20

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 15001 | 0.14 | 0.20 | 52.3 |
| 1 | inside | 223376 | -0.01 | 0.00 | 48.4 |
| 1 | high_breakout | 14937 | -0.15 | -0.10 | 45.2 |
| 3 | low_breakout | 15001 | 0.27 | 0.30 | 53.0 |
| 3 | inside | 223374 | -0.02 | 0.00 | 49.3 |
| 3 | high_breakout | 14937 | -0.22 | -0.20 | 46.3 |
| 5 | low_breakout | 15001 | 0.31 | 0.40 | 52.9 |
| 5 | inside | 223372 | -0.03 | 0.00 | 49.5 |
| 5 | high_breakout | 14937 | -0.30 | -0.40 | 45.9 |
| 10 | low_breakout | 15001 | 0.39 | 0.50 | 53.1 |
| 10 | inside | 223368 | -0.06 | 0.00 | 49.8 |
| 10 | high_breakout | 14936 | -0.39 | -0.50 | 46.4 |
| 20 | low_breakout | 15001 | 0.31 | 0.50 | 51.9 |
| 20 | inside | 223362 | -0.12 | 0.00 | 49.9 |
| 20 | high_breakout | 14932 | -0.43 | -0.40 | 47.9 |
| 40 | low_breakout | 15001 | 0.31 | 0.40 | 51.0 |
| 40 | inside | 223343 | -0.23 | 0.00 | 49.7 |
| 40 | high_breakout | 14931 | -0.54 | -0.60 | 48.0 |
| 80 | low_breakout | 14994 | -0.44 | 0.00 | 49.8 |
| 80 | inside | 223310 | -0.43 | -0.10 | 49.7 |
| 80 | high_breakout | 14931 | -0.68 | -0.60 | 48.7 |

High breakouts: `14937` bars, low breakouts: `15002` bars (~5.90% / 5.92% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 10247 | 0.17 | 0.20 | 52.7 |
| 1 | inside | 232791 | -0.01 | 0.00 | 48.4 |
| 1 | high_breakout | 10256 | -0.16 | -0.20 | 45.0 |
| 3 | low_breakout | 10247 | 0.36 | 0.40 | 53.9 |
| 3 | inside | 232789 | -0.02 | 0.00 | 49.3 |
| 3 | high_breakout | 10256 | -0.27 | -0.30 | 45.6 |
| 5 | low_breakout | 10247 | 0.43 | 0.50 | 53.6 |
| 5 | inside | 232787 | -0.03 | 0.00 | 49.5 |
| 5 | high_breakout | 10256 | -0.39 | -0.50 | 45.4 |
| 10 | low_breakout | 10247 | 0.54 | 0.60 | 53.5 |
| 10 | inside | 232783 | -0.06 | 0.00 | 49.8 |
| 10 | high_breakout | 10255 | -0.51 | -0.60 | 46.2 |
| 20 | low_breakout | 10247 | 0.45 | 0.60 | 52.3 |
| 20 | inside | 232777 | -0.12 | 0.00 | 49.9 |
| 20 | high_breakout | 10251 | -0.55 | -0.50 | 47.7 |
| 40 | low_breakout | 10247 | 0.30 | 0.30 | 50.6 |
| 40 | inside | 232758 | -0.23 | 0.00 | 49.7 |
| 40 | high_breakout | 10250 | -0.56 | -0.70 | 47.6 |
| 80 | low_breakout | 10242 | -0.14 | -0.20 | 49.5 |
| 80 | inside | 232723 | -0.43 | -0.10 | 49.8 |
| 80 | high_breakout | 10250 | -0.95 | -0.80 | 48.3 |

High breakouts: `10256` bars, low breakouts: `10248` bars (~4.05% / 4.05% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 7077 | 0.18 | 0.20 | 53.0 |
| 1 | inside | 239236 | -0.01 | 0.00 | 48.4 |
| 1 | high_breakout | 6941 | -0.19 | -0.20 | 44.8 |
| 3 | low_breakout | 7077 | 0.41 | 0.50 | 54.1 |
| 3 | inside | 239234 | -0.02 | 0.00 | 49.3 |
| 3 | high_breakout | 6941 | -0.35 | -0.40 | 44.9 |
| 5 | low_breakout | 7077 | 0.49 | 0.50 | 53.5 |
| 5 | inside | 239232 | -0.03 | 0.00 | 49.5 |
| 5 | high_breakout | 6941 | -0.46 | -0.50 | 45.4 |
| 10 | low_breakout | 7077 | 0.53 | 0.70 | 53.4 |
| 10 | inside | 239228 | -0.06 | 0.00 | 49.8 |
| 10 | high_breakout | 6940 | -0.60 | -0.60 | 45.7 |
| 20 | low_breakout | 7077 | 0.34 | 0.60 | 51.9 |
| 20 | inside | 239218 | -0.11 | 0.00 | 49.9 |
| 20 | high_breakout | 6940 | -0.57 | -0.50 | 47.7 |
| 40 | low_breakout | 7077 | 0.19 | 0.10 | 50.3 |
| 40 | inside | 239198 | -0.23 | 0.00 | 49.7 |
| 40 | high_breakout | 6940 | -0.45 | -0.60 | 48.0 |
| 80 | low_breakout | 7072 | -0.18 | -0.40 | 49.0 |
| 80 | inside | 239163 | -0.43 | -0.10 | 49.7 |
| 80 | high_breakout | 6940 | -1.21 | -0.90 | 48.1 |

High breakouts: `6941` bars, low breakouts: `7078` bars (~2.74% / 2.79% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 4854 | 0.18 | 0.20 | 52.7 |
| 1 | inside | 243524 | -0.01 | 0.00 | 48.4 |
| 1 | high_breakout | 4796 | -0.22 | -0.20 | 45.2 |
| 3 | low_breakout | 4854 | 0.45 | 0.50 | 54.0 |
| 3 | inside | 243522 | -0.02 | 0.00 | 49.3 |
| 3 | high_breakout | 4796 | -0.45 | -0.40 | 44.8 |
| 5 | low_breakout | 4854 | 0.52 | 0.50 | 53.8 |
| 5 | inside | 243520 | -0.03 | 0.00 | 49.5 |
| 5 | high_breakout | 4796 | -0.61 | -0.60 | 45.0 |
| 10 | low_breakout | 4854 | 0.44 | 0.70 | 53.3 |
| 10 | inside | 243515 | -0.05 | 0.00 | 49.8 |
| 10 | high_breakout | 4796 | -0.87 | -0.70 | 45.8 |
| 20 | low_breakout | 4854 | 0.17 | 0.60 | 52.1 |
| 20 | inside | 243505 | -0.11 | 0.00 | 49.9 |
| 20 | high_breakout | 4796 | -0.80 | -0.40 | 47.9 |
| 40 | low_breakout | 4854 | 0.28 | 0.50 | 51.2 |
| 40 | inside | 243485 | -0.23 | 0.00 | 49.7 |
| 40 | high_breakout | 4796 | -0.77 | -0.80 | 47.9 |
| 80 | low_breakout | 4849 | 0.04 | -0.10 | 49.7 |
| 80 | inside | 243450 | -0.44 | -0.10 | 49.7 |
| 80 | high_breakout | 4796 | -1.80 | -1.10 | 47.9 |

High breakouts: `4796` bars, low breakouts: `4855` bars (~1.89% / 1.92% of dataset).
