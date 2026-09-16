# STRATEGY 03 — SESSION-GATED MEAN REVERSION

Phase 2 · DEV split only · no optimization · source: MARKET_BEHAVIOR_DISCOVERY.md §11 Candidate #3


## 1. Frozen strategy rules (exactly as implemented)


| component | rule |
|---|---|
| Pairs | EURUSD, EURGBP, GBPUSD (Candidate-1 pairs; EURJPY excluded) |
| Signal | *closed* candle i: (close[i] − SMA20)/STD20 (population std) ≤ −1.0 → LONG; ≥ +1.0 → SHORT |
| Session gate | the SIGNAL candle must be London [07:00,12:00) or LondonNY [12:00,16:00) UTC — the one conditioning change vs Candidate 1 |
| Entry | next candle OPEN (no lookahead) |
| Stop | 1.0 × ATR(14) of the signal candle, intrabar-resolved, stop-first |
| Take-profit | none (Candidate 1 has none) |
| Holding period | exit at the CLOSE of entry-bar + 40 bars if not stopped (Candidate-1 hold) |
| Position book | one position at a time |
| Costs | 2 × observed spread of the ENTRY candle (spread × point, in pips) + 1.7 pips slippage + commission; gross AND net reported |

Mechanics are byte-for-byte Candidate 1 (Strategy 01): the loop, ATR-at-signal-candle stop, hold-close exit and cost formula are identical. Strategy 01 code and outputs are untouched. The Candidate-1 baseline numbers below come from the archived `outputs/strategy_01_trades.json`.


## 2. Data


| symbol | dev bars | from | to |
|---|---|---|---|
| EURUSD | 253,335 | 2021-01-03 22:00:00 | 2024-05-29 08:00:00 |
| EURGBP | 255,286 | 2021-01-03 22:00:00 | 2024-05-30 15:15:00 |
| GBPUSD | 224,848 | 2021-01-03 22:00:00 | 2024-06-13 18:25:00 |

DEV split only (``outputs/splits/<SYMBOL>/assignments.csv``); validation and holdout rows are never read.


## 3. Overall results

| symbol | trades | gross_pips | cost_pips | net_pips | avg_net | med_net | win% | PF | dd_pips | loss_streak | avg_hold_h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 8,087 | 2,534.51 | 19,104.90 | -16,570.39 | -2.05 | -6.25 | 17.11 | 0.65 | 16,722.01 | 36 | 1.01 |
| EURGBP | 8,063 | 1,354.65 | 28,838.10 | -27,483.45 | -3.41 | -6.25 | 17.15 | 0.40 | 27,601.59 | 37 | 1.03 |
| GBPUSD | 7,219 | 2,344.16 | 25,326.70 | -22,982.54 | -3.18 | -8.92 | 17.11 | 0.62 | 23,082.85 | 37 | 1.02 |

`win%` = share of trades with net_pips > 0. `dd_pips` = max peak-to-trough drawdown of the cumulative net-pips curve. PF is on net pips.


### 3.1 Combined

| kpi | value |
|---|---|
| trades | 23,369 |
| sum gross pips | 6,233.3 |
| total costs (pips) | 73,269.7 |
| sum net pips | -67,036.4 |
| avg net pips/trade | -2.869 |
| median net pips/trade | -6.76 |
| win rate (net pips > 0) | 17.1% |
| profit factor (net pips) | 0.57 |
| net money $ (0.10 lot) | -67,036.38 |
| expectancy $/trade | -2.87 |
| t-test net-pips mean | t=-30.08, p=9.45e-199 |
| avg MAE / MFE (pips) | 6.73 / 11.02 |
| median MAE / MFE (pips) | 5.50 / 4.80 |
| avg / median holding time | 1.02 h / 0.33 h |

## 4. Filter gain vs Candidate 1 (pure session conditioning)


Candidate #3's acceptance metric is *filter gain vs Candidate 1 must be positive* on the same dev split. Candidate-1 numbers come from the untouched archive `outputs/strategy_01_trades.json`, identical mechanics, no session gate.

| symbol | S03 trades | S03 net_pips | base trades | base net_pips | filter gain (net pips) | avg gain / trade |
|---|---|---|---|---|---|---|
| EURUSD | 8,087 | -16,570.4 | 17,174 | -38,247.1 | 21,676.7 | +0.178 |
| EURGBP | 8,063 | -27,483.5 | 16,420 | -69,639.1 | 42,155.7 | +0.833 |
| GBPUSD | 7,219 | -22,982.5 | 15,107 | -52,741.7 | 29,759.1 | +0.308 |
| ALL | 23,369 | -67,036.4 | 48,701 | -160,627.9 | 93,591.5 | +0.430 |

Positive gain = adding the London/LondonNY gate improved the fade on the dev split; negative = the gate hurt it in-sample.


## 5. Per-pair t-test (net pips)


| symbol | n | mean | t | p |
|---|---:|---:|---:|---:|
| EURUSD | 8,087 | -2.049 | -12.96 | 2.09e-38 |
| EURGBP | 8,063 | -3.409 | -32.51 | 8.63e-232 |
| GBPUSD | 7,219 | -3.184 | -14.23 | 6.21e-46 |
| ALL | 23,369 | -2.869 | -30.08 | 9.45e-199 |

## 6. Per-session results (signal-candle session)


### EURUSD

| session | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| London | 4,951 | -10,240.16 | -2.07 | -5.86 | 15.53 |
| LondonNY | 3,136 | -6,330.23 | -2.02 | -6.99 | 19.61 |

### EURGBP

| session | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| London | 5,134 | -17,506.94 | -3.41 | -6.08 | 15.35 |
| LondonNY | 2,929 | -9,976.51 | -3.41 | -6.59 | 20.31 |

### GBPUSD

| session | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| London | 4,423 | -13,489.65 | -3.05 | -8.48 | 15.71 |
| LondonNY | 2,796 | -9,492.89 | -3.40 | -9.91 | 19.31 |

## 7. Per-year results


### EURUSD

| year | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| 2,021 | 2,340 | -5,150.44 | -2.20 | -5.80 | 17.18 |
| 2,022 | 2,272 | -3,314.40 | -1.46 | -8.14 | 18.93 |
| 2,023 | 2,408 | -5,872.10 | -2.44 | -6.44 | 15.99 |
| 2,024 | 1,067 | -2,233.45 | -2.09 | -4.95 | 15.65 |

### EURGBP

| year | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| 2,021 | 2,371 | -6,985.52 | -2.95 | -6.06 | 17.63 |
| 2,022 | 2,347 | -8,943.91 | -3.81 | -7.53 | 16.79 |
| 2,023 | 2,407 | -8,824.00 | -3.67 | -6.27 | 16.54 |
| 2,024 | 938 | -2,730.02 | -2.91 | -4.96 | 18.44 |

### GBPUSD

| year | trades | sum_net | avg_net | med_net | win% |
|---|---|---|---|---|---|
| 2,021 | 1,851 | -5,367.07 | -2.90 | -8.74 | 17.88 |
| 2,022 | 2,033 | -6,220.63 | -3.06 | -10.80 | 18.15 |
| 2,023 | 2,287 | -8,229.46 | -3.60 | -9.09 | 16.31 |
| 2,024 | 1,048 | -3,165.38 | -3.02 | -6.96 | 15.46 |

## 8. Exit reasons


### EURUSD

| reason | trades | share% | avg_net | win% |
|---|---|---|---|---|
| END | 1 | 0.01 | 15.70 | 100.00 |
| HOLD | 1,504 | 18.60 | 20.65 | 91.95 |
| STOP | 6,582 | 81.39 | -7.24 | 0.00 |

### EURGBP

| reason | trades | share% | avg_net | win% |
|---|---|---|---|---|
| END | 1 | 0.01 | 3.20 | 100.00 |
| HOLD | 1,597 | 19.81 | 11.29 | 86.54 |
| STOP | 6,465 | 80.18 | -7.04 | 0.00 |

### GBPUSD

| reason | trades | share% | avg_net | win% |
|---|---|---|---|---|
| HOLD | 1,357 | 18.80 | 27.20 | 91.01 |
| STOP | 5,862 | 81.20 | -10.22 | 0.00 |

## 9. Interpretation


**Gross vs post-cost.** Gross behavior is the raw fade before costs; post-cost is the same trades minus 73,269.7 pips of costs. Gross sums: 6,233.3 pips total (avg +0.267/trade); after costs net = -67,036.4 pips (avg -2.869/trade), PF 0.57.

**Significance.** Combined t-test on net pips: t=-30.08, p=9.45e-199. A significant negative mean means the dev sample itself is negative; it is not evidence about validation.

**Robustness.** Section 6 and 7 give session and year stability of the sign. A gate that helps only in one year/session, or flips sign, would undermine a robustness claim.

**Session-gate verdict (dev).** The filter gain (section 4) is the decisive dev number for Candidate #3. It is **positive** on every pair and combined (+93,591.5 pips on dev): excluding OffHours/Asian did materially lift the fade edge in-sample. That helps the first half of the acceptance test, but the second half (filtered edge clearing cost) still fails on dev — the gated edge is much less bad, not positive.

## 10. Does Candidate #3 deserve validation?


Acceptance (report §11 Candidate #3): **filter gain vs Candidate 1 must be positive AND the filtered edge must clear cost on validation.**

**DEV verdict (informational — NOT a validation pass):** On the DEV split the session gate produced a combined filter gain of +93,591.5 pips (-3.298 → -2.869 pips/trade). Post-cost edge -2.869 pips/trade vs cost 3.14 pips/trade: does NOT clear cost on DEV. Combined DEV t-test p=9.45e-199. Per-session/per-year signs are in sections 6-7.

This report is DEV-only evidence. It does not run the validation split; whether the candidate deserves validation is a judgement to be made from sections 4-9. It does not claim profitability.
