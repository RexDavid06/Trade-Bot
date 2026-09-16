## Dataset (DEV only)

- **Symbol**: EURJPY
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2025-06-26 03:00:00 .. 2026-03-19 17:05:00
- **Dev candles**: 54,000
- **Validation meta**: {'dev': np.int64(54000), 'val': np.int64(18000), 'holdout': np.int64(18000)}

## Interpretation

Session is assigned from the bar's UTC hour. We report forward pips, hit rate and an average-absolute-move proxy per session. A session with hit rate consistently above/below 50% and non-trivial sample size is where a session-specific edge may exist; a session with large |move| but hit ~50% is high-noise/high-opportunity but not directional.

### Horizon = 1

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 0.11 | 0.10 | 50.3 | 2.97 |
| London | 11238 | 0.03 | 0.10 | 50.5 | 3.44 |
| LondonNY | 9064 | 0.03 | 0.00 | 49.8 | 3.10 |
| NewYork | 11275 | -0.00 | 0.10 | 50.2 | 3.25 |
| OffHours | 6703 | -0.14 | 0.00 | 49.8 | 2.32 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 0.31 | 0.30 | 52.3 | 5.04 |
| London | 11238 | 0.10 | 0.20 | 51.4 | 5.96 |
| LondonNY | 9064 | 0.06 | 0.10 | 50.7 | 5.20 |
| NewYork | 11273 | 0.00 | 0.10 | 50.5 | 5.41 |
| OffHours | 6703 | -0.40 | 0.00 | 49.3 | 4.03 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 0.42 | 0.50 | 52.8 | 6.45 |
| London | 11238 | 0.20 | 0.50 | 51.9 | 7.72 |
| LondonNY | 9064 | 0.11 | 0.20 | 50.9 | 6.68 |
| NewYork | 11271 | 0.00 | 0.30 | 51.3 | 6.89 |
| OffHours | 6703 | -0.48 | -0.10 | 48.4 | 5.15 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 0.67 | 1.10 | 54.4 | 9.16 |
| London | 11238 | 0.47 | 0.80 | 53.0 | 11.11 |
| LondonNY | 9064 | 0.23 | 0.50 | 51.4 | 9.56 |
| NewYork | 11266 | 0.02 | 0.70 | 52.5 | 9.45 |
| OffHours | 6703 | -0.76 | -0.50 | 46.5 | 7.18 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 0.83 | 1.90 | 54.9 | 13.55 |
| London | 11238 | 0.95 | 1.90 | 54.1 | 16.19 |
| LondonNY | 9058 | 0.37 | 1.10 | 52.7 | 14.09 |
| NewYork | 11262 | 0.11 | 1.10 | 53.3 | 12.65 |
| OffHours | 6703 | -0.31 | -1.00 | 45.7 | 9.50 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 1.04 | 2.50 | 54.3 | 20.22 |
| London | 11238 | 1.55 | 3.40 | 55.7 | 22.54 |
| LondonNY | 9038 | 0.89 | 2.90 | 54.5 | 22.16 |
| NewYork | 11262 | 0.37 | 1.40 | 53.5 | 15.78 |
| OffHours | 6703 | 1.04 | 0.40 | 51.4 | 13.41 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 15719 | 2.52 | 5.00 | 55.1 | 30.60 |
| London | 11220 | 1.94 | 5.70 | 55.7 | 31.48 |
| LondonNY | 9016 | 1.19 | 4.30 | 55.1 | 28.13 |
| NewYork | 11262 | 1.92 | 1.70 | 53.2 | 20.41 |
| OffHours | 6703 | 1.95 | 2.40 | 53.5 | 25.95 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 15719 | 29.1 |
| London | 11238 | 20.8 |
| LondonNY | 9064 | 16.8 |
| NewYork | 11276 | 20.9 |
| OffHours | 6703 | 12.4 |
