# SESSION STUDY

## Dataset

- **Dataset**: `eurusd_m5.csv`
- **Date range**: `2025-06-16 23:30:00` .. `2026-09-01 18:20:00`
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
| Asian | 26223 | 0.03 | 0.00 | 48.7 | 1.26 |
| London | 18738 | -0.01 | 0.00 | 49.2 | 1.82 |
| LondonNY | 15064 | -0.00 | 0.00 | 48.2 | 2.10 |
| NewYork | 18789 | 0.00 | 0.00 | 48.6 | 2.34 |
| OffHours | 11185 | -0.07 | 0.00 | 47.8 | 1.50 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.08 | 0.10 | 50.2 | 2.16 |
| London | 18738 | -0.02 | 0.00 | 49.7 | 3.15 |
| LondonNY | 15064 | 0.00 | -0.10 | 48.1 | 3.68 |
| NewYork | 18787 | 0.02 | -0.10 | 48.6 | 4.03 |
| OffHours | 11185 | -0.17 | -0.10 | 47.6 | 2.59 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.11 | 0.10 | 50.8 | 2.77 |
| London | 18738 | -0.03 | 0.00 | 49.9 | 4.09 |
| LondonNY | 15064 | -0.00 | -0.10 | 48.4 | 4.79 |
| NewYork | 18785 | 0.04 | -0.20 | 48.4 | 5.17 |
| OffHours | 11185 | -0.25 | -0.10 | 47.3 | 3.28 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.17 | 0.20 | 51.5 | 3.96 |
| London | 18738 | -0.08 | 0.00 | 49.3 | 5.84 |
| LondonNY | 15064 | 0.06 | -0.20 | 48.6 | 6.96 |
| NewYork | 18780 | 0.01 | -0.30 | 47.9 | 7.20 |
| OffHours | 11185 | -0.36 | -0.20 | 47.5 | 4.51 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.19 | 0.20 | 51.1 | 5.72 |
| London | 18738 | -0.18 | -0.30 | 48.5 | 8.45 |
| LondonNY | 15064 | 0.29 | 0.00 | 49.8 | 10.58 |
| NewYork | 18770 | -0.08 | -0.60 | 47.1 | 9.77 |
| OffHours | 11185 | -0.32 | 0.00 | 50.0 | 5.89 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | 0.03 | 0.10 | 50.2 | 8.35 |
| London | 18738 | -0.60 | -0.60 | 47.9 | 12.09 |
| LondonNY | 15053 | 1.12 | 0.80 | 51.8 | 16.56 |
| NewYork | 18761 | -0.46 | -1.10 | 46.1 | 12.86 |
| OffHours | 11185 | 0.35 | 0.50 | 52.7 | 8.24 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 26223 | -0.44 | 0.00 | 49.8 | 12.97 |
| London | 18735 | -0.22 | -1.00 | 48.1 | 19.91 |
| LondonNY | 15016 | 1.13 | -0.20 | 49.6 | 22.75 |
| NewYork | 18761 | -0.27 | -1.30 | 46.6 | 16.38 |
| OffHours | 11185 | 0.62 | 0.20 | 50.5 | 11.51 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 26223 | 29.1 |
| London | 18738 | 20.8 |
| LondonNY | 15064 | 16.7 |
| NewYork | 18790 | 20.9 |
| OffHours | 11185 | 12.4 |

