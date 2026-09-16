## Dataset (DEV only)

- **Symbol**: EURJPY
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2025-06-26 03:00:00 .. 2026-03-19 17:05:00
- **Dev candles**: 54,000
- **Validation meta**: {'dev': np.int64(54000), 'val': np.int64(18000), 'holdout': np.int64(18000)}

## Interpretation

A bar is a **high breakout** if its close pierces the highest high of the prior `CH` candles (excluding the current bar); **low breakout** if its close pierces the lowest low. Continuation predicts positive forward return after a high breakout; breakdown predicts negative return after a low breakout. Bucket = breakout state at entry.

### Channel = 20

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 2776 | 0.38 | 0.30 | 52.6 |
| 1 | inside | 47907 | 0.03 | 0.10 | 50.3 |
| 1 | high_breakout | 3296 | -0.28 | -0.20 | 46.7 |
| 3 | low_breakout | 2776 | 0.50 | 0.70 | 53.4 |
| 3 | inside | 47905 | 0.08 | 0.20 | 51.3 |
| 3 | high_breakout | 3296 | -0.38 | -0.40 | 46.2 |
| 5 | low_breakout | 2776 | 0.40 | 0.80 | 53.2 |
| 5 | inside | 47903 | 0.14 | 0.30 | 51.7 |
| 5 | high_breakout | 3296 | -0.39 | -0.30 | 47.1 |
| 10 | low_breakout | 2776 | 0.29 | 1.00 | 53.4 |
| 10 | inside | 47898 | 0.26 | 0.60 | 52.3 |
| 10 | high_breakout | 3296 | 0.02 | -0.10 | 49.4 |
| 20 | low_breakout | 2775 | 0.53 | 1.30 | 53.2 |
| 20 | inside | 47889 | 0.50 | 1.10 | 53.1 |
| 20 | high_breakout | 3296 | 0.19 | 0.00 | 49.9 |
| 40 | low_breakout | 2774 | 1.77 | 3.20 | 55.7 |
| 40 | inside | 47870 | 1.01 | 2.00 | 54.3 |
| 40 | high_breakout | 3296 | -0.15 | 0.20 | 50.3 |
| 80 | low_breakout | 2774 | 3.14 | 5.50 | 56.8 |
| 80 | inside | 47831 | 2.00 | 3.70 | 54.7 |
| 80 | high_breakout | 3295 | 1.01 | 1.70 | 52.0 |

High breakouts: `3297` bars, low breakouts: `2776` bars (~6.11% / 5.14% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1810 | 0.39 | 0.30 | 52.4 |
| 1 | inside | 49868 | 0.03 | 0.10 | 50.3 |
| 1 | high_breakout | 2281 | -0.33 | -0.30 | 46.1 |
| 3 | low_breakout | 1810 | 0.57 | 0.55 | 52.6 |
| 3 | inside | 49866 | 0.08 | 0.20 | 51.3 |
| 3 | high_breakout | 2281 | -0.42 | -0.50 | 45.6 |
| 5 | low_breakout | 1810 | 0.54 | 0.90 | 53.6 |
| 5 | inside | 49864 | 0.13 | 0.30 | 51.6 |
| 5 | high_breakout | 2281 | -0.49 | -0.40 | 46.6 |
| 10 | low_breakout | 1810 | 0.52 | 1.30 | 54.5 |
| 10 | inside | 49859 | 0.25 | 0.60 | 52.3 |
| 10 | high_breakout | 2281 | -0.22 | -0.20 | 49.0 |
| 20 | low_breakout | 1809 | 0.75 | 1.50 | 53.9 |
| 20 | inside | 49850 | 0.50 | 1.10 | 53.0 |
| 20 | high_breakout | 2281 | -0.21 | -0.40 | 49.0 |
| 40 | low_breakout | 1808 | 2.46 | 4.55 | 57.7 |
| 40 | inside | 49831 | 1.03 | 2.00 | 54.2 |
| 40 | high_breakout | 2281 | -1.19 | -0.60 | 48.6 |
| 80 | low_breakout | 1808 | 3.84 | 5.50 | 56.8 |
| 80 | inside | 49791 | 2.06 | 3.70 | 54.8 |
| 80 | high_breakout | 2281 | -0.36 | 0.20 | 50.3 |

High breakouts: `2281` bars, low breakouts: `1810` bars (~4.22% / 3.35% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 1142 | 0.37 | 0.30 | 52.0 |
| 1 | inside | 51149 | 0.03 | 0.10 | 50.3 |
| 1 | high_breakout | 1628 | -0.30 | -0.30 | 46.3 |
| 3 | low_breakout | 1142 | 0.42 | 0.45 | 51.8 |
| 3 | inside | 51147 | 0.09 | 0.20 | 51.3 |
| 3 | high_breakout | 1628 | -0.48 | -0.60 | 45.4 |
| 5 | low_breakout | 1142 | 0.33 | 0.35 | 51.3 |
| 5 | inside | 51145 | 0.14 | 0.30 | 51.6 |
| 5 | high_breakout | 1628 | -0.59 | -0.50 | 46.2 |
| 10 | low_breakout | 1142 | 0.27 | 1.00 | 52.7 |
| 10 | inside | 51140 | 0.27 | 0.60 | 52.3 |
| 10 | high_breakout | 1628 | -0.42 | -0.20 | 48.8 |
| 20 | low_breakout | 1142 | 0.21 | 0.85 | 51.9 |
| 20 | inside | 51130 | 0.54 | 1.10 | 53.1 |
| 20 | high_breakout | 1628 | -0.46 | -0.80 | 48.2 |
| 40 | low_breakout | 1142 | 2.45 | 4.40 | 56.8 |
| 40 | inside | 51110 | 1.07 | 2.10 | 54.3 |
| 40 | high_breakout | 1628 | -1.67 | -1.20 | 47.4 |
| 80 | low_breakout | 1142 | 4.82 | 6.90 | 58.1 |
| 80 | inside | 51070 | 2.04 | 3.80 | 54.8 |
| 80 | high_breakout | 1628 | -0.30 | -1.00 | 48.3 |

High breakouts: `1628` bars, low breakouts: `1142` bars (~3.01% / 2.11% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 735 | 0.78 | 0.50 | 54.0 |
| 1 | inside | 51963 | 0.02 | 0.10 | 50.2 |
| 1 | high_breakout | 1141 | -0.20 | -0.20 | 46.5 |
| 3 | low_breakout | 735 | 0.52 | 0.50 | 51.8 |
| 3 | inside | 51961 | 0.08 | 0.20 | 51.2 |
| 3 | high_breakout | 1141 | -0.31 | -0.40 | 46.7 |
| 5 | low_breakout | 735 | 0.47 | 0.70 | 51.8 |
| 5 | inside | 51959 | 0.13 | 0.30 | 51.6 |
| 5 | high_breakout | 1141 | -0.34 | -0.50 | 45.6 |
| 10 | low_breakout | 735 | 0.36 | 0.80 | 52.5 |
| 10 | inside | 51954 | 0.26 | 0.60 | 52.3 |
| 10 | high_breakout | 1141 | -0.21 | -0.30 | 48.7 |
| 20 | low_breakout | 735 | 0.71 | 0.80 | 51.7 |
| 20 | inside | 51944 | 0.50 | 1.10 | 53.0 |
| 20 | high_breakout | 1141 | -0.08 | -0.60 | 48.6 |
| 40 | low_breakout | 735 | 2.86 | 4.70 | 57.4 |
| 40 | inside | 51924 | 1.02 | 2.00 | 54.2 |
| 40 | high_breakout | 1141 | -1.31 | -1.60 | 47.1 |
| 80 | low_breakout | 735 | 4.98 | 7.90 | 58.6 |
| 80 | inside | 51884 | 1.99 | 3.70 | 54.7 |
| 80 | high_breakout | 1141 | 0.40 | 0.00 | 49.9 |

High breakouts: `1141` bars, low breakouts: `735` bars (~2.11% / 1.36% of dataset).
