# EXCURSION ANALYSIS REPORT

## 1. MAE (maximum adverse excursion)
| group | count | MAE pips | MAE R |
|---|---|---|---|
| all | 4109 | median 5.3 | avg 5.9 | p25 3.2 | p75 7.6 | p90 10.7 | median 1.1 | avg 1.0 | p25 0.7 | p75 1.3 | p90 1.5 |
| wins | 1300 | median 2.1 | avg 2.5 | p25 0.9 | p75 3.5 | p90 5.1 | median 0.4 | avg 0.4 | p25 0.2 | p75 0.7 | p90 0.8 |
| losses | 2809 | median 6.4 | avg 7.6 | p25 5.0 | p75 8.7 | p90 12.0 | median 1.2 | avg 1.3 | p25 1.1 | p75 1.4 | p90 1.7 |

## 2. MFE (maximum favorable excursion)
| group | count | MFE pips |
|---|---|---|
| all | 4109 | median 5.1 | avg 6.9 | p25 1.8 | p75 10.3 | p90 15.5 |
| wins | 1300 | median 12.2 | avg 13.6 | p25 9.2 | p75 16.5 | p90 21.6 |
| losses | 2809 | median 2.7 | avg 3.8 | p25 1.1 | p75 5.4 | p90 8.6 |

## 3. BEFORE STOP ANALYSIS (trades that hit SL)
- Count: 2808
- Average MAE at stop: 7.6 pips (1.33R)
- Median MAE at stop: 6.4 pips
- Ever moved favorable before SL: 2695 of 2808 (96.0%)
- Avg MFE before SL: 3.8 pips (median 2.7)

## 4. ENTRY TIMING (losing trades, first adverse move in R)
- Total losing trades: 2809
  - MFE<0.25R (immediate adverse): 785 (27.9%)
  - 0.25-0.5R: 569 (20.3%)
  - 0.5-1R: 725 (25.8%)
  - 1R+ (had room, still lost): 730 (26.0%)

## 5. SIGNAL CONTEXT (win vs loss at entry)
| feature | wins mean | wins median | losses mean | losses median |
|---|---|---|---|---|
| RSI | 50.4658 | 50.6850 | 50.0107 | 49.9700 |
| EMA50 | 1.1640 | 1.1642 | 1.1639 | 1.1642 |
| EMA200 | 1.1640 | 1.1642 | 1.1640 | 1.1643 |
| EMA_sep | -0.0000 | -0.0001 | -0.0000 | -0.0001 |
| ATR | 0.0004 | 0.0003 | 0.0004 | 0.0003 |
| candle_range | 0.0005 | 0.0004 | 0.0005 | 0.0004 |
| dist_price_EMA50 | 0.0000 | 0.0000 | -0.0000 | -0.0000 |
| dist_price_EMA200 | 0.0000 | -0.0000 | -0.0000 | -0.0001 |
