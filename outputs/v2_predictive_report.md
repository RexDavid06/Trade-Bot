# V2 DIRECTIONAL PREDICTIVE POWER (trend-pullback) vs V1

## V2 rule summary

BUY requires **all** of the following on the closed signal candle:

* **Trend**: EMA50 > EMA200, EMA50 rising, EMA200 rising (rising/falling = EMA vs its previous candle).
* **Impulse + pullback**: a recent local high (highest high over the trailing `LOOKBACK=20` candles
  strictly before the signal candle); price closed below it (retraced), the retracement is at least
  `PULLBACK_ATR=0.5` ATR, and price reached within `ZONE_ATR=0.25` ATR of EMA50 during the pullback.
* **Rejection candle**: touches the EMA50 pullback zone (low <= EMA50 + 0.25 ATR), closes bullish,
  above its midpoint, above EMA50.
* **Momentum**: RSI14 crosses from <=50 to >50 on that candle.

SELL mirrors all of these (EMA50 < EMA200 with both falling, pullback up from a recent local low,
bearish rejection below midpoint/EMA50, RSI crossing), all using only data <= the signal candle.

Signal count V2: **2877** total (1327 BUY, 1550 SELL).  V1 for comparison: 41713 total (19404 BUY, 22309 SELL).

Forward returns: move to close[i+H] from the signal close, sign-flipped for SELL (positive =>
predicted direction); pips = move / 0.0001; R = move / (1.5 x ATR at signal candle). Reach stats
+0.5R/+1R/+2R before -1R use the conservative adverse-first intrabar rule, identical to V1. Only
bars after the signal are used (no look-ahead); signals inside the last H candles are dropped at
that horizon, so n can shrink for long horizons.

## V2 results

### V2 BUY (predicted = up)

| H | n | in dir% | avg pips | med pips | avg R | med R | +0.5R<1R | +1R<1R | +2R<1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1327 | 48.61 | 0.05 | 0.00 | 0.00 | 0.00 | 21.63 | 4.07 | 0.38 |
| 3 | 1327 | 48.15 | -0.03 | -0.20 | -0.02 | -0.03 | 45.44 | 16.88 | 3.24 |
| 5 | 1327 | 46.27 | -0.20 | -0.30 | -0.05 | -0.07 | 53.50 | 24.64 | 7.08 |
| 10 | 1327 | 47.10 | -0.36 | -0.30 | -0.08 | -0.07 | 60.51 | 34.82 | 13.04 |
| 20 | 1327 | 44.84 | -0.67 | -1.10 | -0.17 | -0.22 | 62.77 | 42.80 | 20.72 |
| 40 | 1327 | 44.99 | -1.22 | -1.90 | -0.29 | -0.35 | 63.23 | 45.29 | 26.45 |
| 80 | 1327 | 42.73 | -1.72 | -3.40 | -0.45 | -0.67 | 63.23 | 45.74 | 28.18 |

### V2 SELL (predicted = down)

| H | n | in dir% | avg pips | med pips | avg R | med R | +0.5R<1R | +1R<1R | +2R<1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1550 | 44.97 | -0.12 | -0.10 | -0.02 | -0.03 | 23.10 | 3.74 | 0.32 |
| 3 | 1550 | 46.84 | -0.09 | -0.15 | -0.01 | -0.04 | 47.10 | 18.06 | 2.58 |
| 5 | 1550 | 44.58 | -0.14 | -0.30 | -0.03 | -0.08 | 55.61 | 27.16 | 6.97 |
| 10 | 1550 | 45.03 | -0.19 | -0.50 | -0.04 | -0.11 | 62.00 | 38.32 | 14.00 |
| 20 | 1550 | 47.68 | -0.22 | -0.30 | -0.04 | -0.08 | 65.42 | 45.10 | 23.23 |
| 40 | 1549 | 48.74 | -0.37 | -0.30 | -0.05 | -0.08 | 66.30 | 48.29 | 29.37 |
| 80 | 1548 | 47.35 | -1.48 | -0.80 | -0.29 | -0.21 | 66.34 | 48.77 | 32.11 |

### V2 ALL combined

| H | n | in dir% | avg pips | med pips | avg R | med R | +0.5R<1R | +1R<1R | +2R<1R |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2877 | 46.65 | -0.04 | -0.10 | -0.01 | -0.02 | 22.42 | 3.89 | 0.35 |
| 3 | 2877 | 47.45 | -0.06 | -0.20 | -0.02 | -0.03 | 46.33 | 17.52 | 2.88 |
| 5 | 2877 | 45.36 | -0.16 | -0.30 | -0.04 | -0.07 | 54.64 | 26.00 | 7.02 |
| 10 | 2877 | 45.99 | -0.27 | -0.40 | -0.06 | -0.10 | 61.31 | 36.70 | 13.56 |
| 20 | 2877 | 46.37 | -0.43 | -0.60 | -0.10 | -0.13 | 64.20 | 44.04 | 22.07 |
| 40 | 2876 | 47.01 | -0.77 | -0.80 | -0.16 | -0.18 | 64.88 | 46.91 | 28.03 |
| 80 | 2875 | 45.22 | -1.59 | -1.90 | -0.37 | -0.42 | 64.90 | 47.37 | 30.30 |

## V2 vs V1 (ALL signals combined)

| H | V2 n | V2 in dir% | V1 n | V1 in dir% | V2 avg R | V1 avg R | V2 +1R<1R | V1 +1R<1R |
|---|---|---|---|---|---|---|---|---|
| 1 | 2877 | 46.65 | 41713 | 48.23 | -0.01 | -0.00 | 3.89 | 3.13 |
| 3 | 2877 | 47.45 | 41713 | 48.82 | -0.02 | -0.00 | 17.52 | 15.65 |
| 5 | 2877 | 45.36 | 41712 | 48.68 | -0.04 | -0.00 | 26.00 | 25.21 |
| 10 | 2877 | 45.99 | 41708 | 48.85 | -0.06 | 0.00 | 36.70 | 38.40 |
| 20 | 2877 | 46.37 | 41706 | 48.58 | -0.10 | -0.01 | 44.04 | 46.40 |
| 40 | 2876 | 47.01 | 41694 | 48.00 | -0.16 | -0.05 | 46.91 | 49.54 |
| 80 | 2875 | 45.22 | 41671 | 47.07 | -0.37 | -0.18 | 47.37 | 50.05 |

## V2 notes

Configurable structural constants are fixed and NOT optimized: LOOKBACK=20, ZONE_ATR=0.25, PULLBACK_ATR=0.5. The primary objective is directional predictive power, not money P&L.
