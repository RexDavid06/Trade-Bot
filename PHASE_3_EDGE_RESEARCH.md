# PHASE 3 — MARKET EXPANSION / EDGE SEARCH

Research only · DEV split only · no validation/holdout · no strategy, no backtest, no optimization.

Built on the preserved 60/20/20 split; all numbers are raw market behavior in pips unless stated.

## 1. Research objective


Find market behaviors, time horizons, instruments or structural conditions in the currently available historical data whose **raw movement** is large and repeatable enough to plausibly survive realistic round-turn transaction costs.  This is edge search, not strategy construction.

Frozen design (no sweeps): a small economically motivated set of horizons H = {5, 20, 80, 240} bars (~25 min / ~1.7 h / ~6.7 h / ~20 h), momentum windows W = {5, 20, 80}, an ATR(14) regime split (low/normal/high, causal 33/67 quantiles on 50 bars), vanilla session definitions, a prior-20 channel, and per-pair cost = 2×median dev spread + 1.7 pips.

## 2. Dataset inventory


Available source files: four consolidated M5 composites (`data/{eurgbp,eurjpy,eurusd,gbpusd}_m5.csv`) plus the original monthly bid/ask export fragments they were built from.  No new external data is added.

| symbol | tf | bars | first | last | spread_distinct | zero% | spread pips p10 | med | p90 | step!=5min% | dup_ts | dev | val | hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | M5 | 422,225 | 2021-01-03 22:00:00 | 2026-09-09 23:55:00 | 179 | 0.0 | 0.20 | 0.30 | 0.60 | 0.10 | 0 | 253335 | 84445 | 84445 |
| EURGBP | M5 | 425,477 | 2021-01-03 22:00:00 | 2026-09-09 23:55:00 | 322 | 0.0 | 0.60 | 0.90 | 1.50 | 0.10 | 0 | 255286 | 85096 | 85095 |
| GBPUSD | M5 | 374,746 | 2021-01-03 22:00:00 | 2026-09-09 23:55:00 | 306 | 0.0 | 0.60 | 0.90 | 1.40 | 0.13 | 0 | 224848 | 74949 | 74949 |
| EURJPY | M5 | 90,000 | 2025-06-26 03:00:00 | 2026-09-10 19:05:00 | 254 | 27.0 | 0.00 | 1.00 | 2.20 | 0.08 | 0 | 54000 | 18000 | 18000 |

Split counts confirm the preserved 60/20/20 allocation on each symbolized series.


## 3. Data-quality assessment


- **EURUSD / EURGBP / GBPUSD**: continuous 2021-01-03 → 2026-09-09 (5.7 years).  No duplicated timestamps; ~0.1% of consecutive steps differ from 5 min (weekend/session-break rollovers).  Spread column is varied (not constant), never zero for the non-JPY pairs; the p10/med/p90 rows above show narrow, realistic point spreads.  `real_volume` is all zeros (volume data unusable).

- **EURJPY** (degraded): composite covers only 2025-06-26 → 2026-09-10 (~14 months, 90,000 bars), 27% of bars carry a zero spread value.  Spread values look synthesized, not live ticks.  EURJPY is flagged as unreliable and is **excluded from all behaviour tables**; it appears only in the inventory and pair comparison, where it is marked accordingly.

- **Spread semantics**: the `spread` column is best treated as a modeled per-bar spread (many distinct values, plausible range) rather than a live-tick feed.  Costs are therefore estimated from the observed median of this column; real execution costs could differ, and are not claimed.

- **Outliers / bad ticks**: no explicit tick-level validation was performed beyond timestamp continuity; extreme spikes would inflate mean-based movement statistics, so the report reports medians alongside means.

## 4. Time-horizon behavior


Forward movement `close[i+H]−close[i]` (pips) and persistence by horizon, per core pair.  `cont 1-bar` = share where the H-forward move continues the direction of the previous 1-bar move; `cont H-bar` = share where it continues the direction of the previous H-bar move.  `rho1` = 1-bar return autocorrelation (persistence → sign; ≈ 0 → efficient; negative → 1-bar reversal).


### EURUSD  (dev bars 253,335, 1-bar autocorr $\rho_1$ = -0.021)

| symbol | H bars | n | mean_pips | med | std | p_pos% | cont1% | contH% |
|---|---|---|---|---|---|---|---|---|
| EURUSD | 5 | 253,330 | -0.03 | 0.00 | 6.96 | 49.5 | 49.0 | 48.8 |
| EURUSD | 20 | 253,315 | -0.11 | 0.00 | 13.74 | 49.9 | 49.4 | 49.1 |
| EURUSD | 80 | 253,255 | -0.44 | -0.10 | 27.46 | 49.7 | 49.9 | 49.4 |
| EURUSD | 240 | 253,095 | -1.33 | -0.70 | 46.75 | 49.2 | 49.8 | - |

### EURGBP  (dev bars 255,286, 1-bar autocorr $\rho_1$ = -0.065)

| symbol | H bars | n | mean_pips | med | std | p_pos% | cont1% | contH% |
|---|---|---|---|---|---|---|---|---|
| EURGBP | 5 | 255,281 | -0.01 | 0.00 | 4.57 | 49.3 | 47.9 | 47.7 |
| EURGBP | 20 | 255,266 | -0.03 | 0.00 | 8.81 | 49.4 | 48.7 | 47.7 |
| EURGBP | 80 | 255,206 | -0.14 | -0.20 | 17.42 | 49.2 | 49.3 | 48.1 |
| EURGBP | 240 | 255,046 | -0.45 | -1.30 | 29.23 | 47.6 | 49.6 | - |

### GBPUSD  (dev bars 224,848, 1-bar autocorr $\rho_1$ = -0.022)

| symbol | H bars | n | mean_pips | med | std | p_pos% | cont1% | contH% |
|---|---|---|---|---|---|---|---|---|
| GBPUSD | 5 | 224,843 | -0.02 | 0.00 | 10.21 | 49.7 | 48.8 | 48.6 |
| GBPUSD | 20 | 224,828 | -0.08 | 0.00 | 20.13 | 49.9 | 49.4 | 48.8 |
| GBPUSD | 80 | 224,768 | -0.32 | 0.00 | 40.48 | 50.0 | 49.8 | 48.9 |
| GBPUSD | 240 | 224,608 | -0.94 | 0.00 | 68.84 | 50.0 | 49.7 | - |

## 5. Trend / momentum behavior


Prior change over W bars split **strong** vs **weak** by the symbol median |prior change| (a single fixed cut).  `up` = positive prior move (long side if momentum), `dn` = negative.  Reported values are the raw H-forward return in pips and the continuation hit (share where the forward move keeps the prior direction).


### EURUSD

| symbol | W | H | side | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|---|
| EURUSD | 5 | 5 | up | 63,055 | -0.15 | -0.20 | 48.3 | 47.9 |
| EURUSD | 5 | 5 | dn | 63,499 | 0.12 | 0.20 | 48.4 | 51.2 |
| EURUSD | 5 | 20 | up | 63,046 | -0.36 | -0.30 | 48.6 | 48.4 |
| EURUSD | 5 | 20 | dn | 63,499 | 0.11 | 0.20 | 49.0 | 50.8 |
| EURUSD | 5 | 80 | up | 63,043 | -0.73 | -0.60 | 48.8 | 48.7 |
| EURUSD | 5 | 80 | dn | 63,488 | -0.24 | 0.00 | 50.0 | 49.9 |
| EURUSD | 20 | 5 | up | 62,344 | -0.10 | -0.20 | 48.1 | 47.7 |
| EURUSD | 20 | 5 | dn | 63,771 | 0.06 | 0.20 | 48.2 | 51.4 |
| EURUSD | 20 | 20 | up | 62,334 | -0.29 | -0.30 | 48.6 | 48.4 |
| EURUSD | 20 | 20 | dn | 63,771 | 0.11 | 0.30 | 48.8 | 51.0 |
| EURUSD | 20 | 80 | up | 62,334 | -0.81 | -0.60 | 48.8 | 48.7 |
| EURUSD | 20 | 80 | dn | 63,766 | -0.14 | 0.10 | 49.7 | 50.2 |
| EURUSD | 80 | 5 | up | 61,353 | -0.08 | -0.10 | 49.1 | 48.6 |
| EURUSD | 80 | 5 | dn | 64,655 | -0.01 | 0.10 | 48.9 | 50.6 |
| EURUSD | 80 | 20 | up | 61,353 | -0.19 | -0.10 | 49.5 | 49.3 |
| EURUSD | 80 | 20 | dn | 64,655 | -0.10 | 0.10 | 49.3 | 50.4 |
| EURUSD | 80 | 80 | up | 61,353 | -0.70 | -0.20 | 49.5 | 49.3 |
| EURUSD | 80 | 80 | dn | 64,650 | -0.33 | -0.20 | 50.3 | 49.6 |

### EURGBP

| symbol | W | H | side | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|---|
| EURGBP | 5 | 5 | up | 61,759 | -0.22 | -0.20 | 46.9 | 46.3 |
| EURGBP | 5 | 5 | dn | 62,270 | 0.28 | 0.30 | 46.3 | 53.1 |
| EURGBP | 5 | 20 | up | 61,753 | -0.28 | -0.40 | 47.5 | 47.2 |
| EURGBP | 5 | 20 | dn | 62,265 | 0.32 | 0.40 | 47.2 | 52.5 |
| EURGBP | 5 | 80 | up | 61,737 | -0.75 | -0.90 | 47.1 | 46.9 |
| EURGBP | 5 | 80 | dn | 62,251 | 0.13 | 0.10 | 49.6 | 50.2 |
| EURGBP | 20 | 5 | up | 62,511 | -0.16 | -0.20 | 47.3 | 46.7 |
| EURGBP | 20 | 5 | dn | 64,275 | 0.20 | 0.20 | 47.1 | 52.3 |
| EURGBP | 20 | 20 | up | 62,505 | -0.36 | -0.50 | 46.6 | 46.3 |
| EURGBP | 20 | 20 | dn | 64,274 | 0.26 | 0.40 | 47.6 | 52.0 |
| EURGBP | 20 | 80 | up | 62,491 | -1.00 | -1.00 | 46.8 | 46.6 |
| EURGBP | 20 | 80 | dn | 64,273 | 0.41 | 0.20 | 49.2 | 50.7 |
| EURGBP | 80 | 5 | up | 61,379 | -0.13 | -0.10 | 48.2 | 47.6 |
| EURGBP | 80 | 5 | dn | 65,881 | 0.12 | 0.10 | 48.5 | 50.8 |
| EURGBP | 80 | 20 | up | 61,374 | -0.30 | -0.40 | 47.5 | 47.2 |
| EURGBP | 80 | 20 | dn | 65,881 | 0.24 | 0.20 | 48.8 | 50.8 |
| EURGBP | 80 | 80 | up | 61,370 | -0.99 | -1.00 | 46.6 | 46.4 |
| EURGBP | 80 | 80 | dn | 65,881 | 0.71 | 0.50 | 47.9 | 51.9 |

### GBPUSD

| symbol | W | H | side | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|---|
| GBPUSD | 5 | 5 | up | 55,906 | -0.14 | -0.20 | 48.6 | 48.3 |
| GBPUSD | 5 | 5 | dn | 56,030 | 0.28 | 0.40 | 47.7 | 52.0 |
| GBPUSD | 5 | 20 | up | 55,895 | -0.26 | -0.30 | 49.1 | 48.9 |
| GBPUSD | 5 | 20 | dn | 56,030 | 0.30 | 0.50 | 48.6 | 51.2 |
| GBPUSD | 5 | 80 | up | 55,880 | -0.48 | -0.20 | 49.6 | 49.6 |
| GBPUSD | 5 | 80 | dn | 55,997 | 0.07 | 0.30 | 49.6 | 50.4 |
| GBPUSD | 20 | 5 | up | 55,821 | -0.14 | -0.20 | 48.6 | 48.3 |
| GBPUSD | 20 | 5 | dn | 56,423 | 0.13 | 0.30 | 48.3 | 51.4 |
| GBPUSD | 20 | 20 | up | 55,818 | -0.32 | -0.50 | 48.7 | 48.5 |
| GBPUSD | 20 | 20 | dn | 56,415 | 0.42 | 0.40 | 48.7 | 51.2 |
| GBPUSD | 20 | 80 | up | 55,806 | -0.65 | -0.30 | 49.6 | 49.5 |
| GBPUSD | 20 | 80 | dn | 56,379 | 0.63 | 0.80 | 49.0 | 50.9 |
| GBPUSD | 80 | 5 | up | 55,876 | -0.15 | -0.10 | 49.1 | 48.7 |
| GBPUSD | 80 | 5 | dn | 56,426 | 0.08 | 0.20 | 48.8 | 50.8 |
| GBPUSD | 80 | 20 | up | 55,876 | -0.32 | -0.20 | 49.2 | 49.0 |
| GBPUSD | 80 | 20 | dn | 56,412 | 0.31 | 0.40 | 48.7 | 51.1 |
| GBPUSD | 80 | 80 | up | 55,875 | -0.75 | -0.60 | 49.0 | 49.0 |
| GBPUSD | 80 | 80 | dn | 56,383 | 0.78 | 1.30 | 48.1 | 51.8 |

## 6. Volatility-regime behavior


ATR(14) regime (causal 33/67 quantiles over 50 bars): `low`/`normal`/`high`.  `event` = a transition into the state.  `cont%` = share where the H-forward move continues the previous 1-bar direction; `rev%` = share where it reverses it (100−cont% roughly).  Comparing the two after expansion tells whether the move after a volatility expansion is directional or mean-reverting.


### EURUSD

| symbol | state | H | n | mean_pips | med_pips | cont% | rev% |
|---|---|---|---|---|---|---|---|
| EURUSD | low | 5 | 115,295 | -0.07 | 0.00 | 48.8 | 51.2 |
| EURUSD | low | 20 | 115,295 | -0.18 | 0.00 | 49.0 | 51.0 |
| EURUSD | low | 80 | 115,269 | -0.59 | 0.00 | 49.8 | 50.2 |
| EURUSD | normal | 5 | 44,468 | -0.05 | 0.00 | 48.9 | 51.1 |
| EURUSD | normal | 20 | 44,468 | -0.14 | -0.10 | 50.0 | 50.0 |
| EURUSD | normal | 80 | 44,456 | -0.62 | -0.20 | 49.8 | 50.2 |
| EURUSD | high | 5 | 93,567 | 0.04 | 0.00 | 49.3 | 50.7 |
| EURUSD | high | 20 | 93,552 | -0.01 | 0.10 | 49.6 | 50.4 |
| EURUSD | high | 80 | 93,530 | -0.17 | -0.20 | 50.1 | 49.9 |
| EURUSD | expansion | 5 | 5,319 | 0.05 | 0.00 | 47.8 | 52.2 |
| EURUSD | expansion | 20 | 5,319 | 0.08 | 0.20 | 48.7 | 51.3 |
| EURUSD | expansion | 80 | 5,318 | -1.38 | -1.50 | 48.7 | 51.3 |
| EURUSD | contraction | 5 | 5,409 | -0.02 | 0.00 | 49.0 | 51.0 |
| EURUSD | contraction | 20 | 5,409 | -0.24 | -0.20 | 49.1 | 50.9 |
| EURUSD | contraction | 80 | 5,408 | -0.81 | -0.50 | 49.6 | 50.4 |

### EURGBP

| symbol | state | H | n | mean_pips | med_pips | cont% | rev% |
|---|---|---|---|---|---|---|---|
| EURGBP | low | 5 | 121,577 | -0.11 | 0.00 | 47.8 | 52.2 |
| EURGBP | low | 20 | 121,577 | -0.18 | -0.20 | 48.6 | 51.4 |
| EURGBP | low | 80 | 121,550 | -0.05 | -0.10 | 49.5 | 50.5 |
| EURGBP | normal | 5 | 46,802 | 0.07 | 0.00 | 47.6 | 52.4 |
| EURGBP | normal | 20 | 46,802 | 0.11 | 0.10 | 48.5 | 51.5 |
| EURGBP | normal | 80 | 46,789 | -0.30 | -0.20 | 49.0 | 51.0 |
| EURGBP | high | 5 | 86,902 | 0.10 | 0.10 | 48.1 | 51.9 |
| EURGBP | high | 20 | 86,887 | 0.10 | 0.20 | 49.0 | 51.0 |
| EURGBP | high | 80 | 86,867 | -0.18 | -0.40 | 49.2 | 50.8 |
| EURGBP | expansion | 5 | 5,995 | 0.40 | 0.20 | 45.5 | 54.5 |
| EURGBP | expansion | 20 | 5,995 | 0.59 | 0.60 | 46.0 | 54.0 |
| EURGBP | expansion | 80 | 5,992 | 0.09 | -0.10 | 47.3 | 52.7 |
| EURGBP | contraction | 5 | 6,669 | -0.03 | 0.00 | 48.5 | 51.5 |
| EURGBP | contraction | 20 | 6,669 | -0.02 | 0.00 | 50.1 | 49.9 |
| EURGBP | contraction | 80 | 6,665 | -0.14 | -0.20 | 50.0 | 50.0 |

### GBPUSD

| symbol | state | H | n | mean_pips | med_pips | cont% | rev% |
|---|---|---|---|---|---|---|---|
| GBPUSD | low | 5 | 102,946 | -0.09 | 0.00 | 48.6 | 51.4 |
| GBPUSD | low | 20 | 102,931 | -0.25 | 0.00 | 49.2 | 50.8 |
| GBPUSD | low | 80 | 102,914 | -0.50 | -0.10 | 49.8 | 50.2 |
| GBPUSD | normal | 5 | 40,311 | -0.09 | 0.00 | 48.9 | 51.1 |
| GBPUSD | normal | 20 | 40,311 | -0.13 | 0.00 | 49.2 | 50.8 |
| GBPUSD | normal | 80 | 40,297 | -0.23 | 0.40 | 49.9 | 50.1 |
| GBPUSD | high | 5 | 81,586 | 0.10 | 0.10 | 49.0 | 51.0 |
| GBPUSD | high | 20 | 81,586 | 0.16 | 0.20 | 49.7 | 50.3 |
| GBPUSD | high | 80 | 81,557 | -0.16 | 0.10 | 49.7 | 50.3 |
| GBPUSD | expansion | 5 | 4,977 | 0.09 | 0.00 | 48.8 | 51.2 |
| GBPUSD | expansion | 20 | 4,977 | 0.48 | 0.30 | 49.3 | 50.7 |
| GBPUSD | expansion | 80 | 4,975 | -0.57 | -0.40 | 48.1 | 51.9 |
| GBPUSD | contraction | 5 | 5,109 | 0.04 | 0.00 | 49.2 | 50.8 |
| GBPUSD | contraction | 20 | 5,109 | -0.18 | -0.10 | 50.0 | 50.0 |
| GBPUSD | contraction | 80 | 5,106 | -0.78 | 0.05 | 50.9 | 49.1 |

## 7. Session / market-open behavior


Per-session forward behavior (signal = bar in session) plus the **first 6 bars of each session block** (`London open`, `LondonNY open`, `NewYork open`, `Asian open`).  `range_ratio` = mean bar range in the open window / symbol median bar range; `cont%` = share where the H=5 forward move continues the opening bar's direction; `fwd5_mean` = average forward 5-bar move in the window.


### EURUSD

| symbol | session | H | n | mean_pips | med_pips | cont% |
|---|---|---|---|---|---|---|
| EURUSD | Asian | 5 | 73,999 | -0.03 | 0.00 | 49.3 |
| EURUSD | London | 5 | 52,760 | -0.11 | 0.00 | 49.4 |
| EURUSD | LondonNY | 5 | 42,192 | -0.02 | 0.00 | 49.6 |
| EURUSD | NewYork | 5 | 52,740 | -0.01 | 0.00 | 48.8 |
| EURUSD | OffHours | 5 | 31,639 | 0.09 | 0.10 | 47.0 |
| EURUSD | Asian | 20 | 73,992 | -0.02 | 0.00 | 49.7 |
| EURUSD | London | 20 | 52,752 | -0.55 | -0.20 | 49.4 |
| EURUSD | LondonNY | 20 | 42,192 | -0.06 | -0.30 | 50.1 |
| EURUSD | NewYork | 20 | 52,740 | 0.10 | 0.10 | 48.6 |
| EURUSD | OffHours | 20 | 31,639 | -0.01 | 0.30 | 48.7 |
| EURUSD | Asian | 80 | 73,932 | -0.55 | 0.00 | 50.0 |
| EURUSD | London | 80 | 52,752 | -1.52 | -1.90 | 50.2 |
| EURUSD | LondonNY | 80 | 42,192 | 0.19 | 0.00 | 49.9 |
| EURUSD | NewYork | 80 | 52,740 | 0.25 | 0.60 | 49.5 |
| EURUSD | OffHours | 80 | 31,639 | -0.38 | 0.00 | 49.7 |

Session opens (first 6 bars of each block):

| symbol | open | n_bars | range_ratio | fwd5_mean_pips | fwd5_med | cont_open% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURUSD | Asian open | 5,286 | 1.01 | -0.30 | -0.20 | 49.9 | 47.1 |
| EURUSD | London open | 5,286 | 1.79 | 0.32 | 0.40 | 50.4 | 52.0 |
| EURUSD | LondonNY open | 5,274 | 1.64 | -0.03 | 0.00 | 50.0 | 49.8 |
| EURUSD | NewYork open | 5,274 | 1.61 | -0.09 | 0.00 | 49.3 | 49.6 |

### EURGBP

| symbol | session | H | n | mean_pips | med_pips | cont% |
|---|---|---|---|---|---|---|
| EURGBP | Asian | 5 | 74,587 | 0.03 | 0.00 | 48.0 |
| EURGBP | London | 5 | 53,231 | -0.04 | -0.10 | 48.9 |
| EURGBP | LondonNY | 5 | 42,563 | -0.02 | -0.10 | 48.6 |
| EURGBP | NewYork | 5 | 53,159 | -0.22 | -0.10 | 47.7 |
| EURGBP | OffHours | 5 | 31,741 | 0.32 | 0.30 | 45.2 |
| EURGBP | Asian | 20 | 74,587 | 0.10 | 0.10 | 49.1 |
| EURGBP | London | 20 | 53,231 | -0.10 | -0.20 | 49.3 |
| EURGBP | LondonNY | 20 | 42,548 | -0.22 | -0.40 | 49.4 |
| EURGBP | NewYork | 20 | 53,159 | -0.60 | -0.50 | 47.9 |
| EURGBP | OffHours | 20 | 31,741 | 0.95 | 0.80 | 47.4 |
| EURGBP | Asian | 80 | 74,587 | 0.23 | -0.10 | 49.4 |
| EURGBP | London | 80 | 53,191 | -0.61 | -1.10 | 49.6 |
| EURGBP | LondonNY | 80 | 42,528 | -1.36 | -1.65 | 49.8 |
| EURGBP | NewYork | 80 | 53,159 | -0.07 | 0.00 | 49.0 |
| EURGBP | OffHours | 80 | 31,741 | 1.29 | 1.00 | 48.4 |

Session opens (first 6 bars of each block):

| symbol | open | n_bars | range_ratio | fwd5_mean_pips | fwd5_med | cont_open% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURGBP | Asian open | 5,328 | 0.82 | 0.09 | 0.00 | 48.7 | 49.4 |
| EURGBP | London open | 5,328 | 1.86 | 0.10 | 0.10 | 49.0 | 50.6 |
| EURGBP | LondonNY open | 5,322 | 1.78 | 0.25 | 0.20 | 48.7 | 51.2 |
| EURGBP | NewYork open | 5,316 | 1.50 | -0.17 | -0.20 | 48.5 | 47.4 |

### GBPUSD

| symbol | session | H | n | mean_pips | med_pips | cont% |
|---|---|---|---|---|---|---|
| GBPUSD | Asian | 5 | 65,688 | -0.08 | 0.00 | 49.1 |
| GBPUSD | London | 5 | 46,920 | -0.09 | 0.00 | 49.6 |
| GBPUSD | LondonNY | 5 | 37,536 | 0.06 | 0.00 | 48.8 |
| GBPUSD | NewYork | 5 | 46,883 | -0.03 | -0.10 | 48.9 |
| GBPUSD | OffHours | 5 | 27,816 | 0.14 | 0.20 | 46.7 |
| GBPUSD | Asian | 20 | 65,688 | -0.18 | -0.10 | 49.8 |
| GBPUSD | London | 20 | 46,920 | -0.48 | -0.20 | 49.7 |
| GBPUSD | LondonNY | 20 | 37,536 | 0.45 | 0.30 | 49.9 |
| GBPUSD | NewYork | 20 | 46,868 | 0.01 | -0.10 | 48.8 |
| GBPUSD | OffHours | 20 | 27,816 | -0.03 | 0.70 | 48.1 |
| GBPUSD | Asian | 80 | 65,688 | -1.10 | -0.30 | 49.7 |
| GBPUSD | London | 80 | 46,918 | -0.15 | 0.10 | 50.1 |
| GBPUSD | LondonNY | 80 | 37,488 | 0.96 | 0.55 | 50.0 |
| GBPUSD | NewYork | 80 | 46,858 | 0.05 | 0.30 | 49.6 |
| GBPUSD | OffHours | 80 | 27,816 | -1.16 | -0.50 | 49.2 |

Session opens (first 6 bars of each block):

| symbol | open | n_bars | range_ratio | fwd5_mean_pips | fwd5_med | cont_open% | p_pos% |
|---|---|---|---|---|---|---|---|
| GBPUSD | Asian open | 4,692 | 0.96 | -0.55 | -0.40 | 50.2 | 46.4 |
| GBPUSD | London open | 4,692 | 1.80 | 0.12 | 0.10 | 49.9 | 50.4 |
| GBPUSD | LondonNY open | 4,692 | 1.67 | -0.28 | -0.30 | 49.0 | 48.4 |
| GBPUSD | NewYork open | 4,692 | 1.54 | 0.15 | 0.30 | 50.5 | 51.3 |

## 8. Range / breakout structure


Channel = prior-20 high/low (causal).  `state` = up-break (close above prior-20 high), dn-break (close below prior-20 low), inside.  `cont%` = share where the H-forward move continues the break direction (breakout continuation); `persist%` = share where close[i+H] still sits beyond the broken level.  `range_exp` = bar range above its causal rolling median.


### EURUSD

| symbol | state | H | n | mean_pips | med_pips | cont% | persist% |
|---|---|---|---|---|---|---|---|
| EURUSD | up-break | 5 | 28,046 | -0.23 | -0.30 | 47.0 | 60.3 |
| EURUSD | up-break | 20 | 28,040 | -0.42 | -0.40 | 48.2 | 55.1 |
| EURUSD | up-break | 80 | 28,037 | -0.88 | -0.60 | 48.6 | 52.0 |
| EURUSD | dn-break | 5 | 27,820 | 0.23 | 0.30 | 46.9 | 60.0 |
| EURUSD | dn-break | 20 | 27,820 | 0.27 | 0.50 | 47.8 | 55.0 |
| EURUSD | dn-break | 80 | 27,812 | -0.26 | 0.10 | 49.7 | 53.3 |
| EURUSD | inside | 5 | 197,444 | -0.03 | 0.00 | 49.6 | - |
| EURUSD | inside | 20 | 197,435 | -0.12 | 0.00 | 49.8 | - |
| EURUSD | inside | 80 | 197,386 | -0.41 | 0.00 | 50.1 | - |

Range expansion (bar range > causal rolling median):

| symbol | condition | H | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURUSD | range_exp | 5 | 122,215 | 0.02 | 0.00 | 48.7 | 49.9 |
| EURUSD | range_exp | 20 | 122,200 | -0.05 | 0.00 | 49.2 | 50.0 |

### EURGBP

| symbol | state | H | n | mean_pips | med_pips | cont% | persist% |
|---|---|---|---|---|---|---|---|
| EURGBP | up-break | 5 | 26,983 | -0.34 | -0.40 | 44.2 | 57.7 |
| EURGBP | up-break | 20 | 26,979 | -0.48 | -0.60 | 45.5 | 52.4 |
| EURGBP | up-break | 80 | 26,973 | -0.76 | -0.90 | 46.9 | 50.5 |
| EURGBP | dn-break | 5 | 27,057 | 0.36 | 0.30 | 45.3 | 59.0 |
| EURGBP | dn-break | 20 | 27,054 | 0.43 | 0.50 | 45.9 | 53.4 |
| EURGBP | dn-break | 80 | 27,052 | 0.69 | 0.60 | 47.8 | 52.1 |
| EURGBP | inside | 5 | 201,221 | -0.01 | 0.00 | 48.8 | - |
| EURGBP | inside | 20 | 201,213 | -0.04 | 0.00 | 49.6 | - |
| EURGBP | inside | 80 | 201,161 | -0.17 | -0.20 | 49.9 | - |

Range expansion (bar range > causal rolling median):

| symbol | condition | H | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURGBP | range_exp | 5 | 120,456 | 0.05 | 0.00 | 47.3 | 49.9 |
| EURGBP | range_exp | 20 | 120,445 | 0.07 | 0.10 | 48.3 | 50.6 |

### GBPUSD

| symbol | state | H | n | mean_pips | med_pips | cont% | persist% |
|---|---|---|---|---|---|---|---|
| GBPUSD | up-break | 5 | 25,194 | -0.32 | -0.30 | 47.7 | 60.7 |
| GBPUSD | up-break | 20 | 25,190 | -0.77 | -0.70 | 47.5 | 54.5 |
| GBPUSD | up-break | 80 | 25,189 | -1.07 | -0.70 | 49.0 | 52.3 |
| GBPUSD | dn-break | 5 | 24,984 | 0.35 | 0.50 | 46.8 | 60.1 |
| GBPUSD | dn-break | 20 | 24,984 | 0.38 | 0.60 | 47.8 | 54.7 |
| GBPUSD | dn-break | 80 | 24,968 | 0.04 | 0.40 | 49.4 | 52.9 |
| GBPUSD | inside | 5 | 174,645 | -0.03 | 0.00 | 49.3 | - |
| GBPUSD | inside | 20 | 174,634 | -0.05 | 0.00 | 49.9 | - |
| GBPUSD | inside | 80 | 174,591 | -0.27 | 0.10 | 49.9 | - |

Range expansion (bar range > causal rolling median):

| symbol | condition | H | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| GBPUSD | range_exp | 5 | 109,249 | -0.01 | 0.00 | 48.4 | 49.9 |
| GBPUSD | range_exp | 20 | 109,247 | -0.02 | 0.10 | 49.0 | 50.1 |

## 9. Pair comparison


All four pairs (EURJPY flagged unreliable).  `med|ret1|` = median 1-bar |move| in pips; `med_range`, `med_atr` in pips; `spread_med` in pips; `cost` = 2×spread_med + 1.7 pips; `rho1` = 1-bar autocorrelation; `cont20` = share of H=20 moves that continue the previous 20-bar direction (trend persistence); `rev5` = share of H=5 moves reversing the previous 1-bar move; `max_dir20` = max |mean| H=20 forward move in either direction (raw directional magnitude); `mov/cost` = med|ret1|/cost; `edge/cost` = max_dir20/cost.

| symbol | med|ret1| | med_range | med_atr | spread_med | cost | rho1 | cont20% | rev5% | max_dir20 | mov/cost | edge/cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 1.30 | 3.00 | 3.34 | 0.30 | 2.30 | -0.02 | 49.1 | 51.0 | 0.23 | 0.57 | 0.10 |
| EURGBP | 0.90 | 2.10 | 2.35 | 0.90 | 3.50 | -0.07 | 47.7 | 52.1 | 0.26 | 0.26 | 0.07 |
| GBPUSD | 1.80 | 4.20 | 4.64 | 0.90 | 3.50 | -0.02 | 48.8 | 51.2 | 0.34 | 0.51 | 0.10 |
| EURJPY | 2.20 | 5.40 | 5.94 | 2.00 | 5.70 | -0.06 | 48.7 | 51.6 | 0.67 | 0.39 | 0.12 |

## 10. Signal-to-cost analysis


For every behavior/condition/horizon with n ≥ 1000 (see below) the raw mean movement is divided by the pair's realistic round-trip cost.  This is the raw `movement-to-cost` ratio.  Each row below is a distinct behavior/horizon/pair.  Behaviors with ratio ≥ 1.0 are those whose raw expected move could plausibly clear costs if the edge direction were known (this does not make them tradable).

| sym | behavior | condition | H_min | n | mean | med | hit% | std | cost | ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | session | London H=80 | 400 | 52,752 | -1.52 | -1.90 | 47.3 | 37.72 | 2.30 | 0.66 |
| EURUSD | volatility | expansion_event H=80 | 400 | 5,318 | -1.38 | -1.50 | 47.5 | 30.47 | 2.30 | 0.60 |
| EURGBP | session | LondonNY H=80 | 400 | 42,528 | -1.36 | -1.65 | 44.8 | 16.48 | 3.50 | 0.39 |
| EURUSD | breakout | up-break H=80 | 400 | 28,037 | -0.88 | -0.60 | 48.5 | 27.78 | 2.30 | 0.38 |
| EURGBP | session | OffHours H=80 | 400 | 31,741 | 1.29 | 1.00 | 56.1 | 10.41 | 3.50 | 0.37 |
| EURUSD | volatility | contraction_event H=80 | 400 | 5,408 | -0.81 | -0.50 | 48.5 | 28.48 | 2.30 | 0.35 |
| EURUSD | momentum | W=20 H=80 strong-up | 400 | 62,334 | -0.81 | -0.60 | 48.7 | 30.23 | 2.30 | 0.35 |
| GBPUSD | session | OffHours H=80 | 400 | 27,816 | -1.16 | -0.50 | 48.9 | 40.07 | 3.50 | 0.33 |
| EURUSD | momentum | W=5 H=80 strong-up | 400 | 63,043 | -0.73 | -0.60 | 48.7 | 30.33 | 2.30 | 0.32 |
| GBPUSD | session | Asian H=80 | 400 | 65,688 | -1.10 | -0.30 | 49.6 | 35.72 | 3.50 | 0.31 |
| GBPUSD | breakout | up-break H=80 | 400 | 25,189 | -1.07 | -0.70 | 48.9 | 41.66 | 3.50 | 0.30 |
| EURUSD | momentum | W=80 H=80 strong-up | 400 | 61,353 | -0.70 | -0.20 | 49.3 | 28.93 | 2.30 | 0.30 |
| EURGBP | momentum | W=20 H=80 strong-up | 400 | 62,491 | -1.00 | -1.00 | 46.6 | 20.08 | 3.50 | 0.29 |
| EURGBP | momentum | W=80 H=80 strong-up | 400 | 61,370 | -0.99 | -1.00 | 46.4 | 21.09 | 3.50 | 0.28 |
| GBPUSD | session | LondonNY H=80 | 400 | 37,488 | 0.96 | 0.55 | 50.6 | 41.02 | 3.50 | 0.27 |
| EURGBP | session | OffHours H=20 | 100 | 31,741 | 0.95 | 0.80 | 59.5 | 5.78 | 3.50 | 0.27 |
| EURUSD | volatility | normal H=80 | 400 | 44,456 | -0.62 | -0.20 | 49.5 | 28.58 | 2.30 | 0.27 |
| EURUSD | volatility | low H=80 | 400 | 115,269 | -0.59 | 0.00 | 49.9 | 22.93 | 2.30 | 0.26 |
| EURUSD | session | Asian H=80 | 400 | 73,932 | -0.55 | 0.00 | 49.8 | 26.33 | 2.30 | 0.24 |
| EURUSD | session | London H=20 | 100 | 52,752 | -0.55 | -0.20 | 49.1 | 16.05 | 2.30 | 0.24 |
| GBPUSD | momentum | W=80 H=80 strong-dn | 400 | 56,383 | 0.78 | 1.30 | 51.8 | 45.71 | 3.50 | 0.22 |
| GBPUSD | volatility | contraction_event H=80 | 400 | 5,106 | -0.78 | 0.05 | 50.0 | 38.88 | 3.50 | 0.22 |
| GBPUSD | breakout | up-break H=20 | 100 | 25,190 | -0.77 | -0.70 | 47.3 | 21.41 | 3.50 | 0.22 |
| EURGBP | breakout | up-break H=80 | 400 | 26,973 | -0.76 | -0.90 | 46.7 | 18.49 | 3.50 | 0.22 |
| GBPUSD | momentum | W=80 H=80 strong-up | 400 | 55,875 | -0.75 | -0.60 | 49.0 | 40.17 | 3.50 | 0.21 |
| EURGBP | momentum | W=5 H=80 strong-up | 400 | 61,737 | -0.75 | -0.90 | 46.9 | 19.84 | 3.50 | 0.21 |
| EURGBP | momentum | W=80 H=80 strong-dn | 400 | 65,881 | 0.71 | 0.50 | 51.9 | 17.02 | 3.50 | 0.20 |
| EURGBP | breakout | dn-break H=80 | 400 | 27,052 | 0.69 | 0.60 | 52.0 | 18.09 | 3.50 | 0.20 |
| GBPUSD | momentum | W=20 H=80 strong-up | 400 | 55,806 | -0.65 | -0.30 | 49.5 | 43.24 | 3.50 | 0.19 |
| EURUSD | breakout | up-break H=20 | 100 | 28,040 | -0.42 | -0.40 | 47.9 | 14.51 | 2.30 | 0.18 |
| GBPUSD | momentum | W=20 H=80 strong-dn | 400 | 56,379 | 0.63 | 0.80 | 50.9 | 43.26 | 3.50 | 0.18 |
| EURUSD | breakout | inside H=80 | 400 | 197,386 | -0.41 | 0.00 | 49.8 | 27.30 | 2.30 | 0.18 |
| EURGBP | session | London H=80 | 400 | 53,191 | -0.61 | -1.10 | 47.4 | 23.32 | 3.50 | 0.17 |
| EURGBP | session | NewYork H=20 | 100 | 53,159 | -0.60 | -0.50 | 43.7 | 5.89 | 3.50 | 0.17 |
| EURGBP | volatility | expansion_event H=20 | 100 | 5,995 | 0.59 | 0.60 | 53.1 | 10.61 | 3.50 | 0.17 |
| EURUSD | session | OffHours H=80 | 400 | 31,639 | -0.38 | 0.00 | 49.8 | 15.69 | 2.30 | 0.17 |
| GBPUSD | volatility | expansion_event H=80 | 400 | 4,975 | -0.57 | -0.40 | 49.5 | 40.47 | 3.50 | 0.16 |
| EURUSD | momentum | W=5 H=20 strong-up | 100 | 63,046 | -0.36 | -0.30 | 48.4 | 15.90 | 2.30 | 0.16 |
| GBPUSD | session_open | Asian-open window | 25 | 4,692 | -0.55 | -0.40 | 46.4 | 6.35 | 3.50 | 0.16 |
| GBPUSD | volatility | low H=80 | 400 | 102,914 | -0.50 | -0.10 | 49.7 | 37.75 | 3.50 | 0.14 |
| EURUSD | momentum | W=80 H=80 strong-dn | 400 | 64,650 | -0.33 | -0.20 | 49.6 | 29.05 | 2.30 | 0.14 |
| EURUSD | session_open | London-open window | 25 | 5,286 | 0.32 | 0.40 | 52.0 | 9.03 | 2.30 | 0.14 |
| GBPUSD | session | London H=20 | 100 | 46,920 | -0.48 | -0.20 | 49.3 | 22.79 | 3.50 | 0.14 |
| GBPUSD | volatility | expansion_event H=20 | 100 | 4,977 | 0.48 | 0.30 | 50.7 | 21.47 | 3.50 | 0.14 |
| EURGBP | breakout | up-break H=20 | 100 | 26,979 | -0.48 | -0.60 | 45.1 | 9.44 | 3.50 | 0.14 |
| GBPUSD | momentum | W=5 H=80 strong-up | 400 | 55,880 | -0.48 | -0.20 | 49.6 | 44.27 | 3.50 | 0.14 |
| EURUSD | session_open | Asian-open window | 25 | 5,286 | -0.30 | -0.20 | 47.1 | 4.68 | 2.30 | 0.13 |
| GBPUSD | session | LondonNY H=20 | 100 | 37,536 | 0.45 | 0.30 | 50.4 | 27.14 | 3.50 | 0.13 |
| EURUSD | momentum | W=20 H=20 strong-up | 100 | 62,334 | -0.29 | -0.30 | 48.4 | 16.15 | 2.30 | 0.13 |
| EURGBP | breakout | dn-break H=20 | 100 | 27,054 | 0.43 | 0.50 | 53.6 | 9.23 | 3.50 | 0.12 |
| GBPUSD | momentum | W=20 H=20 strong-dn | 100 | 56,415 | 0.42 | 0.40 | 51.2 | 21.55 | 3.50 | 0.12 |
| EURGBP | momentum | W=20 H=80 strong-dn | 400 | 64,273 | 0.41 | 0.20 | 50.7 | 19.06 | 3.50 | 0.12 |
| EURUSD | breakout | dn-break H=20 | 100 | 27,820 | 0.27 | 0.50 | 52.0 | 14.22 | 2.30 | 0.12 |
| EURUSD | breakout | dn-break H=80 | 400 | 27,812 | -0.26 | 0.10 | 50.1 | 28.22 | 2.30 | 0.11 |
| EURGBP | volatility | expansion_event H=5 | 25 | 5,995 | 0.40 | 0.20 | 51.5 | 5.95 | 3.50 | 0.11 |
| EURUSD | session | NewYork H=80 | 400 | 52,740 | 0.25 | 0.60 | 51.8 | 17.69 | 2.30 | 0.11 |
| GBPUSD | breakout | dn-break H=20 | 100 | 24,984 | 0.38 | 0.60 | 52.0 | 20.42 | 3.50 | 0.11 |
| EURUSD | momentum | W=5 H=80 strong-dn | 400 | 63,488 | -0.24 | 0.00 | 49.9 | 30.55 | 2.30 | 0.11 |
| EURUSD | volatility | contraction_event H=20 | 100 | 5,409 | -0.24 | -0.20 | 49.0 | 13.56 | 2.30 | 0.10 |
| EURGBP | momentum | W=20 H=20 strong-up | 100 | 62,505 | -0.36 | -0.50 | 46.3 | 10.76 | 3.50 | 0.10 |
| EURGBP | breakout | dn-break H=5 | 25 | 27,057 | 0.36 | 0.30 | 53.9 | 4.87 | 3.50 | 0.10 |
| EURUSD | breakout | up-break H=5 | 25 | 28,046 | -0.23 | -0.30 | 46.5 | 7.49 | 2.30 | 0.10 |
| GBPUSD | breakout | dn-break H=5 | 25 | 24,984 | 0.35 | 0.50 | 52.8 | 10.81 | 3.50 | 0.10 |
| EURUSD | breakout | dn-break H=5 | 25 | 27,820 | 0.23 | 0.30 | 52.6 | 7.22 | 2.30 | 0.10 |
| EURGBP | breakout | up-break H=5 | 25 | 26,983 | -0.34 | -0.40 | 43.5 | 4.97 | 3.50 | 0.10 |
| EURGBP | session | OffHours H=5 | 25 | 31,741 | 0.32 | 0.30 | 54.9 | 2.85 | 3.50 | 0.09 |
| GBPUSD | breakout | up-break H=5 | 25 | 25,194 | -0.32 | -0.30 | 47.3 | 11.36 | 3.50 | 0.09 |
| EURGBP | momentum | W=5 H=20 strong-dn | 100 | 62,265 | 0.32 | 0.40 | 52.5 | 10.32 | 3.50 | 0.09 |
| GBPUSD | momentum | W=80 H=20 strong-up | 100 | 55,876 | -0.32 | -0.20 | 49.0 | 21.73 | 3.50 | 0.09 |
| GBPUSD | momentum | W=20 H=20 strong-up | 100 | 55,818 | -0.32 | -0.50 | 48.5 | 22.38 | 3.50 | 0.09 |
| GBPUSD | momentum | W=80 H=20 strong-dn | 100 | 56,412 | 0.31 | 0.40 | 51.1 | 22.23 | 3.50 | 0.09 |
| GBPUSD | momentum | W=5 H=20 strong-dn | 100 | 56,030 | 0.30 | 0.50 | 51.2 | 22.53 | 3.50 | 0.09 |
| EURGBP | momentum | W=80 H=20 strong-up | 100 | 61,374 | -0.30 | -0.40 | 47.2 | 10.63 | 3.50 | 0.09 |
| EURGBP | volatility | normal H=80 | 400 | 46,789 | -0.30 | -0.20 | 49.2 | 17.22 | 3.50 | 0.09 |
| EURUSD | momentum | W=80 H=20 strong-up | 100 | 61,353 | -0.19 | -0.10 | 49.3 | 15.33 | 2.30 | 0.08 |
| EURGBP | momentum | W=5 H=5 strong-dn | 25 | 62,270 | 0.28 | 0.30 | 53.1 | 5.43 | 3.50 | 0.08 |
| EURUSD | session | LondonNY H=80 | 400 | 42,192 | 0.19 | 0.00 | 49.8 | 30.87 | 2.30 | 0.08 |
| GBPUSD | session_open | LondonNY-open window | 25 | 4,692 | -0.28 | -0.30 | 48.4 | 16.53 | 3.50 | 0.08 |
| GBPUSD | momentum | W=5 H=5 strong-dn | 25 | 56,030 | 0.28 | 0.40 | 52.0 | 11.71 | 3.50 | 0.08 |
| EURGBP | momentum | W=5 H=20 strong-up | 100 | 61,753 | -0.28 | -0.40 | 47.2 | 10.67 | 3.50 | 0.08 |
| GBPUSD | breakout | inside H=80 | 400 | 174,591 | -0.27 | 0.10 | 50.0 | 40.30 | 3.50 | 0.08 |
| EURUSD | volatility | low H=20 | 100 | 115,295 | -0.18 | 0.00 | 49.9 | 11.64 | 2.30 | 0.08 |
| EURGBP | momentum | W=20 H=20 strong-dn | 100 | 64,274 | 0.26 | 0.40 | 52.0 | 10.07 | 3.50 | 0.07 |
| GBPUSD | momentum | W=5 H=20 strong-up | 100 | 55,895 | -0.26 | -0.30 | 48.9 | 22.36 | 3.50 | 0.07 |
| GBPUSD | volatility | low H=20 | 100 | 102,931 | -0.25 | 0.00 | 49.6 | 19.00 | 3.50 | 0.07 |
| EURUSD | volatility | high H=80 | 400 | 93,530 | -0.17 | -0.20 | 49.5 | 31.70 | 2.30 | 0.07 |
| EURGBP | session_open | LondonNY-open window | 25 | 5,322 | 0.25 | 0.20 | 51.2 | 5.96 | 3.50 | 0.07 |
| EURGBP | momentum | W=80 H=20 strong-dn | 100 | 65,881 | 0.24 | 0.20 | 50.8 | 9.56 | 3.50 | 0.07 |
| EURGBP | session | Asian H=80 | 400 | 74,587 | 0.23 | -0.10 | 49.5 | 19.15 | 3.50 | 0.07 |
| GBPUSD | volatility | normal H=80 | 400 | 40,297 | -0.23 | 0.40 | 50.4 | 39.11 | 3.50 | 0.06 |
| EURUSD | momentum | W=5 H=5 strong-up | 25 | 63,055 | -0.15 | -0.20 | 47.9 | 8.24 | 2.30 | 0.06 |
| EURGBP | momentum | W=5 H=5 strong-up | 25 | 61,759 | -0.22 | -0.20 | 46.3 | 5.53 | 3.50 | 0.06 |
| EURGBP | session | NewYork H=5 | 25 | 53,159 | -0.22 | -0.10 | 47.0 | 3.48 | 3.50 | 0.06 |
| EURGBP | session | LondonNY H=20 | 100 | 42,548 | -0.22 | -0.40 | 47.9 | 11.24 | 3.50 | 0.06 |
| EURUSD | momentum | W=20 H=80 strong-dn | 400 | 63,766 | -0.14 | 0.10 | 50.2 | 30.16 | 2.30 | 0.06 |
| EURUSD | volatility | normal H=20 | 100 | 44,468 | -0.14 | -0.10 | 49.4 | 13.53 | 2.30 | 0.06 |
| EURGBP | momentum | W=20 H=5 strong-dn | 25 | 64,275 | 0.20 | 0.20 | 52.3 | 5.27 | 3.50 | 0.06 |
| EURGBP | volatility | low H=20 | 100 | 121,577 | -0.18 | -0.20 | 47.8 | 6.77 | 3.50 | 0.05 |
| GBPUSD | volatility | contraction_event H=20 | 100 | 5,109 | -0.18 | -0.10 | 49.2 | 20.14 | 3.50 | 0.05 |
| GBPUSD | session | Asian H=20 | 100 | 65,688 | -0.18 | -0.10 | 49.2 | 14.47 | 3.50 | 0.05 |
| EURUSD | breakout | inside H=20 | 100 | 197,435 | -0.12 | 0.00 | 49.9 | 13.56 | 2.30 | 0.05 |
| EURGBP | volatility | high H=80 | 400 | 86,867 | -0.18 | -0.40 | 48.8 | 20.88 | 3.50 | 0.05 |
| EURUSD | momentum | W=5 H=5 strong-dn | 25 | 63,499 | 0.12 | 0.20 | 51.2 | 8.12 | 2.30 | 0.05 |
| EURGBP | session_open | NewYork-open window | 25 | 5,316 | -0.17 | -0.20 | 47.4 | 4.53 | 3.50 | 0.05 |
| EURUSD | momentum | W=5 H=20 strong-dn | 100 | 63,499 | 0.11 | 0.20 | 50.8 | 15.66 | 2.30 | 0.05 |
| EURUSD | momentum | W=20 H=20 strong-dn | 100 | 63,771 | 0.11 | 0.30 | 51.0 | 15.32 | 2.30 | 0.05 |
| EURGBP | breakout | inside H=80 | 400 | 201,161 | -0.17 | -0.20 | 49.1 | 17.17 | 3.50 | 0.05 |
| EURUSD | session | London H=5 | 25 | 52,760 | -0.11 | 0.00 | 49.4 | 7.65 | 2.30 | 0.05 |
| GBPUSD | volatility | high H=20 | 100 | 81,586 | 0.16 | 0.20 | 50.4 | 21.49 | 3.50 | 0.05 |
| GBPUSD | volatility | high H=80 | 400 | 81,557 | -0.16 | 0.10 | 50.1 | 44.30 | 3.50 | 0.05 |
| EURGBP | momentum | W=20 H=5 strong-up | 25 | 62,511 | -0.16 | -0.20 | 46.7 | 5.63 | 3.50 | 0.05 |
| EURUSD | momentum | W=20 H=5 strong-up | 25 | 62,344 | -0.10 | -0.20 | 47.7 | 8.29 | 2.30 | 0.04 |
| EURUSD | momentum | W=80 H=20 strong-dn | 100 | 64,655 | -0.10 | 0.10 | 50.4 | 15.07 | 2.30 | 0.04 |
| EURUSD | session | NewYork H=20 | 100 | 52,740 | 0.10 | 0.10 | 50.3 | 11.07 | 2.30 | 0.04 |
| GBPUSD | momentum | W=80 H=5 strong-up | 25 | 55,876 | -0.15 | -0.10 | 48.7 | 11.16 | 3.50 | 0.04 |
| GBPUSD | session | London H=80 | 400 | 46,918 | -0.15 | 0.10 | 50.1 | 52.08 | 3.50 | 0.04 |
| GBPUSD | session_open | NewYork-open window | 25 | 4,692 | 0.15 | 0.30 | 51.3 | 9.44 | 3.50 | 0.04 |
| EURUSD | session_open | NewYork-open window | 25 | 5,274 | -0.09 | 0.00 | 49.6 | 6.89 | 2.30 | 0.04 |
| EURGBP | volatility | contraction_event H=80 | 400 | 6,665 | -0.14 | -0.20 | 49.0 | 16.27 | 3.50 | 0.04 |
| GBPUSD | session | OffHours H=5 | 25 | 27,816 | 0.14 | 0.20 | 52.5 | 11.44 | 3.50 | 0.04 |
| GBPUSD | momentum | W=20 H=5 strong-up | 25 | 55,821 | -0.14 | -0.20 | 48.3 | 11.70 | 3.50 | 0.04 |
| GBPUSD | momentum | W=5 H=5 strong-up | 25 | 55,906 | -0.14 | -0.20 | 48.3 | 11.22 | 3.50 | 0.04 |
| EURUSD | session | OffHours H=5 | 25 | 31,639 | 0.09 | 0.10 | 52.0 | 3.93 | 2.30 | 0.04 |
| GBPUSD | momentum | W=20 H=5 strong-dn | 25 | 56,423 | 0.13 | 0.30 | 51.4 | 11.33 | 3.50 | 0.04 |
| EURGBP | momentum | W=5 H=80 strong-dn | 400 | 62,251 | 0.13 | 0.10 | 50.2 | 19.63 | 3.50 | 0.04 |
| GBPUSD | volatility | normal H=20 | 100 | 40,311 | -0.13 | 0.00 | 49.6 | 20.10 | 3.50 | 0.04 |
| EURGBP | momentum | W=80 H=5 strong-up | 25 | 61,379 | -0.13 | -0.10 | 47.6 | 5.50 | 3.50 | 0.04 |
| EURUSD | momentum | W=80 H=5 strong-up | 25 | 61,353 | -0.08 | -0.10 | 48.6 | 7.93 | 2.30 | 0.04 |
| EURUSD | volatility | expansion_event H=20 | 100 | 5,319 | 0.08 | 0.20 | 50.5 | 16.55 | 2.30 | 0.03 |
| GBPUSD | session_open | London-open window | 25 | 4,692 | 0.12 | 0.10 | 50.4 | 10.91 | 3.50 | 0.03 |
| EURGBP | momentum | W=80 H=5 strong-dn | 25 | 65,881 | 0.12 | 0.10 | 50.8 | 5.10 | 3.50 | 0.03 |
| EURGBP | volatility | low H=5 | 25 | 121,577 | -0.11 | 0.00 | 48.0 | 3.52 | 3.50 | 0.03 |
| EURUSD | volatility | low H=5 | 25 | 115,295 | -0.07 | 0.00 | 49.3 | 5.37 | 2.30 | 0.03 |
| EURGBP | volatility | normal H=20 | 100 | 46,802 | 0.11 | 0.10 | 50.4 | 8.76 | 3.50 | 0.03 |
| EURGBP | session_open | London-open window | 25 | 5,328 | 0.10 | 0.10 | 50.6 | 5.75 | 3.50 | 0.03 |
| EURGBP | session | London H=20 | 100 | 53,231 | -0.10 | -0.20 | 49.0 | 11.96 | 3.50 | 0.03 |
| EURGBP | volatility | high H=5 | 25 | 86,902 | 0.10 | 0.10 | 50.7 | 5.76 | 3.50 | 0.03 |
| EURGBP | volatility | high H=20 | 100 | 86,887 | 0.10 | 0.20 | 50.9 | 11.06 | 3.50 | 0.03 |
| EURGBP | session | Asian H=20 | 100 | 74,587 | 0.10 | 0.10 | 50.2 | 7.19 | 3.50 | 0.03 |
| GBPUSD | volatility | high H=5 | 25 | 81,586 | 0.10 | 0.10 | 50.1 | 11.53 | 3.50 | 0.03 |
| EURUSD | session | LondonNY H=20 | 100 | 42,192 | -0.06 | -0.30 | 49.0 | 20.58 | 2.30 | 0.03 |
| EURGBP | session_open | Asian-open window | 25 | 5,328 | 0.09 | 0.00 | 49.4 | 2.66 | 3.50 | 0.03 |
| EURGBP | volatility | expansion_event H=80 | 400 | 5,992 | 0.09 | -0.10 | 49.5 | 18.96 | 3.50 | 0.03 |
| GBPUSD | volatility | expansion_event H=5 | 25 | 4,977 | 0.09 | 0.00 | 49.4 | 11.24 | 3.50 | 0.03 |
| EURUSD | momentum | W=20 H=5 strong-dn | 25 | 63,771 | 0.06 | 0.20 | 51.4 | 7.92 | 2.30 | 0.03 |
| GBPUSD | volatility | normal H=5 | 25 | 40,311 | -0.09 | 0.00 | 49.9 | 10.10 | 3.50 | 0.03 |
| GBPUSD | session | London H=5 | 25 | 46,920 | -0.09 | 0.00 | 49.7 | 10.92 | 3.50 | 0.03 |
| GBPUSD | volatility | low H=5 | 25 | 102,946 | -0.09 | 0.00 | 49.4 | 9.07 | 3.50 | 0.02 |
| GBPUSD | momentum | W=80 H=5 strong-dn | 25 | 56,426 | 0.08 | 0.20 | 50.8 | 11.06 | 3.50 | 0.02 |
| GBPUSD | session | Asian H=5 | 25 | 65,688 | -0.08 | 0.00 | 49.2 | 7.15 | 3.50 | 0.02 |
| EURUSD | volatility | expansion_event H=5 | 25 | 5,319 | 0.05 | 0.00 | 49.5 | 8.48 | 2.30 | 0.02 |
| EURUSD | volatility | normal H=5 | 25 | 44,468 | -0.05 | 0.00 | 49.2 | 6.82 | 2.30 | 0.02 |
| EURGBP | volatility | normal H=5 | 25 | 46,802 | 0.07 | 0.00 | 49.9 | 4.47 | 3.50 | 0.02 |
| EURGBP | session | NewYork H=80 | 400 | 53,159 | -0.07 | 0.00 | 49.9 | 10.62 | 3.50 | 0.02 |
| GBPUSD | momentum | W=5 H=80 strong-dn | 400 | 55,997 | 0.07 | 0.30 | 50.4 | 43.58 | 3.50 | 0.02 |
| GBPUSD | session | LondonNY H=5 | 25 | 37,536 | 0.06 | 0.00 | 49.8 | 14.47 | 3.50 | 0.02 |
| EURUSD | volatility | high H=5 | 25 | 93,567 | 0.04 | 0.00 | 49.9 | 8.58 | 2.30 | 0.02 |
| EURUSD | session | Asian H=5 | 25 | 73,999 | -0.03 | 0.00 | 48.9 | 4.80 | 2.30 | 0.02 |
| GBPUSD | session | NewYork H=80 | 400 | 46,858 | 0.05 | 0.30 | 50.6 | 32.48 | 3.50 | 0.01 |
| EURUSD | breakout | inside H=5 | 25 | 197,444 | -0.03 | 0.00 | 49.5 | 6.85 | 2.30 | 0.01 |
| EURUSD | session_open | LondonNY-open window | 25 | 5,274 | -0.03 | 0.00 | 49.8 | 12.63 | 2.30 | 0.01 |
| EURGBP | volatility | low H=80 | 400 | 121,550 | -0.05 | -0.10 | 49.5 | 14.53 | 3.50 | 0.01 |
| GBPUSD | breakout | inside H=20 | 100 | 174,634 | -0.05 | 0.00 | 50.0 | 19.90 | 3.50 | 0.01 |
| GBPUSD | breakout | dn-break H=80 | 400 | 24,968 | 0.04 | 0.40 | 50.6 | 40.59 | 3.50 | 0.01 |
| GBPUSD | volatility | contraction_event H=5 | 25 | 5,109 | 0.04 | 0.00 | 49.8 | 9.08 | 3.50 | 0.01 |
| EURGBP | breakout | inside H=20 | 100 | 201,213 | -0.04 | 0.00 | 49.4 | 8.66 | 3.50 | 0.01 |
| EURUSD | session | LondonNY H=5 | 25 | 42,192 | -0.02 | 0.00 | 49.5 | 10.99 | 2.30 | 0.01 |
| EURGBP | session | London H=5 | 25 | 53,231 | -0.04 | -0.10 | 49.0 | 6.04 | 3.50 | 0.01 |
| EURGBP | volatility | contraction_event H=5 | 25 | 6,669 | -0.03 | 0.00 | 49.8 | 4.10 | 3.50 | 0.01 |
| GBPUSD | session | OffHours H=20 | 100 | 27,816 | -0.03 | 0.70 | 53.5 | 23.30 | 3.50 | 0.01 |
| GBPUSD | breakout | inside H=5 | 25 | 174,645 | -0.03 | 0.00 | 49.7 | 9.94 | 3.50 | 0.01 |
| EURGBP | session | Asian H=5 | 25 | 74,587 | 0.03 | 0.00 | 48.9 | 3.52 | 3.50 | 0.01 |
| GBPUSD | session | NewYork H=5 | 25 | 46,883 | -0.03 | -0.10 | 48.9 | 7.98 | 3.50 | 0.01 |
| EURUSD | volatility | contraction_event H=5 | 25 | 5,409 | -0.02 | 0.00 | 49.3 | 6.34 | 2.30 | 0.01 |
| EURUSD | session | Asian H=20 | 100 | 73,992 | -0.02 | 0.00 | 49.8 | 10.34 | 2.30 | 0.01 |
| EURGBP | volatility | contraction_event H=20 | 100 | 6,669 | -0.02 | 0.00 | 49.6 | 8.47 | 3.50 | 0.01 |
| EURGBP | session | LondonNY H=5 | 25 | 42,563 | -0.02 | -0.10 | 48.9 | 6.06 | 3.50 | 0.01 |
| EURUSD | volatility | high H=20 | 100 | 93,552 | -0.01 | 0.10 | 50.2 | 16.05 | 2.30 | 0.01 |
| EURUSD | momentum | W=80 H=5 strong-dn | 25 | 64,655 | -0.01 | 0.10 | 50.6 | 7.74 | 2.30 | 0.00 |
| EURGBP | breakout | inside H=5 | 25 | 201,221 | -0.01 | 0.00 | 49.4 | 4.47 | 3.50 | 0.00 |
| EURUSD | session | OffHours H=20 | 100 | 31,639 | -0.01 | 0.30 | 52.4 | 7.93 | 2.30 | 0.00 |
| EURUSD | session | NewYork H=5 | 25 | 52,740 | -0.01 | 0.00 | 49.0 | 6.02 | 2.30 | 0.00 |
| GBPUSD | session | NewYork H=20 | 100 | 46,868 | 0.01 | -0.10 | 49.1 | 14.76 | 3.50 | 0.00 |

## 11. Strongest behaviors discovered


No behavior met the ratio ≥ 1.0 / mean ≥ 2.0 pips bar on the DEV split.

## 12. Weakest / rejected behaviors


The behaviors that were clearly negative or too small to review include the M5 continuation family (negative or near-zero raw edges), sessions whose mean forward move is smaller than their own cost (all expected with M5 horizons), and EURJPY (excluded on data quality).  Section 4, 5 and 7 report the raw numbers for each.

## 13. TOP 3 potential research directions


Top 3 raw behaviors by movement-to-cost (n ≥ 1000, DEV only):
1. **session on EURUSD** (London H=80, horizon 400 min): raw mean -1.52 pips, median -1.90, hit 47.3%, n=52,752, cost 2.30 pips, movement-to-cost 0.66.
2. **volatility on EURUSD** (expansion_event H=80, horizon 400 min): raw mean -1.38 pips, median -1.50, hit 47.5%, n=5,318, cost 2.30 pips, movement-to-cost 0.60.
3. **session on EURGBP** (LondonNY H=80, horizon 400 min): raw mean -1.36 pips, median -1.65, hit 44.8%, n=42,528, cost 3.50 pips, movement-to-cost 0.39.
None of these clears the cost bar; they are the LEAST-unattractive raw behaviors, not an edge.

## 14. Recommended next strategy candidate

No M5 behavior on the DEV split clears the movement-to-cost bar; the best raw ratio is 0.66 (EURUSD / session / London H=80, mean -1.52 pips vs 2.30 pips cost).  The evidence-based recommendation is to research MULTI-HOUR / DAILY horizons (H ≥ 240) and the session-open windows, where raw movement is structurally larger (section 7 shows London-open windows at ~1.8× median range), before proposing any new strategy candidate.

## 15. Exact evidence supporting that recommendation

The best raw movement-to-cost ratios on DEV (all below the 1.0 bar):
- EURUSD / session / London H=80 @ H=80: n=52,752, raw mean -1.52 pips, median -1.90, hit 47.3%, std 37.72, cost 2.30 pips, ratio 0.66.
- EURUSD / volatility / expansion_event H=80 @ H=80: n=5,318, raw mean -1.38 pips, median -1.50, hit 47.5%, std 30.47, cost 2.30 pips, ratio 0.60.
- EURGBP / session / LondonNY H=80 @ H=80: n=42,528, raw mean -1.36 pips, median -1.65, hit 44.8%, std 16.48, cost 3.50 pips, ratio 0.39.
- EURUSD / breakout / up-break H=80 @ H=80: n=28,037, raw mean -0.88 pips, median -0.60, hit 48.5%, std 27.78, cost 2.30 pips, ratio 0.38.
- EURGBP / session / OffHours H=80 @ H=80: n=31,741, raw mean +1.29 pips, median +1.00, hit 56.1%, std 10.41, cost 3.50 pips, ratio 0.37.
Sections 4–9 confirm every core-pair M5 forward mean is under ~1.5 pips while costs run 2.3–3.5 pips; no M5-level behavior is a credible edge.

## 16. What should NOT be tested


- M5 continuation/breakout-continuation on these pairs without a separate strong-condition filter (negative raw edges in earlier phases and section 5).
- Any EURJPY-based edge using the current degraded composite (25% zero spreads, 14-month window).
- Parameter variants of Strategies 01–03; those are rejected experiments and must not return in disguise.
- Tight stop loss (1 ATR) continuations of slow mean-reversion fades (proven loss-making under costs in Phase 2).
- Volume-weighted signals: the `real_volume` column is entirely zero.

## 17. Integrity / limitations


- DEV split only; validation and holdout were never read.  60/20/20 split preserved (section 2 counts).
- Research only: no strategy implemented, no backtest run, no parameter optimized, no multiple variants.
- Raw movement is measured at close-to-close horizons with realistic observed spreads; it is NOT P&L. No profitability is claimed anywhere in this report.
- Medians are reported alongside means because means are inflated by outliers; EURJPY is excluded from behaviour tables on data quality.
- `spread` is modeled/synthesized (distinct values but not live ticks); true execution costs are unknown and could be materially different.
