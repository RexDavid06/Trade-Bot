# SCALPER PROBE RESULTS — fixed high-win-rate geometry on DEV (research only)


Entry: direction of the closed M5 bar (unbiased); entry at next bar open; intrabar stops, SL checked first; time-stop 60 bars. Cost = entry + exit observed spread + 1.0 pip slippage. DEV rows only, EURUSD, EURGBP, GBPUSD, EURJPY excluded.


## Win rate vs expectancy (net, after costs)


| symbol | geometry | n | win% | avg_win | avg_loss | exp_net | PF | m2c | years+ |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | A-symmetric | 245,330 | 46.3 | +10.29 | -12.58 | -1.979 | 0.707 | -0.059 | 0/4 |
| EURUSD | B-winrate | 245,330 | 61.8 | +5.97 | -14.81 | -1.967 | 0.652 | -0.050 | 0/4 |
| EURUSD | C-trend | 245,330 | 32.2 | +12.97 | -9.13 | -2.017 | 0.674 | -0.074 | 0/4 |
| EURGBP | A-symmetric | 245,524 | 36.0 | +7.87 | -10.81 | -4.077 | 0.410 | -0.042 | 0/4 |
| EURGBP | B-winrate | 245,524 | 46.5 | +4.56 | -11.16 | -3.851 | 0.355 | 0.030 | 0/4 |
| EURGBP | C-trend | 245,524 | 27.8 | +9.23 | -9.69 | -4.430 | 0.367 | -0.110 | 0/4 |
| GBPUSD | A-symmetric | 219,355 | 46.2 | +10.18 | -15.36 | -3.551 | 0.570 | -0.040 | 0/4 |
| GBPUSD | B-winrate | 219,355 | 63.8 | +4.93 | -18.43 | -3.524 | 0.471 | -0.031 | 0/4 |
| GBPUSD | C-trend | 219,355 | 29.0 | +14.50 | -11.01 | -3.622 | 0.537 | -0.055 | 0/4 |

## The 60:40 tradeoff


A tight TP / wide SL (B-winrate) mechanically raises win% — the question is whether the win% is high enough to pay for the larger losses plus ~2 pips of spreads+slippage per round trip.


| symbol | geometry | win% (raw) | win% (net) | expectancy | years+ |
|---|---|---|---|---|---|
| EURUSD | A-symmetric | 49.5 | 46.3 | -1.979 | 0/4 |
| EURUSD | B-winrate | 64.2 | 61.8 | -1.967 | 0/4 |
| EURUSD | C-trend | 34.6 | 32.2 | -2.017 | 0/4 |
| EURGBP | A-symmetric | 49.0 | 36.0 | -4.077 | 0/4 |
| EURGBP | B-winrate | 59.3 | 46.5 | -3.851 | 0/4 |
| EURGBP | C-trend | 38.7 | 27.8 | -4.430 | 0/4 |
| GBPUSD | A-symmetric | 49.5 | 46.2 | -3.551 | 0/4 |
| GBPUSD | B-winrate | 67.6 | 63.8 | -3.524 | 0/4 |
| GBPUSD | C-trend | 31.1 | 29.0 | -3.622 | 0/4 |

## Full metrics


### EURUSD / A-symmetric (TP 14 / SL 14)

| metric | value |
|---|---|
| n | 245330 |
| win_rate_net | 0.4633677088003913 |
| win_rate_raw | 0.4947784616638813 |
| avg_win_pips | 10.292873731065397 |
| avg_loss_pips | -12.575521830280234 |
| expectancy_net_pips | -1.9790457750784707 |
| mean_gross_pips | -0.11057229038438536 |
| mean_cost_pips | 1.8684734846940854 |
| profit_factor | 0.7067398706662584 |
| total_net_pips | -485519.3000000012 |
| hitrate_raw_m2cost | -0.059177875035507255 |
| exit_reasons | {'SL': 88808, 'TP': 87066, 'time': 69456} |
| years_positive | 0 |
| years_total | 4 |

### EURUSD / B-winrate (TP 8 / SL 20)

| metric | value |
|---|---|
| n | 245330 |
| win_rate_net | 0.6178861125830514 |
| win_rate_raw | 0.642314433620022 |
| avg_win_pips | 5.973306901692002 |
| avg_loss_pips | -14.807904505888393 |
| expectancy_net_pips | -1.9674825744919806 |
| mean_gross_pips | -0.09391228141734602 |
| mean_cost_pips | 1.873570293074634 |
| profit_factor | 0.6522841659580864 |
| total_net_pips | -482682.5000001176 |
| hitrate_raw_m2cost | -0.05012477074624763 |
| exit_reasons | {'SL': 46457, 'TP': 143975, 'time': 54898} |
| years_positive | 0 |
| years_total | 4 |

### EURUSD / C-trend (TP 20 / SL 8)

| metric | value |
|---|---|
| n | 245330 |
| win_rate_net | 0.32175437166265847 |
| win_rate_raw | 0.34604002771776793 |
| avg_win_pips | 12.970052954292097 |
| avg_loss_pips | -9.12667163479381 |
| expectancy_net_pips | -2.0169538988296587 |
| mean_gross_pips | -0.13952512941703066 |
| mean_cost_pips | 1.877428769412628 |
| profit_factor | 0.6741658926104267 |
| total_net_pips | -494819.29999988014 |
| hitrate_raw_m2cost | -0.07431713612265699 |
| exit_reasons | {'SL': 146672, 'TP': 45107, 'time': 53551} |
| years_positive | 0 |
| years_total | 4 |

### EURGBP / A-symmetric (TP 14 / SL 14)

| metric | value |
|---|---|
| n | 245524 |
| win_rate_net | 0.3602743519981753 |
| win_rate_raw | 0.4901924048158225 |
| avg_win_pips | 7.87085443610356 |
| avg_loss_pips | -10.805348002139047 |
| expectancy_net_pips | -4.076791270914449 |
| mean_gross_pips | -0.165307668496763 |
| mean_cost_pips | 3.9114836024176864 |
| profit_factor | 0.4102255490066233 |
| total_net_pips | -1000950.0999999992 |
| hitrate_raw_m2cost | -0.04226214022592001 |
| exit_reasons | {'time': 129017, 'SL': 59302, 'TP': 57205} |
| years_positive | 0 |
| years_total | 4 |

### EURGBP / B-winrate (TP 8 / SL 20)

| metric | value |
|---|---|
| n | 245524 |
| win_rate_net | 0.46484254085140353 |
| win_rate_raw | 0.5929644352486926 |
| avg_win_pips | 4.56265399106303 |
| avg_loss_pips | -11.15970744478438 |
| expectancy_net_pips | -3.851285006760948 |
| mean_gross_pips | 0.11779866734015802 |
| mean_cost_pips | 3.9690836741011064 |
| profit_factor | 0.35513134730748425 |
| total_net_pips | -945582.899999975 |
| hitrate_raw_m2cost | 0.029679058697807962 |
| exit_reasons | {'TP': 112405, 'time': 105730, 'SL': 27389} |
| years_positive | 0 |
| years_total | 4 |

### EURGBP / C-trend (TP 20 / SL 8)

| metric | value |
|---|---|
| n | 245524 |
| win_rate_net | 0.2778547107411088 |
| win_rate_raw | 0.3866628109675633 |
| avg_win_pips | 9.233418352389338 |
| avg_loss_pips | -9.687725601227424 |
| expectancy_net_pips | -4.430396621104357 |
| mean_gross_pips | -0.4383677359444545 |
| mean_cost_pips | 3.9920288851599026 |
| profit_factor | 0.36671938335159393 |
| total_net_pips | -1087768.7000000263 |
| hitrate_raw_m2cost | -0.10981076253582656 |
| exit_reasons | {'time': 103209, 'SL': 116187, 'TP': 26128} |
| years_positive | 0 |
| years_total | 4 |

### GBPUSD / A-symmetric (TP 14 / SL 14)

| metric | value |
|---|---|
| n | 219355 |
| win_rate_net | 0.4623555423856306 |
| win_rate_raw | 0.49453625401746026 |
| avg_win_pips | 10.178668901597936 |
| avg_loss_pips | -15.358294823420222 |
| expectancy_net_pips | -3.5511381094572783 |
| mean_gross_pips | -0.13744660481867865 |
| mean_cost_pips | 3.4136915046386 |
| profit_factor | 0.5699396642320316 |
| total_net_pips | -778959.9000000013 |
| hitrate_raw_m2cost | -0.04026333505295167 |
| exit_reasons | {'TP': 93283, 'SL': 95376, 'time': 30696} |
| years_positive | 0 |
| years_total | 4 |

### GBPUSD / B-winrate (TP 8 / SL 20)

| metric | value |
|---|---|
| n | 219355 |
| win_rate_net | 0.63822570718698 |
| win_rate_raw | 0.6759180324132115 |
| avg_win_pips | 4.926040372004444 |
| avg_loss_pips | -18.431716168706043 |
| expectancy_net_pips | -3.5241954822097843 |
| mean_gross_pips | -0.10678261266042334 |
| mean_cost_pips | 3.4174128695493606 |
| profit_factor | 0.4714859795237457 |
| total_net_pips | -773049.9000001273 |
| hitrate_raw_m2cost | -0.031246623319032652 |
| exit_reasons | {'TP': 143229, 'SL': 52348, 'time': 23778} |
| years_positive | 0 |
| years_total | 4 |

### GBPUSD / C-trend (TP 20 / SL 8)

| metric | value |
|---|---|
| n | 219355 |
| win_rate_net | 0.2897814045724966 |
| win_rate_raw | 0.3113355063709512 |
| avg_win_pips | 14.497618186108724 |
| avg_loss_pips | -11.01475576095944 |
| expectancy_net_pips | -3.6217442045992585 |
| mean_gross_pips | -0.1881543616506141 |
| mean_cost_pips | 3.433589842948645 |
| profit_factor | 0.5370321181583878 |
| total_net_pips | -794447.6999998704 |
| hitrate_raw_m2cost | -0.05479814720357916 |
| exit_reasons | {'TP': 50647, 'SL': 145883, 'time': 22825} |
| years_positive | 0 |
| years_total | 4 |


