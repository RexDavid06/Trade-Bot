# TRADING REPO COMPARISON

**Comparative code/research audit:**
- **OURS** = `C:\Users\ADMIN\Documents\REX\BOT\Trade-Bot`
- **CLONED** = `C:\Users\ADMIN\Documents\REX\CLONED\algorithmic-tradingUR2023I`

**Nature of each repository (verified by file inspection)**

- **OURS** is a *research-first* framework: a small frozen live MT5 bot (`bot.py`), a validated bar-by-bar backtest engine, frozen dataclass configuration, per-symbol instrument canonicalization, dev/val/holdout chronological splits with guard rails, a validation battery, a market-behaviour research suite (7 studies × 4 symbols), and a metrics/diagnostics stack. Data is exported from MT5 and additionally acquired from Dukascopy (bid/ask).
- **CLONED** is a *course repository* (Universidad del Rosario "Trading Algorítmico con Python y MT5", author ELOSPO). It is a portfolio of ~120 mostly standalone, dated, hardcoded MT5 robot scripts (martingale, pivot point, Bollinger, Keltner, MACD/RSI, ADX, anomaly, pairs, news, regression), an `Easy_Trading` broker wrapper library, course backtests (many using the `backtesting.py` library), PyArmor-encrypted "production" copies, and remote `exec()` launchers. Its own `task.md` records a prior read-only audit that selected two surviving strategy concepts (Keltner, Bollinger+ATR).

**Scope rule respected:** nothing in either repository was modified, no live trading was run, no strategy was changed, no parameters were optimized.

---

## PHASE 1 — REPOSITORY INVENTORY

### 1.1 OURS — Architecture

```
bot.py                        LIVE MT5 bot, FROZEN. EURUSD M5. EMA50/200 + RSI14 + ATR14.
dump_mt5_data.py              MT5 → data/eurusd_m5.csv (OHLC + tick_volume + spread + real_volume)
dump_mt5_multi.py             Same for EURUSD/EURGBP/EURJPY/GBPUSD
backtest/
  backtester.py               Bar-by-bar event loop; pluggable signal_fn; next-open fills;
                              conservative intrabar SL-first rule; round-turn cost model
  config.py                   Frozen dataclasses: StrategyConfig, CostConfig, PathConfig
  strategy.py                 V1 signal rules (EXACT bot.py replication) — FROZEN
  strategy_v2.py              V2 trend-pullback experiment — FROZEN
  indicators.py               EMA/RSI/ATR via `ta`; row-i depends only on rows [0..i]
  instruments.py              Per-symbol pip/point/digits/contract single source of truth
  metrics.py                  Win rate, PF, expectancy, drawdown, monthly/long/short, streaks
  reporting.py                trade_log.csv, equity curve CSV/PNG, summary.json, console report
  diagnostics.py              Cost-sensitivity + slice analysis (RSI zone, EMA sep, ATR, …
  excursion.py                MAE/MFE per trade, distance-to-stop analysis
  predictive.py / _v2.py      Forward-stat predictive-power studies (horizon/R-multiple reach)
  experiment.py               EMA-separation sweep with max-loss sequencing
  spread_sensitivity.py       Cost-scenario reruns (observed/2x/min/realistic/high)
  research_safety.py          SplitGuard/HoldoutGuard + audit log against holdout contamination
  validate.py / validate_v2.py 6 integrity checks incl. no-look-ahead, determinism, overlap
  run.py                      CLI entry point (python -m backtest.run)
  data/
    data_split.py             60/20/20 chronological split + JSON manifest + assignments.csv
    data_validation.py        Row/duplicate/gap/OHLC sanity checks per symbol
    research_split.py         Split-aware loading helpers
    validate_all.py           Per-symbol data validation runner
    dukascopy_acquire.py      Bid/ask acquisition via dukascopy-node, normalized to same schema
  market_research/            momentum, mean_reversion, breakout, volatility, sessions,
                              trend_persistence, range_behavior, phase6 (multi-symbol runner),
                              common.py (t-tests/z-tests, forward-return matrices), _loader.py
  strategies/                 benchmark.py, mean_reversion.py, breakout_fade.py
tests/                        pytest: instruments+engine, dukascopy acquisition
data/                         Monthly Dukascopy bid/ask chunk CSVs; concatenated *_m5.csv
outputs/                      trade logs, equity curves, summaries, split manifests, studies
*.md                          BACKTEST.md, MARKET_RESEARCH_REPORT.md, handoff + integrity reports
```

**Main entry points:** `bot.py` (live), `python -m backtest.run` (single backtest), `python -m backtest.validate` (integrity), `python -m backtest.data.data_split` (splits), `python -m backtest.datacquisition` tools, `python -m backtest.market_research.*` (studies).

**Data flow:** MT5/Dukascopy → CSV `time,open,high,low,close,tick_volume,spread,real_volume` → validation → chronological dev/val/holdout split + manifest → engine run → metrics + reports. Outputs are archived under `outputs/`.

**Config:** frozen dataclasses in `backtest/config.py`. `StrategyConfig` (defaults): EMA 50/200, RSI 14 (buy band 40–55, sell band 45–60), ATR 14, SL=1.5×ATR, TP=3.0×ATR, optional `ema_sep_min` filter (0.0 baseline). `CostConfig`: $10,000 start, fixed lot 0.10, contract 100,000, commission $7/lot round-turn, 0.5 pip slippage/side, spread from data × point with optional floor, conservative intrabar=True. `InstrumentConfig` (EURUSD/EURGBP/GBPUSD pip=0.0001 point=0.00001; EURJPY pip=0.01 point=0.001).

### 1.2 CLONED — Architecture

```
README.md / task.md          Repo purpose + prior research handoff task
Easy_Trading.py variants     Basic_funcs class (MT5 adapter + utilities). IB/NT/Mega variants
00. Introducción             Python intro scripts
01. Operaciones Básicas      pivot points (7 versions), martingala (12+ dated versions),
                             Keltner, RSI, BreakThrough, pairs prelim, conexión_mt5
02. Arbitraje Estadístico    ADX, anomaly detection (2024/2025 variants), Bollinger,
                             MACD+RSI, Candel3, Estrategia_cruce_medias, pairs_trading,
                             pivot systems, RSI strategies, MA-anomaly, stoch hypothesis tests,
                             Strike_price_momentum, Volume_on_price
03. Productivizacion         Easy_Trading.py, lib_robots_ur2024.py, robots_uder.py,
                             Robots_ur_bt.py, many `llamada_*.py` callers and `.bat` launchers,
                             `productivo` copies, remote GitHub exec() launchers,
                             param JSON files, PyArmor-encrypted dist/
04. Backtesting              Easy_Trading.py, backtesting_raw/macdrsi/keltner/lin_reg,
                             Ejemplo_backtesting_20XX.py series, Kelly sims, reg_lin_bt,
                             Trades_abiertos.xlsx support file
encriptacion/                PyArmor-encrypted production copies + dist/
libro/, _PDFs/               LaTeX book template, course PDFs
NatGasStrategyAnalysis.py, logger_test.py, efficient_close.py (root-level misc)
```

**Main entry points:** standalone scripts with hardcoded `mt5.initialize(login, password, server, path)` blocks. `Easy_Trading.Basic_funcs` is the only reusable library. No package structure, no `__init__.py` conventions, no CLI.

**Config:** per-robot constant blocks at top of each script; a few strategies externalize parameters to JSON (`parametros_bbands.json`, `parametros_estrategia_btr.json`). No shared config system.

**Strategy/signal modules:** ~20 distinct strategies, each duplicated across dated variants (`sistema_martingala_2024*`…`202608`, `robot_pivot_point*`, `anomaly_detection_*`, `bollinger*_2026*`, etc.).

**Indicators:** `pandas_ta` (`pt.kc`, `pt.ema`, `pt.macd`, `pt.rsi`, `pt.stdev`, …), one file references an unimported `st.supertrend`.

**Risk management:** martingale volume doubling (in 12+ scripts), Kelly criterion (two buggy implementations), one correct risk formula (`Strike_price_momentum.py`).

**Position sizing:** `Basic_funcs.calculate_position_size` (flawed — see Phase 3).

**Execution/broker:** raw MT5 `order_send` dicts; FOK/IOC modes; pending orders (pivot/limit/stop); close-all, close-partial, move-to-breakeven; history queries by comment/magic.

**Backtest engine:** external `backtesting.py` library in several files; vectorized course-analysis scripts with `shift(-N)` forward columns; regression backtest with a broken `var_ind` branch.

**Data loading:** `Basic_funcs.get_data_from_dates`, `extract_data` (pulls last N bars), `_get_data_for_bt`; hardcoded data frame names (`data_eurusd_m1`, `data_xauusd_m1`).

**Logging:** `logger_test.py`; a broken `logger` reference in `Easy_Trading.send_pending_order`; otherwise `print`.

**Metrics:** `backtesting.py` built-in stats; simple win-count/win-rate histograms in course scripts; Kelly sims.

**Tests:** none. **Utilities:** PyArmor obfuscation pipeline, `.bat` launchers, remote exec launchers.

**Research/experimentation:** parameter sweeps via `backtest.optimize(...)` maximised on `'Win Rate [%]'` on the same dataset used for evaluation (overfitting, in-sample); naive train/test month windows.

### 1.3 Oh-Estate summary (natures differ fundamentally)

| | OURS | CLONED |
|---|---|---|
| Character | Research framework + 1 frozen live bot | Live-EA script portfolio + broker wrapper |
| Code volume | ~40 source files, layered modules | ~120 scripts, heavily duplicated |
| Entry discipline | Closed-candle signals, next-open fills | Live: last-close checks; backtests often lookahead |
| Cost model | Explicit spread/slippage/commission | Mostly zero/none; broker-dependent |
| Research hygiene | Dev/val/holdout + guards + validation | In-sample sweeps, contaminated windows |
| Tests | pytest suite | None |

---

## PHASE 2 — STRATEGY COMPARISON

### 2.1 OURS strategy set

**V1 — EMA/RSI/ATR (frozen, mirrors `bot.py`)**
- **Entry (long):** closed-candle `ema_fast > ema_slow` AND `40 < RSI14 < 55`. **Short:** `ema_fast < ema_slow` AND `45 < RSI14 < 60` (strict inequalities, `strategy.py:53-56`).
- **SL/TP:** fixed from **entry candle's ATR**: SL = entry ∓ 1.5·ATR, TP = entry ± 3·ATR (`backtester.py:248-253`). No trailing. One position at a time, no overlap, no session/time filters, no swap.
- **Frequency:** M5, ~a few trades/day per symbol in practice.

**V2 — Trend-pullback (frozen, experimental)**
- Entry requires EMA50>EMA200 with both EMAs rising (slopes from prior candles), price pulled back ≥0.5×ATR from the prior 20-bar impulse extreme and reaching within 0.25×ATR of EMA50, a rejection candle, and RSI crossing 50. Same 1.5/3.0 ATR SL/TP. Not deployed.

**Phase 5 candidates (documented, not optimized, no longer claimed as edges)**
- `mean_reversion.py`: BUY when `close < SMA(10) − 1·σ`, SELL when `close > SMA(10) + 1·σ`.
- `breakout_fade.py`: BUY when `low < 160-bar channel low(past bars) − 0.25·ATR`; SELL when `high > channel high + 0.25·ATR`.

All ours share: no trailing, no session filter, no time filter, no partial exits, no multi-position logic; exits are SL/TP (or forced close at end of data); sizing is fixed 0.10 lot in backtest.

### 2.2 CLONED strategy set (how each operates)

| Strategy | Entry | Exit | Money mgmt | Notes |
|---|---|---|---|---|
| **Keltner breakout** (`sistema_keltner_productivo.py`) | close>upperKC AND green candle AND close>EMA (long); mirror short | SL=`basis`=(KCupp+KClow)/2, TP=last_close±factor_tp×(width) | fixed lots (0.01–0.1) | M1 on US500/EURUSD/XAUUSD; exponential KC (pandas_ta `kc(...,2)`) |
| **Bollinger mean-reversion** (`bandas_bollinger_202605.py`, `parametros_bbands.json`) | close crosses band ± RSI/stochastic, per-symbol JSON (length, std mult) | TP/SL in pips (e.g. 30/10 EURUSD), also mid-band exit | fixed lots 0.01–0.03, max_trades 2–3 | Multi-account launcher |
| **Martingala** (`sistema_martingala_202509.py` + 12 variants) | price beyond mean±0.5σ (12-bar M1 window) | TP at rolling mean, **no SL** | doubles size `last_volume*2` on any losing open trade | Expected ruin; comment magic 202309/202411 |
| **ADX** (`adx_bot_202411*.py`) | ADX + EMA direction | — | `calculate_position_size` (broker) | magic 202411 |
| **Anomaly RSI/EMA** (`anomaly_detection_2024/2025/202509`) | deviation of close from EMA beyond full-sample σ thresholds | exit price = close `shift(-6)` | fixed | Global-sample thresholds → lookahead |
| **MACD+RSI** (`robot_macd_rsi_productivo.py`) | MACD histogram zero-cross + RSI>60 (long) | SL/TP pips (10/30) | Kelly → position size | Backtest variant has `shift(-2)` |
| **Pivot point** (`robot_pivot_point*.py`) | pending orders at S/R levels | SL/TP at other pivots | fixed | Expiry-based pendings |
| **Pairs trading** (`pairs_trading_strategy*.py`) | spread of 2 symbols beyond mean±k·σ → pending orders to converge | mean reversion / opposite pending | fixed | Base pair not clearly static in all versions |
| **Luxor** (`Robot_Luxor_202511.py`) | MA fast×slow cross + price above candle high | SL/TP; 9–12h gate; pending expiry noon | fixed | FOK |
| **Contratendencia Mauricio** | close<EMA200 & RSI low→buy; mirror | SL=close±close·pct | — | — |
| **News gate** (`robot_noticias.py`) | suppresses trading on high-impact calendar events | — | — | Severely buggy condition |
| **Regression** (`robots_ur_bt.py`, `reg_lin_bt.py`) | OLS slope sign on last 10 (hardcoded) bars | — | `bfs.calculate_position_size` | `var_ind` branch dead |

### 2.3 Direct strategy-feature comparison

| | OURS | CLONED |
|---|---|---|
| Entry logic | Deterministic, closed-candle, documented rules | Per-script; many rely on `iloc[-1]` on short windows |
| Exit logic | Fixed ATR-multiple SL/TP, conservative intrabar | pips-based, basis-anchored, mean reversion, or none |
| Indicators | `ta` (EMA/RSI/ATR) – reproduces live bot | `pandas_ta` variety |
| Filters | optional EMA-separation (off by default) | candle colour, EMA trend, news-gate (broken), session gate (Luxor) |
| Stop loss | 1.5×ATR | pips (10), basis (Keltner), none (martingale) |
| Take profit | 3.0×ATR | pips (30), mean, channel width |
| Trailing | none | none (breakeven-mover utility exists) |
| Position mgmt | one position, no overlap, next-open fill | multiple allowed (max_trades), volume stacking (martingale) |
| Time/session filters | none | Luxor 9–12h; none elsewhere |
| Trade frequency | moderate (backtest: thousands/yr total, ~100–350/split) | M1-heavy bots run every minute |
| Long/short | both, mirrored | mostly both; some buy-bias bugs |

---

## PHASE 3 — RISK & EXECUTION COMPARISON

| Concern | OURS | CLONED |
|---|---|---|
| Risk-per-trade | Nominal 1% of balance **live** (`bot.py:51-56`): `lot = balance×0.01/1000`, floored at 0.01. **Backtest:** fixed 0.10 lot. Sizing is NOT SL-distance-aware: actual risk varies with ATR. | `calculate_position_size = capital×leverage×pct / contract_size / mid_price` (`Easy_Trading.py:392-401`) — **ignores SL distance entirely**; callers pass account balance. Undefined, uncontrolled risk. |
| SL distance | 1.5×ATR of entry candle | pips (broker-fixed, as small as 10 pips), KC basis, or none |
| Lot size | 0.01–0.10 typical; floored; discrete rounding | any; rounded to broker step; min/max clamps added only in 04 variant |
| Balance/equity | live: `mt5.account_info().balance`; backtest: fixed $10k equity curve | live reads account_info; equity mostly ignored |
| Spread | Explicit per-bar spread × point (mins floor available); backtest pays round-turn | Not modeled in most backtests; live relies on broker market fill |
| Slippage | 0.5 pip/side ×2 round-turn in backtest | Not modeled |
| Commission | $7/lot round-turn in backtest | Not modeled |
| Swap | Not modeled (both) | Not modeled |
| Broker constraints | demo MT5, FOK fills, deviation 20, 25-point spread gate | multiple brokers (RoboForex-ECN, FxPro), IOC/FOK |
| Filling modes | FOK (live), next-open fills (backtest) | IOC/FOK/pending orders |
| Duplicate orders | `position_exists()` guard (live), one-position engine | `max_trades` per symbol (some), comment/magic-based filters |
| Position limits | 1 | per-symbol configurable (e.g. 2–3) |
| Error handling | MT5 return checks, print; no retry | print; some `try/except` swallowing; no retry; several NameError/bugs |
| Retry behavior | none | none |

**Unrealistic assumptions**
- **CLONED:** (1) `lot = balance×leverage×pct / size / price` ignores stop distance; (2) no spread/slippage/commission in backtests → free trading; (3) martingale assumes unbounded capacity to double; (4) pending-order pairs assumed to fill at arbitrary spread levels; (5) hardcoded credentials forbid safe automation.
- **OURS:** (1) live-vs-backtest sizing mismatch is *documented* but means backtest $ results do not transfer to live risk units; (2) `lot=risk/1000` treats risk as if SL were fixed 100 pips; (3) single-quote data with historically 48.3% zero-spread EURUSD bars (mitigated by min-spread floor); (4) no swap for positions held across rollover (M5, plausible but unverified); (5) backtest uses bid-priced OHLC with a spread column, not true bid/ask paths (Dukascopy path adds real bid/ask, but the canonical merge loses the two-sided time path).

---

## PHASE 4 — BACKTESTING / RESEARCH VALIDITY

For every issue: **where / why it matters / severity / how to test or fix.**

### 4.1 CLONED repository issues

**C1. Negative-shift lookahead in backtest/analysis code.**
- Where: `03…/robot_macd_rsi_productivo.py:61-63` `macd.shift(-2)`, `rsi.shift(-2)`; `02…/bollinger_rsi_202506.py` `shift(-5)`; `02…/anomaly_detection_2024.py:141` / `_2025_simple.py:128` `exit_price = close.shift(-6)`; `02…/analysis_anomaly_202509.py:99` `close.shift(-1)`; `02…/Testeo_de_ho.py:58`, `testeo_de_hipotesis_stoch.py:33` `shift(-3)`; `rsi_analysis_202509.py` `shift(-12)`; `sistema_kelner_202503.py:62` `shift(-10)` (1-hour forward outcome measured on M1).
- Why it matters: signals/outcomes computed with future bars; any backtest using these is guaranteed to be biased optimistically and cannot generalise.
- Severity: **CRITICAL** — invalidates essentially every course backtest that uses these helpers.
- Test/fix: never compute indicator/outcome columns with negative shifts; if outcomes are needed, they must be matched to a *fixed horizon* after the decision bar and never enter the decision function. Re-run decision functions on `df.iloc[:i+1]` only.

**C2. Full-sample statistics used to define trade filters and then evaluate them.**
- Where: `anomaly_detection_2024.py:132-149` — `mu`, `ds_std`, sigma bands computed on the whole series; rows filtered by the 3σ band; win rates measured on the same filtered rows.
- Why: the "extreme" label depends on the future distribution; win-rate measured on in-sample classifications is survivorship/leakage.
- Severity: **HIGH**.
- Fix: rolling/expanding thresholds only; evaluate decisions OOS or after a lagged definition of extremes.

**C3. In-sample parameter optimization maximized on Win Rate.**
- Where: `04…/backtesting_macdrsi.py:57-63` `backtest_2.optimize(sigma=[1.5,2.5,3,3.5], fast/slow×5, rsi_window×3, lim×2, maximize='Win Rate [%]')` on the full-year dataset, then the same class is re-evaluated on months that overlap the training period (`data_test11=2023-08`, `data_test12=2023-09` fall inside train `2023-01-10..2024-01-31`, `:99-111`).
- Why: optimizing on the evaluation set and reusing it as "test" is textbook overfitting + train/test contamination.
- Severity: **HIGH**.
- Fix: fixed-structure walk-forward; tune on dev, tune-hold validation, freeze before holdout; never maximise a metric that is also the evaluation metric.

**C4. Argument-order and copy-paste bugs.**
- Where: `backtesting_macdrsi.py:38-44` passes `(self.sigma, self.slow, self.fast, …)` into `rsimacd_bot_4bt(sigma, fast, slow, …)` → fast/slow silently swapped; `:96` `stats_3 = backtest_2.run()` re-runs the wrong backtest; `link 04…/backtesting_raw.py` references `st.supertrend` without import (NameError); `01…/reg`/`robt_regresion_productivo.py` `range(10)` hardcoded ignoring user count; `02…/reg_lin_bt.py:55-62` `var_ind` never returns BUY branch values (buy signals dead).
- Why: results produced by these scripts are not trustworthy even on clean data.
- Severity: **HIGH** (silent output corruption).
- Fix: unit-test signal functions; remove dead branches; type linting.

**C5. Plaintext broker credentials and remote code execution.**
- Where: dozens of files (e.g. `Sebas.123`, `Genttly.2022`, accounts `67106046`, `67043467`, servers `RoboForex-ECN`, `FxPro`); `03. Productivizacion/*_desde_git*.py`, `ejecutar_robot_*_de_github*.py` fetch Python from `raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/refs/heads/clases/...` and `exec()` it (`anomaly202509_desdegit.py:8`, `llamada_desde_git_pairs_trading.py:8`, etc.).
- Why: credentials are live secrets; `exec()` of a remote branch that is not versioned locally executes unvetted, mutable code with trading privileges.
- Severity: **CRITICAL** (security) and **HIGH** (reproducibility).
- Fix: env-secrets; vendor/pin code; never `exec` remote content.

**C6. Martingale money management.**
- Where: `01…/sistema_martingala_202509.py:72-77` doubles `last_volume*2` on any losing trade, TP at rolling mean, **no stop loss** (12+ variants).
- Why: guarantees ruin on any first adverse run; backtests that look profitable are a function of the surviving simulation path.
- Severity: **CRITICAL**.
- Fix: never adopt; use fixed fractional (or Kelly-fraction) risk per trade with a stop.

**C7. No cost model in backtests.**
- Where: course vector backtests use close/vwap prices, ignore spread/slippage/commission; `backtesting.py` runs use default broker settings.
- Why: M1/M5 strategies with 10–30 pip targets are eaten by costs; results are overstated.
- Severity: **HIGH**.
- Fix: invert cost assumptions; simulate with worst-case spread; require profit > 2× round-turn costs.

**C8. No reproducibility/version pinning and no tests.**
- Severity: **MEDIUM**; fix with requirements lock, pinned data, archived params.

### 4.2 OURS repository issues

**A1. Historical outputs formally invalidated (self-diagnosed).**
- Where: `HISTORICAL_OUTPUTS_STATUS.md` — Phase 5 handoff `PROJECT_RESEARCH_HANDOFF.md` contained **fabricated performance numbers** (not matching `outputs/benchmark/results.json`); Phase 6 studies ran on the full dataset without holdout isolation, contaminating the holdout for 28 hypotheses; EURJPY pip scaling (0.0001 vs 0.01) made phase-5 EURJPY numbers meaningless.
- Severity: **HIGH** (to *current research*, already acknowledged).
- Fix already underway: fresh multi-year data (2021→ now being acquired), clean spread, fixed EURJPY scaling, new splits, Phase-6 re-runs restricted to dev data.

**A2. Data quality: zero/sparse spread.**
- Where: EURUSD ~48.3% zero-spread bars historically; EURGBP 19.6%, EURJPY 27.0%, GBPUSD 24.6% (handoff §3.3).
- Why: cost model relies on the per-bar spread column; zeros understate costs.
- Severity: **HIGH (data) / mitigated by `min_spread_pips` floor in `_cost_price` (`backtester.py:36-39`)**.
- Fix: prefer Dukascopy bid/ask series; floor spreads; run `spread_sensitivity.py` scenarios before any conclusion.

**A3. Live bot vs backtest timing divergence (repaint risk).**
- Where: `bot.py` evaluates `df.iloc[-1]` with `copy_rates_from_pos(...,0,500)` — under MT5 the last row can be the **forming candle**; the bot keys on candle-time change then signals from the forming bar and fills immediately (`bot.py:110-140`). The backtest engine instead signals on a **closed** candle and fills at the next open (`backtester.py:242-291`).
- Why: the live rules do not exactly reproduce the validated backtest rules; the forming candle is incomplete → repaint / slight lookahead in live, and live fills are intra-bar.
- Severity: **MEDIUM**. Fix: use `df.iloc[-2]` for the completed candle (and confirm `copy_rates` returns the closed series), or keep a candle-open clock; re-validate equality between bot and engine on the same data.

**A4. Metrics inconsistency on marginal trades.**
- Where: win/loss/BE is labelled from `net_pips` (`backtester.py:170-175`) while `gross_profit/gross_loss/profit_factor/expectancy` bucket by `net_money` sign (`metrics.py:26-38`). A small positive-pips trade with commission > pip-profit counts as WIN but as a money-loser.
- Severity: **LOW-MEDIUM**; fix by labelling all metrics consistently on `net_money`.

**A5. Fixed-lot backtest vs nominal-1%-risk live sizing.**
- Where: `CostConfig.lot_size=0.10` fixed; `bot.py` uses `balance×1%/1000`. Documented (`config.py:44-48`), but any dollar P&L claim is in a synthetic book.
- Severity: **MEDIUM**; keep documented; add a risk-scaled sizing mode if dollar transferability is wanted.

**A6. Minor hygiene.**
- `.gitignore` covers only `venv` and `meta logins.txt`; data CSVs and `.pyc` are tracked/untracked mess; a 0-byte Dukascopy chunk file present; running interpreter drifted to 3.14 vs documented 3.13 venv; one `data/` folder contains throwaway diag CSVs. Severity: **LOW**.

### 4.3 Comparative validity verdicts

- Look-ahead bias: **CLONED critical** (shift(-N) everywhere), **OURS engineered out** (validated indicators, closed candles, `.shift(1)` channels) except the live bot's forming-candle nuance (A3).
- Data leakage: CLONED — full-sample thresholds & reused test windows (C2, C3). OURS — historical Phase 6 holdout leak (self-identified, guard-railed now).
- Survivorship bias: CLONED — none explicitly but backtests on already-existing single-symbol windows; OURS — none (instrument universe fixed, no survivorship pruning).
- Unrealistic fills: CLONED — immediate fills at close with zero cost; OURS — next-open fills + intrabar SL-first conservative rule (`backtester.py:139-143`).
- Spread/slippage/commission: CLONED — absent; OURS — modeled (with data caveats).
- Parameter/train-test problems: CLONED — systemic in-sample optimization; OURS — disciplined splits; historical rules violations already invalidated.
- Reproducibility: CLONED — poor (unpinned, remote exec, no archives); OURS — good (deterministic engine, frozen config, manifest per split, audit log).

---

## PHASE 5 — ENGINEERING COMPARISON

Scoring (1–10, explained).

| Area | OURS | CLONED | Notes |
|---|---|---|---|
| Code organization | **9** — layered package (engine/config/strategy/data/research/test) | **2** — flat scripts, ~10 duplicate copies of the same strategy | |
| Separation of concerns | **9** — engine (backtester), rules (strategy), costs (costs), data (data/), reporting (reporting) cleanly separated | **3** — everything entangled with MT5 API + credentials + printing | |
| Modularity | **8** — pluggable `signal_fn`; instruments registry; reusable studies | **4** — `Easy_Trading.Basic_funcs` is the only reusable piece | |
| Testability | **9** — pytest suite, validation battery, no-global-state engine | **1** — scripts initialise MT5 at import; hardcoded logins | |
| Configuration management | **8** — frozen dataclasses; a few magic constants left in strategies (MR/breakout files) | **3** — JSON params for some; otherwise hardcoded | |
| Dependency management | **8** — locked `requirements.txt` | **2** — un-pinned, multiple `import pandas_ta` etc., encrypted bundles | |
| Error handling | **5** — MT5 calls printed, little retry | **2** — swallowed exceptions, NameErrors, chained-comparison bug | |
| Logging | **4** — research logs minimal; bot uses print | **1** — print everywhere; a broken logger reference | |
| Type hints | **7** — modern annotations in core modules | **2** — sporadic | |
| Documentation | **7** — BACKTEST.md, per-module docstrings, integrity status docs | **3** — README is a résumé/socials page; docstrings in Spanish are sparse | |
| Extensibility | **8** — new strategies = new signal_fn (benchmark runner exists) | **3** — every new bot is a copy-paste script | |
| Ease of adding new strategies | **8** | **2** | |
| Ease of testing strategies independently | **8** — strategy.py, strategies/, validate | **1** — requires live MT5 connection | |

---

## PHASE 6 — FEATURE DIFFERENCE MATRIX

| Feature | Ours | Cloned Repo | Better Implementation | Worth Adopting? | Reason |
|---|---|---|---|---|---|
| Signal abstraction (`signal_fn`) | Yes | No | Ours | — | |
| Frozen compiled strategy (baseline) | Yes | No | Ours | — | |
| Dev/val/holdout chronological splits | Yes | No (naive train/test) | Ours | — | |
| Holdout access guard + audit log | Yes | No | Ours | — | |
| No-look-ahead indicator validation | Yes (validate.py) | No (shift(-N) bugs) | Ours | — | |
| Conservative intrabar fills | Yes | No | Ours | — | |
| Explicit spread/slippage/commission | Yes | No | Ours | — | |
| MAE/MFE / predictive-power / cost-sensitivity diagnostics | Yes | No | Ours | — | |
| Per-symbol instrument registry | Yes | No (per-script constants) | Ours | — | |
| Automated tests | Yes (pytest) | No | Ours | — | |
| Broker wrapper abstraction | Thin (bot.py) | Mature `Basic_funcs` | Cloned | Study → Yes (concept) | Decouples strategy logic from MT5 plumbing; improves testability of the live layer |
| Partial close / move-to-breakeven utilities | No | Yes (`close_partial`, `send_to_breakeven`) | Cloned | Study | Useful execution primitives; requires engine support |
| News/high-impact calendar gate | No | Broken attempt (`robot_noticias.py`) | Neither (concept good) | Yes (rebuilt) | Suppresses trading in high-vol windows → risk management |
| Per-symbol parameter files (JSON) | No (frozen config) | Yes (`parametros_bbands.json`) | Cloned | Yes | Aligns with config philosophy; keeps per-symbol knobs explicit |
| Max positions per symbol | 1 | Configurable (2–3) | Cloned | Study | Flexibility; must co-exist with one-position discipline |
| Kelly risk sizing | No (1% fixed) | Yes (2 buggy impls) | Neither | Study | Wrong impl; useful notion only |
| Risk-based lot sizing | Partial (fixed in backtest) | Flawed formula | Ours | — | |
| Pending order machinery (limit/stop/expiry) | No | Yes (`send_pending_order`, `buy_limit/…`) | Cloned | Study | Useful for pivot-style strategies later |
| Pairs trading infrastructure | No | Yes (multiple) | Cloned | Reject | Needs careful respec; currently arbitrary windows/pips |
| Martingale | No | Yes (12+ versions) | Ours (absent) | Reject | Guaranteed ruin |
| Remote-exec launchers | No | Yes | Ours (absent) | Reject | Security/reproducibility |
| PyArmor encryption | No | Yes | — | Reject | Obfuscation ≠ protection; untestable |
| Backtesting.py library engine | No (own engine) | Yes | Ours | Reject | Our engine gives research-grade control |
| In-sample optimizer usage | No | Yes (maximize Win Rate) | Ours | Reject | Overfitting |
| Session/time filters in strategies | No | Luxor 9–12h only | N/A | Study | |
| Swap modeling | No | No | Tie | Study | Low relevane for M5 |
| Multi-broker support (IB/NT) | No | `Easy_Trading_Mega/IB/NT` | Cloned | Reject now | Out of scope; harness design only |

---

## PHASE 7 — ADOPTION ANALYSIS

### 7.A ADOPT (genuinely useful; to be independently rebuilt in OUR architecture)

1. **Broker/execution abstraction layer** (concept of `Basic_funcs`, not its code).
   - What: a thin adapter exposing `connect`, `buy`, `sell`, `close_all`, `close_partial`, `move_to_breakeven`, `get_positions`, `get_rates`, `account_info` over MT5.
   - Why: today `bot.py` mixes MT5 plumbing, indicators and logic; a wrapper isolates the frozen strategy from broker API churn and allows the signal layer to be exercised against both live and replayed feeds.
   - Benefit: testable live layer; easier demo/sim swaps; cleaner separation.
   - Risk: scope creep; must remain read-only w.r.t. strategy rules; do not copy the flawed sizing/rounding inside it.
   - Fit: new `backtest/broker.py` or `live/` layer consumed by `bot.py`; backtest engine unchanged.

2. **High-impact news/calendar gate** (concept; rebuild correctly).
   - What: suppress opening new positions inside high-impact news windows (their `robot_noticias.py` logic is broken: `if hora_server in horas_noticias == True`, always False).
   - Benefit: reduces event-risk spikes and the worst live tail losses.
   - Risk: requires a calendar data source + correct timezone handling; must not gate historical backtests unless data is available (keep it a live-only filter and document it).
   - Fit: a `should_skip()` predicate in the live loop / signal layer.

3. **External per-symbol parameter files** (pattern).
   - What: JSON per-symbol strategy/cost parameter dictionaries (cf. `parametros_bbands.json`, `parametros_estrategia_btr.json`).
   - Why: keeps symbol knobs (lot, tf, tp/sl, max_trades) explicit and diffable; complements our frozen dataclasses.
   - Benefit: auditable parameter history; easier controlled experiments.
   - Risk: must remain frozen by default — the frozen-config default `dataclass` remains authoritative; JSON only as explicit overrides.
   - Fit: extend `backtest/config.py` with an optional loader.

4. **Disciplined candidate backlog from the audit survivors**.
   - The cloned repo's own handoff (its `task.md`) shortlisted **Keltner breakout** and **Bollinger+ATR mean-reversion** as the only concepts worth re-specifying. These are legitimate future candidates to be researched *inside our framework* (closed-candle signals, next-open fills, cost model, dev-only search) — **not** imported code, **not** deployed. This is consistent with the phase-4 audit conclusion.
   - Benefit: two additional falsifiable baseline candidates for the existing research pipeline.
   - Risk: none if restricted to dev data with holdout untouched; must resist copying their parameters/results.

### 7.B STUDY ONLY

- **Partial-close and move-to-breakeven** utilities — useful live execution primitives, but our strategy layer is SL/TP-intrabar; introducing them changes the engine's exit semantics and needs careful backtest modeling (a "partial TP" must be simulated, not assumed). Study after the backtest engine supports fractional exits.
- **`max_trades` per symbol** — position-limit flexibility. Trade-off vs our one-position-at-a-time discipline; study before relaxing.
- **Kelly-criterion risk fraction** — the *concept* is sound; their implementations are wrong (03 clamps negatives to 0.01; 04 doesn't clamp; both ignore SL distance in sizing). Study as a possible sizing variant on top of fixed-fractional, never as-is.
- **Pending-order machinery** (limit/stop with expiry) — relevant only if we later research pivot/support-resistance style strategies. Keep on the shelf.
- **Session/time filters** — only Luxor uses one; our market_research sessions study already shows session-dependence is weak. Study within the research suite before adding to any strategy.

### 7.C REJECT

- **All code containing negative `shift(-N)` backtests/analyses** — lookahead (C1).
- **Anomaly-detection strategies** built on full-sample σ thresholds (C2).
- **Martingale money management in any form** (C6).
- **`calculate_position_size` balance×leverage formula** (C3-risk).
- **`exec()` remote-GitHub launchers and the `clases` branch dependency** (C5).
- **PyArmor-obfuscated "production" copies** — untestable, opaque, trial-version runtime; they hide exactly what must be audited.
- **Plaintext credentials within code** — revert to env/config secrets.
- **In-sample `backtest.optimize(..., maximize='Win Rate [%]')` pipelines** — overfitting (C3).
- **Pairs-trading implementations** as written (windows morph, pips conversions inconsistent, spread stats on tiny windows) — reject as code; pairs is a research domain we could revisit from scratch with proper cointegration/hedge-ratio methodology, out of current scope.
- **`reg`/`var_ind`, `st.supertrend`, `fast/slow` swapped, `range(10)` hardcoded** — broken code (C4).
- **The "productivo"/`llamada_*`/`.bat` duplication pattern** and the encryption sub-repos — maintainability debt with no research value.
- **Their backtest metrics and parameter results in general** — because of C1–C4 they carry no evidentiary weight.

---

## PHASE 8 — OUR ADVANTAGES

Reviewed specifically against the research-workflow advantages named in the task:

- **`signal_fn` abstraction** — genuinely present (`backtester.py:31,233`). New strategies are inserted as functions; the runner, cost model and reporting stay untouched. The cloned repo has nothing comparable (each strategy bundles its own loop).
- **Separate strategy experimentation** — `backtest/strategies/` with documented, non-optimized candidates; `predictive.py` measures raw signal power *without* position suppression, and `experiment.py` isolates a single tunable (EMA separation) — controlled experimentation the cloned repo lacks entirely.
- **dev/validation/holdout datasets** — implemented (`data_split.py`) *and enforced* by `research_safety.py` (SplitGuard, HoldoutGuard, access audit log, `validate_no_holdout_access` decorator). This is the single most valuable property: a contamination backstop the cloned repo (with its reused month windows) does not have.
- **Multi-pair testing** — 4-symbol universe with per-symbol instrument canonicalization (`instruments.py`) and the 7×4 study matrix. The cloned repo tests a few symbols ad hoc with inconsistent pip definitions.
- **Diagnostic analysis** — MAE/MFE (`excursion.py`), predictive power, spread sensitivity, cost scenarios, monthly/long/short/streak tables (`metrics.py`) — a decision-support stack absent from the cloned repo (which relies on `backtesting.py`'s single stats object).
- **Frozen baseline** — `strategy.py`/`strategy_v2.py`/`bot.py` explicitly FROZEN; experiment artifacts are separable (`ema_sep_min`) so the baseline is never distored.
- **Reproducibility** — deterministic engine (no RNG), frozen dataclasses, per-split JSON manifests with run ids, and a re-run `validate.py` that must pass identically.
- **Controlled experimentation** — explicit cost-scenario framework and a deliberate "research-only" separation (power studies are not backtests) so exploratory numbers are never mistaken for P&L.

**Weaknesses to acknowledge honestly:** the historical handoff contained fabricated figures (a process failure, now documented and invalidated rather than silently fixed — which itself demonstrates better hygiene than the cloned repo's silent bugs); live-vs-backtest sizing semantics diverge; no trailing/session/swap; `.gitignore` is minimal; and the current dataset is mid-migration so older outputs are stale. These are all known and documented in-repo.

---

## PHASE 9 — FINAL VERDICT

### 1. Executive summary
The two repositories are different *kinds* of software. OURS is a research instrument with strict controls: closed-candle signals, next-open fills, conservative intrabar exits, explicit costs, chronological dev/val/holdout with guard rails, a validation battery, and a diagnostics stack. It is mostly sound but is currently in a data-migration state with several acknowledged self-inflicted integrity wounds (fabricated handoff, Phase-6 holdout leak, zero-spread data, EURJPY scaling) that have been formally invalidated rather than hidden.

The cloned repo is a live-script portfolio from a trading course. Its values are conceptual: a usable MT5 wrapper (with a flawed sizing formula), a few strategy ideas (Keltner with basis-stop, Bollinger+ATR fade), JSON parameterization, and a set of execution utilities. Its backtest/analysis layer is **fundamentally compromised** by negative-shift lookahead, full-sample statistics, in-sample-optimized grids, and train/test windows that overlap. Nothing in the cloned repo's backtest results should be treated as evidence. Its live layer is additionally dangerous (martingale, plaintext credentials, remote `exec()`).

### 2. Architecture comparison
Ours: layered, typed, tested, deterministic, config-frozen, split-guarded research framework with a thin live bot. Cloned: flat, duplicated, untested, MT5-coupled script farm with a reusable-but-flawed wrapper.

### 3. Strategy comparison
Ours: 1 frozen V1 + 1 frozen V2 + 2 documented candidates, all deterministic and cost-modeled. Cloned: ~20 strategies × dated duplicates; the two conceptually salvageable are Keltner breakout (SL at channel basis) and Bollinger+ATR fade; the martingale family must never be used.

### 4. Risk/execution comparison
Ours: fixed 0.10-lot backtest book; nominal 1% live sizing (not SL-distance-aware); explicit spread/slippage/commission in backtest, spread gate live. Cloned: sizing ignores SL entirely; costs absent in backtests; martingale; hardcoded credentials. Ours is materially safer.

### 5. Backtesting validity comparison
Ours is far stronger: lookahead engineered out and re-tested, next-open fills, SL-first intrabar, cost floors; residual issues are documented. Cloned is critically compromised (C1–C4) and its outputs are not usable as evidence.

### 6. Engineering comparison
Ours scores 7–9 in organization, modularity, testability, configurability, extensibility; lower in logging/error handling. Cloned scores 1–4 across the board, with JSON params and the wrapper as the only bright spots.

### 7. Feature matrix
See Phase 6.

### 8. Adopt / Study / Reject
See Phase 7. Adoption targets are *concepts* (broker abstraction, news gate, per-symbol JSON params, the two strategy candidates), rebuilt independently inside our framework.

### 9. Our strengths
signal_fn abstraction, controlled experiments, dev/val/holdout with guard rails + audit trail, multi-pair canonicalized universe, diagnostics (MAE/MFE, predictive power, cost sensitivity), frozen baselines, deterministic reproducibility, a validation battery, and a documented culture of invalidating bad results.

### 10. The 5 most valuable improvements to take from the cloned repo (as concepts, not code)
1. **Broker/execution adapter** (from `Basic_funcs`) that decouples the live strategy from MT5 plumbing and enables replay-testing of the live path.
2. **Calendar/news gate** — a correctly built high-impact-events blackout for live order entry (fixing their broken chained-comparison).
3. **External per-symbol parameter files** — JSON overrides layered on frozen dataclass defaults for auditable per-symbol knobs.
4. **Keltner breakout with SL at the channel basis** and **Bollinger+ATR fade** as the two disciplined candidate baselines for our research pipeline (matching their own audit shortlist), studied strictly on dev data with holdout untouched.
5. **Position-management primitives** (partial close, move-to-breakeven) as future engine features — simulated faithfully before each is ever used live.

### 11. Serious flaws discovered
**Cloned repo:** (a) pervasive negative-shift lookahead and full-sample-threshold leakage that invalidates its backtests; (b) in-sample optimization + overlapping train/test windows; (c) martingale money management; (d) risk sizing that ignores stop distance; (e) plaintext broker credentials; (f) remote `exec()` of non-versioned code; (g) no tests/reproducibility. **Our repo:** (a) past fabricated handoff numbers and a Phase-6 holdout contamination (documented and formally invalidated); (b) live-bot signal evaluated on the possibly-forming candle (`bot.py` `iloc[-1]`) vs. the backtest's closed-candle semantics; (c) 48.3% zero-spread EURUSD history and the EURJPY pip-scaling trap; (d) win/loss vs money bucket inconsistency in `metrics.py`; (e) live/backtest sizing divergence; (f) minor hygiene (gitignore, stale outputs, interpreter drift).

**Bottom line:** architecturally and research-wise our repository is the stronger and safer platform; the cloned repository contributes a small number of useful *concepts* (wrapper design, news gate, per-symbol JSON params, Keltner/Bollinger candidates) that are worth rebuilding independently — and a long list of practices to reject (martingale, lookahead backtests, in-sample optimization, hardcoded secrets, remote exec). Per task constraints, no strategy is recommended for live deployment and no parameters were optimized; the holdout stays untouched until a frozen specification exists.

---
*End of audit. No files in either repository were modified.*