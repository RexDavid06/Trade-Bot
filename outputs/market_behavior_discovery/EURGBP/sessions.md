## Dataset (DEV only)

- **Symbol**: EURGBP
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-30 15:15:00
- **Dev candles**: 255,286
- **Validation meta**: {'dev': np.int64(255286), 'val': np.int64(85096), 'holdout': np.int64(85095)}

## Interpretation

Session is assigned from the bar's UTC hour. We report forward pips, hit rate and an average-absolute-move proxy per session. A session with hit rate consistently above/below 50% and non-trivial sample size is where a session-specific edge may exist; a session with large |move| but hit ~50% is high-noise/high-opportunity but not directional.

### Horizon = 1

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.01 | 0.00 | 47.3 | 0.91 |
| London | 53231 | -0.01 | 0.00 | 48.6 | 1.93 |
| LondonNY | 42567 | -0.01 | 0.00 | 48.9 | 2.02 |
| NewYork | 53159 | -0.06 | 0.00 | 47.1 | 1.15 |
| OffHours | 31741 | 0.10 | 0.00 | 49.4 | 0.99 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.02 | 0.00 | 48.8 | 1.55 |
| London | 53231 | -0.02 | 0.00 | 49.0 | 3.31 |
| LondonNY | 42565 | -0.01 | 0.00 | 49.0 | 3.39 |
| NewYork | 53159 | -0.15 | -0.10 | 47.2 | 1.90 |
| OffHours | 31741 | 0.22 | 0.10 | 53.0 | 1.51 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.03 | 0.00 | 48.9 | 2.00 |
| London | 53231 | -0.04 | -0.10 | 49.0 | 4.24 |
| LondonNY | 42563 | -0.02 | -0.10 | 48.9 | 4.34 |
| NewYork | 53159 | -0.22 | -0.10 | 47.0 | 2.36 |
| OffHours | 31741 | 0.32 | 0.30 | 54.9 | 1.85 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.06 | 0.00 | 49.4 | 2.92 |
| London | 53231 | -0.06 | -0.10 | 48.8 | 5.98 |
| LondonNY | 42558 | -0.07 | -0.20 | 48.4 | 6.00 |
| NewYork | 53159 | -0.35 | -0.30 | 45.4 | 3.10 |
| OffHours | 31741 | 0.52 | 0.50 | 57.3 | 2.49 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.10 | 0.10 | 50.2 | 4.44 |
| London | 53231 | -0.10 | -0.20 | 49.0 | 8.47 |
| LondonNY | 42548 | -0.22 | -0.40 | 47.9 | 8.21 |
| NewYork | 53159 | -0.60 | -0.50 | 43.7 | 3.97 |
| OffHours | 31741 | 0.95 | 0.80 | 59.5 | 3.27 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.19 | 0.10 | 50.2 | 7.35 |
| London | 53231 | -0.19 | -0.50 | 48.1 | 12.15 |
| LondonNY | 42528 | -0.49 | -0.80 | 46.9 | 10.57 |
| NewYork | 53159 | -0.75 | -0.50 | 44.6 | 4.73 |
| OffHours | 31741 | 1.23 | 1.10 | 58.2 | 4.75 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 74587 | 0.23 | -0.10 | 49.5 | 13.46 |
| London | 53191 | -0.61 | -1.10 | 47.4 | 16.96 |
| LondonNY | 42528 | -1.36 | -1.65 | 44.8 | 11.99 |
| NewYork | 53159 | -0.07 | 0.00 | 49.9 | 6.20 |
| OffHours | 31741 | 1.29 | 1.00 | 56.1 | 6.30 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 74587 | 29.2 |
| London | 53231 | 20.9 |
| LondonNY | 42568 | 16.7 |
| NewYork | 53159 | 20.8 |
| OffHours | 31741 | 12.4 |
