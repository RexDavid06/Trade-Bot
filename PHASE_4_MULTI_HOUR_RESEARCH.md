# PHASE 4 — MULTI-HOUR EDGE SEARCH

Research only · DEV split only · 60/20/20 preserved · no strategy, no backtest, no optimization.


## 1. Research objective


Phase 3 established that M5 is cost-deformed (best movement-to-cost 0.66; 100+ M5 behaviors below 1.0).  Phase 4 tests the central question: **does moving to ~1h–~24h horizons and session-open windows reveal a behavior with enough raw movement and stability to plausibly survive realistic costs?**  The answer is researched; a strategy is deliberately not implemented.

## 2. Data used


Consolidated M5 composites `data/{eurusd,eurgbp,gbpusd}_m5.csv` (5.7 years, 2021-01-03 → 2026-09-09), DEV rows only of the preserved chronological 60/20/20 split.  EURJPY is **excluded** (degraded feed: 14-month window, ~27% zero-spread bars; no safe handling demonstrated).

| symbol | dev_bars | first | last | spread_med_pips | cost_pips |
|---|---|---|---|---|---|
| EURUSD | 253,335 | 2021-01-03 22:00:00 | 2024-05-29 08:00:00 | 0.30 | 2.30 |
| EURGBP | 255,286 | 2021-01-03 22:00:00 | 2024-05-30 15:15:00 | 0.90 | 3.50 |
| GBPUSD | 224,848 | 2021-01-03 22:00:00 | 2024-06-13 18:25:00 | 0.90 | 3.50 |

## 3. Data quality


Same assessment as Phase 3 for the three core pairs: no duplicated timestamps, ~0.1% step gaps at weekend/session breaks, spread column never zero and of plausible magnitude, `real_volume` all zero and unused.  Spreads are modeled, not live ticks; costs assume 2×median dev spread + 1.7 pips round turn (EURUSD 2.30, EURGBP 3.50, GBPUSD 3.50).  Reported numbers are raw market movement, medians shown alongside means because means are sensitive to outliers.

## 4. Horizons investigated


A small, economically separated ladder (no sweep): H = 12, 24, 48, 96, 144, 240, 288 M5 bars = ~1h, ~2h, ~4h, ~8h, ~12h, ~20h, ~24h.  These answer TASK.md's requirement (≈1h through ≈20–24h) with clearly separated measurement periods.  Forward returns are measured on overlapping windows (consecutive bar starts), consistent with Phase 3.

## 5. Multi-hour directional behavior


`cont prior-H%` = share where the H-forward move continues the sign of the prior H-bar move; `cont 1-bar%` = share continuing the sign of the last M5 move.  All values pips, dev split.


### EURUSD

| symbol | H_h | n | mean | med | std | p_pos% | cont_priorH% | cont_1bar% |
|---|---|---|---|---|---|---|---|---|
| EURUSD | 1 | 253,323 | -0.07 | 0.00 | 10.68 | 49.7 | 48.7 | 49.0 |
| EURUSD | 2 | 253,311 | -0.13 | 0.00 | 15.05 | 49.9 | 49.0 | 49.4 |
| EURUSD | 4 | 253,287 | -0.26 | 0.00 | 21.27 | 49.8 | 49.8 | 49.7 |
| EURUSD | 8 | 253,239 | -0.53 | -0.10 | 30.07 | 49.6 | 49.1 | 49.9 |
| EURUSD | 12 | 253,191 | -0.80 | -0.40 | 36.67 | 49.3 | 48.4 | 49.8 |
| EURUSD | 20 | 253,095 | -1.33 | -0.70 | 46.75 | 49.2 | 48.5 | 49.8 |
| EURUSD | 24 | 253,047 | -1.59 | -0.90 | 51.13 | 49.0 | 49.2 | 49.8 |

### EURGBP

| symbol | H_h | n | mean | med | std | p_pos% | cont_priorH% | cont_1bar% |
|---|---|---|---|---|---|---|---|---|
| EURGBP | 1 | 255,274 | -0.02 | 0.00 | 6.89 | 49.2 | 47.8 | 48.8 |
| EURGBP | 2 | 255,262 | -0.04 | -0.10 | 9.63 | 49.2 | 47.8 | 48.8 |
| EURGBP | 4 | 255,238 | -0.08 | -0.10 | 13.55 | 49.1 | 48.2 | 49.1 |
| EURGBP | 8 | 255,190 | -0.17 | -0.20 | 19.00 | 49.0 | 47.9 | 49.3 |
| EURGBP | 12 | 255,142 | -0.25 | -0.60 | 22.97 | 48.3 | 47.9 | 49.5 |
| EURGBP | 20 | 255,046 | -0.45 | -1.30 | 29.23 | 47.6 | 48.6 | 49.6 |
| EURGBP | 24 | 254,998 | -0.55 | -1.50 | 31.71 | 47.5 | 49.8 | 49.6 |

### GBPUSD

| symbol | H_h | n | mean | med | std | p_pos% | cont_priorH% | cont_1bar% |
|---|---|---|---|---|---|---|---|---|
| GBPUSD | 1 | 224,836 | -0.05 | 0.00 | 15.65 | 49.8 | 48.8 | 49.2 |
| GBPUSD | 2 | 224,824 | -0.10 | 0.10 | 22.02 | 50.0 | 48.8 | 49.4 |
| GBPUSD | 4 | 224,800 | -0.19 | 0.00 | 31.10 | 50.0 | 49.4 | 49.7 |
| GBPUSD | 8 | 224,752 | -0.39 | 0.10 | 44.36 | 50.0 | 48.7 | 49.6 |
| GBPUSD | 12 | 224,704 | -0.58 | 0.10 | 54.07 | 50.0 | 48.5 | 49.8 |
| GBPUSD | 20 | 224,608 | -0.94 | 0.00 | 68.84 | 50.0 | 49.7 | 49.7 |
| GBPUSD | 24 | 224,560 | -1.10 | 0.50 | 75.12 | 50.3 | 49.2 | 49.8 |

## 6. Multi-hour reversal behavior


For windows of 2h (H=24) and 8h (H=96): a move is 'unusually large' when |prior move| exceeds the 66th percentile of |prior moves| (single fixed tercile cut, not swept).  Returns in pips; `rev%` = share where the next window reverses the prior large move; `cont%` = share continuing it.


### EURUSD

| symbol | condition | H_h | n | mean_pips | med_pips | rev% | cont% |
|---|---|---|---|---|---|---|---|
| EURUSD | threshold 2h-cut | 2 | - | - | 10.00 | - | - |
| EURUSD | prior up large | 2 | 41,912 | -0.38 | -0.50 | 51.8 | 48.2 |
| EURUSD | prior dn large | 2 | 43,863 | 0.12 | 0.20 | 50.9 | 49.1 |
| EURUSD | threshold 8h-cut | 8 | - | - | 22.30 | - | - |
| EURUSD | prior up large | 8 | 40,805 | -1.69 | -1.10 | 52.3 | 47.7 |
| EURUSD | prior dn large | 8 | 44,984 | -0.28 | -0.40 | 49.2 | 50.8 |

### EURGBP

| symbol | condition | H_h | n | mean_pips | med_pips | rev% | cont% |
|---|---|---|---|---|---|---|---|
| EURGBP | threshold 2h-cut | 2 | - | - | 6.20 | - | - |
| EURGBP | prior up large | 2 | 42,208 | -0.42 | -0.60 | 53.3 | 46.7 |
| EURGBP | prior dn large | 2 | 44,159 | 0.21 | 0.20 | 51.2 | 48.8 |
| EURGBP | threshold 8h-cut | 8 | - | - | 13.10 | - | - |
| EURGBP | prior up large | 8 | 41,270 | -1.05 | -1.10 | 53.4 | 46.6 |
| EURGBP | prior dn large | 8 | 45,480 | 0.62 | 0.90 | 53.1 | 46.9 |

### GBPUSD

| symbol | condition | H_h | n | mean_pips | med_pips | rev% | cont% |
|---|---|---|---|---|---|---|---|
| GBPUSD | threshold 2h-cut | 2 | - | - | 14.00 | - | - |
| GBPUSD | prior up large | 2 | 37,936 | -0.24 | -0.40 | 51.1 | 48.9 |
| GBPUSD | prior dn large | 2 | 38,417 | 0.54 | 0.60 | 51.6 | 48.4 |
| GBPUSD | threshold 8h-cut | 8 | - | - | 31.40 | - | - |
| GBPUSD | prior up large | 8 | 37,369 | -0.80 | -1.20 | 51.6 | 48.4 |
| GBPUSD | prior dn large | 8 | 38,893 | 0.54 | 2.10 | 52.6 | 47.4 |

## 7. Session-open behavior


For London (07:00), London/NY overlap (12:00) and New York (16:00) opens: movement between the open bar and the close of the first 1h/2h/4h; `expansion_ratio` = mean first-1h bar range / symbol median 1h bar range.  Then, after a directional first hour (above the open-type median), does the NEXT hour reverse or continue?


### EURUSD

| symbol | window | N_h | n_opens | mean_pips | med_pips | p_pos% | expansion_ratio |
|---|---|---|---|---|---|---|---|
| EURUSD | London open | 1 | 881 | -0.03 | -0.20 | 49.0 | 1.75 |
| EURUSD | London open | 2 | 881 | 0.22 | 1.15 | 52.3 | - |
| EURUSD | London open | 4 | 881 | -0.12 | 0.40 | 50.5 | - |
| EURUSD | LondonNY open | 1 | 879 | -0.28 | -0.40 | 47.7 | 2.02 |
| EURUSD | LondonNY open | 2 | 879 | -0.11 | -0.20 | 49.5 | - |
| EURUSD | LondonNY open | 4 | 879 | -0.30 | -0.70 | 49.0 | - |
| EURUSD | NewYork open | 1 | 879 | -0.11 | -0.20 | 49.4 | 1.44 |
| EURUSD | NewYork open | 2 | 879 | 0.10 | 0.70 | 53.1 | - |
| EURUSD | NewYork open | 4 | 879 | 0.47 | 1.00 | 52.9 | - |

### EURGBP

| symbol | window | N_h | n_opens | mean_pips | med_pips | p_pos% | expansion_ratio |
|---|---|---|---|---|---|---|---|
| EURGBP | London open | 1 | 888 | -0.08 | -0.10 | 48.8 | 1.82 |
| EURGBP | London open | 2 | 888 | 0.32 | 0.10 | 50.3 | - |
| EURGBP | London open | 4 | 888 | 0.26 | -0.30 | 48.8 | - |
| EURGBP | LondonNY open | 1 | 887 | 0.32 | 0.50 | 52.6 | 1.83 |
| EURGBP | LondonNY open | 2 | 887 | 0.21 | -0.30 | 48.6 | - |
| EURGBP | LondonNY open | 4 | 887 | -0.37 | -1.15 | 47.4 | - |
| EURGBP | NewYork open | 1 | 886 | -0.05 | -0.20 | 48.4 | 1.38 |
| EURGBP | NewYork open | 2 | 886 | -0.10 | -0.10 | 47.7 | - |
| EURGBP | NewYork open | 4 | 886 | -0.11 | 0.00 | 49.4 | - |

### GBPUSD

| symbol | window | N_h | n_opens | mean_pips | med_pips | p_pos% | expansion_ratio |
|---|---|---|---|---|---|---|---|
| GBPUSD | London open | 1 | 782 | -0.09 | -0.50 | 49.2 | 1.68 |
| GBPUSD | London open | 2 | 782 | -0.61 | -0.55 | 48.6 | - |
| GBPUSD | London open | 4 | 782 | -1.05 | -1.35 | 47.3 | - |
| GBPUSD | LondonNY open | 1 | 782 | -0.50 | -1.00 | 48.1 | 1.94 |
| GBPUSD | LondonNY open | 2 | 782 | 0.06 | -0.55 | 49.1 | - |
| GBPUSD | LondonNY open | 4 | 782 | 0.84 | 1.30 | 51.4 | - |
| GBPUSD | NewYork open | 1 | 782 | -0.02 | 0.60 | 51.5 | 1.38 |
| GBPUSD | NewYork open | 2 | 782 | 0.26 | 0.80 | 51.8 | - |
| GBPUSD | NewYork open | 4 | 782 | 0.44 | 0.30 | 50.6 | - |

## 8. Volatility-expansion behavior


Causal ATR(14) regimes (33/67 quantiles of 50 bars).  `expansion_event` = entering the high regime.  Forward returns over 2h/4h/8h; `cont%` = continuation of the prior M5 move -> directional vs mean-reverting classification.


### EURUSD

| symbol | regime | H_h | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURUSD | low | 2 | 115,295 | -0.22 | 0.00 | 49.1 | 49.9 |
| EURUSD | low | 4 | 115,275 | -0.31 | 0.10 | 49.5 | 50.1 |
| EURUSD | low | 8 | 115,264 | -0.82 | -0.20 | 49.9 | 49.4 |
| EURUSD | normal | 2 | 44,468 | -0.13 | -0.10 | 49.6 | 49.5 |
| EURUSD | normal | 4 | 44,464 | -0.34 | 0.00 | 49.9 | 49.9 |
| EURUSD | normal | 8 | 44,452 | -0.54 | 0.00 | 49.6 | 49.9 |
| EURUSD | high | 2 | 93,548 | -0.03 | 0.10 | 49.8 | 50.1 |
| EURUSD | high | 4 | 93,548 | -0.17 | -0.20 | 49.8 | 49.4 |
| EURUSD | high | 8 | 93,523 | -0.16 | -0.10 | 50.0 | 49.8 |

### EURGBP

| symbol | regime | H_h | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| EURGBP | low | 2 | 121,577 | -0.21 | -0.20 | 48.6 | 47.9 |
| EURGBP | low | 4 | 121,566 | -0.30 | -0.20 | 49.0 | 48.2 |
| EURGBP | low | 8 | 121,550 | 0.04 | -0.10 | 49.4 | 49.4 |
| EURGBP | normal | 2 | 46,802 | 0.13 | 0.10 | 48.9 | 50.4 |
| EURGBP | normal | 4 | 46,799 | 0.07 | 0.10 | 49.1 | 50.1 |
| EURGBP | normal | 8 | 46,789 | -0.35 | -0.30 | 49.1 | 48.8 |
| EURGBP | high | 2 | 86,883 | 0.10 | 0.10 | 49.0 | 50.5 |
| EURGBP | high | 4 | 86,873 | 0.14 | 0.00 | 49.3 | 49.9 |
| EURGBP | high | 8 | 86,851 | -0.36 | -0.50 | 49.4 | 48.5 |

### GBPUSD

| symbol | regime | H_h | n | mean_pips | med_pips | cont% | p_pos% |
|---|---|---|---|---|---|---|---|
| GBPUSD | low | 2 | 102,927 | -0.28 | 0.00 | 49.2 | 49.7 |
| GBPUSD | low | 4 | 102,914 | -0.22 | 0.00 | 49.5 | 49.9 |
| GBPUSD | low | 8 | 102,913 | -0.90 | -0.20 | 49.5 | 49.5 |
| GBPUSD | normal | 2 | 40,311 | -0.16 | 0.00 | 49.3 | 49.8 |
| GBPUSD | normal | 4 | 40,301 | -0.30 | -0.20 | 49.6 | 49.4 |
| GBPUSD | normal | 8 | 40,287 | -0.10 | 0.40 | 49.8 | 50.5 |
| GBPUSD | high | 2 | 81,586 | 0.17 | 0.20 | 49.7 | 50.5 |
| GBPUSD | high | 4 | 81,585 | -0.12 | 0.20 | 50.0 | 50.4 |
| GBPUSD | high | 8 | 81,552 | 0.11 | 0.40 | 49.6 | 50.4 |

## 9. Multi-hour breakout structure


(i) 24h channel (prior 288 bars): up/down break measured over the following 1h/2h/4h, with continuation and persistence (close beyond the broken level).  (ii) London-open break of the prior 12h window (overnight-range proxy): forward 1h/2h continuation/failure.


### EURUSD

| symbol | break | H_h | n | mean_pips | med_pips | cont% | persist%/p_pos% |
|---|---|---|---|---|---|---|---|
| EURUSD | 24h up-break | 1 | 6,144 | -1.00 | -0.60 | 46.7 | 56.1 |
| EURUSD | 24h up-break | 2 | 6,144 | -1.21 | -0.90 | 46.3 | 53.1 |
| EURUSD | 24h up-break | 4 | 6,144 | -1.51 | -1.30 | 46.5 | 51.8 |
| EURUSD | 24h dn-break | 1 | 6,408 | -0.10 | 0.40 | 48.1 | 57.2 |
| EURUSD | 24h dn-break | 2 | 6,408 | -0.15 | 0.45 | 48.2 | 55.5 |
| EURUSD | 24h dn-break | 4 | 6,406 | 0.25 | 0.50 | 48.9 | 54.1 |

### EURGBP

| symbol | break | H_h | n | mean_pips | med_pips | cont% | persist%/p_pos% |
|---|---|---|---|---|---|---|---|
| EURGBP | 24h up-break | 1 | 5,517 | -0.40 | -0.70 | 45.3 | 54.5 |
| EURGBP | 24h up-break | 2 | 5,515 | -0.55 | -0.80 | 45.6 | 52.5 |
| EURGBP | 24h up-break | 4 | 5,514 | -0.60 | -1.45 | 45.0 | 49.5 |
| EURGBP | 24h dn-break | 1 | 5,967 | 0.58 | 0.50 | 46.0 | 54.9 |
| EURGBP | 24h dn-break | 2 | 5,967 | 0.83 | 0.90 | 44.7 | 52.4 |
| EURGBP | 24h dn-break | 4 | 5,967 | 1.03 | 0.80 | 46.7 | 52.0 |

### GBPUSD

| symbol | break | H_h | n | mean_pips | med_pips | cont% | persist%/p_pos% |
|---|---|---|---|---|---|---|---|
| GBPUSD | 24h up-break | 1 | 5,773 | -0.83 | -0.90 | 46.6 | 56.6 |
| GBPUSD | 24h up-break | 2 | 5,773 | -0.69 | -0.50 | 48.6 | 55.7 |
| GBPUSD | 24h up-break | 4 | 5,773 | -0.42 | -0.10 | 49.8 | 54.6 |
| GBPUSD | 24h dn-break | 1 | 5,744 | 0.25 | 0.80 | 47.3 | 57.0 |
| GBPUSD | 24h dn-break | 2 | 5,741 | 0.17 | 1.00 | 47.7 | 54.8 |
| GBPUSD | 24h dn-break | 4 | 5,733 | 0.04 | 0.40 | 49.3 | 54.8 |

## 10. Pair comparison


`med|1h|` = median |1-hour move| pips; `med_range` M5 bar range; `med_atr` M5 ATR(14); `spread_med` pips; `cost` pips; `rho1` 1-bar (M5) return autocorr; `persist1h%` = 1h forward continuing prior-1h sign; `rev_large%` = 1h forward reversing an unusually large prior-1h move; `max_dir` = max |mean| forward move 1h–4h in either direction; `mov/cost` and `edge/cost` = ratios.

| symbol | med|1h| | med_range | med_atr | spread_med | cost | rho1 | persist1h% | rev_large% | max_dir | mov/cost | edge/cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 4.50 | 3.00 | 3.34 | 0.30 | 2.30 | -0.01 | 48.7 | 51.2 | 0.30 | 1.96 | 0.13 |
| EURGBP | 2.80 | 2.10 | 2.35 | 0.90 | 3.50 | -0.00 | 47.8 | 52.5 | 0.45 | 0.80 | 0.13 |
| GBPUSD | 6.20 | 4.20 | 4.64 | 0.90 | 3.50 | -0.00 | 48.8 | 51.0 | 0.47 | 1.77 | 0.13 |

## 11. Signal-to-cost analysis


For every behavior/condition/horizon with n ≥ 1000: ratio = |raw expected movement| / realistic round-trip cost.  Classification: **potentially viable** (ratio ≥ 1.0 and |mean| ≥ 2.0 pips), **borderline** (0.5 ≤ ratio < 1.0), **economically insufficient** (ratio < 0.5).  Sorting best-first.

| cls | sym | behavior | condition | H_min | n | mean | med | hit% | std | cost | ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BORDER | EURUSD | multi-hour reversal | prior up-8h large move, next 8h | 480 | 40,805 | -1.69 | -1.10 | 47.6 | 31.29 | 2.30 | 0.73 |
| BORDER | EURUSD | breakout_24h | 24h up-break after 4h | 240 | 6,144 | -1.51 | -1.30 | 46.4 | 24.25 | 2.30 | 0.66 |
| BORDER | EURUSD | session_open_window_bars | in London-open first 4h window -> forward 4h | 240 | 42,240 | -1.39 | -1.10 | 47.8 | 26.60 | 2.30 | 0.60 |
| BORDER | EURUSD | breakout_24h | 24h up-break after 2h | 120 | 6,144 | -1.21 | -0.90 | 46.1 | 18.54 | 2.30 | 0.53 |
| INSUFF | EURUSD | breakout_24h | 24h up-break after 1h | 60 | 6,144 | -1.00 | -0.60 | 46.5 | 13.44 | 2.30 | 0.44 |
| INSUFF | EURUSD | vol_expansion | low after 8h | 480 | 115,264 | -0.82 | -0.20 | 49.4 | 25.18 | 2.30 | 0.36 |
| INSUFF | EURGBP | multi-hour reversal | prior up-8h large move, next 8h | 480 | 41,270 | -1.05 | -1.10 | 46.5 | 24.25 | 3.50 | 0.30 |
| INSUFF | EURGBP | breakout_24h | 24h dn-break after 4h | 240 | 5,967 | 1.03 | 0.80 | 53.1 | 14.45 | 3.50 | 0.29 |
| INSUFF | GBPUSD | session_open_window_bars | in London-open first 4h window -> forward 4h | 240 | 37,536 | -1.00 | 0.00 | 49.9 | 36.73 | 3.50 | 0.29 |
| INSUFF | EURGBP | session_open_window_bars | in NewYork-open first 4h window -> forward 4h | 240 | 42,528 | -0.97 | -0.70 | 43.8 | 7.89 | 3.50 | 0.28 |
| INSUFF | GBPUSD | vol_expansion | low after 8h | 480 | 102,913 | -0.90 | -0.20 | 49.5 | 42.03 | 3.50 | 0.26 |
| INSUFF | GBPUSD | session_open_window_bars | in LondonNY-open first 4h window -> forward 4h | 240 | 37,518 | 0.85 | 0.90 | 51.1 | 36.96 | 3.50 | 0.24 |
| INSUFF | EURGBP | breakout_24h | 24h dn-break after 2h | 120 | 5,967 | 0.83 | 0.90 | 55.0 | 11.04 | 3.50 | 0.24 |
| INSUFF | GBPUSD | breakout_24h | 24h up-break after 1h | 60 | 5,773 | -0.83 | -0.90 | 46.4 | 17.47 | 3.50 | 0.24 |
| INSUFF | EURUSD | vol_expansion | normal after 8h | 480 | 44,452 | -0.54 | 0.00 | 49.9 | 31.61 | 2.30 | 0.24 |
| INSUFF | GBPUSD | multi-hour reversal | prior up-8h large move, next 8h | 480 | 37,369 | -0.80 | -1.20 | 48.3 | 43.24 | 3.50 | 0.23 |
| INSUFF | GBPUSD | breakout_24h | 24h up-break after 2h | 120 | 5,773 | -0.69 | -0.50 | 48.4 | 22.98 | 3.50 | 0.20 |
| INSUFF | GBPUSD | session_open_window_bars | in LondonNY-open first 2h window -> forward 2h | 120 | 18,768 | 0.66 | 0.10 | 50.1 | 33.01 | 3.50 | 0.19 |
| INSUFF | EURGBP | multi-hour reversal | prior dn-8h large move, next 8h | 480 | 45,480 | 0.62 | 0.90 | 52.9 | 18.29 | 3.50 | 0.18 |
| INSUFF | EURGBP | breakout_24h | 24h up-break after 4h | 240 | 5,514 | -0.60 | -1.45 | 44.8 | 18.05 | 3.50 | 0.17 |
| INSUFF | EURGBP | breakout_24h | 24h dn-break after 1h | 60 | 5,967 | 0.58 | 0.50 | 53.6 | 8.00 | 3.50 | 0.17 |
| INSUFF | EURUSD | multi-hour reversal | prior up-2h large move, next 2h | 120 | 41,912 | -0.38 | -0.50 | 48.0 | 18.69 | 2.30 | 0.16 |
| INSUFF | EURGBP | breakout_24h | 24h up-break after 2h | 120 | 5,515 | -0.55 | -0.80 | 45.4 | 12.57 | 3.50 | 0.16 |
| INSUFF | EURGBP | session_open_window_bars | in LondonNY-open first 4h window -> forward 4h | 240 | 42,528 | -0.54 | -0.90 | 46.6 | 15.15 | 3.50 | 0.16 |
| INSUFF | GBPUSD | multi-hour reversal | prior dn-8h large move, next 8h | 480 | 38,893 | 0.54 | 2.10 | 52.6 | 53.18 | 3.50 | 0.15 |
| INSUFF | GBPUSD | multi-hour reversal | prior dn-2h large move, next 2h | 120 | 38,417 | 0.54 | 0.60 | 51.4 | 24.59 | 3.50 | 0.15 |
| INSUFF | EURUSD | session_open_window_bars | in NewYork-open first 4h window -> forward 4h | 240 | 42,192 | 0.34 | 0.30 | 51.1 | 15.28 | 2.30 | 0.15 |
| INSUFF | EURUSD | vol_expansion | normal after 4h | 240 | 44,464 | -0.34 | 0.00 | 49.9 | 22.65 | 2.30 | 0.15 |
| INSUFF | EURUSD | vol_expansion | low after 4h | 240 | 115,275 | -0.31 | 0.10 | 50.1 | 18.56 | 2.30 | 0.14 |
| INSUFF | GBPUSD | breakout_24h | 24h up-break after 4h | 240 | 5,773 | -0.42 | -0.10 | 49.7 | 31.33 | 3.50 | 0.12 |
| INSUFF | EURUSD | multi-hour reversal | prior dn-8h large move, next 8h | 480 | 44,984 | -0.28 | -0.40 | 49.1 | 31.67 | 2.30 | 0.12 |
| INSUFF | EURGBP | multi-hour reversal | prior up-2h large move, next 2h | 120 | 42,208 | -0.42 | -0.60 | 46.5 | 12.54 | 3.50 | 0.12 |
| INSUFF | EURUSD | session_open_window_bars | in NewYork-open first 2h window -> forward 2h | 120 | 21,096 | 0.27 | 0.30 | 51.3 | 14.45 | 2.30 | 0.12 |
| INSUFF | EURGBP | breakout_24h | 24h up-break after 1h | 60 | 5,517 | -0.40 | -0.70 | 45.0 | 9.49 | 3.50 | 0.11 |
| INSUFF | GBPUSD | session_open_window_bars | in London-open first 2h window -> forward 2h | 120 | 18,768 | -0.39 | 0.00 | 49.9 | 23.67 | 3.50 | 0.11 |
| INSUFF | EURUSD | breakout_24h | 24h dn-break after 4h | 240 | 6,406 | 0.25 | 0.50 | 51.0 | 24.18 | 2.30 | 0.11 |
| INSUFF | EURGBP | vol_expansion | high after 8h | 480 | 86,851 | -0.36 | -0.50 | 48.5 | 22.11 | 3.50 | 0.10 |
| INSUFF | EURGBP | vol_expansion | normal after 8h | 480 | 46,789 | -0.35 | -0.30 | 48.8 | 18.75 | 3.50 | 0.10 |
| INSUFF | EURUSD | vol_expansion | low after 2h | 120 | 115,295 | -0.22 | 0.00 | 49.9 | 12.91 | 2.30 | 0.09 |
| INSUFF | EURGBP | vol_expansion | low after 4h | 240 | 121,566 | -0.30 | -0.20 | 48.2 | 10.70 | 3.50 | 0.09 |
| INSUFF | GBPUSD | vol_expansion | normal after 4h | 240 | 40,301 | -0.30 | -0.20 | 49.4 | 32.08 | 3.50 | 0.09 |
| INSUFF | GBPUSD | vol_expansion | low after 2h | 120 | 102,927 | -0.28 | 0.00 | 49.7 | 20.86 | 3.50 | 0.08 |
| INSUFF | EURUSD | session_open_window_bars | in LondonNY-open first 1h window -> forward 1h | 60 | 10,548 | -0.17 | -0.20 | 49.2 | 18.07 | 2.30 | 0.07 |
| INSUFF | EURUSD | vol_expansion | high after 4h | 240 | 93,548 | -0.17 | -0.20 | 49.4 | 23.60 | 2.30 | 0.07 |
| INSUFF | GBPUSD | session_open_window_bars | in NewYork-open first 2h window -> forward 2h | 120 | 18,750 | 0.25 | 0.10 | 50.2 | 19.04 | 3.50 | 0.07 |
| INSUFF | GBPUSD | session_open_window_bars | in LondonNY-open first 1h window -> forward 1h | 60 | 9,384 | -0.25 | -0.40 | 48.7 | 23.00 | 3.50 | 0.07 |
| INSUFF | EURUSD | vol_expansion | high after 8h | 480 | 93,523 | -0.16 | -0.10 | 49.8 | 34.53 | 2.30 | 0.07 |
| INSUFF | GBPUSD | breakout_24h | 24h dn-break after 1h | 60 | 5,744 | 0.25 | 0.80 | 52.5 | 18.19 | 3.50 | 0.07 |
| INSUFF | GBPUSD | session_open_window_bars | in NewYork-open first 4h window -> forward 4h | 240 | 37,488 | 0.24 | 0.00 | 49.9 | 20.52 | 3.50 | 0.07 |
| INSUFF | GBPUSD | multi-hour reversal | prior up-2h large move, next 2h | 120 | 37,936 | -0.24 | -0.40 | 48.8 | 25.84 | 3.50 | 0.07 |
| INSUFF | EURGBP | session_open_window_bars | in London-open first 4h window -> forward 4h | 240 | 42,624 | -0.23 | -0.60 | 48.2 | 18.59 | 3.50 | 0.07 |
| INSUFF | EURUSD | breakout_24h | 24h dn-break after 2h | 120 | 6,408 | -0.15 | 0.45 | 51.6 | 17.34 | 2.30 | 0.07 |
| INSUFF | GBPUSD | vol_expansion | low after 4h | 240 | 102,914 | -0.22 | 0.00 | 49.9 | 29.35 | 3.50 | 0.06 |
| INSUFF | EURGBP | multi-hour reversal | prior dn-2h large move, next 2h | 120 | 44,159 | 0.21 | 0.20 | 50.9 | 12.04 | 3.50 | 0.06 |
| INSUFF | EURGBP | vol_expansion | low after 2h | 120 | 121,577 | -0.21 | -0.20 | 47.9 | 7.41 | 3.50 | 0.06 |
| INSUFF | EURUSD | vol_expansion | normal after 2h | 120 | 44,468 | -0.13 | -0.10 | 49.5 | 15.07 | 2.30 | 0.05 |
| INSUFF | EURUSD | multi-hour reversal | prior dn-2h large move, next 2h | 120 | 43,863 | 0.12 | 0.20 | 50.7 | 17.64 | 2.30 | 0.05 |
| INSUFF | EURUSD | session_open_window_bars | in London-open first 1h window -> forward 1h | 60 | 10,561 | 0.12 | 0.40 | 51.1 | 13.27 | 2.30 | 0.05 |
| INSUFF | GBPUSD | vol_expansion | high after 2h | 120 | 81,586 | 0.17 | 0.20 | 50.5 | 23.24 | 3.50 | 0.05 |
| INSUFF | GBPUSD | breakout_24h | 24h dn-break after 2h | 120 | 5,741 | 0.17 | 1.00 | 52.1 | 24.61 | 3.50 | 0.05 |
| INSUFF | EURUSD | session_open_window_bars | in London-open first 2h window -> forward 2h | 120 | 21,120 | -0.11 | 0.40 | 51.1 | 17.14 | 2.30 | 0.05 |
| INSUFF | GBPUSD | vol_expansion | normal after 2h | 120 | 40,311 | -0.16 | 0.00 | 49.8 | 22.39 | 3.50 | 0.05 |
| INSUFF | EURUSD | breakout_24h | 24h dn-break after 1h | 60 | 6,408 | -0.10 | 0.40 | 51.7 | 12.66 | 2.30 | 0.04 |
| INSUFF | GBPUSD | session_open_window_bars | in NewYork-open first 1h window -> forward 1h | 60 | 9,384 | 0.15 | 0.40 | 51.3 | 13.20 | 3.50 | 0.04 |
| INSUFF | EURGBP | vol_expansion | high after 4h | 240 | 86,873 | 0.14 | 0.00 | 49.9 | 16.63 | 3.50 | 0.04 |
| INSUFF | EURGBP | vol_expansion | normal after 2h | 120 | 46,802 | 0.13 | 0.10 | 50.4 | 9.75 | 3.50 | 0.04 |
| INSUFF | GBPUSD | session_open_window_bars | in London-open first 1h window -> forward 1h | 60 | 9,384 | -0.13 | 0.10 | 50.2 | 17.84 | 3.50 | 0.04 |
| INSUFF | GBPUSD | vol_expansion | high after 4h | 240 | 81,585 | -0.12 | 0.20 | 50.4 | 32.73 | 3.50 | 0.03 |
| INSUFF | EURGBP | session_open_window_bars | in LondonNY-open first 1h window -> forward 1h | 60 | 10,644 | 0.12 | 0.10 | 50.2 | 9.26 | 3.50 | 0.03 |
| INSUFF | GBPUSD | vol_expansion | high after 8h | 480 | 81,552 | 0.11 | 0.40 | 50.4 | 47.95 | 3.50 | 0.03 |
| INSUFF | EURGBP | session_open_window_bars | in NewYork-open first 1h window -> forward 1h | 60 | 10,632 | -0.11 | -0.10 | 48.3 | 5.95 | 3.50 | 0.03 |
| INSUFF | GBPUSD | vol_expansion | normal after 8h | 480 | 40,287 | -0.10 | 0.40 | 50.5 | 42.56 | 3.50 | 0.03 |
| INSUFF | EURGBP | vol_expansion | high after 2h | 120 | 86,883 | 0.10 | 0.10 | 50.5 | 12.02 | 3.50 | 0.03 |
| INSUFF | EURGBP | session_open_window_bars | in London-open first 1h window -> forward 1h | 60 | 10,656 | 0.09 | -0.10 | 49.5 | 9.42 | 3.50 | 0.02 |
| INSUFF | EURUSD | session_open_window_bars | in LondonNY-open first 2h window -> forward 2h | 120 | 21,096 | 0.06 | -0.40 | 49.0 | 25.42 | 2.30 | 0.02 |
| INSUFF | EURGBP | vol_expansion | normal after 4h | 240 | 46,799 | 0.07 | 0.10 | 50.1 | 13.80 | 3.50 | 0.02 |
| INSUFF | EURGBP | session_open_window_bars | in NewYork-open first 2h window -> forward 2h | 120 | 21,264 | -0.07 | 0.00 | 49.2 | 7.21 | 3.50 | 0.02 |
| INSUFF | EURUSD | session_open_window_bars | in LondonNY-open first 4h window -> forward 4h | 240 | 42,192 | -0.05 | -0.10 | 49.6 | 27.71 | 2.30 | 0.02 |
| INSUFF | EURGBP | session_open_window_bars | in London-open first 2h window -> forward 2h | 120 | 21,312 | -0.05 | -0.30 | 48.3 | 12.93 | 3.50 | 0.01 |
| INSUFF | EURUSD | vol_expansion | high after 2h | 120 | 93,548 | -0.03 | 0.10 | 50.1 | 17.31 | 2.30 | 0.01 |
| INSUFF | EURGBP | vol_expansion | low after 8h | 480 | 121,550 | 0.04 | -0.10 | 49.4 | 16.52 | 3.50 | 0.01 |
| INSUFF | GBPUSD | breakout_24h | 24h dn-break after 4h | 240 | 5,733 | 0.04 | 0.40 | 50.6 | 33.70 | 3.50 | 0.01 |
| INSUFF | EURUSD | session_open_window_bars | in NewYork-open first 1h window -> forward 1h | 60 | 10,548 | 0.02 | 0.00 | 50.0 | 9.95 | 2.30 | 0.01 |
| INSUFF | EURGBP | session_open_window_bars | in LondonNY-open first 2h window -> forward 2h | 120 | 21,280 | -0.03 | -0.60 | 48.0 | 13.31 | 3.50 | 0.01 |

## 12. Strongest economically viable behaviors


No behavior clears the `potentially viable` bar on the DEV split.  The best raw ratios on DEV are listed in section 11; the strongest of them are reported in section 14.

## 13. Behaviors rejected


Rejected / economically insufficient on the DEV split:

- Multi-hour continuation of large moves (section 5/6): hit rates ~50% and forward means near zero or negative after cost.
- Short-window continuation at any M5-derived horizon (cost-dominated).
- Breakout continuation at 1h–4h after 24h-channel breaks (negative forward means; see section 9).
- Session-open drift at 1h/2h on London, LondonNY and NewYork (means below cost; section 7).
- Any EURJPY-based behavior (excluded on data quality).
- Volume-based behaviors (`real_volume` is all zeros).

## 14. Exact evidence for any candidate

No candidate clears the viability bar.  Closest raw behaviors on DEV (still below it):
- EURUSD / multi-hour reversal / prior up-8h large move, next 8h @ H=480 min: n=40,805, raw mean -1.69, median -1.10, hit 47.6%, cost 2.30, movement-to-cost 0.73.
- EURUSD / breakout_24h / 24h up-break after 4h @ H=240 min: n=6,144, raw mean -1.51, median -1.30, hit 46.4%, cost 2.30, movement-to-cost 0.66.
- EURUSD / session_open_window_bars / in London-open first 4h window -> forward 4h @ H=240 min: n=42,240, raw mean -1.39, median -1.10, hit 47.8%, cost 2.30, movement-to-cost 0.60.
- EURUSD / breakout_24h / 24h up-break after 2h @ H=120 min: n=6,144, raw mean -1.21, median -0.90, hit 46.1%, cost 2.30, movement-to-cost 0.53.
- EURUSD / breakout_24h / 24h up-break after 1h @ H=60 min: n=6,144, raw mean -1.00, median -0.60, hit 46.5%, cost 2.30, movement-to-cost 0.44.

## 15. Limitations


- DEV only; validation/holdout never read; 60/20/20 preserved.
- Research only, no strategy/backtest/optimization; overlapping windows inflate effective n for high-horizon rows.
- Means are outlier-sensitive; medians reported alongside.
- Spread column is modeled, not live ticks; real execution costs could differ materially.
- Results are raw movement, not P&L; nothing is claimed profitable.

## 16. Recommended next action

**NO** — no multi-hour or session-open behavior on the current FX dataset clears the viability bar on DEV (best raw ratio 0.73; EURUSD / multi-hour reversal / prior up-8h large move, next 8h, mean -1.69 pips vs 2.30 pips cost).  The dataset does not currently provide enough evidence for a viable strategy.  Recommended next research directions, in order: (1) better/true spread data (the spread column is modeled, not live ticks) to re-examine real costs; (2) another timeframe (e.g., H1/H4 bar construction rather than M5 aggregation); (3) another instrument/market with structurally different spread-to-move ratios.  Do NOT invent a strategy simply because the phase needs one.
