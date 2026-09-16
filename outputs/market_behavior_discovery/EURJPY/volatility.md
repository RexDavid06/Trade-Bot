## Dataset (DEV only)

- **Symbol**: EURJPY
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2025-06-26 03:00:00 .. 2026-03-19 17:05:00
- **Dev candles**: 54,000
- **Validation meta**: {'dev': np.int64(54000), 'val': np.int64(18000), 'holdout': np.int64(18000)}

## Interpretation

Regime is assigned causally from a rolling quantile of ATR (low/normal/high). We report forward pips and directional hit rate by regime. Low |avg| / hit ~ 50% in a regime means it is not directional; a regime where |forward| is large and hit rate is not ~50% is where an edge could live. Also report absolute forward move (|pips|) per regime to see how much room there is to capture.

### Horizon = 1

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19768 | 0.05 | 0.10 | 50.3 | 1.29 | 0.197 | 0.84 | 0.401 | False |
| low | 23524 | -0.02 | 0.00 | 49.9 | -0.93 | 0.350 | -0.44 | 0.658 | False |
| normal | 10707 | 0.07 | 0.10 | 50.6 | 1.54 | 0.124 | 1.25 | 0.213 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23524 | 2.44 | 1.80 |
| normal | 10707 | 3.10 | 2.30 |
| high | 19768 | 3.79 | 2.80 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19768 | 0.19 | 0.30 | 51.5 | 2.96 | 0.003 | 4.31 | 0.000 | False |
| low | 23524 | -0.06 | 0.10 | 50.7 | -1.39 | 0.166 | 2.27 | 0.023 | False |
| normal | 10705 | 0.14 | 0.20 | 51.1 | 1.83 | 0.067 | 2.27 | 0.023 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23524 | 4.21 | 3.10 |
| normal | 10705 | 5.29 | 3.90 |
| high | 19768 | 6.35 | 4.80 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19768 | 0.27 | 0.50 | 52.1 | 3.45 | 0.001 | 6.03 | 0.000 | False |
| low | 23524 | -0.04 | 0.20 | 50.8 | -0.83 | 0.405 | 2.41 | 0.016 | False |
| normal | 10703 | 0.20 | 0.40 | 51.7 | 2.08 | 0.038 | 3.45 | 0.001 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23524 | 5.47 | 4.00 |
| normal | 10703 | 6.79 | 5.00 |
| high | 19768 | 8.07 | 6.00 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19763 | 0.47 | 1.00 | 53.2 | 4.31 | 0.000 | 9.08 | 0.000 | False |
| low | 23524 | 0.01 | 0.30 | 51.1 | 0.11 | 0.912 | 3.26 | 0.001 | False |
| normal | 10703 | 0.34 | 0.80 | 52.9 | 2.51 | 0.012 | 5.96 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23524 | 7.82 | 5.70 |
| normal | 10703 | 9.84 | 7.40 |
| high | 19763 | 11.18 | 8.40 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19753 | 0.73 | 1.70 | 53.8 | 5.02 | 0.000 | 10.68 | 0.000 | False |
| low | 23524 | 0.35 | 0.60 | 52.0 | 3.09 | 0.002 | 6.17 | 0.000 | False |
| normal | 10703 | 0.34 | 1.20 | 53.1 | 1.77 | 0.076 | 6.39 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23524 | 11.71 | 8.30 |
| normal | 10703 | 14.21 | 10.40 |
| high | 19753 | 15.25 | 11.70 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19750 | 1.28 | 2.70 | 55.0 | 6.79 | 0.000 | 14.07 | 0.000 | False |
| low | 23513 | 1.17 | 1.60 | 53.5 | 7.01 | 0.000 | 10.85 | 0.000 | False |
| normal | 10697 | 0.00 | 1.90 | 53.6 | 0.00 | 0.996 | 7.49 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23513 | 17.92 | 12.50 |
| normal | 10697 | 20.96 | 16.00 |
| high | 19750 | 19.93 | 15.50 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 19735 | 2.66 | 4.20 | 55.0 | 9.94 | 0.000 | 14.07 | 0.000 | False |
| low | 23498 | 1.55 | 3.45 | 54.8 | 6.55 | 0.000 | 14.59 | 0.000 | False |
| normal | 10687 | 1.68 | 3.10 | 53.7 | 4.49 | 0.000 | 7.55 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 23498 | 26.44 | 20.00 |
| normal | 10687 | 28.91 | 22.40 |
| high | 19735 | 28.45 | 22.40 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 23524 | 43.6 |
| normal | 10708 | 19.8 |
| high | 19768 | 36.6 |
