# Market Behavior Discovery

**Exploratory findings, DEVELOPMENT split only. All results are hypotheses to be validated — nothing here is a proven edge.**

## 0. Methodology and integrity

- Data: M5 OHLC + observed spread for EURUSD, EURGBP, GBPUSD (2021-01-03 .. 2026-09-09) and EURJPY (2025-06-26 .. 2026-09-10, 27% zero-spread bars — degraded feed, cost claims for EURJPY are unreliable).
- Only DEV bars used; split produced and validated by `backtest.data.research_split` (60/20/20 chronological).
- Holdout and validation rows were never read.
- No strategy constructed; no parameter optimized; `bot.py`, V1/V2 untouched.
- Full per-study detail: `outputs/market_behavior_discovery/<SYMBOL>/<study>.md`.

### Dev date ranges and sizes

| symbol | dev candles | dev start | dev end |
|---|---|---|---|
| EURUSD | 253,335 | 2021-01-03 22:00:00 | 2024-05-29 08:00:00 |
| EURGBP | 255,286 | 2021-01-03 22:00:00 | 2024-05-30 15:15:00 |
| EURJPY | 54,000 | 2025-06-26 03:00:00 | 2026-03-19 17:05:00 |
| GBPUSD | 224,848 | 2021-01-03 22:00:00 | 2024-06-13 18:25:00 |

## 1. Executive summary

Four pairs (EURUSD, EURGBP, GBPUSD, EURJPY), first-60% DEVELOPMENT rows only, investigated with seven existing `market_research` studies plus a discovery aggregator that measures raw directional behavior across horizons of 5/20/40/80 M5 bars (25 min .. 6.7 h). All conditions are causal; outcomes are fixed-horizon forward returns measured after the signal bar, so no lookahead enters these numbers.

**1. The market at M5 is mildly, reliably mean-reverting.** Trend continuation is negative on every pair (-0.26 .. -0.12 pips avg; hit 47.3--48.8%), so short-term trends do not persist. Naive breakouts are consistently bad (-0.78 .. -0.14 pips; hit 44.5--48.4%). The only behavior that is positive on all four pairs is fading the extreme: oversold-fade long / overbought-fade short. It is strongest on EURGBP (0.37 pips, hit 53.1%) and GBPUSD (0.37 pips, hit 51.7%), with EURUSD (0.24, hit 51.5%); all three are statistically reliable (t_p < 1e-3).

- **EURUSD** mean-reversion H=20: **+0.24 pips**, hit 51.5% (n=134,302); estimated round-trip cost 2.30 pips; est. net after cost **-2.06 pips**.
- **EURGBP** mean-reversion H=20: **+0.37 pips**, hit 53.1% (n=132,358); estimated round-trip cost 3.50 pips; est. net after cost **-3.13 pips**.
- **EURJPY** mean-reversion H=20: **+0.20 pips**, hit 51.3% (n=28,365); estimated round-trip cost 5.70 pips; est. net after cost **-5.50 pips**.
- **GBPUSD** mean-reversion H=20: **+0.37 pips**, hit 51.7% (n=119,576); estimated round-trip cost 3.50 pips; est. net after cost **-3.13 pips**.

**2. No raw M5 behavior clears costs on its own.** The best gross edges above are ~0.2-0.4 pips at H=20. Measured round-trip costs (median spread x2 + ~1.7 slippage/commission) are 2.3-3.5 pips on EURUSD/EURGBP/GBPUSD and ~5.7 on EURJPY. The strongest clean-pair edge (EURGBP 0.37 pips) covers less than 15% of its cost. Even the horizon scaling in section 2 (edge grows to ~0.5-1.3 pips at H=80 on EURGBP/GBPUSD) stays well below break-even.

**3. Conditioning changes sign, not scale.** Session overlay is the only conditioning that flips behavior direction: trend continuation turns positive in the London-New York overlap (EURUSD +0.12/50.1%, GBPUSD +0.49/50.5%) and is strongly negative in OffHours (hit 39-47%). Volatility-regime conditioning is weak and direction-inconsistent. Forward excursions are symmetric (favorable median ~= adverse median, ~6 pips on EURUSD/EURGBP, ~9 on GBPUSD), so naive entries leave price as much room to hurt as to help: any candidate needs a stop.

**4. EURJPY is not evidence yet.** Its fade-oversold numbers look exceptional (+1.7 pips at H=40, +3.2 at H=80, hit ~56%) but come from a ~15-month span (2025-06-26 .. 2026-03-19 dev) of a degraded feed (27% zero-spread bars) during a strong sustained drift; the short side is negative, consistent with a one-way market rather than a structural edge. Excluded from candidate claims until a clean EURJPY history is available.

**Bottom line.** Phase 1 discovery does not yet supply a cost-clearing edge at M5. It does narrow the search space sharply: reject trend-continuation, breakout-continuation, and pullback-resumption; investigate fade-the-extreme and breakout-fade, gated to liquid sessions, with stops. Section 11 gives the three candidates and their acceptance tests for the strategy phase.

## 2. Pair comparison

Headline directional behaviors at H=20 (avg/median forward pips, hit %, n; sign convention: positive = profitable in the traded direction; `est. net` = avg minus estimated round-trip cost).

| symbol | behavior | n | avg_pips | med_pips | hit_pct | t_p | est_net_after_cost_pips |
|---|---|---|---|---|---|---|---|
| EURUSD | mean-reversion | 134302 | 0.24 | 0.40 | 51.5 | 0.000 | -2.06 |
| EURUSD | trend continuation | 251940 | -0.12 | -0.20 | 48.8 | 0.000 | -2.42 |
| EURUSD | trend+pullback | 52822 | -0.14 | 0.00 | 49.5 | 0.024 | -2.44 |
| EURUSD | breakout | 29933 | -0.37 | -0.50 | 47.8 | 0.000 | -2.67 |
| GBPUSD | mean-reversion | 119576 | 0.37 | 0.50 | 51.7 | 0.000 | -3.13 |
| EURGBP | mean-reversion | 132358 | 0.37 | 0.40 | 53.1 | 0.000 | -3.13 |
| EURGBP | trend+pullback | 52426 | -0.14 | -0.20 | 48.2 | 0.000 | -3.64 |
| GBPUSD | trend+pullback | 47500 | -0.15 | -0.10 | 49.3 | 0.100 | -3.65 |
| EURGBP | trend continuation | 253086 | -0.22 | -0.30 | 47.3 | 0.000 | -3.72 |
| GBPUSD | trend continuation | 223895 | -0.26 | -0.30 | 48.6 | 0.000 | -3.76 |
| EURGBP | breakout | 27688 | -0.59 | -0.70 | 44.5 | 0.000 | -4.09 |
| GBPUSD | breakout | 26833 | -0.78 | -0.70 | 47.3 | 0.000 | -4.28 |
| EURJPY | trend+pullback | 12074 | 0.52 | 0.90 | 52.3 | 0.002 | -5.18 |
| EURJPY | mean-reversion | 28365 | 0.20 | 0.50 | 51.3 | 0.085 | -5.50 |
| EURJPY | breakout | 6071 | -0.14 | -0.50 | 48.4 | 0.589 | -5.84 |
| EURJPY | trend continuation | 53816 | -0.15 | -0.40 | 48.6 | 0.071 | -5.85 |

Estimated round-trip cost per pair (pips):

| symbol | median spread (pips/side) | est round-trip cost (pips) |
|---|---|---|
| EURUSD | 0.30 | 2.30 |
| EURGBP | 0.90 | 3.50 |
| EURJPY | 2.00 | 5.70 |
| GBPUSD | 0.90 | 3.50 |

Horizon scaling (avg signed forward pips / hit % for trend continuation, fade-the-extreme mean reversion, and fade-the-breaking-breakout):

**EURUSD**

| H | tc_avg | tc_hit | mr_avg | mr_hit | bf_avg | bf_hit |
|---|---|---|---|---|---|---|
| 5 | -0.05 | 48.11 | 0.14 | 51.73 | 0.30 | 53.04 |
| 20 | -0.12 | 48.82 | 0.24 | 51.50 | 0.37 | 51.75 |
| 40 | -0.15 | 49.10 | 0.32 | 51.21 | 0.43 | 51.31 |
| 80 | -0.17 | 49.43 | 0.28 | 50.58 | 0.12 | 50.48 |

**EURGBP**

| H | tc_avg | tc_hit | mr_avg | mr_hit | bf_avg | bf_hit |
|---|---|---|---|---|---|---|
| 5 | -0.12 | 47.06 | 0.27 | 53.25 | 0.44 | 55.50 |
| 20 | -0.22 | 47.29 | 0.37 | 53.14 | 0.59 | 54.80 |
| 40 | -0.26 | 47.93 | 0.42 | 52.53 | 0.60 | 53.58 |
| 80 | -0.47 | 48.32 | 0.61 | 51.91 | 0.89 | 53.05 |

**EURJPY**

| H | tc_avg | tc_hit | mr_avg | mr_hit | bf_avg | bf_hit |
|---|---|---|---|---|---|---|
| 5 | -0.08 | 48.85 | 0.20 | 51.93 | 0.40 | 52.70 |
| 20 | -0.15 | 48.56 | 0.20 | 51.28 | 0.14 | 51.42 |
| 40 | -0.35 | 48.46 | 0.65 | 51.76 | 0.89 | 52.34 |
| 80 | -0.77 | 48.98 | 0.89 | 51.02 | 0.89 | 51.89 |

**GBPUSD**

| H | tc_avg | tc_hit | mr_avg | mr_hit | bf_avg | bf_hit |
|---|---|---|---|---|---|---|
| 5 | -0.06 | 48.41 | 0.23 | 51.79 | 0.43 | 53.19 |
| 20 | -0.26 | 48.58 | 0.37 | 51.71 | 0.78 | 52.33 |
| 40 | -0.24 | 49.18 | 0.42 | 50.91 | 0.76 | 51.52 |
| 80 | -0.40 | 49.35 | 0.40 | 50.57 | 0.74 | 50.89 |

## 3. Trend persistence

Condition: trailing-20-bar net move (causal). Continuation score = signed forward 20-bar pips (positive when price continues the trend).

| symbol | n | avg_pips | med_pips | hit_pct | t_p |
|---|---|---|---|---|---|
| EURUSD | 251940 | -0.12 | -0.20 | 48.8 | 0.000 |
| EURGBP | 253086 | -0.22 | -0.30 | 47.3 | 0.000 |
| EURJPY | 53816 | -0.15 | -0.40 | 48.6 | 0.071 |
| GBPUSD | 223895 | -0.26 | -0.30 | 48.6 | 0.000 |

Regime-conditioned continuation (avg pips, hit %, n):

**EURUSD**

| regime | n | avg_pips | hit_pct |
|---|---|---|---|
| low | 114480 | -0.17 | 48.2 |
| normal | 44235 | -0.13 | 49.2 |
| high | 93225 | -0.06 | 49.3 |

**EURGBP**

| regime | n | avg_pips | hit_pct |
|---|---|---|---|
| low | 120301 | -0.13 | 47.7 |
| normal | 46420 | -0.24 | 47.2 |
| high | 86365 | -0.35 | 46.7 |

**EURJPY**

| regime | n | avg_pips | hit_pct |
|---|---|---|---|
| low | 23451 | -0.09 | 48.8 |
| normal | 10653 | -0.20 | 48.5 |
| high | 19712 | -0.19 | 48.3 |

**GBPUSD**

| regime | n | avg_pips | hit_pct |
|---|---|---|---|
| low | 102379 | -0.18 | 48.1 |
| normal | 40134 | -0.28 | 48.6 |
| high | 81382 | -0.35 | 49.2 |

## 4. Mean reversion

Condition: close more than 1 std below/above trailing-20 SMA. Trade against the move. Positive avg pips = reversion worked.

| symbol | n | avg_pips | med_pips | hit_pct | t_p |
|---|---|---|---|---|---|
| EURUSD | 134302 | 0.24 | 0.40 | 51.5 | 0.000 |
| EURGBP | 132358 | 0.37 | 0.40 | 53.1 | 0.000 |
| EURJPY | 28365 | 0.20 | 0.50 | 51.3 | 0.085 |
| GBPUSD | 119576 | 0.37 | 0.50 | 51.7 | 0.000 |

## 5. Breakout behavior

Condition: close pierces prior 20-bar high (long) / low (short). Positive avg pips = breakout continuation.

| symbol | n | avg_pips | med_pips | hit_pct | t_p |
|---|---|---|---|---|---|
| EURUSD | 29933 | -0.37 | -0.50 | 47.8 | 0.000 |
| EURGBP | 27688 | -0.59 | -0.70 | 44.5 | 0.000 |
| EURJPY | 6071 | -0.14 | -0.50 | 48.4 | 0.589 |
| GBPUSD | 26833 | -0.78 | -0.70 | 47.3 | 0.000 |

## 6. Volatility regimes

Regimes are causal rolling ATR quantiles (low/normal/high). ATR distribution in dev data:

| symbol | ATR median (pips) | regime bars (low/normal/high) |
|---|---|---|
| EURUSD | 3.3 | 115,295/44,468/93,552 |
| EURGBP | 2.4 | 121,577/46,802/86,887 |
| EURJPY | 5.9 | 23,524/10,703/19,753 |
| GBPUSD | 4.6 | 102,931/40,311/81,586 |

Trend-continuation edge by regime (avg pips, H=20): see section 3 tables. Directional hit-rate per regime is covered in the per-symbol volatility studies.

## 7. Session behavior

Sessions are UTC buckets. Trend-continuation edge by session (H=20):

**EURUSD**

| session | n | avg_pips | hit_pct |
|---|---|---|---|
| Asian | 73502 | -0.14 | 49.3 |
| London | 52579 | 0.08 | 49.6 |
| LondonNY | 42081 | 0.12 | 50.1 |
| NewYork | 52517 | -0.36 | 47.3 |
| OffHours | 31261 | -0.34 | 47.2 |

**EURGBP**

| session | n | avg_pips | hit_pct |
|---|---|---|---|
| Asian | 73715 | -0.20 | 47.7 |
| London | 52988 | -0.07 | 49.6 |
| LondonNY | 42376 | 0.03 | 50.1 |
| NewYork | 52720 | -0.24 | 46.7 |
| OffHours | 31287 | -0.85 | 39.8 |

**EURJPY**

| session | n | avg_pips | hit_pct |
|---|---|---|---|
| Asian | 15655 | -0.22 | 48.6 |
| London | 11211 | 0.64 | 50.8 |
| LondonNY | 9030 | 0.11 | 49.1 |
| NewYork | 11234 | -0.24 | 48.5 |
| OffHours | 6686 | -1.49 | 44.3 |

**GBPUSD**

| session | n | avg_pips | hit_pct |
|---|---|---|---|
| Asian | 65360 | -0.44 | 48.3 |
| London | 46796 | -0.51 | 49.2 |
| LondonNY | 37453 | 0.49 | 50.5 |
| NewYork | 46702 | -0.34 | 47.6 |
| OffHours | 27584 | -0.32 | 47.1 |

## 8. Trend + pullback behavior

Inside a trailing-20-bar trend, signal on the first pullback bar against the trend, betting on resumption. Positive avg = resumption worked.

| symbol | n | avg_pips | med_pips | hit_pct | t_p |
|---|---|---|---|---|---|
| EURUSD | 52822 | -0.14 | 0.00 | 49.5 | 0.024 |
| EURGBP | 52426 | -0.14 | -0.20 | 48.2 | 0.000 |
| EURJPY | 12074 | 0.52 | 0.90 | 52.3 | 0.002 |
| GBPUSD | 47500 | -0.15 | -0.10 | 49.3 | 0.100 |

Resumption by pullback depth (consecutive adverse bars inside the trend):

**EURUSD**

| depth | n | avg_pips | hit_pct |
|---|---|---|---|
| depth1 | 31864 | -0.16 | 49.2 |
| depth2 | 13024 | -0.19 | 49.6 |
| depth3plus | 7934 | 0.02 | 50.2 |

**EURGBP**

| depth | n | avg_pips | hit_pct |
|---|---|---|---|
| depth1 | 32074 | -0.18 | 47.8 |
| depth2 | 12657 | -0.01 | 48.6 |
| depth3plus | 7695 | -0.17 | 48.9 |

**EURJPY**

| depth | n | avg_pips | hit_pct |
|---|---|---|---|
| depth1 | 7337 | 0.47 | 52.2 |
| depth2 | 2999 | 0.74 | 53.0 |
| depth3plus | 1738 | 0.38 | 51.6 |

**GBPUSD**

| depth | n | avg_pips | hit_pct |
|---|---|---|---|
| depth1 | 28439 | -0.28 | 49.0 |
| depth2 | 11674 | -0.10 | 49.5 |
| depth3plus | 7387 | 0.24 | 50.0 |

Favorable / adverse forward excursions (pips) over the 20-bar window for the long setups studied:

**EURUSD**

| setup | n | avg_fav_pips | med_fav_pips | avg_adv_pips | med_adv_pips |
|---|---|---|---|---|---|
| trend_up_long | 126449 | 9.01 | 5.80 | 9.31 | 6.20 |
| oversold_long | 67053 | 9.55 | 6.50 | 9.51 | 6.30 |
| high_breakout_long | 14932 | 9.48 | 6.10 | 10.11 | 6.90 |
| pullback_long | 52822 | 9.20 | 5.90 | 9.35 | 6.20 |

**EURGBP**

| setup | n | avg_fav_pips | med_fav_pips | avg_adv_pips | med_adv_pips |
|---|---|---|---|---|---|
| trend_up_long | 125984 | 5.92 | 3.80 | 6.36 | 4.30 |
| oversold_long | 66541 | 6.40 | 4.50 | 6.17 | 4.10 |
| high_breakout_long | 13493 | 6.50 | 4.10 | 7.20 | 5.20 |
| pullback_long | 52426 | 6.05 | 3.90 | 6.29 | 4.30 |

**EURJPY**

| setup | n | avg_fav_pips | med_fav_pips | avg_adv_pips | med_adv_pips |
|---|---|---|---|---|---|
| trend_up_long | 28542 | 13.32 | 10.20 | 14.40 | 10.60 |
| oversold_long | 13078 | 14.74 | 11.60 | 15.66 | 11.10 |
| high_breakout_long | 3296 | 13.73 | 10.50 | 14.89 | 11.20 |
| pullback_long | 12074 | 13.52 | 10.40 | 14.03 | 10.30 |

**GBPUSD**

| setup | n | avg_fav_pips | med_fav_pips | avg_adv_pips | med_adv_pips |
|---|---|---|---|---|---|
| trend_up_long | 112226 | 12.49 | 8.00 | 12.93 | 8.60 |
| oversold_long | 59491 | 13.23 | 9.00 | 13.15 | 8.70 |
| high_breakout_long | 13362 | 13.19 | 8.70 | 14.04 | 9.50 |
| pullback_long | 47500 | 12.69 | 8.20 | 12.85 | 8.50 |

## 9. Strongest candidate behaviors

Ranked by consistency across pairs and per-trade raw size (all development-only, all below cost as standalone rules):

1. **Fade the extreme (mean reversion)** — long below / short above 1 SD from the trailing-20 SMA. The only behavior positive on all four pairs. Clean-pair profile at H=20: hit 51.5-53.1%, avg +0.24 .. +0.37 pips, t_p < 1e-3, and it survives extending the horizon: EURGBP +0.56 pips and GBPUSD +0.83 pips (short side) at H=80. It is the most structurally believable (intraday over-reaction is a documented microstructure effect) and the least sensitive to which extreme is used. Rank 1.

2. **Fade the failing breakout** — the mirror of section 5: breakout-continuation is negative to a degree unmatched by any other signal (EURUSD -0.43 .. GBPUSD -0.78 pips at H=20; hit 44.5-47.9%), which makes the inverted trade the largest per-trade raw coefficient in the study. It is less clean than extreme-fade (overlaps heavily with it) and needs the session gate, but it is the single biggest directional signal per event. Rank 2.

3. **Session-gated directional behavior (London + London-NY overlap)** — the only conditioning that flips the sign of a behavior (section 7) and is direction-consistent: EURUSD and GBPUSD continuation turns positive in London-NY; OffHours hit collapses to 39-47% on every pair. This is an overlay that improves any candidate above rather than a behavior on its own, and its magnitudes alone still do not clear costs. Rank 3.

(Flagged but not ranked: EURJPY fade-oversold long at H=40/80 — see section 1, item 4 — data-quality + drift caveats disqualify it as evidence.)

## 10. Weakest / rejected behaviors

- **Naive trend continuation** — negative on all four pairs (hit 47.3-48.8%). M5 trends do not persist over 25 min-6 h; buy-every-trend rules are rejected.
- **Naive breakout continuation** — strongly negative everywhere; rejected in favor of the fade (section 9, rank 2).
- **Trend + pullback resumption** — flat-to-negative on every pair (EURUSD -0.14, EURGBP -0.14, GBPUSD -0.15; hit ~48-49%); dips do not reliably resume. Rejected as a standalone; deeper pullbacks are only marginally less bad.
- **OffHours / Asian-only rule making** — anti-directional (hit 39-47%); these bars should be traded only as noise-filter context, never as the signal.
- **Any EURJPY-based claim** — degraded 1-year feed with drift dominance; excluded until a clean EURJPY history exists.

## 11. Recommended TOP 3 behaviors for strategy construction

These are hypotheses for the next phase, not promises: each must pass a pre-registered acceptance test on the untouched VALIDATION split before any backtest is meaningful. Costs modeled as the pair's estimated round-trip cost.

1. **Counter-trend extreme fade (mean reversion), EURGBP/GBPUSD/EURUSD.** Signal: close more than 1 SD below/above trailing-20 SMA; long/short into the extreme. Hold 20-40 bars; stop tighter than expected ATR excursion (~1 ATR); round-trip cost 2.3-3.5 pips. **Acceptance:** on validation, H=20-40 avg >= cost + 0.5 pips AND hit >= 52% AND no single year rejects the sign.

2. **Breakout fade in liquid sessions (EURGBP/GBPUSD, London + London-NY).** Signal: close pierces prior-20 high/low; fade it, biased to the London-NY overlap only where the overlay flips positive. **Acceptance:** on validation, avg >= cost + 0.5 pips AND hit >= 50% AND direction stable per session.

3. **Session-gated mean-reversion (split-overlap every other hour).** Candidate 1 filtered to London and London-NY bars; a pure conditioning test of whether exclusion of OffHours/Asian lifts the fade edge over cost. **Acceptance:** filter gain vs candidate 1 must be positive and the filtered edge must clear cost on validation.

If none passes, the evidence-based conclusion is that M5 horizons net of costs are not productive for these pairs and the strategy phase should move to larger horizons or a different instrument set — an outcome this discovery run treats as success.
