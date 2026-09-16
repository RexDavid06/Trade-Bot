PHASE 5 — BROKER-ACCURATE DATA + MARKET EXPANSION

OBJECTIVE

Phase 3 and Phase 4 both failed to identify an economically viable forex behavior.

Phase 3:
- M5 behavior did not clear realistic costs.
- Best movement-to-cost ratio: 0.66.

Phase 4:
- 1h–24h multi-hour behavior also did not clear costs.
- Best movement-to-cost ratio: 0.73.
- No behavior was classified as potentially viable.

Therefore:

DO NOT create another M5 strategy.
DO NOT create Strategy 04.
DO NOT tune Strategies 01–03.
DO NOT modify bot.py.
DO NOT optimize parameters.

The purpose of Phase 5 is to determine whether the problem is:

A. inadequate/overestimated historical cost data,
B. timeframe construction,
C. the selected FX pairs,
D. or the FX market itself.

The ultimate project goal remains:

FIND ONE CREDIBLE EDGE → VALIDATE IT → CONNECT IT TO MT5 DEMO.

This phase must move us toward that goal without unnecessary infrastructure work.

==================================================
PHASE 5A — AUDIT CURRENT DATA/COST MODEL
==================================================

Before obtaining anything new, inspect the existing project and document:

1. What historical price data is currently available.
2. Which files contain bid/ask/spread information.
3. How spread is represented.
4. How transaction costs are currently modeled.
5. What slippage/commission assumptions are used.
6. Whether the historical spread represents actual broker conditions.
7. Which broker/account the current MT5 bot is configured to use.
8. Whether historical data can realistically represent that broker's execution environment.

Do NOT modify the existing strategy engine merely to perform this audit.

==================================================
PHASE 5B — BROKER-ACCURATE DATA
==================================================

We eventually need historical data that is as close as practical to the broker/account that will be used for demo trading.

First inspect the repository and local machine for existing MT5/exported historical data.

Look for:

- MT5 history
- CSV exports
- tick data
- bid/ask data
- broker-specific data
- existing data download utilities
- symbol specifications
- contract specifications

Do NOT download random historical data from an arbitrary source merely to produce another backtest.

If broker-accurate historical bid/ask data is NOT already available locally:

STOP the implementation portion and clearly report:

- what is missing
- what exact data is required
- what format the data should have
- how much history is needed
- which symbols/timeframes are needed
- what broker information is needed

Do not fabricate broker data.

==================================================
PHASE 5C — TIMEFRAME CONSTRUCTION
==================================================

If suitable underlying data exists, construct/verify:

- M5
- M15
- H1
- H4

from the same underlying source where possible.

Important:

Do NOT independently source different datasets for each timeframe.

Where tick or bid/ask data exists, preserve:

- timestamp
- bid
- ask
- spread
- OHLC construction rules

Document timezone/session assumptions.

Ensure bars are constructed without lookahead.

==================================================
PHASE 5D — COST REALISM
==================================================

Determine the actual trading economics for the intended MT5 demo account.

Document:

- typical spread
- commission
- minimum lot
- lot step
- contract size
- stop distance restrictions
- execution/filling constraints
- trading hours
- symbol specifications

Do not guess values.

If exact values cannot be obtained from the repository or broker configuration, clearly mark them UNKNOWN.

Do not silently substitute generic values.

==================================================
PHASE 5E — RECHECK EXISTING MARKET BEHAVIORS
==================================================

ONLY after reliable data/cost information is available:

Re-test the existing broad market behaviors that were already identified in Phases 3 and 4.

Do NOT create new strategies.

Investigate only:

1. directional persistence
2. multi-hour reversal
3. session-open behavior
4. volatility expansion
5. breakout continuation/failure
6. movement-to-cost

Use a small number of economically motivated horizons.

Do not perform a parameter sweep.

The purpose is NOT to find a profitable backtest.

The purpose is to determine whether improved data/cost modeling materially changes the economic conclusion.

==================================================
PHASE 5F — MARKET EXPANSION DECISION
==================================================

If broker-accurate FX data STILL shows no economically viable behavior:

DO NOT continue searching endlessly through EURUSD/EURGBP/GBPUSD.

Expand the research universe.

Investigate a SMALL, predefined set of liquid instruments available through the intended MT5 broker.

Before researching them, inspect broker availability/specifications if possible.

Potential categories may include:

- major FX pairs not previously studied
- selected indices
- selected commodities
- selected liquid CFDs

Do NOT automatically assume any instrument is better.

Do NOT search hundreds of symbols.

Create a small, economically justified universe.

For every candidate instrument measure:

- available history
- spread/cost burden
- typical movement
- volatility
- movement-to-cost
- basic directional persistence
- basic reversal behavior
- session behavior where applicable

The central question remains:

"Does this market have enough movement relative to realistic trading costs to justify strategy construction?"

==================================================
PHASE 5G — ECONOMIC VIABILITY GATE
==================================================

Use the existing research philosophy.

A behavior is NOT interesting merely because:

- it has a positive average,
- it has statistical significance,
- it looks profitable before costs,
- or it works in one period.

The behavior must have enough movement to plausibly survive realistic transaction costs.

Use:

movement-to-cost ratio = expected gross movement / realistic round-trip cost

Classify findings as:

1. ECONOMICALLY INSUFFICIENT
2. BORDERLINE
3. POTENTIALLY VIABLE

Do not invent arbitrary thresholds.

Use the project's existing viability logic and explain it.

==================================================
PHASE 5H — IF A VIABLE BEHAVIOR IS FOUND
==================================================

If and ONLY IF a behavior clearly reaches the project's viability bar:

DO NOT immediately implement it.

Produce a candidate specification containing:

- instrument
- timeframe
- signal concept
- entry timing
- exit concept
- expected movement
- estimated realistic cost
- movement-to-cost ratio
- sample size
- development period
- known failure conditions
- data limitations
- reasons it deserves formal strategy validation

Then STOP.

Do not create Strategy 04 yet.

Do not touch bot.py.

We will review the candidate before implementation.

==================================================
PHASE 5I — IF NOTHING IS VIABLE
==================================================

If nothing clears the viability bar:

DO NOT invent another strategy.

Instead give a clear decision among:

A. obtain better broker/tick/spread data
B. investigate another timeframe
C. investigate another instrument class
D. change broker/data source
E. reconsider the premise of this trading bot project

Explain which limitation is currently preventing credible strategy construction.

==================================================
STRICT PROTECTION RULES
==================================================

DO NOT MODIFY:

- bot.py
- V1
- V2
- Strategy 01
- Strategy 02
- Strategy 03

DO NOT:

- read validation data
- read holdout data
- change the 60/20/20 split
- optimize parameters
- run large parameter sweeps
- tune thresholds repeatedly
- create Strategy 04
- alter frozen historical outputs
- fabricate broker data
- fabricate spread data
- fabricate commission data
- use lookahead
- use future information
- select results because they look profitable

Research code may be added under:

backtest/market_research/

Outputs may be written under:

outputs/

==================================================
OUTPUT
==================================================

Create:

PHASE_5_BROKER_DATA_AND_MARKET_EXPANSION.md

If research code is required:

backtest/market_research/

If structured results are required:

outputs/phase_5_market_research.json

The report must contain:

1. Objective
2. Current data audit
3. Current cost-model audit
4. Broker/account execution requirements
5. Available historical data
6. Missing data
7. Timeframe construction assessment
8. Broker-accurate cost assessment
9. Existing FX behavior re-check
10. Market expansion universe
11. Instrument-level findings
12. Movement-to-cost analysis
13. Economically insufficient behaviors
14. Borderline behaviors
15. Potentially viable behaviors
16. Exact evidence for any candidate
17. Limitations
18. Final decision
19. Recommended next action

==================================================
TESTS
==================================================

If research code is added:

Run the existing test suite.

Expected existing baseline:

74 tests passing.

Do not modify tests simply to make them pass.

==================================================
STOP CONDITION
==================================================

STOP after producing:

PHASE_5_BROKER_DATA_AND_MARKET_EXPANSION.md

Do not implement any trading strategy.

Do not modify bot.py.

Do not connect to MT5.

Do not start demo trading yet.

Report exactly what was discovered and what the next concrete action should be.

The goal is no longer "perform more research."

The goal is:

FIND WHETHER THERE IS A CREDIBLE MARKET/BEHAVIOR WORTH TURNING INTO THE FIRST DEMO STRATEGY.