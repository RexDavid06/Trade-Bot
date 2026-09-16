# SESSION STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-26 01:30:00` .. `2026-09-10 17:35:00`
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
| Asian | 26237 | 9.49 | 10.00 | 50.2 | 262.89 |
| London | 18738 | 1.44 | 10.00 | 51.0 | 314.73 |
| LondonNY | 15064 | 0.03 | 0.00 | 49.6 | 293.16 |
| NewYork | 18781 | 0.37 | 10.00 | 50.3 | 303.60 |
| OffHours | 11179 | -16.66 | 0.00 | 49.1 | 215.56 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 26.48 | 30.00 | 52.0 | 447.09 |
| London | 18738 | 4.58 | 30.00 | 51.8 | 546.29 |
| LondonNY | 15064 | -1.18 | 10.00 | 50.7 | 495.42 |
| NewYork | 18779 | 2.37 | 20.00 | 51.1 | 509.16 |
| OffHours | 11179 | -46.29 | 0.00 | 48.9 | 377.89 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 37.24 | 50.00 | 52.9 | 572.32 |
| London | 18738 | 8.50 | 50.00 | 52.4 | 711.09 |
| LondonNY | 15064 | -1.92 | 20.00 | 50.7 | 637.47 |
| NewYork | 18777 | 4.83 | 30.00 | 51.8 | 648.38 |
| OffHours | 11179 | -64.12 | -20.00 | 47.7 | 488.57 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 58.49 | 90.00 | 54.8 | 816.38 |
| London | 18738 | 25.93 | 80.00 | 53.3 | 1022.53 |
| LondonNY | 15064 | -11.00 | 40.00 | 51.4 | 926.54 |
| NewYork | 18772 | 18.45 | 80.00 | 53.3 | 894.15 |
| OffHours | 11179 | -111.01 | -70.00 | 45.5 | 690.36 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 61.38 | 140.00 | 54.6 | 1195.65 |
| London | 18738 | 57.17 | 170.00 | 54.4 | 1488.97 |
| LondonNY | 15064 | -51.54 | 100.00 | 52.7 | 1395.14 |
| NewYork | 18762 | 66.36 | 120.00 | 54.0 | 1196.07 |
| OffHours | 11179 | -109.07 | -120.00 | 43.9 | 904.11 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 51.87 | 180.00 | 54.3 | 1776.29 |
| London | 18738 | 71.70 | 290.00 | 55.8 | 2113.25 |
| LondonNY | 15044 | -53.36 | 260.00 | 54.8 | 2155.13 |
| NewYork | 18762 | 109.20 | 160.00 | 54.2 | 1502.43 |
| OffHours | 11179 | -1.05 | -60.00 | 47.4 | 1221.51 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26237 | 105.38 | 350.00 | 55.1 | 2745.19 |
| London | 18726 | -21.02 | 490.00 | 56.2 | 3061.74 |
| LondonNY | 15016 | 66.32 | 550.00 | 57.2 | 2807.09 |
| NewYork | 18762 | 185.55 | 150.00 | 53.0 | 1951.40 |
| OffHours | 11179 | 86.56 | 100.00 | 51.9 | 2296.21 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 26237 | 29.2 |
| London | 18738 | 20.8 |
| LondonNY | 15064 | 16.7 |
| NewYork | 18782 | 20.9 |
| OffHours | 11179 | 12.4 |

