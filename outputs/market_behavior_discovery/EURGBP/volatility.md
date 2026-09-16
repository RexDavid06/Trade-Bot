## Dataset (DEV only)

- **Symbol**: EURGBP
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-30 15:15:00
- **Dev candles**: 255,286
- **Validation meta**: {'dev': np.int64(255286), 'val': np.int64(85096), 'holdout': np.int64(85095)}

## Interpretation

Regime is assigned causally from a rolling quantile of ATR (low/normal/high). We report forward pips and directional hit rate by regime. Low |avg| / hit ~ 50% in a regime means it is not directional; a regime where |forward| is large and hit rate is not ~50% is where an edge could live. Also report absolute forward move (|pips|) per regime to see how much room there is to capture.

### Horizon = 1

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86906 | 0.03 | 0.00 | 49.3 | 3.60 | 0.000 | -4.10 | 0.000 | False |
| low | 121577 | -0.03 | 0.00 | 47.1 | -6.97 | 0.000 | -19.94 | 0.000 | False |
| normal | 46802 | 0.01 | 0.00 | 48.1 | 1.18 | 0.237 | -8.13 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121577 | 1.03 | 0.70 |
| normal | 46802 | 1.35 | 0.90 |
| high | 86906 | 1.85 | 1.30 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86904 | 0.07 | 0.10 | 50.3 | 4.65 | 0.000 | 2.06 | 0.040 | False |
| low | 121577 | -0.08 | 0.00 | 48.0 | -9.84 | 0.000 | -13.83 | 0.000 | False |
| normal | 46802 | 0.04 | 0.00 | 49.3 | 2.28 | 0.023 | -3.01 | 0.003 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121577 | 1.74 | 1.10 |
| normal | 46802 | 2.27 | 1.50 |
| high | 86904 | 3.08 | 2.20 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86902 | 0.10 | 0.10 | 50.7 | 5.04 | 0.000 | 3.93 | 0.000 | False |
| low | 121577 | -0.11 | 0.00 | 48.0 | -11.33 | 0.000 | -13.77 | 0.000 | False |
| normal | 46802 | 0.07 | 0.00 | 49.9 | 3.23 | 0.001 | -0.43 | 0.664 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121577 | 2.21 | 1.50 |
| normal | 46802 | 2.89 | 1.90 |
| high | 86902 | 3.92 | 2.80 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86897 | 0.12 | 0.20 | 51.2 | 4.55 | 0.000 | 7.00 | 0.000 | False |
| low | 121577 | -0.17 | -0.10 | 47.5 | -11.87 | 0.000 | -17.31 | 0.000 | False |
| normal | 46802 | 0.11 | 0.10 | 50.3 | 3.71 | 0.000 | 1.11 | 0.267 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121577 | 3.05 | 2.00 |
| normal | 46802 | 4.04 | 2.60 |
| high | 86897 | 5.46 | 3.80 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86887 | 0.10 | 0.20 | 50.9 | 2.61 | 0.009 | 5.29 | 0.000 | False |
| low | 121577 | -0.18 | -0.20 | 47.8 | -9.50 | 0.000 | -15.05 | 0.000 | False |
| normal | 46802 | 0.11 | 0.10 | 50.4 | 2.66 | 0.008 | 1.92 | 0.054 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121577 | 4.27 | 2.80 |
| normal | 46802 | 5.71 | 3.70 |
| high | 86887 | 7.59 | 5.40 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86873 | 0.12 | 0.00 | 50.0 | 2.34 | 0.020 | -0.22 | 0.825 | False |
| low | 121574 | -0.27 | -0.20 | 48.1 | -9.79 | 0.000 | -13.53 | 0.000 | False |
| normal | 46799 | 0.11 | 0.10 | 50.1 | 1.83 | 0.067 | 0.24 | 0.806 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121574 | 6.23 | 4.00 |
| normal | 46799 | 8.18 | 5.30 |
| high | 86873 | 10.43 | 7.30 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 86867 | -0.18 | -0.40 | 48.8 | -2.55 | 0.011 | -7.27 | 0.000 | False |
| low | 121550 | -0.05 | -0.10 | 49.5 | -1.16 | 0.246 | -3.81 | 0.000 | False |
| normal | 46789 | -0.30 | -0.20 | 49.2 | -3.74 | 0.000 | -3.49 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 121550 | 9.44 | 6.20 |
| normal | 46789 | 11.79 | 8.10 |
| high | 86867 | 14.36 | 9.90 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 121577 | 47.6 |
| normal | 46802 | 18.3 |
| high | 86907 | 34.0 |
