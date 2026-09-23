# FRONTIER PROBE RESULTS — pre-registered untested behaviors on DEV (research only)


Definitions frozen before running (see module). DEV rows only, EURUSD/EURGBP/GBPUSD, EURJPY excluded. Cost = entry + exit observed spread + 1.0 pip slippage. Screen: n >= 1000, movement-to-cost >= 1.0 with |raw mean| >= 2 pips, t p < 0.05, >= 2/3 symbols positive, >= 60% years positive, no year > 50% / window > 40% of net.


## Verdicts


| experiment | sym | hold | n | raw | net_exp | m2c | win% | PF | verdict | bucket |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G-DAYGAP | EURUSD | H=6 | 212 | -0.98 | -8.380 | 0.13 | 2.4 | 0.007 | INSUFF | UNRESOLVED |
| G-DAYGAP | EURGBP | H=6 | 255 | -3.06 | -21.309 | 0.17 | 0.4 | 0.000 | INSUFF | UNRESOLVED |
| G-DAYGAP | GBPUSD | H=6 | 274 | -1.30 | -12.211 | 0.12 | 10.9 | 0.047 | INSUFF | UNRESOLVED |
| G-DAYGAP | EURUSD | H=24 | 212 | -2.84 | -8.323 | 0.52 | 18.9 | 0.088 | INSUFF | UNRESOLVED |
| G-DAYGAP | EURGBP | H=24 | 255 | -4.67 | -17.977 | 0.35 | 3.5 | 0.006 | INSUFF | UNRESOLVED |
| G-DAYGAP | GBPUSD | H=24 | 274 | -2.60 | -10.674 | 0.32 | 21.5 | 0.160 | INSUFF | UNRESOLVED |
| P-WICK | EURUSD | H=2 | 4,507 | -0.62 | -2.720 | 0.29 | 38.8 | 0.581 | INSUFF | REJECTED |
| P-WICK | EURGBP | H=2 | 4,893 | -0.32 | -4.199 | 0.08 | 26.8 | 0.287 | INSUFF | REJECTED |
| P-WICK | GBPUSD | H=2 | 4,085 | -0.33 | -4.026 | 0.09 | 37.8 | 0.562 | INSUFF | REJECTED |
| P-WICK | EURUSD | H=6 | 4,506 | -0.56 | -2.658 | 0.27 | 44.7 | 0.743 | INSUFF | REJECTED |
| P-WICK | EURGBP | H=6 | 4,893 | -0.41 | -4.266 | 0.11 | 34.2 | 0.467 | INSUFF | REJECTED |
| P-WICK | GBPUSD | H=6 | 4,084 | +0.05 | -3.602 | 0.01 | 43.5 | 0.756 | INSUFF | REJECTED |

## Full metrics


### G-DAYGAP / EURUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 7.397641509433963 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 0.5 |
| avg_loss_pips | -8.641545893719695 |
| avg_win_pips | 2.46000000000033 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -8.379716981131958 |
| exposure | 0.005021019598555273 |
| gross_loss_pips | 375.9999999999808 |
| gross_profit_pips | 167.80000000000572 |
| max_drawdown_pips | 1766.7999999999752 |
| max_window_share | 0.06676048409794663 |
| max_year_share | 0.32929918378835477 |
| mean_raw_pips | -0.9820754716979957 |
| movement_to_cost | 0.13275521265062493 |
| n | 212 |
| net_usd_norm | -1776.4999999999766 |
| pip | 0.0001 |
| profit_factor | 0.006876118067979544 |
| reason | n=212 below 1000 |
| symbol | EURUSD |
| timeframe | M5 |
| total_cost_pips | 1568.3 |
| total_net_pips | -1776.4999999999766 |
| trades | 212 |
| verdict | INSUFF |
| win_rate | 0.02358490566037736 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### G-DAYGAP / EURGBP / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 18.253333333333334 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 0.5 |
| avg_loss_pips | -21.396850393700763 |
| avg_win_pips | 1.0000000000000497 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -21.309019607843112 |
| exposure | 0.005993278127276858 |
| gross_loss_pips | 957.4999999999955 |
| gross_profit_pips | 178.30000000000237 |
| max_drawdown_pips | 5381.899999999998 |
| max_window_share | 0.05697670138761075 |
| max_year_share | 0.3451544039162281 |
| mean_raw_pips | -3.0556862745097773 |
| movement_to_cost | 0.16740428823099582 |
| n | 255 |
| net_usd_norm | -5433.799999999998 |
| pip | 0.0001 |
| profit_factor | 0.0001839994112018935 |
| reason | n=255 below 1000 |
| symbol | EURGBP |
| timeframe | M5 |
| total_cost_pips | 4654.6 |
| total_net_pips | -5433.799999999998 |
| trades | 255 |
| verdict | INSUFF |
| win_rate | 0.00392156862745098 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### G-DAYGAP / GBPUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 10.906204379562045 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 0.5 |
| avg_loss_pips | -14.384426229508186 |
| avg_win_pips | 5.466666666666634 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -12.210948905109486 |
| exposure | 0.0073116060627623995 |
| gross_loss_pips | 844.9999999999891 |
| gross_profit_pips | 487.4999999999896 |
| max_drawdown_pips | 3348.299999999996 |
| max_window_share | 0.056040408870822886 |
| max_year_share | 0.30793831071791594 |
| mean_raw_pips | -1.3047445255474435 |
| movement_to_cost | 0.11963323628819043 |
| n | 274 |
| net_usd_norm | -3345.7999999999956 |
| pip | 0.0001 |
| profit_factor | 0.04672630919140667 |
| reason | n=274 below 1000 |
| symbol | GBPUSD |
| timeframe | M5 |
| total_cost_pips | 2988.3 |
| total_net_pips | -3345.7999999999956 |
| trades | 274 |
| verdict | INSUFF |
| win_rate | 0.10948905109489052 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### G-DAYGAP / EURUSD / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 5.48679245283019 |
| avg_duration_bars | 24.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -11.253488372092953 |
| avg_win_pips | 4.280000000000231 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -8.32264150943386 |
| exposure | 0.02008407839422109 |
| gross_loss_pips | 1054.199999999993 |
| gross_profit_pips | 453.0000000000145 |
| max_drawdown_pips | 1735.599999999978 |
| max_window_share | 0.07742008614826705 |
| max_year_share | 0.3662434822035788 |
| mean_raw_pips | -2.835849056603672 |
| movement_to_cost | 0.5168500687757723 |
| n | 212 |
| net_usd_norm | -1764.3999999999783 |
| pip | 0.0001 |
| profit_factor | 0.08844802645175157 |
| reason | n=212 below 1000 |
| symbol | EURUSD |
| timeframe | M5 |
| total_cost_pips | 1163.2 |
| total_net_pips | -1764.3999999999783 |
| trades | 212 |
| verdict | INSUFF |
| win_rate | 0.18867924528301888 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### G-DAYGAP / EURGBP / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 13.308235294117646 |
| avg_duration_bars | 24.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -18.7512195121951 |
| avg_win_pips | 3.1777777777779774 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -17.977254901960755 |
| exposure | 0.02397311250910743 |
| gross_loss_pips | 1510.399999999992 |
| gross_profit_pips | 319.79999999999905 |
| max_drawdown_pips | 4546.699999999993 |
| max_window_share | 0.06524584442214576 |
| max_year_share | 0.36156799441560267 |
| mean_raw_pips | -4.669019607843109 |
| movement_to_cost | 0.3508368694012237 |
| n | 255 |
| net_usd_norm | -4584.199999999993 |
| pip | 0.0001 |
| profit_factor | 0.0062001387443639065 |
| reason | n=255 below 1000 |
| symbol | EURGBP |
| timeframe | M5 |
| total_cost_pips | 3393.6 |
| total_net_pips | -4584.199999999993 |
| trades | 255 |
| verdict | INSUFF |
| win_rate | 0.03529411764705882 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### G-DAYGAP / GBPUSD / H=24

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 8.07080291970803 |
| avg_duration_bars | 24.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -16.20372093023249 |
| avg_win_pips | 9.474576271186349 |
| bars_min | 5 |
| bucket | UNRESOLVED |
| commission | 0.0 |
| expectancy_net_pips | -10.674452554744493 |
| exposure | 0.029246424251049598 |
| gross_loss_pips | 1820.59999999999 |
| gross_profit_pips | 1107.1999999999994 |
| max_drawdown_pips | 2906.7999999999915 |
| max_window_share | 0.0561405908096277 |
| max_year_share | 0.3263471006564577 |
| mean_raw_pips | -2.603649635036463 |
| movement_to_cost | 0.32260106719724646 |
| n | 274 |
| net_usd_norm | -2924.7999999999915 |
| pip | 0.0001 |
| profit_factor | 0.1604569722716565 |
| reason | n=274 below 1000 |
| symbol | GBPUSD |
| timeframe | M5 |
| total_cost_pips | 2211.4 |
| total_net_pips | -2924.7999999999915 |
| trades | 274 |
| verdict | INSUFF |
| win_rate | 0.21532846715328466 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / EURUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.1010206345684495 |
| avg_duration_bars | 2.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -10.609720710917689 |
| avg_win_pips | 9.710399999999982 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -2.719724872420702 |
| exposure | 0.4268396628468605 |
| gross_loss_pips | 23490.100000000046 |
| gross_profit_pips | 20701.59999999994 |
| max_drawdown_pips | 12358.200000000095 |
| max_window_share | 0.05728597301310144 |
| max_year_share | 0.38860154350698883 |
| mean_raw_pips | -0.6187042378522528 |
| movement_to_cost | 0.29447794451544496 |
| n | 4507 |
| net_usd_norm | -12257.800000000112 |
| pip | 0.0001 |
| profit_factor | 0.5809442412225199 |
| reason | movement-to-cost 0.29 (bar 1.0), |mean| 0.62 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 9469.300000000001 |
| total_net_pips | -12257.800000000112 |
| trades | 4507 |
| verdict | INSUFF |
| win_rate | 0.38828489017084533 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / EURGBP / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.884344982628245 |
| avg_duration_bars | 2.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -8.045145089285723 |
| avg_win_pips | 6.329870129870127 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -4.199468628653185 |
| exposure | 0.45963082992813864 |
| gross_loss_pips | 15930.399999999994 |
| gross_profit_pips | 14388.49999999996 |
| max_drawdown_pips | 20547.899999999998 |
| max_window_share | 0.04649114269028622 |
| max_year_share | 0.3479462721432745 |
| mean_raw_pips | -0.3151236460249405 |
| movement_to_cost | 0.08112658567512712 |
| n | 4893 |
| net_usd_norm | -20548.0 |
| pip | 0.0001 |
| profit_factor | 0.28736413514694514 |
| reason | movement-to-cost 0.08 (bar 1.0), |mean| 0.32 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 19006.100000000002 |
| total_net_pips | -20548.0 |
| trades | 4893 |
| verdict | INSUFF |
| win_rate | 0.2675250357653791 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / GBPUSD / H=2

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.6920685434516525 |
| avg_duration_bars | 2.0 |
| avg_duration_hours | 2.0 |
| avg_loss_pips | -14.783949645948068 |
| avg_win_pips | 13.698120544394106 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -4.025605875152969 |
| exposure | 0.435872812633376 |
| gross_loss_pips | 28249.79999999999 |
| gross_profit_pips | 26887.30000000011 |
| max_drawdown_pips | 16488.599999999886 |
| max_window_share | 0.07294795860039162 |
| max_year_share | 0.35561217664157163 |
| mean_raw_pips | -0.3335373317013171 |
| movement_to_cost | 0.09033887853812668 |
| n | 4085 |
| net_usd_norm | -16444.599999999882 |
| pip | 0.0001 |
| profit_factor | 0.5624201720027278 |
| reason | movement-to-cost 0.09 (bar 1.0), |mean| 0.33 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 15082.1 |
| total_net_pips | -16444.599999999882 |
| trades | 4085 |
| verdict | INSUFF |
| win_rate | 0.3777233782129743 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / EURUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 2.0976031957390147 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 6.0 |
| avg_loss_pips | -18.710919309514278 |
| avg_win_pips | 17.186799007444154 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -2.658122503328914 |
| exposure | 1.2802348707263946 |
| gross_loss_pips | 41426.600000000035 |
| gross_profit_pips | 38900.89999999995 |
| max_drawdown_pips | 12432.20000000008 |
| max_window_share | 0.07395533291588333 |
| max_year_share | 0.4409851805468546 |
| mean_raw_pips | -0.5605193075898997 |
| movement_to_cost | 0.2672189424236746 |
| n | 4506 |
| net_usd_norm | -11977.500000000095 |
| pip | 0.0001 |
| profit_factor | 0.743021182649664 |
| reason | movement-to-cost 0.27 (bar 1.0), |mean| 0.56 (bar 2.0) |
| symbol | EURUSD |
| timeframe | H1 |
| total_cost_pips | 9451.800000000001 |
| total_net_pips | -11977.500000000095 |
| trades | 4506 |
| verdict | INSUFF |
| win_rate | 0.4471815357301376 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / EURGBP / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.85417944001635 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 6.0 |
| avg_loss_pips | -12.152079453755436 |
| avg_win_pips | 10.939018551765392 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -4.266278356836304 |
| exposure | 1.378892489784416 |
| gross_loss_pips | 27438.800000000007 |
| gross_profit_pips | 25422.399999999965 |
| max_drawdown_pips | 20875.300000000047 |
| max_window_share | 0.04918346914236734 |
| max_year_share | 0.33782676803242145 |
| mean_raw_pips | -0.41209891681995514 |
| movement_to_cost | 0.10692260784261953 |
| n | 4893 |
| net_usd_norm | -20874.900000000045 |
| pip | 0.0001 |
| profit_factor | 0.46685140726362473 |
| reason | movement-to-cost 0.11 (bar 1.0), |mean| 0.41 (bar 2.0) |
| symbol | EURGBP |
| timeframe | H1 |
| total_cost_pips | 18858.5 |
| total_net_pips | -20874.900000000045 |
| trades | 4893 |
| verdict | INSUFF |
| win_rate | 0.34150827713059473 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |

### P-WICK / GBPUSD / H=6

| metric | value |
|---|---|
| _pos_symbols | 0 |
| avg_cost_pips | 3.6516895200783543 |
| avg_duration_bars | 6.0 |
| avg_duration_hours | 6.0 |
| avg_loss_pips | -26.12237640936687 |
| avg_win_pips | 25.6057930258718 |
| bars_min | 60 |
| bucket | REJECTED |
| commission | 0.0 |
| expectancy_net_pips | -3.6021302644466053 |
| exposure | 1.3072983354673495 |
| gross_loss_pips | 51976.59999999996 |
| gross_profit_pips | 52179.00000000003 |
| max_drawdown_pips | 14791.399999999929 |
| max_window_share | 0.11355371114328687 |
| max_year_share | 0.4079300664124359 |
| mean_raw_pips | 0.04955925563174954 |
| movement_to_cost | 0.01357159620478527 |
| n | 4084 |
| net_usd_norm | -14711.09999999993 |
| pip | 0.0001 |
| profit_factor | 0.755784535394485 |
| reason | movement-to-cost 0.01 (bar 1.0), |mean| 0.05 (bar 2.0) |
| symbol | GBPUSD |
| timeframe | H1 |
| total_cost_pips | 14913.5 |
| total_net_pips | -14711.09999999993 |
| trades | 4084 |
| verdict | INSUFF |
| win_rate | 0.43535749265426055 |
| years_count | 4 |
| years_positive_share | 0.0 |
| years_total | 4 |
