# STRATEGY 02 — BREAKOUT FADE

Phase 2 · DEV split only · no optimization · source: MARKET_BEHAVIOR_DISCOVERY.md §11 Candidate #2


## 1. Frozen strategy rules (exactly as implemented)


| component | rule |
|---|---|
| Pairs | EURGBP, GBPUSD (EURJPY excluded per TASK.md) |
| Signal (breakout) | *closed* candle i: `close[i] > max(high[i-20..i-1])` → upside breakout; `close[i] < min(low[i-20..i-1])` → downside breakout (causal prior-20 channel, identical to discovery `_breakout_states`) |
| Trade (fade) | SELL after an upside breakout, BUY after a downside breakout |
| Session gate | signal candle hour UTC ∈ [07:00, 16:00) = London [7,12) ∪ LondonNY [12,16) — the discovery report's liquid-session condition |
| Entry | next candle OPEN (no lookahead) |
| Stop | 1.5 × ATR(14) from entry, invalidation of the fade — existing backtester's fixed StrategyConfig default (not invented, not tuned) |
| Target | 3.0 × ATR(14) — existing backtester default |
| Holding period | exit at close of entry-bar + 20 (max_hold_bars=20, discovery headline horizon H=20); SL/TP resolved first, conservatively |
| Position book | one position at a time (engine default); re-entry allowed on the next bar after an exit |
| Costs | observed spread of the ENTRY candle (×1, point-scaled) + 0.5 pip slippage per side + $7/lot commission at 0.10 lots |

Only implementation detail the discovery report left unspecified — the fixed-horizon exit — was expressed with the **minimal** additive engine extension `max_hold_bars` in `run_backtest` (existing callers unaffected). The backtester was not redesigned.


## 2. Data


| symbol | dev bars | from | to |
|---|---|---|---|
| EURGBP | 255,286 | 2021-01-03 22:00:00 | 2024-05-30 15:15:00 |
| GBPUSD | 224,848 | 2021-01-03 22:00:00 | 2024-06-13 18:25:00 |

DEV split only (split column = `dev`); validation and holdout rows are never read.


## 3. Overall results


| symbol | bars | trades | gross$ | gross_l$ | net$ | avg_net_pips | med_net_pips | win% | PF | maxDD$ | loss_streak | avg_hold_h |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EURGBP | 255,286 | 6,955 | 16,888.17 | 34,411.00 | -17,522.83 | -1.82 | -5.33 | 34.0 | 0.49 | 17,533.11 | 18 | 0.71 |
| GBPUSD | 224,848 | 6,499 | 35,836.18 | 53,335.04 | -17,498.86 | -1.99 | -8.89 | 34.8 | 0.67 | 17,524.97 | 17 | 0.68 |

Gross$ / gross_l$ / net$ and maxDD$ are USD at 0.10 lots. `win%` = share of trades with net_pips > 0. `loss_streak` = longest consecutive losing trades. `avg_hold_h` = mean holding time in hours.


### 3.1 All pairs combined

| kpi | value |
|---|---|
| trades | 13,454 |
| sum gross pips | 155.0 |
| total costs (pips) | 25,758.9 |
| sum net pips | -25,603.9 |
| avg net pips/trade | -1.903 |
| median net pips/trade | -6.14 |
| win rate (net pips > 0) | 35.2% |
| profit factor (net pips) | 0.69 |
| gross profit $ (winners) | 65,275.71 |
| gross loss $ (losers) | -65,120.71 |
| total costs $ | 35,176.70 |
| net profit $ | -35,021.69 |
| expectancy $/trade | -2.60 |
| t-test net-pips mean | t=-18.38, p=1.83e-75 |
| avg MAE / MFE (pips) | 7.81 / 9.30 |
| median MAE / MFE (pips) | 6.30 / 6.60 |
| avg holding time | 0.70 h |

Max drawdown across pairs is not a single pooled curve; per-pair maxDD$ is in the table above.


## 4. Per-pair t-test (net pips)


| symbol | n | mean | t | p |
|---|---:|---:|---:|---:|
| EURGBP | 6955 | -1.819 | -19.32 | 3.58e-83 |
| GBPUSD | 6499 | -1.993 | -10.53 | 6.01e-26 |

## 5. Per-session results (entry-candle session)


### EURGBP

| session | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| London | 4,065 | -7,915.56 | -1.95 | -5.20 | 34.37 |
| LondonNY | 2,830 | -4,799.17 | -1.70 | -5.64 | 35.58 |
| NewYork | 60 | 60.40 | 1.01 | 1.15 | 55.00 |

### GBPUSD

| session | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| London | 3,608 | -6,696.29 | -1.86 | -8.41 | 35.28 |
| LondonNY | 2,838 | -6,241.85 | -2.20 | -9.85 | 35.34 |
| NewYork | 53 | -11.42 | -0.22 | -7.00 | 41.51 |

## 6. Per-year results


### EURGBP

| year | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| 2,021 | 2,061 | -3,680.02 | -1.79 | -5.58 | 34.55 |
| 2,022 | 2,046 | -3,568.58 | -1.74 | -6.68 | 36.31 |
| 2,023 | 2,029 | -4,114.72 | -2.03 | -5.56 | 34.40 |
| 2,024 | 819 | -1,291.02 | -1.58 | -4.10 | 34.68 |

### GBPUSD

| year | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| 2,021 | 1,723 | -2,923.27 | -1.70 | -9.06 | 35.52 |
| 2,022 | 1,837 | -3,462.68 | -1.88 | -10.53 | 36.15 |
| 2,023 | 2,009 | -4,557.55 | -2.27 | -9.41 | 35.14 |
| 2,024 | 930 | -2,006.07 | -2.16 | -6.90 | 33.98 |

## 7. Exit reasons


### EURGBP

| reason | trades | share% | avg_net | win% |
|---|---|---|---|---|
| HOLD | 1,036 | 14.9 | 0.99 | 56.66 |
| SL | 4,065 | 58.4 | -7.37 | 0.00 |
| TP | 1,854 | 26.7 | 8.78 | 99.78 |

### GBPUSD

| reason | trades | share% | avg_net | win% |
|---|---|---|---|---|
| HOLD | 857 | 13.2 | 3.72 | 66.28 |
| SL | 3,912 | 60.2 | -12.52 | 0.00 |
| TP | 1,730 | 26.6 | 18.99 | 100.00 |

## 8. Interpretation


**Gross edge vs post-cost edge.** Report the gross sums explicitly: gross profit = 65,275.71$, gross loss = -65,120.71$, total costs = 35,176.70$.  The net result is **-35,021.69$** (-25,603.9 pips) on 13,454 trades, avg -2.60$/trade, PF 0.69, win rate 35.2%.

**Significance.** Combined t-test of net pips: t=-18.38, p=1.83e-75. A negative/positive mean at p<0.05 means the DEV sample itself deviates from zero; it says nothing yet about validation or the future.

**Robustness.** Year-by-year sign stability (section 6) and session-by-session stability (section 5) are the check: any year or session that flips sign to the opposite of the overall direction weakens the candidate's robustness claim. Note the session gate is applied to the signal candle, but entries can fill in an adjacent session boundary bar.

**No stop-optimization.** The 1.5/3.0 ATR risk model is the backtester's pre-existing default; the fixed 20-bar hold is the discovery headline horizon. No parameter was swept at any point and no alternative variant was evaluated. Strategy 01 remains untouched as the rejected historical experiment.

## 9. Does Candidate #2 deserve validation?


Pre-registered acceptance test (from discovery §11 Candidate #2), to be applied on the untouched VALIDATION split: **avg net >= cost + 0.5 pips AND hit >= 50% AND direction stable per session.**

**Verdict on the DEV sample (informational only — it is NOT a validation pass):** DEV post-cost edge = -1.903 pips/trade vs an acceptance threshold of about +2.415 pips/trade (avg cost 1.91 pips + 0.5). DEV sample FAILS the threshold, win rate 35.2% is below 50%. Per-session direction stability must be judged from section 5.

This report is DEV-only evidence: it does **not** test the validation split and therefore cannot approve or reject the candidate by itself. It records whether the dev numbers even point in the acceptance direction before any validation spend.
