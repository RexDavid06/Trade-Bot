# EDGE DISCOVERY RESULTS

Research only · DEV split only · 60/20/20 preserved · no strategy, no backtest, no optimization · bot.py / V1 / V2 / Strategies 01-03 untouched · EURJPY excluded.


## 1. Method and integrity


- Data: DEV rows of `data/{eurusd,eurgbp,gbpusd}_m5.csv` (clean Dukascopy M5, observed bid/ask spread) resampled to M15/H1/H4 with the standard UTC-anchored floor aggregation (no lookahead).
- Execution: signal on the closed bar t, entry at the open of bar t+1, exit at the close of bar t+H (fixed horizon).
- Cost model: real observed round-trip spread + 1.0 pip slippage (0.5/side).
- All definitions frozen in EDGE_DISCOVERY_PLAN.md (Part C) BEFORE results.
- No ML, no sweeps, no SL/TP parameters, no holdout or validation bars read.
- `net_usd_norm` uses the configured account convention (0.10 lot, $10 per pip-lot → $1/pip).
- `exposure` = n × mean duration / frame length; identical signals during the same horizon overlap, so it measures rule activity and may exceed 1.0 (it is NOT a portfolio weighting).


## 2. Pre-registered screen (restated)


VIABLE* requires: n ≥ 1000; movement-to-cost ≥ 1.0 with |raw mean| ≥ 2.0 pips; net expectancy significantly positive (t p<0.05); positive on ≥ 2 of 3 symbols; ≥ 60% of years positive; no year &gt; 50% and no 4-week window &gt; 40% of total net.


## 3. Experiment verdicts


Tables below follow Part E item 3: only rules that cleared n ≥ 1000 on at least one symbol appear here; rules too rare for the available history are classified in section 5.


### B-PB — aligned two-timeframe pullback resumption (B - trend pullbacks)


B-PB: holds [12, 24] bars of H1. Pullback resumption inside an established higher-TF trend; H1 raw movement is the largest in the ladder.


**H=12 (12h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 4,104 | -0.493 | -2.566 | 0.238 | 45.2 | 0.830 | 11,655.500 | INSUFF | movement-to-cost 0.24 (bar 1.0), |mean|  |
| EURGBP | 4,494 | -1.525 | -5.436 | 0.390 | 37.8 | 0.511 | 24,444.500 | INSUFF | movement-to-cost 0.39 (bar 1.0), |mean|  |
| GBPUSD | 3,573 | -0.565 | -4.210 | 0.155 | 45.3 | 0.806 | 15,414.900 | INSUFF | movement-to-cost 0.16 (bar 1.0), |mean|  |

**H=24 (24h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 4,102 | 0.370 | -1.661 | 0.182 | 47.7 | 0.919 | 9,085.000 | INSUFF | movement-to-cost 0.18 (bar 1.0), |mean|  |
| EURGBP | 4,489 | -0.587 | -4.510 | 0.149 | 42.1 | 0.674 | 20,465.000 | INSUFF | movement-to-cost 0.15 (bar 1.0), |mean|  |
| GBPUSD | 3,570 | -0.444 | -4.072 | 0.122 | 48.0 | 0.863 | 14,735.400 | INSUFF | movement-to-cost 0.12 (bar 1.0), |mean|  |



### E-SQZ — low-ATR squeeze then range breakout (E - volatility contraction then expansion)


E-SQZ: holds [2, 4] bars of H4. Contracted volatility followed by a breakout tests the 'squeeze pop' direction; Phases 3/4 never combined the two.

Max events across symbols/holds = 388 < 1000 → nothing to table; see section 5 (UNRESOLVED).




### G-CANDLE — single large-body candle momentum (G - momentum following unusually large candles)


G-CANDLE: holds [4, 12] bars of M15. Event-based momentum (Phases 1/3 used window momentum); M15 gives many events and cost-plausible 1h/3h holds.

Max events across symbols/holds = 921 < 1000 → nothing to table; see section 5 (UNRESOLVED).




### H-ALIGN — H1/H4 trend-sign confluence (H - multi-timeframe directional alignment)


H-ALIGN: holds [2, 6] bars of H4. Confluence of short and long timeframe trend; genuinely untested dimension at the largest raw-movement scale.


**H=2 (8h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 3,391 | -0.524 | -2.549 | 0.259 | 44.3 | 0.784 | 9,036.900 | INSUFF | movement-to-cost 0.26 (bar 1.0), |mean|  |
| EURGBP | 3,320 | -0.903 | -4.381 | 0.260 | 35.8 | 0.510 | 14,644.700 | INSUFF | movement-to-cost 0.26 (bar 1.0), |mean|  |
| GBPUSD | 2,950 | -2.296 | -5.833 | 0.649 | 42.7 | 0.668 | 17,286.600 | BORDER | movement-to-cost 0.65 (bar 1.0), |mean|  |

**H=6 (24h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 3,389 | -0.918 | -2.904 | 0.462 | 46.4 | 0.859 | 10,843.200 | INSUFF | movement-to-cost 0.46 (bar 1.0), |mean|  |
| EURGBP | 3,318 | -1.334 | -4.748 | 0.391 | 42.3 | 0.661 | 16,513.000 | INSUFF | movement-to-cost 0.39 (bar 1.0), |mean|  |
| GBPUSD | 2,949 | -3.295 | -6.753 | 0.953 | 45.9 | 0.780 | 19,877.400 | BORDER | movement-to-cost 0.95 (bar 1.0), |mean|  |



### J-FADE-REGIME — fade extremes gated to the low-ATR regime (J - regime-dependent behavior)


J-FADE-REGIME: holds [4, 12] bars of H1. Phase-1 fade-the-extreme (positive raw) may clear costs once restricted to a range-bound regime; frozen threshold, not swept.


**H=4 (4h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 3,529 | -0.025 | -1.841 | 0.014 | 47.1 | 0.773 | 6,882.700 | INSUFF | movement-to-cost 0.01 (bar 1.0), |mean|  |
| EURGBP | 2,939 | 0.789 | -2.621 | 0.231 | 38.7 | 0.573 | 7,686.500 | INSUFF | movement-to-cost 0.23 (bar 1.0), |mean|  |
| GBPUSD | 3,111 | 0.973 | -2.239 | 0.303 | 45.5 | 0.800 | 7,052.100 | INSUFF | movement-to-cost 0.30 (bar 1.0), |mean|  |

**H=12 (12h)**

| sym | n | raw_mean | net_exp | mov/cost | hit% | PF | maxDD | verdict | reason |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 3,529 | 1.010 | -0.976 | 0.509 | 50.9 | 0.936 | 6,618.000 | BORDER | movement-to-cost 0.51 (bar 1.0), |mean|  |
| EURGBP | 2,939 | 2.737 | -1.057 | 0.721 | 46.7 | 0.887 | 3,778.500 | BORDER | movement-to-cost 0.72 (bar 1.0), |mean|  |
| GBPUSD | 3,111 | 4.141 | 0.610 | 1.173 | 49.3 | 1.033 | 8,311.800 | REJECTED | net expectancy not significantly positiv |



## 4. Verdict buckets (plan Part E item 4)


- **DISCOVERED** — cleared the full pre-registered screen. None this round.
- **REJECTED** — failed the screen; the exact failing criterion is in the reason below.
- **UNRESOLVED** — plausible but too few qualifying events in the available clean history to reach n ≥ 1000.
- **NOT TESTED** — intentionally excluded: EURJPY (degraded feed, ~46% zero-spread rows), volume-dependent rules (real volume is zeros), session-only entries, and the broker universe without local data.


| bucket | experiment | sym | hold | n | mean | m2c | screen | reason |
|---|---|---|---|---|---|---|---|---|
| REJECTED | B-PB | EURUSD | H=12 | 4,104 | -0.49 | 0.24 | INSUFF | movement-to-cost 0.24 (bar 1.0), |mean| 0.49 (bar 2.0) |
| REJECTED | B-PB | EURGBP | H=12 | 4,494 | -1.53 | 0.39 | INSUFF | movement-to-cost 0.39 (bar 1.0), |mean| 1.53 (bar 2.0) |
| REJECTED | B-PB | GBPUSD | H=12 | 3,573 | -0.57 | 0.16 | INSUFF | movement-to-cost 0.16 (bar 1.0), |mean| 0.57 (bar 2.0) |
| REJECTED | B-PB | EURUSD | H=24 | 4,102 | +0.37 | 0.18 | INSUFF | movement-to-cost 0.18 (bar 1.0), |mean| 0.37 (bar 2.0) |
| REJECTED | B-PB | EURGBP | H=24 | 4,489 | -0.59 | 0.15 | INSUFF | movement-to-cost 0.15 (bar 1.0), |mean| 0.59 (bar 2.0) |
| REJECTED | B-PB | GBPUSD | H=24 | 3,570 | -0.44 | 0.12 | INSUFF | movement-to-cost 0.12 (bar 1.0), |mean| 0.44 (bar 2.0) |
| UNRESOLVED | E-SQZ | EURUSD | H=2 | 358 | +0.74 | 0.37 | INSUFF | n=358 below 1000 |
| UNRESOLVED | E-SQZ | EURGBP | H=2 | 388 | -3.14 | 0.90 | INSUFF | n=388 below 1000 |
| UNRESOLVED | E-SQZ | GBPUSD | H=2 | 359 | -6.58 | 2.02 | INSUFF | n=359 below 1000 |
| UNRESOLVED | E-SQZ | EURUSD | H=4 | 358 | +0.79 | 0.42 | INSUFF | n=358 below 1000 |
| UNRESOLVED | E-SQZ | EURGBP | H=4 | 388 | -3.09 | 0.90 | INSUFF | n=388 below 1000 |
| UNRESOLVED | E-SQZ | GBPUSD | H=4 | 359 | -8.96 | 2.78 | INSUFF | n=359 below 1000 |
| UNRESOLVED | G-CANDLE | EURUSD | H=4 | 921 | -0.79 | 0.45 | INSUFF | n=921 below 1000 |
| UNRESOLVED | G-CANDLE | EURGBP | H=4 | 884 | -0.39 | 0.11 | INSUFF | n=884 below 1000 |
| UNRESOLVED | G-CANDLE | GBPUSD | H=4 | 695 | -0.08 | 0.03 | INSUFF | n=695 below 1000 |
| UNRESOLVED | G-CANDLE | EURUSD | H=12 | 921 | -0.44 | 0.25 | INSUFF | n=921 below 1000 |
| UNRESOLVED | G-CANDLE | EURGBP | H=12 | 884 | -0.09 | 0.03 | INSUFF | n=884 below 1000 |
| UNRESOLVED | G-CANDLE | GBPUSD | H=12 | 695 | -0.85 | 0.28 | INSUFF | n=695 below 1000 |
| REJECTED | H-ALIGN | EURUSD | H=2 | 3,391 | -0.52 | 0.26 | INSUFF | movement-to-cost 0.26 (bar 1.0), |mean| 0.52 (bar 2.0) |
| REJECTED | H-ALIGN | EURGBP | H=2 | 3,320 | -0.90 | 0.26 | INSUFF | movement-to-cost 0.26 (bar 1.0), |mean| 0.90 (bar 2.0) |
| REJECTED | H-ALIGN | GBPUSD | H=2 | 2,950 | -2.30 | 0.65 | BORDER | movement-to-cost 0.65 (bar 1.0), |mean| 2.30 (bar 2.0) |
| REJECTED | H-ALIGN | EURUSD | H=6 | 3,389 | -0.92 | 0.46 | INSUFF | movement-to-cost 0.46 (bar 1.0), |mean| 0.92 (bar 2.0) |
| REJECTED | H-ALIGN | EURGBP | H=6 | 3,318 | -1.33 | 0.39 | INSUFF | movement-to-cost 0.39 (bar 1.0), |mean| 1.33 (bar 2.0) |
| REJECTED | H-ALIGN | GBPUSD | H=6 | 2,949 | -3.29 | 0.95 | BORDER | movement-to-cost 0.95 (bar 1.0), |mean| 3.29 (bar 2.0) |
| REJECTED | J-FADE-REGIME | EURUSD | H=4 | 3,529 | -0.02 | 0.01 | INSUFF | movement-to-cost 0.01 (bar 1.0), |mean| 0.02 (bar 2.0) |
| REJECTED | J-FADE-REGIME | EURGBP | H=4 | 2,939 | +0.79 | 0.23 | INSUFF | movement-to-cost 0.23 (bar 1.0), |mean| 0.79 (bar 2.0) |
| REJECTED | J-FADE-REGIME | GBPUSD | H=4 | 3,111 | +0.97 | 0.30 | INSUFF | movement-to-cost 0.30 (bar 1.0), |mean| 0.97 (bar 2.0) |
| REJECTED | J-FADE-REGIME | EURUSD | H=12 | 3,529 | +1.01 | 0.51 | BORDER | movement-to-cost 0.51 (bar 1.0), |mean| 1.01 (bar 2.0) |
| REJECTED | J-FADE-REGIME | EURGBP | H=12 | 2,939 | +2.74 | 0.72 | BORDER | movement-to-cost 0.72 (bar 1.0), |mean| 2.74 (bar 2.0) |
| REJECTED | J-FADE-REGIME | GBPUSD | H=12 | 3,111 | +4.14 | 1.17 | REJECTED | net expectancy not significantly positive |

STOP CONDITION (TASK.md): no rule cleared the full pre-registered screen. Per the plan, nothing was optimized, no parameter re-tested, and no validation or holdout bar was read for ANY rule.


## 5. Full per-experiment metrics


### B-PB / EURUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.074 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -27.597 |
| avg_win_pips | 27.811 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -2.566 |
| exposure | 2.332 |
| gross_loss_pips | 57,540.200 |
| gross_profit_pips | 55,517.500 |
| max_drawdown_pips | 11,655.500 |
| max_window_share | 0.128 |
| max_year_share | 0.341 |
| mean_raw_pips | -0.493 |
| movement_to_cost | 0.238 |
| n | 4,104 |
| net_usd_norm | -10,532.500 |
| pip | 0.000 |
| profit_factor | 0.830 |
| reason | movement-to-cost 0.24 (bar 1.0), |mean| 0.49 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 8,509.800 |
| total_net_pips | -10,532.500 |
| trades | 4,104 |
| verdict | INSUFF |
| win_rate | 0.452 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### B-PB / EURGBP / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.911 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -17.858 |
| avg_win_pips | 15.037 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -5.436 |
| exposure | 2.533 |
| gross_loss_pips | 39,499.500 |
| gross_profit_pips | 32,645.200 |
| max_drawdown_pips | 24,444.500 |
| max_window_share | 0.055 |
| max_year_share | 0.381 |
| mean_raw_pips | -1.525 |
| movement_to_cost | 0.390 |
| n | 4,494 |
| net_usd_norm | -24,430.500 |
| pip | 0.000 |
| profit_factor | 0.511 |
| reason | movement-to-cost 0.39 (bar 1.0), |mean| 1.53 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 17,576.200 |
| total_net_pips | -24,430.500 |
| trades | 4,494 |
| verdict | INSUFF |
| win_rate | 0.378 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### B-PB / GBPUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.645 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -39.733 |
| avg_win_pips | 38.663 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -4.210 |
| exposure | 2.287 |
| gross_loss_pips | 70,530.200 |
| gross_profit_pips | 68,510.200 |
| max_drawdown_pips | 15,414.900 |
| max_window_share | 0.105 |
| max_year_share | 0.331 |
| mean_raw_pips | -0.565 |
| movement_to_cost | 0.155 |
| n | 3,573 |
| net_usd_norm | -15,042.400 |
| pip | 0.000 |
| profit_factor | 0.806 |
| reason | movement-to-cost 0.16 (bar 1.0), |mean| 0.57 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 13,022.400 |
| total_net_pips | -15,042.400 |
| trades | 3,573 |
| verdict | INSUFF |
| win_rate | 0.453 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### B-PB / EURUSD / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.031 |
| avg_duration_bars | 24.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -39.417 |
| avg_win_pips | 39.722 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -1.661 |
| exposure | 4.662 |
| gross_loss_pips | 80,224.300 |
| gross_profit_pips | 81,741.100 |
| max_drawdown_pips | 9,085.000 |
| max_window_share | 0.246 |
| max_year_share | 0.556 |
| mean_raw_pips | 0.370 |
| movement_to_cost | 0.182 |
| n | 4,102 |
| net_usd_norm | -6,812.600 |
| pip | 0.000 |
| profit_factor | 0.919 |
| reason | movement-to-cost 0.18 (bar 1.0), |mean| 0.37 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 8,329.400 |
| total_net_pips | -6,812.600 |
| trades | 4,102 |
| verdict | INSUFF |
| win_rate | 0.477 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### B-PB / EURGBP / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.924 |
| avg_duration_bars | 24.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -23.861 |
| avg_win_pips | 22.099 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -4.510 |
| exposure | 5.060 |
| gross_loss_pips | 52,158.400 |
| gross_profit_pips | 49,525.600 |
| max_drawdown_pips | 20,465.000 |
| max_window_share | 0.093 |
| max_year_share | 0.311 |
| mean_raw_pips | -0.587 |
| movement_to_cost | 0.149 |
| n | 4,489 |
| net_usd_norm | -20,247.300 |
| pip | 0.000 |
| profit_factor | 0.674 |
| reason | movement-to-cost 0.15 (bar 1.0), |mean| 0.59 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 17,614.500 |
| total_net_pips | -20,247.300 |
| trades | 4,489 |
| verdict | INSUFF |
| win_rate | 0.421 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### B-PB / GBPUSD / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.629 |
| avg_duration_bars | 24.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -57.248 |
| avg_win_pips | 53.574 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -4.072 |
| exposure | 4.571 |
| gross_loss_pips | 99,579.400 |
| gross_profit_pips | 97,995.900 |
| max_drawdown_pips | 14,735.400 |
| max_window_share | 0.152 |
| max_year_share | 0.349 |
| mean_raw_pips | -0.444 |
| movement_to_cost | 0.122 |
| n | 3,570 |
| net_usd_norm | -14,537.900 |
| pip | 0.000 |
| profit_factor | 0.863 |
| reason | movement-to-cost 0.12 (bar 1.0), |mean| 0.44 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 12,954.400 |
| total_net_pips | -14,537.900 |
| trades | 3,570 |
| verdict | INSUFF |
| win_rate | 0.480 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### E-SQZ / EURUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.978 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -22.340 |
| avg_win_pips | 24.007 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -1.238 |
| exposure | 0.131 |
| gross_loss_pips | 3,963.300 |
| gross_profit_pips | 4,228.200 |
| max_drawdown_pips | 775.500 |
| max_window_share | 0.675 |
| max_year_share | 1.346 |
| mean_raw_pips | 0.740 |
| movement_to_cost | 0.374 |
| n | 358 |
| net_usd_norm | -443.100 |
| pip | 0.000 |
| profit_factor | 0.898 |
| reason | n=358 below 1000 |
| symbol | EURUSD |
| timeframe | H4 |
| total_cost_pips | 708.000 |
| total_net_pips | -443.100 |
| trades | 358 |
| verdict | INSUFF |
| win_rate | 0.455 |
| years_count | 4 |
| years_positive_share | 0.500 |
| years_total | 4 |

### E-SQZ / EURGBP / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.473 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -16.347 |
| avg_win_pips | 14.364 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -6.611 |
| exposure | 0.141 |
| gross_loss_pips | 3,456.300 |
| gross_profit_pips | 2,238.600 |
| max_drawdown_pips | 2,543.600 |
| max_window_share | 0.119 |
| max_year_share | 0.466 |
| mean_raw_pips | -3.138 |
| movement_to_cost | 0.904 |
| n | 388 |
| net_usd_norm | -2,565.100 |
| pip | 0.000 |
| profit_factor | 0.408 |
| reason | n=388 below 1000 |
| symbol | EURGBP |
| timeframe | H4 |
| total_cost_pips | 1,347.400 |
| total_net_pips | -2,565.100 |
| trades | 388 |
| verdict | INSUFF |
| win_rate | 0.317 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### E-SQZ / GBPUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.250 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -33.049 |
| avg_win_pips | 26.917 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -9.831 |
| exposure | 0.148 |
| gross_loss_pips | 6,568.600 |
| gross_profit_pips | 4,206.200 |
| max_drawdown_pips | 3,600.400 |
| max_window_share | 0.241 |
| max_year_share | 0.420 |
| mean_raw_pips | -6.581 |
| movement_to_cost | 2.025 |
| n | 359 |
| net_usd_norm | -3,529.200 |
| pip | 0.000 |
| profit_factor | 0.515 |
| reason | n=359 below 1000 |
| symbol | GBPUSD |
| timeframe | H4 |
| total_cost_pips | 1,166.800 |
| total_net_pips | -3,529.200 |
| trades | 359 |
| verdict | INSUFF |
| win_rate | 0.387 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### E-SQZ / EURUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.868 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 16.000 |
| avg_loss_pips | -26.610 |
| avg_win_pips | 29.121 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -1.080 |
| exposure | 0.262 |
| gross_loss_pips | 4,813.600 |
| gross_profit_pips | 5,095.900 |
| max_drawdown_pips | 1,121.700 |
| max_window_share | 0.837 |
| max_year_share | 1.764 |
| mean_raw_pips | 0.789 |
| movement_to_cost | 0.422 |
| n | 358 |
| net_usd_norm | -386.500 |
| pip | 0.000 |
| profit_factor | 0.925 |
| reason | n=358 below 1000 |
| symbol | EURUSD |
| timeframe | H4 |
| total_cost_pips | 668.800 |
| total_net_pips | -386.500 |
| trades | 358 |
| verdict | INSUFF |
| win_rate | 0.458 |
| years_count | 4 |
| years_positive_share | 0.500 |
| years_total | 4 |

### E-SQZ / EURGBP / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.455 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 16.000 |
| avg_loss_pips | -20.591 |
| avg_win_pips | 15.979 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -6.548 |
| exposure | 0.282 |
| gross_loss_pips | 4,110.500 |
| gross_profit_pips | 2,910.400 |
| max_drawdown_pips | 2,529.000 |
| max_window_share | 0.169 |
| max_year_share | 0.570 |
| mean_raw_pips | -3.093 |
| movement_to_cost | 0.895 |
| n | 388 |
| net_usd_norm | -2,540.500 |
| pip | 0.000 |
| profit_factor | 0.484 |
| reason | n=388 below 1000 |
| symbol | EURGBP |
| timeframe | H4 |
| total_cost_pips | 1,340.400 |
| total_net_pips | -2,540.500 |
| trades | 388 |
| verdict | INSUFF |
| win_rate | 0.384 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### E-SQZ / GBPUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.217 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 16.000 |
| avg_loss_pips | -43.244 |
| avg_win_pips | 38.774 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -12.173 |
| exposure | 0.297 |
| gross_loss_pips | 8,949.500 |
| gross_profit_pips | 5,734.100 |
| max_drawdown_pips | 4,570.000 |
| max_window_share | 0.246 |
| max_year_share | 0.393 |
| mean_raw_pips | -8.957 |
| movement_to_cost | 2.784 |
| n | 359 |
| net_usd_norm | -4,370.200 |
| pip | 0.000 |
| profit_factor | 0.547 |
| reason | n=359 below 1000 |
| symbol | GBPUSD |
| timeframe | H4 |
| total_cost_pips | 1,154.800 |
| total_net_pips | -4,370.200 |
| trades | 359 |
| verdict | INSUFF |
| win_rate | 0.379 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### G-CANDLE / EURUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.767 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 1.000 |
| avg_loss_pips | -11.663 |
| avg_win_pips | 10.694 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -2.560 |
| exposure | 0.044 |
| gross_loss_pips | 5,416.400 |
| gross_profit_pips | 4,686.200 |
| max_drawdown_pips | 2,362.500 |
| max_window_share | 0.103 |
| max_year_share | 0.310 |
| mean_raw_pips | -0.793 |
| movement_to_cost | 0.449 |
| n | 921 |
| net_usd_norm | -2,357.900 |
| pip | 0.000 |
| profit_factor | 0.630 |
| reason | n=921 below 1000 |
| symbol | EURUSD |
| timeframe | M15 |
| total_cost_pips | 1,627.700 |
| total_net_pips | -2,357.900 |
| trades | 921 |
| verdict | INSUFF |
| win_rate | 0.407 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### G-CANDLE / EURGBP / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.587 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 1.000 |
| avg_loss_pips | -8.757 |
| avg_win_pips | 6.779 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -3.977 |
| exposure | 0.042 |
| gross_loss_pips | 3,336.200 |
| gross_profit_pips | 2,991.300 |
| max_drawdown_pips | 3,519.900 |
| max_window_share | 0.076 |
| max_year_share | 0.398 |
| mean_raw_pips | -0.390 |
| movement_to_cost | 0.109 |
| n | 884 |
| net_usd_norm | -3,515.400 |
| pip | 0.000 |
| profit_factor | 0.344 |
| reason | n=884 below 1000 |
| symbol | EURGBP |
| timeframe | M15 |
| total_cost_pips | 3,170.500 |
| total_net_pips | -3,515.400 |
| trades | 884 |
| verdict | INSUFF |
| win_rate | 0.308 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### G-CANDLE / GBPUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.996 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 1.000 |
| avg_loss_pips | -16.074 |
| avg_win_pips | 14.347 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -3.074 |
| exposure | 0.037 |
| gross_loss_pips | 5,258.900 |
| gross_profit_pips | 5,204.700 |
| max_drawdown_pips | 2,168.100 |
| max_window_share | 0.309 |
| max_year_share | 0.386 |
| mean_raw_pips | -0.078 |
| movement_to_cost | 0.026 |
| n | 695 |
| net_usd_norm | -2,136.300 |
| pip | 0.000 |
| profit_factor | 0.666 |
| reason | n=695 below 1000 |
| symbol | GBPUSD |
| timeframe | M15 |
| total_cost_pips | 2,082.100 |
| total_net_pips | -2,136.300 |
| trades | 695 |
| verdict | INSUFF |
| win_rate | 0.427 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### G-CANDLE / EURUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.764 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 3.000 |
| avg_loss_pips | -16.805 |
| avg_win_pips | 17.845 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -2.207 |
| exposure | 0.131 |
| gross_loss_pips | 8,034.700 |
| gross_profit_pips | 7,626.700 |
| max_drawdown_pips | 2,012.000 |
| max_window_share | 0.140 |
| max_year_share | 0.545 |
| mean_raw_pips | -0.443 |
| movement_to_cost | 0.251 |
| n | 921 |
| net_usd_norm | -2,033.000 |
| pip | 0.000 |
| profit_factor | 0.773 |
| reason | n=921 below 1000 |
| symbol | EURUSD |
| timeframe | M15 |
| total_cost_pips | 1,625.000 |
| total_net_pips | -2,033.000 |
| trades | 921 |
| verdict | INSUFF |
| win_rate | 0.421 |
| years_count | 4 |
| years_positive_share | 0.250 |
| years_total | 4 |

### G-CANDLE / EURGBP / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.437 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 3.000 |
| avg_loss_pips | -13.025 |
| avg_win_pips | 12.189 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -3.527 |
| exposure | 0.125 |
| gross_loss_pips | 5,387.100 |
| gross_profit_pips | 5,307.900 |
| max_drawdown_pips | 3,087.500 |
| max_window_share | 0.076 |
| max_year_share | 0.389 |
| mean_raw_pips | -0.090 |
| movement_to_cost | 0.026 |
| n | 884 |
| net_usd_norm | -3,117.700 |
| pip | 0.000 |
| profit_factor | 0.566 |
| reason | n=884 below 1000 |
| symbol | EURGBP |
| timeframe | M15 |
| total_cost_pips | 3,038.500 |
| total_net_pips | -3,117.700 |
| trades | 884 |
| verdict | INSUFF |
| win_rate | 0.377 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### G-CANDLE / GBPUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.022 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 3.000 |
| avg_loss_pips | -25.566 |
| avg_win_pips | 22.752 |
| bars_min | 15 |
| commission | 0.000 |
| expectancy_net_pips | -3.875 |
| exposure | 0.111 |
| gross_loss_pips | 8,648.600 |
| gross_profit_pips | 8,055.500 |
| max_drawdown_pips | 2,888.900 |
| max_window_share | 0.327 |
| max_year_share | 0.513 |
| mean_raw_pips | -0.853 |
| movement_to_cost | 0.282 |
| n | 695 |
| net_usd_norm | -2,693.100 |
| pip | 0.000 |
| profit_factor | 0.725 |
| reason | n=695 below 1000 |
| symbol | GBPUSD |
| timeframe | M15 |
| total_cost_pips | 2,100.000 |
| total_net_pips | -2,693.100 |
| trades | 695 |
| verdict | INSUFF |
| win_rate | 0.449 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### H-ALIGN / EURUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.024 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -21.187 |
| avg_win_pips | 20.863 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -2.549 |
| exposure | 1.243 |
| gross_loss_pips | 36,111.200 |
| gross_profit_pips | 34,332.700 |
| max_drawdown_pips | 9,036.900 |
| max_window_share | 0.112 |
| max_year_share | 0.294 |
| mean_raw_pips | -0.524 |
| movement_to_cost | 0.259 |
| n | 3,391 |
| net_usd_norm | -8,643.400 |
| pip | 0.000 |
| profit_factor | 0.784 |
| reason | movement-to-cost 0.26 (bar 1.0), |mean| 0.52 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H4 |
| total_cost_pips | 6,864.900 |
| total_net_pips | -8,643.400 |
| trades | 3,391 |
| verdict | INSUFF |
| win_rate | 0.443 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### H-ALIGN / EURGBP / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.478 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -13.950 |
| avg_win_pips | 12.747 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -4.381 |
| exposure | 1.207 |
| gross_loss_pips | 22,559.600 |
| gross_profit_pips | 19,560.400 |
| max_drawdown_pips | 14,644.700 |
| max_window_share | 0.069 |
| max_year_share | 0.348 |
| mean_raw_pips | -0.903 |
| movement_to_cost | 0.260 |
| n | 3,320 |
| net_usd_norm | -14,544.800 |
| pip | 0.000 |
| profit_factor | 0.510 |
| reason | movement-to-cost 0.26 (bar 1.0), |mean| 0.90 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H4 |
| total_cost_pips | 11,545.600 |
| total_net_pips | -14,544.800 |
| trades | 3,320 |
| verdict | INSUFF |
| win_rate | 0.358 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### H-ALIGN / GBPUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.537 |
| avg_duration_bars | 2.000 |
| avg_duration_hours | 8.000 |
| avg_loss_pips | -30.640 |
| avg_win_pips | 27.439 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -5.833 |
| exposure | 1.219 |
| gross_loss_pips | 45,793.600 |
| gross_profit_pips | 39,019.500 |
| max_drawdown_pips | 17,286.600 |
| max_window_share | 0.069 |
| max_year_share | 0.290 |
| mean_raw_pips | -2.296 |
| movement_to_cost | 0.649 |
| n | 2,950 |
| net_usd_norm | -17,208.700 |
| pip | 0.000 |
| profit_factor | 0.668 |
| reason | movement-to-cost 0.65 (bar 1.0), |mean| 2.30 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H4 |
| total_cost_pips | 10,434.600 |
| total_net_pips | -17,208.700 |
| trades | 2,950 |
| verdict | BORDER |
| win_rate | 0.427 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### H-ALIGN / EURUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.986 |
| avg_duration_bars | 6.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -38.591 |
| avg_win_pips | 38.247 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -2.904 |
| exposure | 3.727 |
| gross_loss_pips | 66,448.600 |
| gross_profit_pips | 63,336.300 |
| max_drawdown_pips | 10,843.200 |
| max_window_share | 0.179 |
| max_year_share | 0.415 |
| mean_raw_pips | -0.918 |
| movement_to_cost | 0.462 |
| n | 3,389 |
| net_usd_norm | -9,842.700 |
| pip | 0.000 |
| profit_factor | 0.859 |
| reason | movement-to-cost 0.46 (bar 1.0), |mean| 0.92 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H4 |
| total_cost_pips | 6,730.400 |
| total_net_pips | -9,842.700 |
| trades | 3,389 |
| verdict | INSUFF |
| win_rate | 0.464 |
| years_count | 4 |
| years_positive_share | 0.250 |
| years_total | 4 |

### H-ALIGN / EURGBP / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.414 |
| avg_duration_bars | 6.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -24.319 |
| avg_win_pips | 21.900 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -4.748 |
| exposure | 3.619 |
| gross_loss_pips | 40,243.800 |
| gross_profit_pips | 35,817.400 |
| max_drawdown_pips | 16,513.000 |
| max_window_share | 0.084 |
| max_year_share | 0.339 |
| mean_raw_pips | -1.334 |
| movement_to_cost | 0.391 |
| n | 3,318 |
| net_usd_norm | -15,754.100 |
| pip | 0.000 |
| profit_factor | 0.661 |
| reason | movement-to-cost 0.39 (bar 1.0), |mean| 1.33 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H4 |
| total_cost_pips | 11,327.700 |
| total_net_pips | -15,754.100 |
| trades | 3,318 |
| verdict | INSUFF |
| win_rate | 0.423 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### H-ALIGN / GBPUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.458 |
| avg_duration_bars | 6.000 |
| avg_duration_hours | 24.000 |
| avg_loss_pips | -56.685 |
| avg_win_pips | 52.148 |
| bars_min | 240 |
| commission | 0.000 |
| expectancy_net_pips | -6.753 |
| exposure | 3.656 |
| gross_loss_pips | 85,044.700 |
| gross_profit_pips | 75,328.700 |
| max_drawdown_pips | 19,877.400 |
| max_window_share | 0.145 |
| max_year_share | 0.323 |
| mean_raw_pips | -3.295 |
| movement_to_cost | 0.953 |
| n | 2,949 |
| net_usd_norm | -19,914.100 |
| pip | 0.000 |
| profit_factor | 0.780 |
| reason | movement-to-cost 0.95 (bar 1.0), |mean| 3.29 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H4 |
| total_cost_pips | 10,198.100 |
| total_net_pips | -19,914.100 |
| trades | 2,949 |
| verdict | BORDER |
| win_rate | 0.459 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### J-FADE-REGIME / EURUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 1.816 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 4.000 |
| avg_loss_pips | -15.326 |
| avg_win_pips | 13.325 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -1.841 |
| exposure | 0.668 |
| gross_loss_pips | 25,362.100 |
| gross_profit_pips | 25,274.000 |
| max_drawdown_pips | 6,882.700 |
| max_window_share | 0.144 |
| max_year_share | 0.457 |
| mean_raw_pips | -0.025 |
| movement_to_cost | 0.014 |
| n | 3,529 |
| net_usd_norm | -6,496.300 |
| pip | 0.000 |
| profit_factor | 0.773 |
| reason | movement-to-cost 0.01 (bar 1.0), |mean| 0.02 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 6,408.200 |
| total_net_pips | -6,496.300 |
| trades | 3,529 |
| verdict | INSUFF |
| win_rate | 0.471 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### J-FADE-REGIME / EURGBP / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.410 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 4.000 |
| avg_loss_pips | -10.010 |
| avg_win_pips | 9.089 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -2.621 |
| exposure | 0.552 |
| gross_loss_pips | 12,562.800 |
| gross_profit_pips | 14,880.600 |
| max_drawdown_pips | 7,686.500 |
| max_window_share | 0.097 |
| max_year_share | 0.362 |
| mean_raw_pips | 0.789 |
| movement_to_cost | 0.231 |
| n | 2,939 |
| net_usd_norm | -7,703.400 |
| pip | 0.000 |
| profit_factor | 0.573 |
| reason | movement-to-cost 0.23 (bar 1.0), |mean| 0.79 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 10,021.200 |
| total_net_pips | -7,703.400 |
| trades | 2,939 |
| verdict | INSUFF |
| win_rate | 0.387 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### J-FADE-REGIME / GBPUSD / H=4

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.212 |
| avg_duration_bars | 4.000 |
| avg_duration_hours | 4.000 |
| avg_loss_pips | -20.539 |
| avg_win_pips | 19.640 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -2.239 |
| exposure | 0.664 |
| gross_loss_pips | 29,658.400 |
| gross_profit_pips | 32,685.300 |
| max_drawdown_pips | 7,052.100 |
| max_window_share | 0.154 |
| max_year_share | 0.448 |
| mean_raw_pips | 0.973 |
| movement_to_cost | 0.303 |
| n | 3,111 |
| net_usd_norm | -6,964.500 |
| pip | 0.000 |
| profit_factor | 0.800 |
| reason | movement-to-cost 0.30 (bar 1.0), |mean| 0.97 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 9,991.400 |
| total_net_pips | -6,964.500 |
| trades | 3,111 |
| verdict | INSUFF |
| win_rate | 0.455 |
| years_count | 4 |
| years_positive_share | 0.000 |
| years_total | 4 |

### J-FADE-REGIME / EURUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 1 |
| avg_cost_pips | 1.986 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -30.983 |
| avg_win_pips | 27.946 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -0.976 |
| exposure | 2.005 |
| gross_loss_pips | 50,246.000 |
| gross_profit_pips | 53,810.900 |
| max_drawdown_pips | 6,618.000 |
| max_window_share | 0.484 |
| max_year_share | 1.029 |
| mean_raw_pips | 1.010 |
| movement_to_cost | 0.509 |
| n | 3,529 |
| net_usd_norm | -3,443.800 |
| pip | 0.000 |
| profit_factor | 0.936 |
| reason | movement-to-cost 0.51 (bar 1.0), |mean| 1.01 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 7,008.700 |
| total_net_pips | -3,443.800 |
| trades | 3,529 |
| verdict | BORDER |
| win_rate | 0.509 |
| years_count | 4 |
| years_positive_share | 0.500 |
| years_total | 4 |

### J-FADE-REGIME / EURGBP / H=12

| metric | value |
|---|---|
| _pos_symbols | 1 |
| avg_cost_pips | 3.794 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -17.589 |
| avg_win_pips | 17.798 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | -1.057 |
| exposure | 1.656 |
| gross_loss_pips | 21,928.100 |
| gross_profit_pips | 29,970.900 |
| max_drawdown_pips | 3,778.500 |
| max_window_share | 0.447 |
| max_year_share | 0.875 |
| mean_raw_pips | 2.737 |
| movement_to_cost | 0.721 |
| n | 2,939 |
| net_usd_norm | -3,107.300 |
| pip | 0.000 |
| profit_factor | 0.887 |
| reason | movement-to-cost 0.72 (bar 1.0), |mean| 2.74 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 11,150.100 |
| total_net_pips | -3,107.300 |
| trades | 2,939 |
| verdict | BORDER |
| win_rate | 0.467 |
| years_count | 4 |
| years_positive_share | 0.250 |
| years_total | 4 |

### J-FADE-REGIME / GBPUSD / H=12

| metric | value |
|---|---|
| _pos_symbols | 1 |
| avg_cost_pips | 3.531 |
| avg_duration_bars | 12.000 |
| avg_duration_hours | 12.000 |
| avg_loss_pips | -36.123 |
| avg_win_pips | 38.421 |
| bars_min | 60 |
| commission | 0.000 |
| expectancy_net_pips | 0.610 |
| exposure | 1.992 |
| gross_loss_pips | 51,557.800 |
| gross_profit_pips | 64,440.400 |
| max_drawdown_pips | 8,311.800 |
| max_window_share | 1.053 |
| max_year_share | 0.927 |
| mean_raw_pips | 4.141 |
| movement_to_cost | 1.173 |
| n | 3,111 |
| net_usd_norm | 1,897.200 |
| pip | 0.000 |
| profit_factor | 1.033 |
| reason | net expectancy not significantly positive |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 10,985.400 |
| total_net_pips | 1,897.200 |
| trades | 3,111 |
| verdict | REJECTED |
| win_rate | 0.493 |
| years_count | 4 |
| years_positive_share | 0.750 |
| years_total | 4 |
