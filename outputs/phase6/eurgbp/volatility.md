# VOLATILITY STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:20:00` .. `2026-09-10 17:35:00`
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
| high | 33142 | 0.03 | 0.00 | 48.8 | 3.38 | 0.001 | -4.39 | 0.000 | False |
| low | 40739 | -0.02 | 0.00 | 46.2 | -4.56 | 0.000 | -15.29 | 0.000 | False |
| normal | 16118 | -0.01 | 0.00 | 47.1 | -0.57 | 0.570 | -7.34 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 0.67 | 0.50 |
| normal | 16118 | 0.90 | 0.60 |
| high | 33142 | 1.20 | 0.90 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33140 | 0.07 | 0.00 | 49.9 | 4.26 | 0.000 | -0.47 | 0.637 | False |
| low | 40739 | -0.06 | 0.00 | 47.2 | -7.21 | 0.000 | -11.29 | 0.000 | False |
| normal | 16118 | 0.02 | 0.00 | 49.1 | 1.33 | 0.184 | -2.33 | 0.020 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 1.12 | 0.80 |
| normal | 16118 | 1.48 | 1.00 |
| high | 33140 | 1.99 | 1.40 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33138 | 0.10 | 0.10 | 50.4 | 5.02 | 0.000 | 1.33 | 0.184 | False |
| low | 40739 | -0.09 | -0.10 | 46.9 | -8.63 | 0.000 | -12.32 | 0.000 | False |
| normal | 16118 | 0.04 | 0.00 | 49.0 | 1.91 | 0.057 | -2.47 | 0.013 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 1.43 | 1.00 |
| normal | 16118 | 1.88 | 1.30 |
| high | 33138 | 2.54 | 1.80 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33133 | 0.15 | 0.10 | 51.2 | 5.46 | 0.000 | 4.30 | 0.000 | False |
| low | 40739 | -0.16 | -0.10 | 46.4 | -10.81 | 0.000 | -14.50 | 0.000 | False |
| normal | 16118 | 0.13 | 0.00 | 49.4 | 4.32 | 0.000 | -1.56 | 0.119 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 2.02 | 1.40 |
| normal | 16118 | 2.63 | 1.80 |
| high | 33133 | 3.59 | 2.70 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33123 | 0.16 | 0.30 | 51.7 | 4.18 | 0.000 | 6.05 | 0.000 | False |
| low | 40739 | -0.19 | -0.10 | 47.3 | -9.29 | 0.000 | -11.05 | 0.000 | False |
| normal | 16118 | 0.24 | 0.20 | 51.5 | 5.33 | 0.000 | 3.84 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 2.88 | 2.00 |
| normal | 16118 | 3.81 | 2.60 |
| high | 33123 | 4.98 | 3.70 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33104 | 0.08 | 0.20 | 51.1 | 1.64 | 0.102 | 4.05 | 0.000 | False |
| low | 40739 | -0.06 | -0.10 | 48.5 | -1.97 | 0.048 | -5.98 | 0.000 | False |
| normal | 16117 | 0.13 | 0.10 | 50.7 | 2.04 | 0.041 | 1.71 | 0.087 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 4.22 | 2.90 |
| normal | 16117 | 5.53 | 3.70 |
| high | 33104 | 6.57 | 4.70 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 33064 | -0.16 | 0.00 | 49.7 | -2.36 | 0.018 | -1.17 | 0.244 | False |
| low | 40739 | 0.24 | 0.20 | 50.9 | 5.17 | 0.000 | 3.81 | 0.000 | False |
| normal | 16117 | 0.03 | 0.10 | 50.3 | 0.35 | 0.730 | 0.67 | 0.503 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 40739 | 6.43 | 4.50 |
| normal | 16117 | 7.80 | 5.40 |
| high | 33064 | 8.80 | 6.20 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 40739 | 45.3 |
| normal | 16118 | 17.9 |
| high | 33143 | 36.8 |

