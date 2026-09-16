# VOLATILITY STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:30:00` .. `2026-09-10 17:35:00`
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
| high | 31858 | 4.04 | 10.00 | 50.5 | 1.31 | 0.190 | 1.84 | 0.066 | False |
| low | 39386 | -2.86 | 0.00 | 49.6 | -1.67 | 0.094 | -1.59 | 0.111 | False |
| normal | 18755 | 4.32 | 10.00 | 50.7 | 1.23 | 0.220 | 1.99 | 0.046 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39386 | 222.57 | 160.00 |
| normal | 18755 | 279.26 | 200.00 |
| high | 31858 | 355.30 | 250.00 |

### Horizon = 3

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31856 | 16.61 | 30.00 | 52.0 | 3.31 | 0.001 | 7.03 | 0.000 | False |
| low | 39386 | -8.90 | 10.00 | 50.5 | -2.80 | 0.005 | 1.82 | 0.068 | False |
| normal | 18755 | 5.93 | 20.00 | 51.2 | 1.04 | 0.298 | 3.34 | 0.001 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39386 | 388.52 | 270.00 |
| normal | 18755 | 476.64 | 330.00 |
| high | 31856 | 595.62 | 420.00 |

### Horizon = 5

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31854 | 27.81 | 60.00 | 52.7 | 4.43 | 0.000 | 9.78 | 0.000 | False |
| low | 39386 | -13.34 | 10.00 | 50.6 | -3.12 | 0.002 | 2.47 | 0.014 | False |
| normal | 18755 | 6.45 | 30.00 | 51.6 | 0.90 | 0.371 | 4.26 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39386 | 508.56 | 350.00 |
| normal | 18755 | 612.28 | 430.00 |
| high | 31854 | 755.52 | 540.00 |

### Horizon = 10

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31849 | 51.85 | 120.00 | 54.4 | 6.09 | 0.000 | 15.75 | 0.000 | False |
| low | 39386 | -20.19 | 20.00 | 50.7 | -3.34 | 0.001 | 2.81 | 0.005 | False |
| normal | 18755 | 5.55 | 60.00 | 52.7 | 0.51 | 0.609 | 7.41 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39386 | 734.49 | 510.00 |
| normal | 18755 | 892.86 | 620.00 |
| high | 31849 | 1047.60 | 750.00 |

### Horizon = 20

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31839 | 78.40 | 180.00 | 55.0 | 6.77 | 0.000 | 17.80 | 0.000 | False |
| low | 39386 | -8.57 | 30.00 | 51.0 | -0.99 | 0.321 | 3.80 | 0.000 | False |
| normal | 18755 | -12.12 | 90.00 | 52.9 | -0.77 | 0.443 | 7.82 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39386 | 1092.50 | 740.00 |
| normal | 18755 | 1294.42 | 870.00 |
| high | 31839 | 1429.97 | 1030.00 |

### Horizon = 40

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31830 | 87.13 | 280.00 | 55.9 | 5.40 | 0.000 | 20.95 | 0.000 | False |
| low | 39378 | 42.50 | 80.00 | 52.1 | 3.42 | 0.001 | 8.37 | 0.000 | False |
| normal | 18752 | -27.10 | 170.00 | 53.9 | -1.27 | 0.205 | 10.79 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39378 | 1632.86 | 1080.00 |
| normal | 18752 | 1884.50 | 1280.00 |
| high | 31830 | 1911.14 | 1390.00 |

### Horizon = 80

**Signed forward pips by volatility regime:**

| group | n | avg_pips | med_pips | hit_pct | t | t_p | z | z_p | small |
|---|---|---|---|---|---|---|---|---|---|
| high | 31826 | 69.23 | 360.00 | 55.3 | 2.93 | 0.003 | 18.78 | 0.000 | False |
| low | 39361 | 121.96 | 290.00 | 54.8 | 6.85 | 0.000 | 19.21 | 0.000 | False |
| normal | 18733 | 43.36 | 280.00 | 54.1 | 1.50 | 0.134 | 11.30 | 0.000 | False |

**Absolute forward |pips| by regime (how far price actually moves):**

| regime | n | avg_abs_pips | med_abs_pips |
|---|---|---|---|
| low | 39361 | 2422.02 | 1720.00 |
| normal | 18733 | 2658.58 | 1890.00 |
| high | 31826 | 2785.65 | 1990.00 |

## Regime frequency

| regime | bars | % |
|---|---|---|
| low | 39386 | 43.8 |
| normal | 18755 | 20.8 |
| high | 31859 | 35.4 |

