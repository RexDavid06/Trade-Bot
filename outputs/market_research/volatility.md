# VOLATILITY STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-16 23:30:00` .. `2026-09-01 18:20:00`
- **Candles**: `90,000`
- **Timeframe**: M5 (EURUSD)

## Configuration

- **atr_period**: `14`
- **regime_atr_lookback**: `50`
- **forward_horizons**: `[1, 3, 5, 10, 20, 40, 80]`

## Interpretation

Regime is assigned causally from a rolling quantile of ATR (low/normal/high). We report forward pips and directional hit rate by regime. Low |avg| / hit ~ 50% in a regime means it is not directional; a regime where |forward| is large and hit rate is not ~50% is where an edge could live. Also report absolute forward move (|pips|) per regime to see how much room there is to capture.

### Horizon = 1

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33434 | 0.01 | 0.00 | 49.0 | 0.79 | 0.429 | -3.61 | 0.000 | False |
| low | 39619 | -0.01 | 0.00 | 48.1 | -1.15 | 0.251 | -7.58 | 0.000 | False |
| normal | 16946 | 0.00 | 0.00 | 48.9 | 0.07 | 0.941 | -2.87 | 0.004 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39619 | 1.37 | 1.00 |
| normal | 16946 | 1.77 | 1.20 |
| high | 33434 | 2.25 | 1.60 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33432 | 0.05 | 0.00 | 49.4 | 1.54 | 0.124 | -2.09 | 0.037 | False |
| low | 39619 | -0.03 | 0.00 | 48.9 | -1.66 | 0.097 | -4.30 | 0.000 | False |
| normal | 16946 | -0.02 | 0.00 | 48.7 | -0.50 | 0.615 | -3.38 | 0.001 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39619 | 2.41 | 1.70 |
| normal | 16946 | 3.03 | 2.20 |
| high | 33432 | 3.86 | 2.70 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33430 | 0.09 | 0.00 | 49.7 | 2.14 | 0.033 | -1.01 | 0.314 | False |
| low | 39619 | -0.06 | 0.00 | 48.9 | -2.65 | 0.008 | -4.43 | 0.000 | False |
| normal | 16946 | -0.01 | 0.00 | 49.2 | -0.23 | 0.821 | -2.06 | 0.040 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39619 | 3.14 | 2.20 |
| normal | 16946 | 3.90 | 2.80 |
| high | 33430 | 4.92 | 3.50 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33425 | 0.14 | -0.10 | 49.4 | 2.56 | 0.010 | -2.02 | 0.044 | False |
| low | 39619 | -0.13 | 0.00 | 49.3 | -3.62 | 0.000 | -2.98 | 0.003 | False |
| normal | 16946 | 0.04 | -0.10 | 49.3 | 0.64 | 0.525 | -1.94 | 0.053 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39619 | 4.61 | 3.20 |
| normal | 16946 | 5.48 | 3.90 |
| high | 33425 | 6.83 | 4.80 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33415 | 0.13 | -0.20 | 48.7 | 1.79 | 0.073 | -4.71 | 0.000 | False |
| low | 39619 | -0.08 | 0.10 | 50.2 | -1.59 | 0.111 | 0.65 | 0.517 | False |
| normal | 16946 | -0.02 | -0.20 | 48.7 | -0.26 | 0.794 | -3.40 | 0.001 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39619 | 6.82 | 4.60 |
| normal | 16946 | 8.02 | 5.80 |
| high | 33415 | 9.31 | 6.60 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33413 | 0.10 | -0.50 | 48.2 | 1.01 | 0.314 | -6.41 | 0.000 | False |
| low | 39604 | 0.01 | 0.20 | 50.6 | 0.16 | 0.872 | 2.46 | 0.014 | False |
| normal | 16943 | -0.13 | -0.20 | 49.0 | -1.03 | 0.305 | -2.56 | 0.011 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39604 | 10.23 | 6.90 |
| normal | 16943 | 11.82 | 8.30 |
| high | 33413 | 12.66 | 9.20 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33404 | 0.44 | -0.50 | 48.7 | 3.07 | 0.002 | -4.64 | 0.000 | False |
| low | 39593 | -0.33 | -0.30 | 49.0 | -3.29 | 0.001 | -4.18 | 0.000 | False |
| normal | 16923 | 0.10 | -0.50 | 48.8 | 0.57 | 0.570 | -3.08 | 0.002 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39593 | 14.30 | 10.20 |
| normal | 16923 | 17.25 | 12.80 |
| high | 33404 | 18.94 | 13.90 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 39619 | 44.0 |
| normal | 16946 | 18.8 |
| high | 33435 | 37.1 |

