## Dataset (DEV only)

- **Symbol**: GBPUSD
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-06-13 18:25:00
- **Dev candles**: 224,848
- **Validation meta**: {'dev': np.int64(224848), 'val': np.int64(74949), 'holdout': np.int64(74949)}

## Interpretation

Session is assigned from the bar's UTC hour. We report forward pips, hit rate and an average-absolute-move proxy per session. A session with hit rate consistently above/below 50% and non-trivial sample size is where a session-specific edge may exist; a session with large |move| but hit ~50% is high-noise/high-opportunity but not directional.

### Horizon = 1

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.02 | 0.00 | 48.6 | 2.03 |
| London | 46920 | -0.02 | 0.00 | 49.0 | 3.53 |
| LondonNY | 37536 | 0.02 | 0.00 | 49.5 | 4.41 |
| NewYork | 46887 | -0.02 | 0.00 | 48.4 | 2.41 |
| OffHours | 27816 | 0.05 | 0.00 | 48.3 | 1.62 |

### Horizon = 3

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.05 | 0.00 | 49.2 | 3.53 |
| London | 46920 | -0.05 | 0.00 | 49.7 | 6.10 |
| LondonNY | 37536 | 0.04 | 0.00 | 49.8 | 7.70 |
| NewYork | 46885 | -0.03 | 0.00 | 48.9 | 4.12 |
| OffHours | 27816 | 0.11 | 0.10 | 51.6 | 2.94 |

### Horizon = 5

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.08 | 0.00 | 49.2 | 4.61 |
| London | 46920 | -0.09 | 0.00 | 49.7 | 7.86 |
| LondonNY | 37536 | 0.06 | 0.00 | 49.8 | 9.96 |
| NewYork | 46883 | -0.03 | -0.10 | 48.9 | 5.21 |
| OffHours | 27816 | 0.14 | 0.20 | 52.5 | 3.99 |

### Horizon = 10

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.11 | 0.00 | 49.4 | 6.69 |
| London | 46920 | -0.21 | -0.10 | 49.5 | 11.26 |
| LondonNY | 37536 | 0.15 | 0.00 | 49.9 | 13.84 |
| NewYork | 46878 | -0.00 | -0.10 | 48.6 | 7.05 |
| OffHours | 27816 | 0.10 | 0.50 | 53.7 | 6.25 |

### Horizon = 20

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.18 | -0.10 | 49.2 | 9.85 |
| London | 46920 | -0.48 | -0.20 | 49.3 | 16.41 |
| LondonNY | 37536 | 0.45 | 0.30 | 50.4 | 19.21 |
| NewYork | 46868 | 0.01 | -0.10 | 49.1 | 9.37 |
| OffHours | 27816 | -0.03 | 0.70 | 53.5 | 10.17 |

### Horizon = 40

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -0.43 | -0.40 | 49.0 | 15.33 |
| London | 46920 | -0.71 | 0.10 | 50.1 | 24.95 |
| LondonNY | 37526 | 0.77 | 0.60 | 50.8 | 25.01 |
| NewYork | 46858 | 0.22 | 0.10 | 50.2 | 12.11 |
| OffHours | 27816 | -0.50 | 0.30 | 50.7 | 16.65 |

### Horizon = 80

**Forward pips by session:**

| session | n | avg_pips | med_pips | hit_pct | avg_abs_pips |
|---|---|---|---|---|---|
| Asian | 65688 | -1.10 | -0.30 | 49.6 | 26.13 |
| London | 46918 | -0.15 | 0.10 | 50.1 | 38.04 |
| LondonNY | 37488 | 0.96 | 0.55 | 50.6 | 29.15 |
| NewYork | 46858 | 0.05 | 0.30 | 50.6 | 19.81 |
| OffHours | 27816 | -1.16 | -0.50 | 48.9 | 20.61 |

## Session frequency

| session | bars | % |
|---|---|---|
| Asian | 65688 | 29.2 |
| London | 46920 | 20.9 |
| LondonNY | 37536 | 16.7 |
| NewYork | 46888 | 20.9 |
| OffHours | 27816 | 12.4 |
