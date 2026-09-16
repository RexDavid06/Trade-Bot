# SESSION STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-25 23:45:00` .. `2026-09-10 17:35:00`
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
| Asian | 26255 | 0.06 | 0.00 | 48.8 | 1.54 |
| London | 18735 | -0.01 | 0.00 | 48.8 | 2.31 |
| LondonNY | 15047 | 0.01 | 0.00 | 48.6 | 2.71 |
| NewYork | 18781 | 0.00 | 0.00 | 49.1 | 2.93 |
| OffHours | 11181 | -0.16 | 0.00 | 47.0 | 1.79 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | 0.13 | 0.10 | 50.6 | 2.60 |
| London | 18735 | -0.01 | 0.00 | 49.5 | 4.05 |
| LondonNY | 15047 | 0.04 | -0.10 | 49.1 | 4.80 |
| NewYork | 18779 | 0.01 | -0.10 | 48.8 | 5.01 |
| OffHours | 11181 | -0.38 | -0.10 | 47.0 | 3.12 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | 0.19 | 0.10 | 51.3 | 3.30 |
| London | 18735 | -0.02 | 0.00 | 49.9 | 5.30 |
| LondonNY | 15047 | 0.06 | -0.10 | 49.3 | 6.24 |
| NewYork | 18777 | 0.03 | -0.20 | 48.6 | 6.44 |
| OffHours | 11181 | -0.60 | -0.40 | 45.7 | 3.99 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | 0.27 | 0.20 | 51.5 | 4.68 |
| London | 18735 | -0.02 | 0.20 | 50.5 | 7.68 |
| LondonNY | 15047 | 0.20 | 0.00 | 49.6 | 9.19 |
| NewYork | 18772 | -0.03 | -0.10 | 49.2 | 8.96 |
| OffHours | 11181 | -0.94 | -0.70 | 43.9 | 5.43 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | 0.29 | 0.30 | 51.2 | 6.69 |
| London | 18735 | -0.05 | 0.30 | 50.7 | 11.14 |
| LondonNY | 15047 | 0.58 | 0.10 | 50.2 | 13.77 |
| NewYork | 18762 | -0.17 | -0.50 | 48.4 | 12.20 |
| OffHours | 11181 | -1.36 | -0.80 | 43.8 | 6.90 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | 0.03 | 0.30 | 50.9 | 9.86 |
| London | 18735 | -0.16 | 0.30 | 50.4 | 16.02 |
| LondonNY | 15027 | 1.54 | 1.60 | 52.5 | 20.95 |
| NewYork | 18762 | -0.80 | -1.10 | 47.0 | 15.76 |
| OffHours | 11181 | -1.06 | -0.50 | 46.9 | 9.29 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26255 | -0.56 | 0.40 | 50.8 | 16.65 |
| London | 18723 | 0.89 | 1.40 | 51.9 | 25.18 |
| LondonNY | 14999 | 1.64 | 0.30 | 50.4 | 27.80 |
| NewYork | 18762 | -1.66 | -1.60 | 46.4 | 19.10 |
| OffHours | 11181 | -0.63 | -0.50 | 48.1 | 12.87 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 26255 | 29.2 |
| London | 18735 | 20.8 |
| LondonNY | 15047 | 16.7 |
| NewYork | 18782 | 20.9 |
| OffHours | 11181 | 12.4 |

