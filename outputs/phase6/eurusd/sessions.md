# SESSION STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 22:45:00` .. `2026-09-10 17:35:00`
- **Candles**: `90,000`
- **Timeframe**: M5 (EURUSD)

## Configuration

- **sessions_utc**: `['Asian', 'London', 'LondonNY', 'NewYork', 'OffHours']`
- **forward_horizons**: `[1, 3, 5, 10, 20, 40, 80]`

## Interpretation

Session is assigned from the bar's UTC hour. We report forward pips, hit rate and an average-absolute-move proxy per session. A session with hit rate consistently above/below 50% and non-trivial sample size is where a session-specific edge may exist; a session with large |move| but hit ~50% is high-noise/high-opportunity but not directional.

### Horizon = 1

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.03 | 0.00 | 48.7 | 1.24 |
| London | 18738 | -0.00 | 0.00 | 49.2 | 1.79 |
| LondonNY | 15064 | -0.00 | 0.00 | 48.2 | 2.09 |
| NewYork | 18780 | -0.00 | 0.00 | 48.6 | 2.31 |
| OffHours | 11194 | -0.06 | 0.00 | 47.8 | 1.47 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.06 | 0.10 | 50.1 | 2.11 |
| London | 18738 | -0.02 | 0.00 | 49.8 | 3.11 |
| LondonNY | 15064 | 0.00 | -0.10 | 48.2 | 3.65 |
| NewYork | 18778 | 0.00 | -0.10 | 48.5 | 3.96 |
| OffHours | 11194 | -0.15 | -0.10 | 47.4 | 2.53 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.09 | 0.10 | 50.7 | 2.72 |
| London | 18738 | -0.02 | 0.00 | 50.0 | 4.04 |
| LondonNY | 15064 | 0.00 | -0.10 | 48.5 | 4.75 |
| NewYork | 18776 | 0.01 | -0.20 | 48.2 | 5.07 |
| OffHours | 11194 | -0.21 | -0.10 | 47.2 | 3.20 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.13 | 0.20 | 51.4 | 3.88 |
| London | 18738 | -0.05 | 0.00 | 49.5 | 5.77 |
| LondonNY | 15064 | 0.08 | -0.10 | 48.7 | 6.94 |
| NewYork | 18771 | -0.05 | -0.40 | 47.6 | 7.03 |
| OffHours | 11194 | -0.28 | -0.20 | 47.7 | 4.38 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.13 | 0.20 | 50.9 | 5.60 |
| London | 18738 | -0.16 | -0.30 | 48.5 | 8.36 |
| LondonNY | 15064 | 0.34 | 0.10 | 50.2 | 10.57 |
| NewYork | 18761 | -0.21 | -0.70 | 46.6 | 9.51 |
| OffHours | 11194 | -0.20 | 0.10 | 50.1 | 5.71 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | -0.07 | 0.00 | 49.9 | 8.22 |
| London | 18738 | -0.55 | -0.60 | 47.9 | 12.00 |
| LondonNY | 15044 | 1.11 | 1.00 | 52.1 | 16.46 |
| NewYork | 18761 | -0.61 | -1.30 | 45.5 | 12.40 |
| OffHours | 11194 | 0.46 | 0.60 | 53.0 | 8.00 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | -0.52 | -0.10 | 49.5 | 12.84 |
| London | 18726 | -0.15 | -0.90 | 48.3 | 19.86 |
| LondonNY | 15016 | 0.97 | -0.30 | 49.5 | 22.19 |
| NewYork | 18761 | -0.41 | -1.40 | 46.3 | 15.68 |
| OffHours | 11194 | 0.55 | 0.20 | 50.5 | 11.16 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 26223 | 29.1 |
| London | 18738 | 20.8 |
| LondonNY | 15064 | 16.7 |
| NewYork | 18781 | 20.9 |
| OffHours | 11194 | 12.4 |

