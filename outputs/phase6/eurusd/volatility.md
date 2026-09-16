# VOLATILITY STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 22:45:00` .. `2026-09-10 17:35:00`
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
| high | 33449 | 0.01 | 0.00 | 49.1 | 0.72 | 0.472 | -3.45 | 0.001 | False |
| low | 39612 | -0.01 | 0.00 | 48.0 | -1.41 | 0.159 | -7.95 | 0.000 | False |
| normal | 16938 | 0.01 | 0.00 | 48.9 | 0.33 | 0.745 | -2.87 | 0.004 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 1.35 | 0.90 |
| normal | 16938 | 1.74 | 1.20 |
| high | 33449 | 2.22 | 1.60 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33449 | 0.05 | 0.00 | 49.5 | 1.46 | 0.144 | -1.96 | 0.050 | False |
| low | 39612 | -0.04 | 0.00 | 48.8 | -2.13 | 0.033 | -4.93 | 0.000 | False |
| normal | 16936 | -0.00 | 0.00 | 48.8 | -0.13 | 0.897 | -3.14 | 0.002 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 2.36 | 1.60 |
| normal | 16936 | 2.98 | 2.10 |
| high | 33449 | 3.81 | 2.70 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33449 | 0.08 | 0.00 | 49.7 | 2.04 | 0.042 | -0.93 | 0.350 | False |
| low | 39612 | -0.07 | 0.00 | 48.8 | -3.13 | 0.002 | -4.90 | 0.000 | False |
| normal | 16934 | 0.00 | 0.00 | 49.2 | 0.07 | 0.942 | -2.07 | 0.038 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 3.09 | 2.10 |
| normal | 16934 | 3.83 | 2.70 |
| high | 33449 | 4.86 | 3.50 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33447 | 0.14 | -0.10 | 49.4 | 2.58 | 0.010 | -2.05 | 0.040 | False |
| low | 39612 | -0.14 | 0.00 | 49.2 | -4.09 | 0.000 | -3.04 | 0.002 | False |
| normal | 16931 | 0.03 | -0.10 | 49.1 | 0.48 | 0.630 | -2.25 | 0.024 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 4.52 | 3.10 |
| normal | 16931 | 5.37 | 3.80 |
| high | 33447 | 6.74 | 4.80 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33437 | 0.12 | -0.30 | 48.6 | 1.60 | 0.109 | -5.27 | 0.000 | False |
| low | 39612 | -0.10 | 0.10 | 50.2 | -1.98 | 0.048 | 0.83 | 0.404 | False |
| normal | 16931 | -0.05 | -0.20 | 48.7 | -0.55 | 0.581 | -3.51 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 6.68 | 4.50 |
| normal | 16931 | 7.87 | 5.70 |
| high | 33437 | 9.19 | 6.50 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33417 | 0.04 | -0.60 | 47.9 | 0.43 | 0.664 | -7.71 | 0.000 | False |
| low | 39612 | -0.02 | 0.20 | 50.6 | -0.30 | 0.765 | 2.35 | 0.019 | False |
| normal | 16931 | -0.13 | -0.20 | 49.2 | -1.01 | 0.311 | -2.21 | 0.027 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 9.99 | 6.70 |
| normal | 16931 | 11.62 | 8.20 |
| high | 33417 | 12.50 | 9.10 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33377 | 0.49 | -0.50 | 48.9 | 3.50 | 0.000 | -4.15 | 0.000 | False |
| low | 39612 | -0.48 | -0.40 | 48.7 | -4.89 | 0.000 | -5.24 | 0.000 | False |
| normal | 16931 | -0.05 | -0.60 | 48.6 | -0.30 | 0.766 | -3.60 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39612 | 13.92 | 9.90 |
| normal | 16931 | 16.92 | 12.60 |
| high | 33377 | 18.67 | 13.60 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 39612 | 44.0 |
| normal | 16939 | 18.8 |
| high | 33449 | 37.2 |

