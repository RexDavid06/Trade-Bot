## Dataset (DEV only)

- **Symbol**: EURGBP
- **Split**: output from `research_split` (60/20/20 chronological)
- **Dev date range**: 2021-01-03 22:00:00 .. 2024-05-30 15:15:00
- **Dev candles**: 255,286
- **Validation meta**: {'dev': np.int64(255286), 'val': np.int64(85096), 'holdout': np.int64(85095)}

## Interpretation

A bar is a **high breakout** if its close pierces the highest high of the prior `CH` candles (excluding the current bar); **low breakout** if its close pierces the lowest low. Continuation predicts positive forward return after a high breakout; breakdown predicts negative return after a low breakout. Bucket = breakout state at entry.

### Channel = 20

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 14196 | 0.26 | 0.20 | 53.7 |
| 1 | inside | 227575 | -0.01 | 0.00 | 48.0 |
| 1 | high_breakout | 13494 | -0.19 | -0.20 | 43.8 |
| 3 | low_breakout | 14196 | 0.42 | 0.30 | 55.2 |
| 3 | inside | 227573 | -0.01 | 0.00 | 49.0 |
| 3 | high_breakout | 13494 | -0.34 | -0.30 | 43.1 |
| 5 | low_breakout | 14196 | 0.47 | 0.40 | 54.9 |
| 5 | inside | 227571 | -0.02 | 0.00 | 49.3 |
| 5 | high_breakout | 13494 | -0.40 | -0.50 | 42.6 |
| 10 | low_breakout | 14196 | 0.54 | 0.50 | 54.3 |
| 10 | inside | 227567 | -0.03 | 0.00 | 49.2 |
| 10 | high_breakout | 13493 | -0.43 | -0.50 | 44.3 |
| 20 | low_breakout | 14195 | 0.64 | 0.70 | 54.9 |
| 20 | inside | 227558 | -0.05 | 0.00 | 49.3 |
| 20 | high_breakout | 13493 | -0.54 | -0.70 | 44.6 |
| 40 | low_breakout | 14195 | 0.58 | 0.60 | 52.8 |
| 40 | inside | 227539 | -0.08 | -0.10 | 49.1 |
| 40 | high_breakout | 13492 | -0.62 | -0.90 | 45.0 |
| 80 | low_breakout | 14194 | 0.93 | 0.80 | 52.7 |
| 80 | inside | 227502 | -0.16 | -0.20 | 49.1 |
| 80 | high_breakout | 13490 | -0.84 | -1.10 | 46.2 |

High breakouts: `13494` bars, low breakouts: `14196` bars (~5.29% / 5.56% of dataset).

### Channel = 40

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 9529 | 0.34 | 0.20 | 54.6 |
| 1 | inside | 236296 | -0.01 | 0.00 | 48.0 |
| 1 | high_breakout | 9420 | -0.19 | -0.20 | 44.1 |
| 3 | low_breakout | 9529 | 0.50 | 0.40 | 55.8 |
| 3 | inside | 236294 | -0.01 | 0.00 | 49.0 |
| 3 | high_breakout | 9420 | -0.31 | -0.40 | 43.3 |
| 5 | low_breakout | 9529 | 0.55 | 0.50 | 55.4 |
| 5 | inside | 236292 | -0.02 | 0.00 | 49.3 |
| 5 | high_breakout | 9420 | -0.36 | -0.50 | 42.5 |
| 10 | low_breakout | 9529 | 0.64 | 0.60 | 54.6 |
| 10 | inside | 236288 | -0.03 | 0.00 | 49.3 |
| 10 | high_breakout | 9419 | -0.37 | -0.60 | 44.3 |
| 20 | low_breakout | 9529 | 0.73 | 0.80 | 54.9 |
| 20 | inside | 236278 | -0.05 | 0.00 | 49.3 |
| 20 | high_breakout | 9419 | -0.49 | -0.70 | 44.7 |
| 40 | low_breakout | 9529 | 0.72 | 0.80 | 53.3 |
| 40 | inside | 236259 | -0.08 | -0.10 | 49.1 |
| 40 | high_breakout | 9418 | -0.63 | -0.90 | 45.1 |
| 80 | low_breakout | 9529 | 1.24 | 1.10 | 53.6 |
| 80 | inside | 236220 | -0.16 | -0.20 | 49.1 |
| 80 | high_breakout | 9417 | -1.00 | -1.30 | 45.9 |

High breakouts: `9420` bars, low breakouts: `9529` bars (~3.69% / 3.73% of dataset).

### Channel = 80

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 6369 | 0.38 | 0.30 | 55.2 |
| 1 | inside | 242313 | -0.01 | 0.00 | 48.0 |
| 1 | high_breakout | 6523 | -0.17 | -0.20 | 44.4 |
| 3 | low_breakout | 6369 | 0.56 | 0.50 | 56.3 |
| 3 | inside | 242311 | -0.01 | 0.00 | 49.0 |
| 3 | high_breakout | 6523 | -0.29 | -0.40 | 43.3 |
| 5 | low_breakout | 6369 | 0.60 | 0.60 | 55.9 |
| 5 | inside | 242309 | -0.02 | 0.00 | 49.3 |
| 5 | high_breakout | 6523 | -0.34 | -0.50 | 42.6 |
| 10 | low_breakout | 6369 | 0.71 | 0.70 | 54.7 |
| 10 | inside | 242305 | -0.03 | 0.00 | 49.3 |
| 10 | high_breakout | 6522 | -0.31 | -0.60 | 44.5 |
| 20 | low_breakout | 6369 | 0.75 | 0.80 | 54.4 |
| 20 | inside | 242295 | -0.04 | 0.00 | 49.4 |
| 20 | high_breakout | 6522 | -0.46 | -0.70 | 44.7 |
| 40 | low_breakout | 6369 | 0.73 | 0.70 | 52.6 |
| 40 | inside | 242276 | -0.07 | -0.10 | 49.1 |
| 40 | high_breakout | 6521 | -0.75 | -1.00 | 45.2 |
| 80 | low_breakout | 6369 | 1.30 | 1.00 | 53.0 |
| 80 | inside | 242237 | -0.15 | -0.20 | 49.2 |
| 80 | high_breakout | 6520 | -1.41 | -1.60 | 45.0 |

High breakouts: `6523` bars, low breakouts: `6369` bars (~2.56% / 2.49% of dataset).

### Channel = 160

| H | state | n | avg_pips | med_pips | hit_pct |
|---|---|---|---|---|---|
| 1 | low_breakout | 4354 | 0.41 | 0.30 | 55.7 |
| 1 | inside | 246264 | -0.01 | 0.00 | 48.0 |
| 1 | high_breakout | 4507 | -0.17 | -0.20 | 44.8 |
| 3 | low_breakout | 4354 | 0.66 | 0.60 | 57.1 |
| 3 | inside | 246262 | -0.01 | 0.00 | 49.0 |
| 3 | high_breakout | 4507 | -0.27 | -0.40 | 44.0 |
| 5 | low_breakout | 4354 | 0.66 | 0.60 | 56.3 |
| 5 | inside | 246260 | -0.02 | 0.00 | 49.3 |
| 5 | high_breakout | 4507 | -0.32 | -0.50 | 43.1 |
| 10 | low_breakout | 4354 | 0.75 | 0.70 | 54.5 |
| 10 | inside | 246256 | -0.03 | 0.00 | 49.2 |
| 10 | high_breakout | 4506 | -0.32 | -0.60 | 45.1 |
| 20 | low_breakout | 4354 | 0.80 | 0.70 | 54.0 |
| 20 | inside | 246246 | -0.05 | 0.00 | 49.3 |
| 20 | high_breakout | 4506 | -0.43 | -0.80 | 45.2 |
| 40 | low_breakout | 4354 | 0.82 | 0.50 | 51.7 |
| 40 | inside | 246227 | -0.09 | -0.10 | 49.1 |
| 40 | high_breakout | 4505 | -0.56 | -0.80 | 46.4 |
| 80 | low_breakout | 4354 | 1.35 | 0.80 | 52.4 |
| 80 | inside | 246188 | -0.17 | -0.20 | 49.2 |
| 80 | high_breakout | 4504 | -1.42 | -2.00 | 44.2 |

High breakouts: `4507` bars, low breakouts: `4354` bars (~1.77% / 1.71% of dataset).
