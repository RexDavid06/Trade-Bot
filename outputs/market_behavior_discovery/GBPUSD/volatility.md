## Dataset (DEV only)

- **Symbol**: GBPUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-06-13 18:25:00
- **Dev candles**: 224,848
- **Validation meta**: {'dev': np.int64(224848), 'val': np.int64(74949), 'holdout': np.int64(74949)}

## Interpretation

Regime is assigned causally from a rolling quantile of ATR (low/normal/high). We report forward pips and directional hit rate by regime. Low |avg| / hit ~ 50% in a regime means it is not directional; a regime where |forward| is large and hit rate is not ~50% is where an edge could live. Also report absolute forward move (|pips|) per regime to see how much room there is to capture.

### Horizon = 1

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | 0.02 | 0.00 | 49.3 | 0.86 | 0.389 | -3.89 | 0.000 | False |
| low | 102950 | -0.02 | 0.00 | 48.2 | -1.57 | 0.116 | -11.46 | 0.000 | False |
| normal | 40311 | -0.01 | 0.00 | 48.9 | -0.26 | 0.798 | -4.62 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102950 | 2.08 | 1.30 |
| normal | 40311 | 2.77 | 1.90 |
| high | 81586 | 3.64 | 2.50 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | 0.05 | 0.10 | 50.0 | 1.72 | 0.086 | 0.14 | 0.889 | False |
| low | 102948 | -0.06 | 0.00 | 49.2 | -2.73 | 0.006 | -4.84 | 0.000 | False |
| normal | 40311 | -0.03 | 0.00 | 49.8 | -0.72 | 0.470 | -0.68 | 0.495 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102948 | 3.69 | 2.30 |
| normal | 40311 | 4.83 | 3.20 |
| high | 81586 | 6.23 | 4.40 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | 0.10 | 0.10 | 50.1 | 2.41 | 0.016 | 0.45 | 0.654 | False |
| low | 102946 | -0.09 | 0.00 | 49.4 | -3.01 | 0.003 | -3.58 | 0.000 | False |
| normal | 40311 | -0.09 | 0.00 | 49.9 | -1.78 | 0.075 | -0.57 | 0.567 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102946 | 4.84 | 3.10 |
| normal | 40311 | 6.29 | 4.10 |
| high | 81586 | 7.96 | 5.60 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | 0.14 | 0.20 | 50.5 | 2.51 | 0.012 | 3.07 | 0.002 | False |
| low | 102941 | -0.15 | 0.00 | 49.5 | -3.56 | 0.000 | -3.16 | 0.002 | False |
| normal | 40311 | -0.13 | 0.00 | 49.5 | -1.90 | 0.057 | -2.14 | 0.033 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102941 | 7.10 | 4.40 |
| normal | 40311 | 8.92 | 5.90 |
| high | 81586 | 11.04 | 7.80 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | 0.16 | 0.20 | 50.4 | 2.19 | 0.029 | 2.53 | 0.011 | False |
| low | 102931 | -0.25 | 0.00 | 49.6 | -4.30 | 0.000 | -2.41 | 0.016 | False |
| normal | 40311 | -0.13 | 0.00 | 49.6 | -1.31 | 0.190 | -1.53 | 0.126 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102931 | 10.70 | 6.40 |
| normal | 40311 | 13.01 | 8.60 |
| high | 81586 | 15.13 | 10.80 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81586 | -0.04 | 0.20 | 50.3 | -0.41 | 0.681 | 1.75 | 0.080 | False |
| low | 102914 | -0.23 | 0.00 | 49.9 | -2.77 | 0.006 | -0.62 | 0.533 | False |
| normal | 40308 | -0.22 | -0.20 | 49.5 | -1.55 | 0.121 | -2.18 | 0.029 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102914 | 16.05 | 9.80 |
| normal | 40308 | 19.53 | 13.30 |
| high | 81586 | 20.93 | 14.90 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 81557 | -0.16 | 0.10 | 50.1 | -1.02 | 0.310 | 0.76 | 0.447 | False |
| low | 102914 | -0.50 | -0.10 | 49.7 | -4.21 | 0.000 | -2.18 | 0.029 | False |
| normal | 40297 | -0.23 | 0.40 | 50.4 | -1.17 | 0.243 | 1.78 | 0.075 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 102914 | 23.48 | 15.50 |
| normal | 40297 | 27.58 | 19.80 |
| high | 81557 | 31.47 | 22.60 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 102951 | 45.8 |
| normal | 40311 | 17.9 |
| high | 81586 | 36.3 |
