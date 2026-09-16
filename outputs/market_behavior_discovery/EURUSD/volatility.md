## Dataset (DEV only)

- **Symbol**: EURUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-29 08:00:00
- **Dev candles**: 253,335
- **Validation meta**: {'dev': np.int64(253335), 'val': np.int64(84445), 'holdout': np.int64(84445)}

## Interpretation

Regime is assigned causally from a rolling quantile of ATR (low/normal/high). We report forward pips and directional hit rate by regime. Low |avg| / hit ~ 50% in a regime means it is not directional; a regime where |forward| is large and hit rate is not ~50% is where an edge could live. Also report absolute forward move (|pips|) per regime to see how much room there is to capture.

### Horizon = 1

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93571 | 0.01 | 0.00 | 49.2 | 0.71 | 0.479 | -4.85 | 0.000 | False |
| low | 115295 | -0.01 | 0.00 | 47.7 | -1.66 | 0.096 | -15.59 | 0.000 | False |
| normal | 44468 | -0.02 | 0.00 | 48.9 | -1.42 | 0.155 | -4.69 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115295 | 1.46 | 1.00 |
| normal | 44468 | 2.01 | 1.40 |
| high | 93571 | 2.68 | 1.80 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93569 | 0.03 | 0.00 | 49.8 | 1.23 | 0.218 | -1.00 | 0.319 | False |
| low | 115295 | -0.04 | 0.00 | 48.9 | -3.43 | 0.001 | -7.64 | 0.000 | False |
| normal | 44468 | -0.04 | 0.00 | 49.4 | -1.71 | 0.087 | -2.60 | 0.009 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115295 | 2.55 | 1.70 |
| normal | 44468 | 3.48 | 2.40 |
| high | 93569 | 4.58 | 3.20 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93567 | 0.04 | 0.00 | 49.9 | 1.35 | 0.177 | -0.48 | 0.631 | False |
| low | 115295 | -0.07 | 0.00 | 49.3 | -4.56 | 0.000 | -4.41 | 0.000 | False |
| normal | 44468 | -0.05 | 0.00 | 49.2 | -1.49 | 0.137 | -3.46 | 0.001 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115295 | 3.32 | 2.20 |
| normal | 44468 | 4.48 | 3.00 |
| high | 93567 | 5.88 | 4.10 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93562 | 0.02 | 0.10 | 50.2 | 0.61 | 0.540 | 1.12 | 0.261 | False |
| low | 115295 | -0.10 | 0.00 | 49.6 | -4.41 | 0.000 | -2.54 | 0.011 | False |
| normal | 44468 | -0.10 | -0.10 | 49.3 | -2.12 | 0.034 | -3.10 | 0.002 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115295 | 4.83 | 3.10 |
| normal | 44468 | 6.33 | 4.30 |
| high | 93562 | 8.18 | 5.70 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93552 | -0.01 | 0.10 | 50.2 | -0.25 | 0.800 | 1.48 | 0.138 | False |
| low | 115295 | -0.18 | 0.00 | 49.9 | -5.14 | 0.000 | -0.87 | 0.385 | False |
| normal | 44468 | -0.14 | -0.10 | 49.4 | -2.15 | 0.032 | -2.55 | 0.011 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115295 | 7.18 | 4.60 |
| normal | 44468 | 9.17 | 6.20 |
| high | 93552 | 11.18 | 7.80 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93548 | -0.15 | -0.30 | 49.2 | -2.06 | 0.040 | -5.13 | 0.000 | False |
| low | 115283 | -0.26 | 0.10 | 50.2 | -5.26 | 0.000 | 1.32 | 0.186 | False |
| normal | 44464 | -0.26 | -0.10 | 49.5 | -2.68 | 0.007 | -2.24 | 0.025 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115283 | 10.92 | 7.00 |
| normal | 44464 | 14.05 | 9.70 |
| high | 93548 | 15.08 | 10.60 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 93530 | -0.17 | -0.20 | 49.5 | -1.60 | 0.109 | -3.19 | 0.001 | False |
| low | 115269 | -0.59 | 0.00 | 49.9 | -8.80 | 0.000 | -0.54 | 0.590 | False |
| normal | 44456 | -0.62 | -0.20 | 49.5 | -4.60 | 0.000 | -1.92 | 0.055 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 115269 | 15.62 | 10.80 |
| normal | 44456 | 20.19 | 14.35 |
| high | 93530 | 22.80 | 16.50 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 115295 | 45.5 |
| normal | 44468 | 17.6 |
| high | 93572 | 36.9 |
