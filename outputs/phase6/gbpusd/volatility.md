# VOLATILITY STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 23:45:00` .. `2026-09-10 17:35:00`
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
| high | 32668 | 0.02 | 0.00 | 49.1 | 0.96 | 0.335 | -3.25 | 0.001 | False |
| low | 39189 | -0.02 | 0.00 | 48.1 | -1.88 | 0.060 | -7.36 | 0.000 | False |
| normal | 18142 | 0.01 | 0.00 | 48.8 | 0.21 | 0.831 | -3.15 | 0.002 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 1.70 | 1.20 |
| normal | 18142 | 2.16 | 1.50 |
| high | 32668 | 2.86 | 2.10 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32668 | 0.07 | 0.00 | 49.8 | 1.67 | 0.094 | -0.56 | 0.573 | False |
| low | 39189 | -0.08 | 0.00 | 48.7 | -3.44 | 0.001 | -4.98 | 0.000 | False |
| normal | 18140 | 0.03 | 0.00 | 49.6 | 0.71 | 0.476 | -1.04 | 0.299 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 3.00 | 2.10 |
| normal | 18140 | 3.69 | 2.60 |
| high | 32668 | 4.92 | 3.50 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32668 | 0.11 | 0.00 | 49.9 | 2.10 | 0.035 | -0.33 | 0.740 | False |
| low | 39189 | -0.12 | 0.00 | 48.9 | -4.11 | 0.000 | -4.17 | 0.000 | False |
| normal | 18138 | 0.04 | 0.00 | 49.5 | 0.70 | 0.484 | -1.32 | 0.186 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 3.90 | 2.80 |
| normal | 18138 | 4.76 | 3.30 |
| high | 32668 | 6.32 | 4.60 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32665 | 0.18 | 0.10 | 50.3 | 2.58 | 0.010 | 1.15 | 0.252 | False |
| low | 39189 | -0.21 | -0.10 | 48.7 | -4.95 | 0.000 | -5.04 | 0.000 | False |
| normal | 18136 | 0.06 | 0.00 | 49.9 | 0.87 | 0.386 | -0.19 | 0.847 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 5.66 | 4.00 |
| normal | 18136 | 6.81 | 4.80 |
| high | 32665 | 8.83 | 6.40 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32655 | 0.18 | 0.00 | 49.8 | 1.93 | 0.054 | -0.58 | 0.561 | False |
| low | 39189 | -0.23 | -0.10 | 49.0 | -3.66 | 0.000 | -4.05 | 0.000 | False |
| normal | 18136 | 0.01 | 0.00 | 49.6 | 0.13 | 0.898 | -1.02 | 0.305 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 8.34 | 5.70 |
| normal | 18136 | 9.77 | 6.90 |
| high | 32655 | 12.06 | 8.80 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32635 | 0.21 | 0.00 | 49.9 | 1.66 | 0.096 | -0.42 | 0.678 | False |
| low | 39189 | -0.37 | -0.10 | 49.3 | -4.09 | 0.000 | -2.77 | 0.006 | False |
| normal | 18136 | 0.09 | 0.20 | 50.6 | 0.58 | 0.563 | 1.49 | 0.138 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 12.17 | 8.20 |
| normal | 18136 | 14.22 | 10.10 |
| high | 32635 | 16.51 | 12.20 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 32595 | 0.13 | 0.00 | 49.9 | 0.73 | 0.465 | -0.35 | 0.727 | False |
| low | 39189 | -0.42 | -0.20 | 49.5 | -3.48 | 0.000 | -2.02 | 0.044 | False |
| normal | 18136 | 0.01 | -0.10 | 49.7 | 0.06 | 0.955 | -0.70 | 0.485 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39189 | 16.99 | 12.30 |
| normal | 18136 | 20.38 | 14.60 |
| high | 32595 | 24.31 | 18.10 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 39189 | 43.5 |
| normal | 18143 | 20.2 |
| high | 32668 | 36.3 |

