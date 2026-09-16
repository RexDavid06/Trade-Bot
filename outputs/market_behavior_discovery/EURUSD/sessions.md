## Dataset (DEV only)

- **Symbol**: EURUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-29 08:00:00
- **Dev candles**: 253,335
- **Validation meta**: {'dev': np.int64(253335), 'val': np.int64(84445), 'holdout': np.int64(84445)}

## Interpretation

Session is assigned from the bar's UTC hour. We report forward pips, hit rate and an average-absolute-move proxy per session. A session with hit rate consistently above/below 50% and non-trivial sample size is where a session-specific edge may exist; a session with large |move| but hit ~50% is high-noise/high-opportunity but not directional.

### Horizon = 1

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73999 | -0.01 | 0.00 | 48.3 | 1.47 |
| London | 52764 | -0.02 | 0.00 | 48.8 | 2.52 |
| LondonNY | 42192 | -0.01 | 0.00 | 49.4 | 3.32 |
| NewYork | 52740 | -0.01 | 0.00 | 48.6 | 1.81 |
| OffHours | 31639 | 0.03 | 0.00 | 46.9 | 1.01 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73999 | -0.02 | 0.00 | 48.8 | 2.54 |
| London | 52762 | -0.07 | 0.00 | 49.6 | 4.31 |
| LondonNY | 42192 | -0.01 | 0.00 | 49.6 | 5.81 |
| NewYork | 52740 | -0.01 | 0.00 | 48.8 | 3.05 |
| OffHours | 31639 | 0.07 | 0.10 | 50.5 | 1.75 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73999 | -0.03 | 0.00 | 48.9 | 3.31 |
| London | 52760 | -0.11 | 0.00 | 49.4 | 5.55 |
| LondonNY | 42192 | -0.02 | 0.00 | 49.5 | 7.54 |
| NewYork | 52740 | -0.01 | 0.00 | 49.0 | 3.87 |
| OffHours | 31639 | 0.09 | 0.10 | 52.0 | 2.29 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73999 | -0.03 | 0.00 | 49.5 | 4.82 |
| London | 52755 | -0.24 | -0.10 | 49.2 | 7.93 |
| LondonNY | 42192 | -0.06 | -0.10 | 49.3 | 10.56 |
| NewYork | 52740 | 0.02 | 0.00 | 49.2 | 5.25 |
| OffHours | 31639 | 0.08 | 0.30 | 52.7 | 3.38 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73992 | -0.02 | 0.00 | 49.8 | 7.15 |
| London | 52752 | -0.55 | -0.20 | 49.1 | 11.51 |
| LondonNY | 42192 | -0.06 | -0.30 | 49.0 | 14.63 |
| NewYork | 52740 | 0.10 | 0.10 | 50.3 | 6.91 |
| OffHours | 31639 | -0.01 | 0.30 | 52.4 | 5.22 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73972 | -0.05 | -0.10 | 49.4 | 11.20 |
| London | 52752 | -1.08 | -0.90 | 47.8 | 17.84 |
| LondonNY | 42192 | -0.11 | -0.30 | 49.4 | 18.84 |
| NewYork | 52740 | 0.29 | 0.30 | 51.6 | 8.63 |
| OffHours | 31639 | -0.19 | 0.30 | 50.9 | 8.67 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 73932 | -0.55 | 0.00 | 49.8 | 19.29 |
| London | 52752 | -1.52 | -1.90 | 47.3 | 27.72 |
| LondonNY | 42192 | 0.19 | 0.00 | 49.8 | 21.97 |
| NewYork | 52740 | 0.25 | 0.60 | 51.8 | 12.22 |
| OffHours | 31639 | -0.38 | 0.00 | 49.8 | 11.73 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 73999 | 29.2 |
| London | 52765 | 20.8 |
| LondonNY | 42192 | 16.7 |
| NewYork | 52740 | 20.8 |
| OffHours | 31639 | 12.5 |
