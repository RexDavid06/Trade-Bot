You are auditing my algorithmic-trading research repository.

IMPORTANT: This is an AUDIT ONLY. Do not implement a strategy, modify strategy code, modify bot.py, modify V1/V2, run optimization, run backtests, read validation/holdout data, or change any research configuration.

## OBJECTIVE

I need a rigorous reconstruction of where the trading research currently stands so we can decide what genuinely new behavioral dimension to investigate next.

The latest completed DEV-only research round is documented in the supplied EDGE DISCOVERY RESULTS.

The latest experiment found:

* B-PB — aligned two-timeframe pullback resumption → REJECTED
* E-SQZ — low-ATR squeeze then range breakout → UNRESOLVED because event count was below n=1000
* G-CANDLE — large-body candle momentum → UNRESOLVED because event count was below n=1000
* H-ALIGN — H1/H4 trend-sign confluence → REJECTED
* J-FADE-REGIME — low-ATR regime fade → REJECTED; GBPUSD H1/H=12 produced positive raw/net results but failed statistical significance and concentration requirements
* No experiment cleared the full pre-registered viability screen.

The research constraints remain:

* DEV split only
* 60/20/20 preserved
* validation and holdout MUST NOT be read
* no optimization
* no parameter sweeps
* no strategy implementation
* no changes to bot.py
* no changes to V1/V2
* no changes to Strategies 01-03
* EURJPY remains excluded because of known degraded data quality
* volume-dependent research remains excluded because the available real volume is unusable
* research must remain evidence-first and pre-registered

## FIRST: INSPECT THE REPOSITORY

Before making any conclusion, inspect the repository structure and relevant files.

Look for:

* TASK.md
* EDGE_DISCOVERY_PLAN.md
* EDGE_DISCOVERY_RESULTS.md
* research documentation
* strategy definitions
* experiment definitions
* backtest engine
* feature/indicator calculations
* data loading code
* split definitions
* DEV/validation/holdout handling
* reports
* experiment logs
* previous research notes
* bot.py
* V1
* V2
* Strategies 01-03
* any archived or abandoned experiments

Do not assume filenames are exactly as listed above. Search the repository.

Use read-only inspection.

## SECOND: RECONSTRUCT THE RESEARCH HISTORY

Create a chronological research map.

For every experiment you can identify, record:

1. Experiment ID/name
2. Behavioral hypothesis
3. Market behavior being tested
4. Direction:

   * trend following
   * mean reversion
   * breakout
   * momentum
   * volatility
   * regime dependence
   * multi-timeframe structure
   * candle/event behavior
   * etc.
5. Timeframe
6. Holding horizon
7. Symbols
8. Signal/event definition
9. Whether it used indicators or price structure
10. Whether it was event-based or continuously active
11. Whether it was tested on DEV/validation/holdout
12. Whether costs were included
13. Result
14. Final classification:

* DISCOVERED
* REJECTED
* UNRESOLVED
* NOT TESTED

15. Exact reason for the classification
16. Source file(s) supporting the conclusion

Do NOT infer that two experiments are different merely because their names differ.

## THIRD: BUILD A BEHAVIORAL-DIMENSION MAP

This is the most important part.

Create a matrix of the actual behavioral dimensions investigated so far.

At minimum examine:

### A. Trend behavior

* trend continuation
* trend pullback/resumption
* trend reversal
* trend exhaustion
* trend acceleration/deceleration
* multi-timeframe trend alignment

### B. Mean reversion

* unconditional mean reversion
* extreme-price fade
* regime-conditioned mean reversion
* volatility-conditioned mean reversion
* distance-from-equilibrium behavior

### C. Momentum

* short-term momentum
* medium-term momentum
* long-term momentum
* large-candle continuation
* breakout continuation
* momentum after volatility expansion

### D. Volatility

* volatility contraction
* volatility expansion
* squeeze/breakout
* volatility regime persistence
* volatility shock
* volatility mean reversion
* volatility clustering

### E. Market structure

* swing highs/lows
* break of structure
* failed breakouts
* range boundaries
* support/resistance behavior
* compression before expansion
* rejection/wick behavior

### F. Time/seasonality

* hour-of-day
* day-of-week
* session transitions
* overlap periods
* overnight behavior
* weekend effects
* month/quarter effects

IMPORTANT:
Do not actually test session/time effects now. Only determine whether they have already been tested.

### G. Cross-timeframe behavior

* alignment
* disagreement
* transition between regimes
* higher-TF trend + lower-TF reversal
* lower-TF impulse inside higher-TF range
* timeframe-specific persistence

### H. Cross-asset / cross-symbol behavior

* pair-relative behavior
* EURUSD/GBPUSD/EURGBP relationships
* lead/lag
* correlated-pair divergence
* relative strength
* cross-pair confirmation

Again, only identify whether these dimensions have been tested. Do not run them.

### I. Event/context behavior

* news
* volatility shocks
* large gaps
* spread expansion
* unusual candle ranges
* unusual consecutive returns
* regime transitions

Again, research/audit only.

## FOURTH: DISTINGUISH "TESTED" FROM "ACTUALLY EXHAUSTED"

This distinction is critical.

For each behavioral dimension classify it as exactly one of:

### EXHAUSTED

Multiple reasonable formulations have already been tested and evidence is consistently weak/negative.

### TESTED-BUT-NOT-EXHAUSTED

At least one formulation has been tested, but materially different formulations remain.

### UNRESOLVED

The available experiment did not have enough observations or otherwise could not reach the predefined evidence threshold.

### UNTESTED

No meaningful experiment in the repository tests this behavior.

### INVALID/UNAVAILABLE

The behavior cannot currently be researched reliably because of data or infrastructure limitations.

Provide evidence for each classification.

Do NOT classify something as exhausted merely because a superficially similar strategy failed.

## FIFTH: DETECT REDUNDANT RESEARCH

Identify experiments that are behaviorally overlapping.

For example, determine whether any apparently different experiments are actually variations of the same underlying hypothesis:

* trend following vs trend alignment
* pullback continuation vs momentum continuation
* squeeze breakout vs volatility expansion
* extreme fade vs mean reversion
* candle momentum vs short-term momentum

Do not force equivalence.

For each overlap, explain:

* why they are related
* what dimension is actually different
* whether testing another version would provide new information or simply repeat previous work

## SIXTH: IDENTIFY THE RESEARCH FRONTIER

After reconstructing the history, identify the genuinely unexplored behavioral dimensions.

The output should answer:

> "What important market behavior have we NOT meaningfully tested yet?"

Do NOT give me strategy parameters.

Do NOT give me optimized thresholds.

Do NOT give me entry/exit rules.

Do NOT write implementation code.

Instead, identify research hypotheses at the conceptual level.

Example format:

* Behavioral dimension:
* What has already been tested:
* What remains untested:
* Why it is genuinely different:
* What evidence would distinguish it from previously tested ideas:
* Data requirements:
* Potential contamination/leakage risks:
* Expected event-count concern:
* Whether it is suitable for the existing DEV dataset:

## SEVENTH: PRIORITIZE WITHOUT "PICKING A WINNER"

Do NOT rank strategies by expected profitability.

Instead, classify candidate research dimensions by research usefulness:

### HIGH INFORMATION VALUE

A result would materially expand what we know about the market.

### MEDIUM INFORMATION VALUE

Useful but overlaps substantially with existing research.

### LOW INFORMATION VALUE

Likely to repeat an already tested behavioral dimension.

### BLOCKED

Cannot be researched reliably with current data.

This is a research-priority classification, NOT a profitability ranking.

## EIGHTH: CHECK THE DATA LIMITATIONS

Audit whether the existing DEV dataset is capable of supporting the remaining candidate dimensions.

Explicitly check:

* available date range
* available symbols
* M5 granularity
* observed bid/ask spread availability
* volume quality
* missing data
* zero-spread frequency
* session/timezone information
* news/event data availability
* whether H4 aggregation is valid
* whether cross-symbol synchronization is possible
* whether enough observations exist for candidate event-based experiments

Do not acquire new data.

Do not use external data.

Do not modify the dataset.

## NINTH: CHECK RESEARCH-INTEGRITY RISKS

Look specifically for:

* lookahead bias
* future-bar leakage
* resampling leakage
* signal/entry timing mistakes
* use of incomplete candles
* train/DEV contamination
* validation/holdout access
* threshold selection after observing results
* hidden parameter sweeps
* multiple-testing problems
* duplicated experiments disguised as new hypotheses
* cost-model inconsistencies
* symbol-specific assumptions
* accidental use of EURJPY
* accidental use of zero/invalid volume

If you find a concern, document it.

DO NOT modify it.

## TENTH: FINAL REPORT

Produce a document named:

RESEARCH_STATE_AUDIT.md

The report must contain these sections:

# Research State Audit

## 1. Executive Summary

State exactly where the research stands.

## 2. Repository Evidence

List the files inspected and what each contributed.

## 3. Chronological Experiment History

Table of all meaningful research experiments.

## 4. Behavioral Dimension Matrix

Use:

| Dimension | Tested? | Exhausted? | Status | Evidence |
| --------- | ------- | ---------- | ------ | -------- |

## 5. Redundant / Overlapping Research

Explain behavioral overlap.

## 6. Confirmed Rejections

List experiments that should not be revisited unless a genuinely new hypothesis is introduced.

## 7. Unresolved Experiments

List experiments that remain unresolved and why.

Do not silently upgrade unresolved → promising.

## 8. Untested Behavioral Dimensions

This is the key section.

Identify genuinely untested areas.

## 9. Data Feasibility

For each untested dimension, state whether the current DEV dataset can support research.

## 10. Research-Integrity Findings

Any leakage, split, execution, or cost-model concerns.

## 11. Research Frontier

Identify the remaining conceptual research directions.

For each:

* hypothesis
* novelty relative to previous work
* required data
* likely event-count issue
* major leakage risk
* whether it can be pre-registered cleanly

## 12. Recommended NEXT AUDIT/RESEARCH TASK

Give ONE next research task at the conceptual level.

This must NOT be a strategy implementation.

It should be phrased like:

"Investigate whether X behavior exists in Y timeframe under Z pre-registered definition."

Do not provide optimized thresholds.

Do not run the experiment.

Do not implement it.

## 13. Explicit Stop Condition

State that no strategy should be implemented or promoted until a future pre-registered DEV experiment clears the existing viability screen.

## FINAL RULES

READ ONLY.

No code modifications.

No parameter changes.

No strategy changes.

No bot changes.

No V1/V2 changes.

No backtests.

No optimization.

No parameter sweeps.

No validation reads.

No holdout reads.

No external data.

No new strategy implementation.

No profitability predictions.

No "best strategy."

No ranking by expected returns.

The purpose of this task is to understand the research map and identify what has genuinely NOT been investigated yet.

When finished, show me:

1. The generated `RESEARCH_STATE_AUDIT.md`
2. A concise summary of the most important findings
3. The exact next research dimension identified by the audit
4. Why it is genuinely different from everything already tested

STOP after producing the audit.
