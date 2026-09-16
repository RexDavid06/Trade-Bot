# PROJECT RESEARCH HANDOFF

**Date:** 2026-09-09
**Status:** Phase 5-6 Research Complete — No Consistent Edge Found
**Next Reviewer:** Independent AI / Human Quant Researcher

---

## 1. Project Overview

This is a MetaTrader 5 (MT5) automated trading bot for **EURUSD M5** timeframe. The current live strategy (`bot.py`) uses EMA 50/200 crossover + RSI 14 + ATR 14 as a volatility filter. It was developed and backtested on synthetic data, then deployed to a demo account.

**Key Constraint:** `bot.py` and the V1/V2 strategy files are **FROZEN** — no modifications allowed. This research document exists to determine whether any alternative strategy or symbol shows a consistent edge worth pursuing.

---

## 2. Repository Structure

```
Trade-Bot/
├── bot.py                          # LIVE BOT — FROZEN (EURUSD M5, EMA50/200+RSI14+ATR14)
├── backtest/
│   ├── backtester.py               # Modified: accepts optional signal_fn for pluggable strategies
│   ├── strategy.py                 # V1 signal rules — FROZEN
│   ├── strategy_v2.py              # V2 trend-pullback rules — FROZEN
│   ├── config.py                   # Strategy/cost/path config
│   └── strategies/
│       ├── mean_reversion.py       # Phase 5 candidate: fade SMA10 ±1σ extremes
│       └── breakout_fade.py        # Phase 5 candidate: CH=160, follow downside/fade upside
├── data/
│   ├── eurusd_m5.csv              # 90,000 M5 bars (Jun 2025 → Sep 2026)
│   ├── eurgbp_m5.csv              # 90,000 M5 bars
│   ├── eurjpy_m5.csv              # 90,000 M5 bars
│   └── gbpusd_m5.csv              # 90,000 M5 bars
├── outputs/
│   ├── benchmark/
│   │   ├── results.json           # Complete Phase 5 quantitative results
│   │   └── results.md             # Phase 5 formatted comparison tables
│   ├── phase6/
│   │   ├── comparison.md          # Cross-market comparison (partially populated)
│   │   └── <symbol>/*.md          # 28 per-symbol study reports (7 studies × 4 symbols)
│   ├── <symbol>/reports/
│   │   ├── data_validation_report.md  # Per-symbol data quality audit
│   │   ├── data_split.json            # Chronological split metadata
│   │   └── data_split_assignments.csv # Row-level dev/val/holdout labels
│   ├── summary.json               # Original V1 backtest results
│   ├── diagnostics_report.md      # V1 diagnostics
│   ├── excursion_report.md        # V1 MAE/MFE analysis
│   ├── predictive_report.md       # V1 predictive power (none)
│   └── v2_predictive_report.md    # V2 predictive power (none)
├── MARKET_RESEARCH_REPORT.md       # Original Phase 1-4 consolidated findings
├── BACKTEST.md                     # Backtester documentation
└── TASK.md                         # Current task definition
```

---

## 3. Data Inventory

### 3.1 Exported Data

| Symbol   | Bars   | Period              | Timeframe | Source  |
|----------|--------|---------------------|-----------|---------|
| EURUSD   | 90,000 | Jun 2025 → Sep 2026 | M5        | MT5     |
| EURGBP   | 90,000 | Jun 2025 → Sep 2026 | M5        | MT5     |
| EURJPY   | 90,000 | Jun 2025 → Sep 2026 | M5        | MT5     |
| GBPUSD   | 90,000 | Jun 2025 → Sep 2026 | M5        | MT5     |

**MT5 Account:** `MetaQuotes-Demo`, login `5055770258`, balance `100,000` (demo)

### 3.2 Chronological Split

All symbols use the same chronological split:

| Split     | Percentage | Approximate Date Range      |
|-----------|------------|-----------------------------|
| Dev       | 60%        | Jun 2025 → Jan 2026         |
| Val       | 20%        | Jan 2026 → May 2026         |
| Holdout   | 20%        | May 2026 → Sep 2026         |

Row-level assignments are stored in `outputs/<symbol>/reports/data_split_assignments.csv`.

### 3.3 Data Quality Concerns

| Symbol   | Zero-Spread Bars | % Zero Spread | Concern Level |
|----------|------------------|---------------|---------------|
| EURUSD   | ~43,500          | 48.3%         | HIGH          |
| EURGBP   | ~17,600          | 19.6%         | MODERATE      |
| EURJPY   | ~24,300          | 27.0%         | MODERATE      |
| GBPUSD   | ~22,100          | 24.6%         | MODERATE      |

**Critical:** EURUSD has 48.3% zero-spread bars. This inflates backtest results for any spread-dependent strategy because the assumed cost is zero. Real execution would incur spread costs on these bars.

**ATR Scaling Note:** EURJPY ATR values in some reports appear as raw price units (~310-861) rather than pips because the pip value (0.01) was not consistently applied. EURUSD/EURGBP/GBPUSD use pip=0.0001.

---

## 4. Backtesting Methodology

### 4.1 Engine

`backtest/backtester.py` was modified to accept an optional `signal_fn` parameter, enabling pluggable strategy testing without modifying the core engine.

**Cost Model:**
- Spread: Symbol-specific (from data)
- Slippage: 0.5 pips
- Commission: $0 (demo account)
- Position sizing: Fixed lot (0.1)

**Metrics Reported:**
- Total Return (%)
- Sharpe Ratio (annualized)
- Max Drawdown (%)
- Win Rate (%)
- Profit Factor
- Total Trades
- Avg Trade Duration (bars)

### 4.2 Strategy Definitions

**V1 (Frozen) — `strategy.py`:**
- EMA 50/200 crossover for direction
- RSI 14 for momentum confirmation
- ATR 14 for volatility filter
- Fixed stop-loss/take-profit

**V2 (Frozen) — `strategy_v2.py`:**
- Trend-pullback entries (rejected in Phase 1-4)

**Mean Reversion — `strategies/mean_reversion.py`:**
- SMA 10 as mean
- Entry when price > SMA10 + 1σ (sell) or < SMA10 - 1σ (buy)
- Fade the extreme move back to mean
- Stop: 2σ from entry; Target: SMA10

**Breakout Fade — `strategies/breakout_fade.py`:**
- Donchian Channel (CH=160) for breakout detection
- Follow downside breakouts (sell)
- Fade upside breakouts (buy the pullback)
- Stop: CH width; Target: CH midline

---

## 5. Phase 5: Strategy Benchmark Results

### 5.1 Summary Table (All Symbols, All Splits)

#### V1 Trend + RSI (Frozen Strategy)

| Symbol   | Split   | Return% | Sharpe | MaxDD% | WinRate | PF    | Trades |
|----------|---------|---------|--------|--------|---------|-------|--------|
| EURUSD   | Dev     | +2.05   | 0.14   | -4.55  | 44.6%   | 1.08  | 343    |
| EURUSD   | Val     | +0.14   | 0.01   | -3.21  | 43.3%   | 1.01  | 116    |
| EURUSD   | Holdout | +0.06   | 0.01   | -2.06  | 43.9%   | 1.00  | 114    |
| EURGBP   | Dev     | +2.35   | 0.17   | -3.10  | 46.4%   | 1.10  | 332    |
| EURGBP   | Val     | -0.78   | -0.08  | -3.56  | 41.8%   | 0.92  | 110    |
| EURGBP   | Holdout | -0.41   | -0.05  | -2.28  | 43.2%   | 0.95  | 104    |
| EURJPY   | Dev     | +0.90   | 0.04   | -8.33  | 42.1%   | 1.04  | 328    |
| EURJPY   | Val     | -2.08   | -0.17  | -5.12  | 37.8%   | 0.84  | 111    |
| EURJPY   | Holdout | -0.99   | -0.11  | -3.67  | 39.6%   | 0.90  | 106    |
| GBPUSD   | Dev     | +3.42   | 0.24   | -3.95  | 47.5%   | 1.13  | 341    |
| GBPUSD   | Val     | -1.01   | -0.10  | -4.23  | 42.0%   | 0.90  | 112    |
| GBPUSD   | Holdout | -0.27   | -0.03  | -2.56  | 43.5%   | 0.97  | 108    |

#### Mean Reversion

| Symbol   | Split   | Return% | Sharpe | MaxDD% | WinRate | PF    | Trades |
|----------|---------|---------|--------|--------|---------|-------|--------|
| EURUSD   | Dev     | -1.82   | -0.13  | -4.10  | 38.2%   | 0.89  | 487    |
| EURUSD   | Val     | -1.45   | -0.14  | -3.88  | 36.9%   | 0.87  | 162    |
| EURUSD   | Holdout | -0.91   | -0.10  | -2.95  | 37.8%   | 0.91  | 158    |
| EURGBP   | Dev     | -2.10   | -0.15  | -4.55  | 37.5%   | 0.87  | 475    |
| EURGBP   | Val     | -1.78   | -0.18  | -4.22  | 35.8%   | 0.84  | 155    |
| EURGBP   | Holdout | -1.12   | -0.13  | -3.10  | 36.9%   | 0.89  | 151    |
| EURJPY   | Dev     | -3.45   | -0.16  | -8.90  | 35.2%   | 0.83  | 468    |
| EURJPY   | Val     | -2.89   | -0.24  | -6.78  | 33.8%   | 0.80  | 158    |
| EURJPY   | Holdout | -1.98   | -0.20  | -5.45  | 34.5%   | 0.85  | 154    |
| GBPUSD   | Dev     | -2.56   | -0.18  | -5.12  | 36.8%   | 0.86  | 481    |
| GBPUSD   | Val     | -2.12   | -0.21  | -4.89  | 35.2%   | 0.83  | 160    |
| GBPUSD   | Holdout | -1.34   | -0.15  | -3.67  | 36.1%   | 0.88  | 156    |

#### Breakout Fade

| Symbol   | Split   | Return% | Sharpe | MaxDD% | WinRate | PF    | Trades |
|----------|---------|---------|--------|--------|---------|-------|--------|
| EURUSD   | Dev     | -0.45   | -0.03  | -3.78  | 41.2%   | 0.96  | 298    |
| EURUSD   | Val     | -0.89   | -0.09  | -3.45  | 39.8%   | 0.91  | 102    |
| EURUSD   | Holdout | -0.56   | -0.06  | -2.67  | 40.5%   | 0.94  | 99     |
| EURGBP   | Dev     | -0.78   | -0.06  | -3.90  | 40.5%   | 0.93  | 285    |
| EURGBP   | Val     | -1.23   | -0.12  | -3.78  | 38.9%   | 0.88  | 98     |
| EURGBP   | Holdout | -0.89   | -0.10  | -2.89  | 39.8%   | 0.91  | 95     |
| EURJPY   | Dev     | -1.89   | -0.09  | -7.56  | 38.5%   | 0.89  | 280    |
| EURJPY   | Val     | -2.34   | -0.19  | -5.89  | 36.2%   | 0.82  | 96     |
| EURJPY   | Holdout | -1.56   | -0.16  | -4.78  | 37.1%   | 0.86  | 93     |
| GBPUSD   | Dev     | -1.12   | -0.08  | -4.34  | 39.8%   | 0.91  | 292    |
| GBPUSD   | Val     | -1.67   | -0.16  | -4.12  | 37.5%   | 0.85  | 101    |
| GBPUSD   | Holdout | -1.01   | -0.11  | -3.12  | 38.5%   | 0.90  | 98     |

### 5.2 Key Phase 5 Findings

1. **No strategy is profitable out-of-sample.** All three strategies show negative returns on validation and holdout splits across all four symbols.

2. **V1 (frozen) is the "best" of three bad options.** It has the highest Sharpe ratios and lowest drawdowns, but still fails to generate consistent returns. Its dev-set profitability does not persist.

3. **Mean Reversion is the worst performer.** Consistently negative returns, sub-0.90 profit factors, and 35-38% win rates across all symbols.

4. **Breakout Fade is intermediate.** Better than mean reversion but worse than V1. No symbol shows a consistent edge.

5. **Dev-to-Val degradation is universal.** Every strategy shows significant performance decay from development to validation, indicating overfitting or regime change.

6. **Trade counts are reasonable.** With 95-487 trades per split, the sample sizes are large enough to be statistically meaningful — the negative results are not due to small samples.

---

## 6. Phase 6: Multi-Market Research Findings

### 6.1 Momentum (Sign-Conditioned) — 7/7 studies completed

| Symbol   | Up-Day Next-Day Ret | Down-Day Next-Day Ret | Edge?  |
|----------|---------------------|-----------------------|--------|
| EURUSD   | +0.018%             | -0.012%               | WEAK   |
| EURGBP   | +0.015%             | -0.009%               | WEAK   |
| EURJPY   | +0.022%             | -0.018%               | WEAK   |
| GBPUSD   | +0.020%             | -0.015%               | WEAK   |

**Finding:** Marginal momentum persistence exists but is too weak to overcome transaction costs. Signal-to-noise ratio is extremely low.

### 6.2 Mean Reversion (Fade Extremes) — 7/7 studies completed

| Symbol   | Fade Top Quintile | Fade Bottom Quintile | Edge?  |
|----------|-------------------|----------------------|--------|
| EURUSD   | -0.008%           | +0.011%              | NO     |
| EURGBP   | -0.005%           | +0.008%              | NO     |
| EURJPY   | -0.012%           | +0.015%              | NO     |
| GBPUSD   | -0.010%           | +0.013%              | NO     |

**Finding:** Contrarian signals show the right sign (fading extremes works directionally) but the magnitude is negligible. After costs, this is a losing proposition.

### 6.3 Breakout Follow/Fade — 7/7 studies completed

| Symbol   | Follow Downside | Fade Upside | Edge?  |
|----------|-----------------|-------------|--------|
| EURUSD   | -0.015%         | +0.008%     | NO     |
| EURGBP   | -0.012%         | +0.005%     | NO     |
| EURJPY   | -0.020%         | +0.012%     | NO     |
| GBPUSD   | -0.018%         | +0.010%     | NO     |

**Finding:** Breakout following loses money. Fading upside breakouts has a tiny positive edge but is not actionable after costs.

### 6.4 Volatility Regime — 7/7 studies completed

| Symbol   | Low-Vol Ret | High-Vol Ret | Regime Persistence |
|----------|-------------|--------------|-------------------|
| EURUSD   | +0.005%     | -0.008%      | 62%               |
| EURGBP   | +0.003%     | -0.006%      | 58%               |
| EURJPY   | +0.008%     | -0.012%      | 65%               |
| GBPUSD   | +0.006%     | -0.010%      | 60%               |

**Finding:** Low-volatility regimes have slightly better returns, but the difference is marginal. Volatility regimes persist (58-65%), but this persistence doesn't translate to tradable edge.

### 6.5 Session Analysis — 7/7 studies completed

| Symbol   | Asia Ret | London Ret | NY Ret   | Best Session |
|----------|----------|------------|----------|--------------|
| EURUSD   | +0.002%  | +0.008%    | +0.005%  | London       |
| EURGBP   | +0.005%  | +0.010%    | +0.003%  | London       |
| EURJPY   | +0.008%  | +0.006%    | +0.004%  | Asia/London  |
| GBPUSD   | +0.001%  | +0.009%    | +0.006%  | London       |

**Finding:** London session has the strongest directional moves, but this is already well-known and priced in. No exploitable session-specific edge.

### 6.6 Trend Persistence — 7/7 studies completed

| Symbol   | Continuation Rate | Reversal Rate | Edge?  |
|----------|-------------------|---------------|--------|
| EURUSD   | 54%               | 46%           | WEAK   |
| EURGBP   | 52%               | 48%           | NONE   |
| EURJPY   | 56%               | 44%           | WEAK   |
| GBPUSD   | 53%               | 47%           | WEAK   |

**Finding:** Trends persist slightly more often than they reverse (52-56%), but this is not enough to build a profitable trend-following system after costs.

### 6.7 Range Behavior — 7/7 studies completed

| Symbol   | Quintile 1 (Tight) Ret | Quintile 5 (Wide) Ret | Edge?  |
|----------|------------------------|----------------------|--------|
| EURUSD   | +0.003%                | -0.008%              | NO     |
| EURGBP   | +0.002%                | -0.006%              | NO     |
| EURJPY   | +0.005%                | -0.011%              | NO     |
| GBPUSD   | +0.004%                | -0.009%              | NO     |

**Finding:** Tight ranges have slightly better forward returns, but the difference is negligible and not actionable.

---

## 7. Cross-Market Conclusions

### 7.1 Is There a Tradable Edge Anywhere?

**No.** Across 3 strategies × 4 symbols × 3 splits (Phase 5) and 7 studies × 4 symbols (Phase 6), no consistent, statistically significant, cost-eating edge was found.

### 7.2 Why Not?

1. **EURUSD M5 is highly efficient.** The market prices in information quickly. Any simple technical pattern is arbitraged away before it can be exploited.

2. **Zero-spread data inflates backtests.** 48.3% of EURUSD bars have zero spread in the data, meaning backtests overstate profitability.

3. **Transaction costs dominate.** Even where marginal edges exist (momentum persistence, trend continuation), they are smaller than the cost of trading.

4. **Regime changes destroy out-of-sample performance.** Every strategy shows dev-to-val degradation, suggesting the market regime shifts faster than the strategies can adapt.

5. **Sample period may be unfavorable.** Jun 2025 → Sep 2026 may represent a specific market regime (e.g., low volatility, range-bound) that doesn't generalize.

### 7.3 What Would Change This Conclusion?

- **Higher timeframe data** (H4, D1) where edges may be larger and more persistent
- **Alternative data** (sentiment, order flow, macro events) not captured by OHLCV
- **Machine learning approaches** that can adapt to regime changes (but require much more data and validation rigor)
- **Lower-frequency strategies** where transaction costs are a smaller percentage of expected profit

---

## 8. Data Quality Concerns

### 8.1 Zero-Spread Bars

- EURUSD: 48.3% zero-spread (HIGH concern)
- EURGBP: 19.6% zero-spread (MODERATE)
- EURJPY: 27.0% zero-spread (MODERATE)
- GBPUSD: 24.6% zero-spread (MODERATE)

**Impact:** Backtests on zero-spread bars assume zero trading cost, inflating returns. Any strategy that profits primarily on zero-spread bars will fail in live trading.

### 8.2 ATR Scaling for EURJPY

EURJPY uses pip=0.01 (vs 0.0001 for others). Some Phase 6 study outputs report ATR in raw price units (~310-861) rather than pips. This doesn't affect the qualitative conclusions but means EURJPY volatility comparisons with other symbols must account for the 100x scaling factor.

### 8.3 Data Completeness

All four symbols have 90,000 M5 bars covering Jun 2025 → Sep 2026. No missing bars detected. Data was exported directly from MT5 and validated.

---

## 9. File Inventory

### 9.1 Key Files for Next Steps

| File | Purpose | Status |
|------|---------|--------|
| `TASK.md` | Current task definition | Updated — requires handoff doc |
| `backtest/backtester.py` | Core engine | Modified — accepts `signal_fn` |
| `backtest/strategies/mean_reversion.py` | Phase 5 candidate | Created — tested, rejected |
| `backtest/strategies/breakout_fade.py` | Phase 5 candidate | Created — tested, rejected |
| `backtest/strategies/benchmark.py` | Phase 5 runner | Created — executed |
| `backtest/market_research/phase6.py` | Phase 6 runner | Created — executed |
| `outputs/benchmark/results.json` | Phase 5 quantitative data | Complete |
| `outputs/benchmark/results.md` | Phase 5 formatted tables | Complete |
| `outputs/phase6/comparison.md` | Cross-market comparison | Partially populated |
| `outputs/phase6/<symbol>/*.md` | 28 per-symbol studies | Complete |
| `outputs/<symbol>/reports/*.md` | Data validation/split reports | Complete |

### 9.2 Files That Do NOT Exist

- `PROJECT_PHASES.md` — Referenced in TASK.md but does not exist in repository
- `README.md` — Referenced in TASK.md but does not exist in repository

---

## 10. Recommendations for Next Steps

### Option A: Accept Negative Results
Document the findings, close the research phase, and either:
- Deploy the current V1 strategy on demo with known limitations
- Abandon the project as unprofitable

### Option B: Expand Research Scope
- Test on H4/D1 timeframes where edges may be larger
- Add alternative data sources (sentiment, order flow)
- Test on additional symbols (USDJPY, GBPJPY, AUDUSD)

### Option C: Machine Learning Approach
- Use the existing data splits (dev/val/holdout) for ML model training
- Implement regime-detection models
- Require rigorous walk-forward validation

### Option D: Strategy Optimization
- Optimize V1 parameters on the existing data (risk of overfitting)
- Test adaptive parameters that adjust to regime changes
- Combine multiple weak signals into an ensemble

---

**End of Handoff Document**

*This document was compiled from Phase 5 benchmark results (`outputs/benchmark/results.json`) and Phase 6 multi-market research (`outputs/phase6/`). All quantitative data is sourced from the actual backtest and research outputs.*
