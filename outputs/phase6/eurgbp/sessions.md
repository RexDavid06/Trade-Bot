# SESSION STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:20:00` .. `2026-09-10 17:35:00`
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
| Asian | 26239 | 0.05 | 0.00 | 46.9 | 0.61 |
| London | 18736 | 0.00 | 0.00 | 47.7 | 0.96 |
| LondonNY | 15064 | -0.01 | 0.00 | 48.1 | 1.17 |
| NewYork | 18781 | -0.00 | 0.00 | 48.3 | 1.15 |
| OffHours | 11179 | -0.11 | 0.00 | 44.8 | 0.75 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.12 | 0.00 | 49.8 | 0.98 |
| London | 18736 | 0.00 | 0.00 | 48.8 | 1.64 |
| LondonNY | 15064 | -0.02 | 0.00 | 48.3 | 1.97 |
| NewYork | 18779 | -0.01 | 0.00 | 49.1 | 1.89 |
| OffHours | 11179 | -0.24 | -0.10 | 44.3 | 1.23 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.18 | 0.10 | 50.8 | 1.21 |
| London | 18736 | 0.01 | 0.00 | 48.5 | 2.15 |
| LondonNY | 15064 | -0.04 | -0.10 | 48.2 | 2.54 |
| NewYork | 18777 | -0.01 | 0.00 | 49.3 | 2.39 |
| OffHours | 11179 | -0.34 | -0.20 | 42.7 | 1.54 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.32 | 0.20 | 52.5 | 1.64 |
| London | 18736 | -0.00 | -0.10 | 48.7 | 3.21 |
| LondonNY | 15064 | -0.07 | -0.10 | 48.6 | 3.68 |
| NewYork | 18772 | -0.02 | 0.00 | 48.8 | 3.27 |
| OffHours | 11179 | -0.55 | -0.50 | 39.6 | 2.11 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.39 | 0.30 | 54.4 | 2.19 |
| London | 18736 | -0.05 | -0.20 | 47.8 | 4.83 |
| LondonNY | 15064 | -0.12 | -0.20 | 48.7 | 5.43 |
| NewYork | 18762 | -0.06 | -0.10 | 48.9 | 4.40 |
| OffHours | 11179 | -0.45 | -0.40 | 44.0 | 2.81 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.47 | 0.30 | 53.1 | 3.40 |
| London | 18736 | -0.27 | -0.40 | 47.5 | 7.11 |
| LondonNY | 15044 | -0.16 | -0.50 | 47.6 | 7.82 |
| NewYork | 18762 | -0.45 | -0.50 | 46.3 | 5.57 |
| OffHours | 11179 | 0.53 | 0.40 | 55.1 | 3.04 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26239 | 0.57 | 0.20 | 50.9 | 6.45 |
| London | 18724 | -0.65 | -0.80 | 46.8 | 10.28 |
| LondonNY | 15016 | -0.34 | -0.30 | 48.9 | 10.20 |
| NewYork | 18762 | -0.23 | 0.00 | 49.6 | 6.37 |
| OffHours | 11179 | 1.02 | 1.00 | 58.3 | 3.96 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 26239 | 29.2 |
| London | 18736 | 20.8 |
| LondonNY | 15064 | 16.7 |
| NewYork | 18782 | 20.9 |
| OffHours | 11179 | 12.4 |

