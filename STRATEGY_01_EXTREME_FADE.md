# Strategy 01 — Counter-Trend Extreme Fade (Phase 2)

**Development split only. Exploration report of a frozen rule — hypothesis, not a proven edge; nothing validated, nothing optimized.**

## 1. Frozen specification (source: MARKET_BEHAVIOR_DISCOVERY.md §11, candidate #1)

- **Signal** (closed M5 candle \(i\)): `dist = (close - SMA20)/STD20` (population std over trailing 20 bars). `dist <= -1` -> LONG (oversold); `dist >= +1` -> SHORT (overbought).
- **Entry**: open of candle \(i+1\) (never inside the forming candle).
- **Stop**: 1 x ATR(14) at candle \(i\), intrabar-resolved.
- **Hold**: close of candle `entry+40` if the stop has not fired (upper bound of the report's pre-specified "20-40 bars"; frozen, not swept).
- **One position at a time**; no session / regime gate (those belong to candidates #2/#3, not here).
- **Pairs**: EURUSD, EURGBP, GBPUSD (report excludes EURJPY on data quality).
- **Cost model** (report §2): round-turn = 2 x observed per-side spread (observed bars) + 1.7 pips slippage/commission. Gross AND net both reported.

## 2. Datasets used (DEV only)

| symbol | dev candles | dev start | dev end |
|---|---|---|---|
| EURUSD | 253,335 | 2021-01-03 22:00:00 | 2024-05-29 08:00:00 |
| EURGBP | 255,286 | 2021-01-03 22:00:00 | 2024-05-30 15:15:00 |
| GBPUSD | 224,848 | 2021-01-03 22:00:00 | 2024-06-13 18:25:00 |

Split assignments come from `outputs/splits/<SYMBOL>/assignments.csv` (research_split 60/20/20 chronological). Only `dev` rows were read; `val` and `holdout` rows were never loaded.

## 3. Overall results (net pips per trade, after costs)

| symbol | trades | sum_net_pips | avg_net | med_net | win% | t_p | PF | dd_pips | gross | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 17174 | -38,247.07 | -2.23 | -5.17 | 17.73 | 4.01e-146 | 0.56 | 38,248.05 | 5,253.13 | 43,500.20 |
| EURGBP | 16420 | -69,639.13 | -4.24 | -5.58 | 14.76 | 0 | 0.26 | 69,693.82 | 3,350.87 | 72,990.00 |
| GBPUSD | 15107 | -52,741.68 | -3.49 | -7.54 | 17.65 | 1.1e-162 | 0.53 | 52,822.60 | 7,048.82 | 59,790.50 |
| ALL | 48701 | -160,627.88 | -3.30 | -5.92 | 16.71 | 0 | 0.45 | 160,704.30 | 15,652.82 | 176,280.70 |

Values in pips (all pairs pip = 0.0001, so pips are comparable). `win%` = share of trades with net_pips > 0; `t_p` = two-sided t-test of mean net_pips = 0; `PF` = profit factor on net pips; `dd_pips` = max peak-to-trough drawdown of the cumulative net-pips curve; `gross` / `cost` = sums over trades.

### 3.1 Gross metrics (before costs)

| symbol | trades | sum_gross | avg_gross | med_gross | gross_win% |
|---|---|---|---|---|---|
| EURUSD | 17174 | 5,253.1 | +0.31 | -2.67 | 19.5 |
| EURGBP | 16420 | 3,350.9 | +0.20 | -1.88 | 21.1 |
| GBPUSD | 15107 | 7,048.8 | +0.47 | -3.77 | 19.7 |

### 3.2 Reference — same signal, NO stop, NO costs (not the strategy)

| symbol | n (ref) | avg_pips | med_pips | win% |
|---|---|---|---|---|
| EURUSD | 134,294 | +0.32 | +0.40 | 51.2 |
| EURGBP | 132,353 | +0.42 | +0.50 | 52.5 |
| GBPUSD | 119,562 | +0.41 | +0.40 | 50.9 |
This reference reinvestigates the discovery's fade signal with the *same entry* (next bar open) and the strategy's 40-bar horizon, but removes the frozen 1-ATR stop and all costs. It isolates what the stop does to the raw behaviour (see section 10). It is NOT the strategy and carries no costs.

## 4. Direction breakdown

| symbol | direction | trades | sum_net | avg_net | win% |
|---|---|---|---|---|---|
| EURUSD | LONG | 8587 | -19,583.11 | -2.28 | 17.55 |
| EURUSD | SHORT | 8587 | -18,663.96 | -2.17 | 17.91 |
| EURGBP | LONG | 8072 | -38,554.92 | -4.78 | 13.57 |
| EURGBP | SHORT | 8348 | -31,084.21 | -3.72 | 15.92 |
| GBPUSD | LONG | 7534 | -27,910.74 | -3.70 | 17.14 |
| GBPUSD | SHORT | 7573 | -24,830.94 | -3.28 | 18.17 |

## 5. Behaviour by volatility regime (at signal bar)

| symbol | regime | trades | sum_net | avg_net | win% |
|---|---|---|---|---|---|
| EURUSD | low | 6110 | -14,619.25 | -2.39 | 17.71 |
| EURUSD | normal | 2976 | -6,593.70 | -2.22 | 15.86 |
| EURUSD | high | 8088 | -17,034.12 | -2.11 | 18.43 |
| EURGBP | low | 6305 | -28,406.34 | -4.51 | 13.02 |
| EURGBP | normal | 2832 | -12,968.72 | -4.58 | 14.51 |
| EURGBP | high | 7283 | -28,264.07 | -3.88 | 16.37 |
| GBPUSD | low | 5468 | -20,595.85 | -3.77 | 17.28 |
| GBPUSD | normal | 2565 | -8,595.38 | -3.35 | 17.12 |
| GBPUSD | high | 7074 | -23,550.45 | -3.33 | 18.14 |

## 6. Behaviour by session (UTC, entry bar)

| symbol | session | trades | sum_net | avg_net | win% |
|---|---|---|---|---|---|
| EURUSD | Asian | 5696 | -11,604.68 | -2.04 | 15.40 |
| EURUSD | London | 3839 | -7,547.08 | -1.97 | 16.44 |
| EURUSD | LondonNY | 3209 | -7,234.15 | -2.25 | 19.07 |
| EURUSD | NewYork | 2755 | -6,652.24 | -2.41 | 24.75 |
| EURUSD | OffHours | 1675 | -5,208.92 | -3.11 | 14.51 |
| EURGBP | Asian | 5355 | -19,823.39 | -3.70 | 12.03 |
| EURGBP | London | 4128 | -13,831.09 | -3.35 | 16.16 |
| EURGBP | LondonNY | 2978 | -10,344.47 | -3.47 | 19.74 |
| EURGBP | NewYork | 2617 | -12,923.23 | -4.94 | 15.32 |
| EURGBP | OffHours | 1342 | -12,716.95 | -9.48 | 9.24 |
| GBPUSD | Asian | 5120 | -17,699.16 | -3.46 | 14.96 |
| GBPUSD | London | 3468 | -10,628.68 | -3.06 | 16.67 |
| GBPUSD | LondonNY | 2801 | -9,289.51 | -3.32 | 19.49 |
| GBPUSD | NewYork | 2379 | -8,709.00 | -3.66 | 23.88 |
| GBPUSD | OffHours | 1339 | -6,415.33 | -4.79 | 15.61 |

## 7. Behaviour by year (entry bar)

| symbol | year | trades | sum_net | avg_net | win% |
|---|---|---|---|---|---|
| EURUSD | 2021 | 5039 | -11,788.00 | -2.34 | 17.48 |
| EURUSD | 2022 | 4896 | -9,210.73 | -1.88 | 19.30 |
| EURUSD | 2023 | 5077 | -12,347.84 | -2.43 | 17.02 |
| EURUSD | 2024 | 2162 | -4,900.50 | -2.27 | 16.42 |
| EURGBP | 2021 | 4923 | -18,383.35 | -3.73 | 15.28 |
| EURGBP | 2022 | 4799 | -21,703.49 | -4.52 | 15.77 |
| EURGBP | 2023 | 4825 | -22,174.03 | -4.60 | 13.84 |
| EURGBP | 2024 | 1873 | -7,378.26 | -3.94 | 13.19 |
| GBPUSD | 2021 | 4002 | -12,373.14 | -3.09 | 17.82 |
| GBPUSD | 2022 | 4292 | -15,341.67 | -3.57 | 18.69 |
| GBPUSD | 2023 | 4709 | -18,163.72 | -3.86 | 17.09 |
| GBPUSD | 2024 | 2104 | -6,863.15 | -3.26 | 16.49 |

## 8. Distribution and excursions (net pips; MAE/MFE in pips)

| symbol | avg_net | med_net | p10 | p90 | skew | avg_MAE | med_MAE | avg_MFE | med_MFE |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | -2.23 | -5.17 | -8.93 | 9.20 | 4.26 | 5.15 | 4.00 | 8.61 | 3.80 |
| EURGBP | -4.24 | -5.58 | -8.79 | 3.80 | 2.27 | 3.51 | 2.80 | 5.99 | 2.80 |
| GBPUSD | -3.49 | -7.54 | -12.45 | 12.80 | 3.94 | 7.20 | 5.70 | 11.86 | 5.30 |

Positive skew = right tail; `skew` computed on net pips. MAE/MFE are intrabar adverse/favorable excursions from the entry price while the position was held.

## 9. Exit reasons

| symbol | reason | count |
|---|---|---|
| EURUSD | STOP | 13684 |
| EURUSD | HOLD | 3490 |
| EURUSD | END | 0 |
| EURGBP | STOP | 12793 |
| EURGBP | HOLD | 3626 |
| EURGBP | END | 1 |
| GBPUSD | STOP | 11987 |
| GBPUSD | HOLD | 3119 |
| GBPUSD | END | 1 |

## 10. Interpretations and integrity

- **The frozen stop changes everything.** The raw Phase-1 fade signal (|dist|>=1, close-horizon, no stop, no costs) had a hit rate near 51-53% and a small positive gross average. Section 3.2 reproduces that profile with this entry and horizon. Once the report's frozen 1-ATR stop and cost model are applied (the actual strategy), 78-80% of trades exit by STOP before the reversion completes, gross win rate collapses to ~20%, and the net expectancy is strongly negative on every pair (-2.2 to -4.2 pips/trade). The adverse excursion to a 1-ATR stop is larger than the typical reversion payoff, so the stop truncates the slow, small-payoff mean reversion it was meant to protect.
- **Net result is deeply negative after costs.** Summed over the dev set: -160,628 pips net across 48,701 trades, profit factor 0.45, max drawdown of the cumulative net-pips curve ~160,704 pips. This is consistent with the Phase-1 conclusion that no naive M5 fade clears costs as specified.
- **No optimization.** Every constant above came from the report (SMA/σ window, ±1σ, 1 x ATR stop, cost model, pairs) or a single documented choice (hold = 40 bars, upper bound of the pre-specified 20-40 range). Nothing was swept to improve profit; the section 3.2 reference is diagnostic only and is not a variant the strategy may switch to.
- **No lookahead.** Signals use only bars up to and including the signal candle; entries occur on the next bar's open; `dist`, ATR, regime and session are all causal at decision time. Stops are resolved intrabar exactly at the stop level.
- **DEV only.** val/holdout were never read. `bot.py`, V1/V2 and the backtester engine were not modified.

_End of Strategy 01 exploration. Reported performance is DEVELOPMENT-only, post-cost, and is not claimed to be profitable; no validation or holdout was performed._
