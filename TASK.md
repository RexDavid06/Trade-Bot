We are beginning Strategy V2.

Strategy V1 has been conclusively shown to have no useful directional predictive power. Do NOT modify or delete V1, bot.py, or the existing backtesting modules.

Build V2 as a separate experimental strategy.

## V2 OBJECTIVE

Test the hypothesis:

"A trend-pullback setup with an established trend, a meaningful retracement toward EMA50, rejection, and momentum confirmation has better directional predictive power than the existing V1 signal."

This is an experiment, not an optimization.

## TREND

Use:

* EMA50
* EMA200

BUY trend:

* EMA50 > EMA200
* EMA50 is rising
* EMA200 is rising

SELL trend:

* EMA50 < EMA200
* EMA50 is falling
* EMA200 is falling

Define "rising/falling" using the difference between the current EMA and its previous candle value.

## PULLBACK

For BUY:

* Identify a recent bullish impulse/local high.
* Price must subsequently retrace toward EMA50.
* During the pullback, price must reach within 0.25 ATR of EMA50.
* Pullback distance from the recent impulse extreme must be at least 0.5 ATR.

For SELL:

* Mirror the BUY logic using a recent bearish impulse/local low.
* Price must retrace toward EMA50.
* Price must reach within 0.25 ATR of EMA50.
* Pullback distance must be at least 0.5 ATR.

IMPORTANT:
Use a deterministic, explicitly documented method for identifying the recent impulse extreme. Do not use future candles to identify it.

## REJECTION CANDLE

BUY:

* Candle touches/enters the EMA50 pullback zone.
* Candle closes bullish.
* Candle closes above its midpoint.
* Candle closes above EMA50.

SELL:

* Candle touches/enters the EMA50 pullback zone.
* Candle closes bearish.
* Candle closes below its midpoint.
* Candle closes below EMA50.

## MOMENTUM CONFIRMATION

BUY:

* RSI14 crosses from below 50 to above 50 on the rejection/confirmation candle.

SELL:

* RSI14 crosses from above 50 to below 50.

## ENTRY

* Signal must be generated using only information available at the closed signal candle.
* Enter at the next candle open.
* No look-ahead bias.

## INITIAL TRADE MANAGEMENT

For the first V2 experiment only:

* SL = 1.5 × ATR at entry
* TP = 3 × ATR at entry
* Maximum one open position
* Same spread assumptions
* Same slippage assumptions
* Same commission assumptions

Do not optimize these values.

## IMPORTANT EXPERIMENT RULES

Do NOT:

* modify bot.py
* modify V1
* change V1 rules
* add MACD
* add additional indicators
* optimize thresholds
* run parameter sweeps
* choose parameters based on profitability
* change SL/TP

Create V2 separately, for example:

backtest/
strategy_v2.py
predictive_v2.py
...

## FIRST TEST

The primary objective is NOT money P&L.

Measure the directional predictive power of V2 signals independently of SL/TP.

For every V2 signal, calculate forward performance at:

* 1 candle
* 3 candles
* 5 candles
* 10 candles
* 20 candles
* 40 candles
* 80 candles

For BUY, positive means upward movement.

For SELL, positive means downward movement.

Report:

* total signals
* BUY signals
* SELL signals
* directional hit rate
* average forward return in pips
* median forward return
* average forward return in R
* median forward return
* percentage reaching +0.5R before -1R
* percentage reaching +1R before -1R
* percentage reaching +2R before -1R

Also compare V2 directly with the existing V1 predictive results.

## OUTPUT

Create:

outputs/v2_predictive_report.md

and CSV files containing the underlying results.

Clearly document:

* exact V2 rules
* how impulse extremes are identified
* how pullbacks are identified
* how EMA slope is calculated
* how rejection is identified
* how RSI crossing is detected
* how forward returns are calculated

Run all existing validation tests and add appropriate V2 validation tests.

The key question is:

"Does V2 contain measurable directional predictive power that V1 does not?"

Do not optimize anything yet.
