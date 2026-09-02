# TRADE BOT — PHASE 5: STRATEGY BENCHMARKING

We are now moving from market-behavior research into **Phase 5: Strategy Benchmarking**.

The goal is NOT to find the best-looking backtest through optimization.

The goal is to take the strongest market behaviors discovered in Phases 1–4 and test whether they can be converted into **simple, defensible, executable trading strategies that survive realistic costs**.

## IMPORTANT PROJECT RULES

Before doing anything:

1. Inspect the existing project structure.
2. Read:

   * `MARKET_RESEARCH_REPORT.md`
   * `BACKTEST.md`
   * `TASK.md`
   * existing files under `backtest/market_research/`
   * existing data validation/split modules
   * existing backtesting infrastructure.
3. Do NOT modify:

   * `bot.py`
   * V1 strategy files
   * V2 strategy files
   * V1/V2 validation logic
   * existing market-research results.
4. V1 and V2 are research artifacts and must remain reproducible.
5. Do not optimize parameters.
6. Do not perform parameter sweeps.
7. Do not combine multiple strategies.
8. Do not use the holdout set to make strategy decisions.
9. Every signal must be causal.
10. Every execution assumption must be explicitly documented.

---

# 1. DATA FOUNDATION

Use the existing chronological split:

* Development: first 60%
* Validation: next 20%
* Holdout: final 20%

Do not shuffle data.

The current dataset is approximately:

* 90,000 EURUSD M5 bars
* approximately 15 months
* June 2025 → September 2026

Treat this dataset as **preliminary**, not as the final research foundation.

The historical spread field is known to be unreliable:

* approximately 46% of candles have zero spread
* the final ~200 candles have zero spread

Therefore:

### DO NOT use the historical spread column as the actual execution spread.

Instead create a configurable synthetic cost model.

Baseline:

* spread = 0.5 pip
* slippage = 0.5 pip per side
* commission = $7 per lot round turn

Also run cost-stress scenarios:

* 0.5 pip spread
* 0.75 pip spread
* 1.0 pip spread

Keep slippage and commission constant unless there is a strong technical reason to expose them as configuration.

Document this clearly.

---

# 2. BUILD A COMMON STRATEGY BENCHMARK FRAMEWORK

Create a clean reusable framework for strategy experiments.

Suggested structure:

```text
backtest/
    strategies/
        __init__.py
        mean_reversion.py
        upside_breakout_fade.py
        downside_breakout_continuation.py

    benchmark/
        __init__.py
        engine.py
        execution.py
        costs.py
        metrics.py
        reporting.py
        run.py
        validate.py
```

Adapt the structure to the existing project rather than unnecessarily duplicating existing functionality.

The framework should separate:

### A. Signal generation

"What does the market tell us?"

from:

### B. Execution

"How much would we actually make or lose after spread, slippage and commission?"

This distinction is important.

---

# 3. STRATEGY A — MEAN REVERSION

Research showed that extreme deviation from a recent mean was followed by mild reversion.

This is currently the strongest candidate from the market research.

Use a **causal standardized distance from a trailing mean**.

Conceptually:

```text
distance = (close - trailing_mean) / trailing_std
```

No future data may influence the mean or standard deviation.

Use a simple, conventional extreme-deviation rule.

Initial hypothesis:

### LONG

When price is sufficiently below the trailing mean:

```text
distance <= -2.0
```

generate a LONG signal.

### SHORT

When:

```text
distance >= +2.0
```

generate a SHORT signal.

Signal is generated using a CLOSED candle.

Entry occurs at the NEXT candle's open.

Do not use the current candle's future information.

---

## Mean-reversion exit

Do NOT blindly reuse V1's 3 ATR target.

The strategy is specifically testing reversion toward the mean.

Use:

### Take profit

Trailing mean at the time of the signal.

### Stop loss

1.5 × ATR.

### Maximum holding period

Use a fixed, clearly documented holding limit so trades cannot remain open indefinitely.

Choose a reasonable conventional value and document the rationale.

Do NOT optimize this value.

If the existing framework already has a clean maximum-holding-period implementation, reuse it.

---

# 4. STRATEGY B — UPSIDE BREAKOUT FADE

Market research found that upside breakouts were followed by negative forward returns during this sample.

Test the hypothesis:

> A break above a recent high tends to fail rather than continue.

Use a simple causal breakout definition.

Initial benchmark:

```text
previous_high = highest high of the previous N completed candles
```

Use one fixed conventional short-term breakout window.

Do NOT test multiple N values.

Choose a single value, document why it was chosen, and freeze it.

Signal:

```text
current high > previous_high
AND
current close < previous_high
```

This represents a failed upside breakout / rejection.

Generate:

```text
SHORT
```

on the signal candle close.

Enter at next candle open.

### Exit

Use a simple ATR-based risk model:

* SL = 1.5 × ATR
* TP = 3 × ATR

Do not optimize these values.

---

# 5. STRATEGY C — DOWNSIDE BREAKOUT CONTINUATION

Market research found that downside breaks were followed by positive forward returns.

Because the direction is DOWN, test:

> A downside breakout may continue lower.

Use the same fixed breakout window chosen for Strategy B.

Signal:

```text
current low < previous_low
AND
current close < previous_low
```

Generate:

```text
SHORT
```

Enter at the next candle open.

### Exit

Use:

* SL = 1.5 × ATR
* TP = 3 × ATR

Do not optimize.

---

# 6. POSITION RULES

For all three strategies:

* one position at a time
* no overlapping positions
* no pyramiding
* no martingale
* no averaging down
* no dynamic position sizing during the initial benchmark
* fixed 0.10 lot for comparability with previous research
* signal on closed candle
* next-candle-open execution

Keep the benchmark focused on strategy behavior rather than money management.

---

# 7. COST MODEL

Every strategy must be tested with realistic synthetic transaction costs.

At minimum report:

### Gross / theoretical

No trading costs.

### Baseline

```text
spread = 0.5 pip
slippage = 0.5 pip per side
commission = $7/lot round turn
```

### Stress 1

```text
spread = 0.75 pip
```

### Stress 2

```text
spread = 1.0 pip
```

The cost model must be centralized and configurable.

Do not bury cost assumptions inside strategy code.

---

# 8. DEVELOPMENT → VALIDATION → HOLDOUT

This is extremely important.

Initially run all three strategies on the DEVELOPMENT dataset.

Do NOT use the holdout to choose rules.

For each strategy:

```text
Development
     ↓
Does the hypothesis show promise?
     ↓
Validation
     ↓
Does it survive?
     ↓
Holdout
```

The holdout is the final untouched test.

If a strategy performs badly on development:

DO NOT modify it just to make it profitable.

Record the failure.

---

# 9. REQUIRED METRICS

For every strategy and every cost scenario calculate:

### Trade statistics

* number of trades
* win rate
* average win
* average loss
* reward/risk
* expectancy in R
* expectancy in money
* profit factor

### Risk

* maximum drawdown
* maximum drawdown %
* longest losing streak
* longest winning streak

### Performance

* total gross P/L
* total net P/L
* return %
* average trade
* average duration

### Direction

* long performance
* short performance

### Time

* session performance
* monthly performance
* yearly performance where enough data exists

### Cost sensitivity

Clearly show:

```text
0 cost
0.5 pip spread
0.75 pip spread
1.0 pip spread
```

This is critical.

We need to know whether an apparent market behavior survives transaction costs.

---

# 10. SEPARATE PREDICTIVE EDGE FROM EXECUTION EDGE

For each strategy, report two layers.

## Layer 1 — Market behavior

Before transaction costs:

* average forward return
* directional hit rate
* average R
* distribution of outcomes

This answers:

> Does the market behavior actually exist?

## Layer 2 — Tradable strategy

After:

* spread
* slippage
* commission

This answers:

> Can the behavior actually be traded?

Do not confuse these two.

A behavior that produces +0.15 pip before costs but -0.8 pip after costs should be classified as:

```text
Observed behavior but not currently tradable.
```

---

# 11. DATA QUALITY / LOOKAHEAD VALIDATION

Create validation checks for Phase 5.

At minimum verify:

### Determinism

Same data → same signals and trades.

### No lookahead

Signals may only use information available at or before the signal candle.

### Next-open execution

A signal generated at candle T cannot execute using candle T close as the entry price.

### No overlapping positions

### Correct SL/TP

### Correct cost application

### Correct chronological split

### No holdout contamination

### Maximum holding period correctness

If possible, create a test that modifies future candles after a signal and confirms the signal itself does not change.

---

# 12. REPORTING

Create a clear report such as:

```text
PHASE_5_STRATEGY_BENCHMARK_REPORT.md
```

Also save machine-readable results to:

```text
outputs/strategy_benchmarks/
```

Suggested files:

```text
mean_reversion.csv
upside_breakout_fade.csv
downside_breakout_continuation.csv
summary.csv
cost_sensitivity.csv
monthly_results.csv
validation_results.csv
```

Use the project's existing output conventions where appropriate.

---

# 13. FINAL CLASSIFICATION

Each strategy must receive a research classification.

Use categories such as:

### FAILED

No meaningful edge or clearly negative after realistic costs.

### INTERESTING BUT NOT TRADABLE

Some market behavior exists, but realistic costs destroy the advantage.

### PROMISING

Positive development and validation evidence with reasonable trade count and acceptable drawdown.

### HOLDOUT VALIDATED

Only use this classification if the strategy survives the untouched holdout without changing the rules after seeing it.

Do not call anything "profitable strategy" merely because one backtest run is positive.

---

# 14. DO NOT OPTIMIZE

This phase is a BENCHMARK.

Absolutely do NOT:

* sweep parameters
* optimize ATR multipliers
* optimize RSI
* optimize breakout windows
* optimize holding periods
* optimize sessions
* optimize spread assumptions
* optimize entry thresholds
* select the best combination
* combine strategies
* reverse losing strategies automatically
* create filters solely because they improve development results

If a strategy fails, report the failure.

That is useful research.

---

# 15. DO NOT CREATE V3 OR MODIFY LIVE CODE

Do not create or modify the live trading bot.

Do not modify:

```text
bot.py
```

Do not modify V1.

Do not modify V2.

Do not connect any Phase 5 strategy to MT5 execution.

This phase is research only.

---

# 16. RUN THE RESEARCH

After implementation:

1. Run validation.
2. Run all three strategies on development.
3. Run validation for strategies that meet clearly pre-defined advancement criteria.
4. Run holdout only for strategies that legitimately survive development + validation.
5. Generate the final report.
6. Check that all outputs are deterministic.
7. Check git diff carefully.

Do not silently change strategy rules because of results.

---

# 17. FINAL RESPONSE TO ME

When finished, report:

1. Files created/modified.
2. Validation status.
3. Exact frozen rules for each strategy.
4. Development results.
5. Validation results.
6. Holdout results, if legitimately reached.
7. Cost sensitivity.
8. Which hypotheses survived and which failed.
9. Whether any strategy deserves Phase 6.
10. Any data-quality limitation that prevents a strong conclusion.

Most importantly:

**Do not tell me that a strategy is good simply because it made money.**

Judge the evidence statistically and conservatively.

The purpose of this phase is to determine whether the market behaviors discovered in Phase 1–4 can actually become robust trading strategies.

If none survive, say so clearly.

That is a successful research outcome.
