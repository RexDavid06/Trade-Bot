# RAW DIRECTIONAL PREDICTIVE POWER OF BUY/SELL SIGNALS

Signal count: **41713** total (19404 BUY, 22309 SELL).

## Methodology (no look-ahead)

1. **Signals** — every closed candle matching the exact existing strategy
   rules (BUY: EMA50>EMA200 AND 40<RSI<55; SELL: EMA50<EMA200 AND 45<RSI<60)
   is counted independently. The one-position-at-a-time *execution* rule is
   intentionally NOT applied: we measure the predictive power of the signal
   itself, not the simulated trade sequence.
2. **Forward momentum** — after the signal candle `i`, the forward move to
   the close of candle `i+H` is measured. For a BUY it is `close[i+H] -
   close[i]`; for a SELL it is `close[i] - close[i+H]`, so a positive move
   is always *in the predicted direction*. Only future bars are used, and only
   information available at candle `i` (close, ATR) defines the prediction, so
   there is no look-ahead.
3. **Pips** — move / pip, with pip = 0.0001 (EURUSD).
4. **R** — move / (1.5 x ATR at the signal candle). 1R is the stop-distance the
   strategy would use (SL = 1.5 x ATR), letting forward returns be compared to
   the strategy's own risk scale.
5. **'Reached +X R before -1R'** — walking candles 1..H from the signal close, a
   signal counts if it touches +X R (in the predicted direction) on some candle
   before it ever touches -1 R. The conservative intrabar rule is used (adverse
   first), matching the backtest engine, so both-touched-in-one-candle counts as
   not reaching the target first.
6. **Coverage** — signals within the last H candles of the dataset are excluded
   at that horizon (their forward window is incomplete), so `n` may shrink for
   the longest horizons.

## BUY signals (predicted direction = up)

| H (candles) | n | in dir% | avg pips | med pips | avg R | med R | +0.5R before -1R | +1R before -1R | +2R before -1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 19404 | 48.11 | -0.02 | 0.00 | -0.00 | 0.00 | 19.65 | 2.88 | 0.28 |
| 3 | 19404 | 48.75 | -0.02 | 0.00 | -0.01 | 0.00 | 43.21 | 14.67 | 2.05 |
| 5 | 19404 | 48.46 | -0.07 | -0.10 | -0.02 | -0.02 | 53.04 | 23.70 | 4.79 |
| 10 | 19404 | 48.12 | -0.11 | -0.20 | -0.03 | -0.04 | 61.75 | 36.52 | 11.47 |
| 20 | 19404 | 47.52 | -0.28 | -0.40 | -0.06 | -0.08 | 64.61 | 44.29 | 19.82 |
| 40 | 19404 | 46.17 | -0.48 | -1.00 | -0.12 | -0.21 | 65.17 | 47.33 | 26.26 |
| 80 | 19404 | 44.38 | -1.33 | -2.60 | -0.29 | -0.51 | 65.23 | 47.84 | 28.79 |

## SELL signals (predicted direction = down)

| H (candles) | n | in dir% | avg pips | med pips | avg R | med R | +0.5R before -1R | +1R before -1R | +2R before -1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 22309 | 48.34 | 0.01 | 0.00 | 0.00 | 0.00 | 22.17 | 3.34 | 0.28 |
| 3 | 22309 | 48.88 | 0.00 | 0.00 | 0.00 | 0.00 | 46.49 | 16.51 | 2.13 |
| 5 | 22308 | 48.87 | 0.03 | 0.00 | 0.01 | 0.00 | 56.27 | 26.53 | 5.44 |
| 10 | 22304 | 49.48 | 0.14 | 0.00 | 0.03 | 0.00 | 64.84 | 40.03 | 13.57 |
| 20 | 22302 | 49.49 | 0.22 | 0.00 | 0.03 | 0.00 | 68.03 | 48.24 | 23.67 |
| 40 | 22290 | 49.59 | 0.11 | -0.10 | 0.00 | -0.02 | 68.66 | 51.46 | 31.02 |
| 80 | 22267 | 49.42 | -0.38 | -0.20 | -0.08 | -0.04 | 68.76 | 51.99 | 34.01 |

## ALL signals combined (predicted-direction space)

| H (candles) | n | in dir% | avg pips | med pips | avg R | med R | +0.5R before -1R | +1R before -1R | +2R before -1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 41713 | 48.23 | -0.01 | 0.00 | -0.00 | 0.00 | 21.00 | 3.13 | 0.28 |
| 3 | 41713 | 48.82 | -0.01 | 0.00 | -0.00 | 0.00 | 44.97 | 15.65 | 2.09 |
| 5 | 41712 | 48.68 | -0.02 | -0.10 | -0.00 | -0.01 | 54.76 | 25.21 | 5.14 |
| 10 | 41708 | 48.85 | 0.03 | -0.10 | 0.00 | -0.02 | 63.40 | 38.40 | 12.59 |
| 20 | 41706 | 48.58 | -0.01 | -0.20 | -0.01 | -0.04 | 66.43 | 46.40 | 21.87 |
| 40 | 41694 | 48.00 | -0.16 | -0.50 | -0.05 | -0.10 | 67.04 | 49.54 | 28.81 |
| 80 | 41671 | 47.07 | -0.82 | -1.30 | -0.18 | -0.26 | 67.11 | 50.05 | 31.58 |

