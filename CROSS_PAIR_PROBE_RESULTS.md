# CROSS-PAIR PROBE RESULTS — EURUSD/GBPUSD divergence traded on EURGBP (research only)


Pre-registered rule frozen before running (see module). DEV rows only; three legs synchronized on the UTC hour index (inner join); signal uses closed bars only up to t; entry open[t+1], exit close[t+H]; real observed EURGBP spread + 1.0 pip slippage; EURJPY excluded. Verdict judged on the FROZEN momentum rule only.


## Result (H=12)


| metric | value |
|---|---|
| n | 12838 |
| win_rate | 0.3993612712260477 |
| expectancy_net_pips | -4.228953107960747 |
| mean_raw_pips | -0.4412603209222671 |
| avg_win_pips | 16.32100643651258 |
| avg_loss_pips | -17.892504214758144 |
| profit_factor | 0.6064966720809222 |
| movement_to_cost | 0.11649844528898015 |
| total_cost_pips | 48626.4 |
| total_net_pips | -54291.30000000022 |
| max_drawdown_pips | 54508.500000000226 |
| years_positive_share | 0.0 |
| max_year_share | 0.35814393834739455 |
| t_test | {'n': 12838, 't': -18.810594321092744, 'p': 6.18405957610657e-79, 'mean': -4.228953107960747, 'se': 0.22481762329107946} |
| verdict | INSUFF |
| reason | movement-to-cost 0.12 (bar 1.0), |mean| 0.44 (bar 2.0) |
| bucket | REJECTED |

## Screen pass check


- n >= 1000: True
- movement-to-cost >= 1.0 and |raw| >= 2.0: 0.11649844528898015
- t p < 0.05 and net > 0: 6.18405957610657e-79
- exit reasons never applied; fixed horizon only.

