# DIAGNOSTIC REPORT

## 1. COST SENSITIVITY
| variant | spread | slippage/pip | comm/lot | trades | net P/L | profit factor | expectancy | win rate | total R |
|---|---|---|---|---|---|---|---|---|---|
| zero_costs | 0 | 0.0 | 0.0 | 4109 | $-1,144 | 0.93 | $-0.28 (-0.050R) | 31.7% | -206R |
| spread_only | CSV | 0.0 | 0.0 | 4109 | $-2,326 | 0.86 | $-0.57 (-0.109R) | 31.6% | -447R |
| baseline | CSV | 0.5 | 7.0 | 4109 | $-9,311 | 0.57 | $-2.27 (-0.313R) | 31.6% | -1285R |

## 2. R-MULTIPLE ANALYSIS
- Average winner: 1.739R
- Average loser: -1.262R
- Median winner: 1.778R
- Median loser: -1.228R
- Expectancy: -0.313R per trade
- Total R: -1285R
- Distribution: {'<-3': 2, '-3..-2': 12, '-2..-1': 2794, '-1..-0.5': 0, '-0.5..0': 1, '0..0.5': 3, '0.5..1': 10, '1..2': 1287, '2..3': 0, '>3': 0}

## 3. LONG VS SHORT
| side | trades | win rate | profit factor | expectancy | total R | net P/L |
|---|---|---|---|---|---|---|
| BUY | 1940 | 30.1% | 0.52 | -0.360R | -698R | $-4,999 |
| SELL | 2169 | 33.1% | 0.61 | -0.271R | -587R | $-4,312 |

## 4. RSI ENTRY ZONES
| zone | trades | win rate | profit factor | expectancy R | total R |
|---|---|---|---|---|---|
| BUY 40-45 | 878 | 27.6% | 0.46 | -0.444R | -390R |
| BUY 45-50 | 358 | 30.7% | 0.52 | -0.346R | -124R |
| BUY 50-55 | 704 | 32.8% | 0.61 | -0.262R | -184R |
| SELL 45-50 | 789 | 33.7% | 0.66 | -0.253R | -200R |
| SELL 50-55 | 407 | 34.4% | 0.67 | -0.218R | -89R |
| SELL 55-60 | 973 | 32.0% | 0.55 | -0.307R | -298R |

## 5. MARKET REGIME
### EMA50/EMA200 separation (absolute)
| bucket | trades | win rate | profit factor | expectancy R | total R |
|---|---|---|---|---|---|
| tiny<0.5p | 159 | 37.7% | 0.68 | -0.159R | -25R |
| 0.5-1p | 191 | 31.9% | 0.57 | -0.306R | -58R |
| 1-2p | 353 | 33.1% | 0.62 | -0.275R | -97R |
| 2-4p | 672 | 30.7% | 0.49 | -0.363R | -244R |
| strong>4p | 2734 | 31.3% | 0.58 | -0.315R | -860R |
### ATR level
| bucket | trades | win rate | profit factor | expectancy R | total R |
|---|---|---|---|---|---|
| low<5p | 3329 | 31.2% | 0.51 | -0.355R | -1183R |
| 5-8p | 692 | 34.4% | 0.77 | -0.110R | -76R |
| 8-11p | 77 | 29.9% | 0.69 | -0.189R | -15R |
| 11-15p | 9 | 0.0% | 0.00 | -1.063R | -10R |
| high>15p | 2 | 0.0% | 0.00 | -1.045R | -2R |
### Trend strength (EMA separation / ATR)
| bucket | trades | win rate | profit factor | expectancy R | total R |
|---|---|---|---|---|---|
| weak<5% | 46 | 30.4% | 0.53 | -0.345R | -16R |
| 5-10% | 56 | 39.3% | 0.93 | -0.062R | -3R |
| 10-20% | 130 | 35.4% | 0.63 | -0.204R | -27R |
| 20-40% | 250 | 31.6% | 0.56 | -0.268R | -67R |
| strong>40% | 3627 | 31.4% | 0.56 | -0.323R | -1172R |

## 6. TRADE DURATION
- Average duration: 100 min
- Median duration: 35 min
- Avg winning trade duration: 148 min
- Avg losing trade duration: 78 min

## 7. LOSS/WIN SEQUENCES
- Longest winning streak: 6
- Longest losing streak: 21
- Average winning streak: 1.5
- Average losing streak: 3.2
