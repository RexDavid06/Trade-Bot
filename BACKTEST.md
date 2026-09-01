# Backtesting System for the EURUSD M5 Strategy

A standalone backtester for the strategy implemented in `bot.py`. It measures
whether the live strategy has a statistical edge **before** any optimization.
`bot.py`, the live strategy, and its rules are **not modified**.

## Requirements

* Python 3.13 venv (already set up in `venv/`)
* `requirements.txt` packages plus `matplotlib` (already installed)

## Running the backtest

    venv\Scripts\python.exe -m backtest.run

Optional flags:

    venv\Scripts\python.exe -m backtest.run --data path\to\data.csv --out path\to\outputs

## Validating the backtester

    venv\Scripts\python.exe -m backtest.validate

Checks: deterministic results, exact reproduction of the strategy rules,
no look-ahead in indicators, no overlapping trades, correct SL/TP first-touch
exits, and fills only on the next candle open after a signal.

## Diagnostics (analysis only, no strategy change)

    venv\Scripts\python.exe -m backtest.diagnostics

Writes `outputs/diagnostics_report.md` (readable summary) and
`outputs/diagnostics_trades.csv` (every trade with R-multiple, signal RSI, EMA
separation, duration). It only **re-runs / slices** the existing strategy — it
does not alter entry rules, SL/TP, add filters, or touch `bot.py`.

Covered: cost sensitivity (zero / spread-only / baseline), R-multiple
distribution, long-vs-short, RSI entry zones, market-regime buckets (EMA
separation, ATR level, trend strength = EMA-sep/ATR), trade duration and
win/loss sequences.

## Excursion analysis (MAE/MFE — analysis only)

    venv\Scripts\python.exe -m backtest.excursion

Writes `outputs/excursion_report.md`. Every trade now carries MAE (maximum
adverse excursion, pips + R), MFE (maximum favorable excursion, pips) and
signal context (RSI, EMA fast/slow, EMA separation, ATR, signal candle range,
price-to-EMA distance) recorded by the engine from the same bars it walked
(with no change to entry rules, SL/TP, or bot.py). It reports:

1. MAE / MFE distributions (median, average, p25, p75, p90).
2. Before-stop behaviour for SL trades (MAE, whether price ever moved
   favorable, MFE before the stop).
3. Entry timing for losers, bucketed by favorable room (MFE in R) before the
   stop.
4. Signal context compared between winners and losers.

Caveat: MAE.MFE are estimated from candle OHLC (no tick data), so a candled
gap can push a stop-sweep's measured excursion beyond the exact SL level.
MAE-based timing buckets for losers are degenerate (a loser always reaches ~1R),
which is why section 3 buckets by MFE (favorable room) instead.

## EMA-separation experiment (controlled, single-parameter)

    venv\Scripts\python.exe -m backtest.experiment

Tests the hypothesis that the strategy loses because the EMA50/EMA200 trend
trigger fires when the two EMAs are too close (market ranging). It adds a
single opt-in filter to signal generation — require the normalized separation
`abs(EMA50 - EMA200) / ATR` to EXCEED a threshold — and re-runs the SAME
strategy across a sensible range while keeping every other parameter, SL/TP,
one-position rule, execution and costs unchanged. Threshold 0.00 reproduces
bot.py exactly (baseline). No new indicator is added and bot.py is untouched.

Writes `outputs/separation_experiment.csv` and
`outputs/separation_experiment.md` with, per threshold: total/BUY/SELL trades,
win rate, profit factor, expectancy R, total R, net P/L, max drawdown and
longest losing streak, plus a change-vs-baseline table.

Result: the hypothesis is FALSIFIED. Filtering for stronger trend separation
(up to 0.50) removes trades but does not improve the edge — win rate stays
flat (~31.5%), profit factor stays ~0.56, and expectancy R actually worsens
slightly (−0.31R → −0.33R). Losing is removed proportionally with winning, so
the strategy has a consistent negative per-trade edge regardless of trend
strength. This is an investigation of the relationship only — no "best"
threshold is selected.

## Raw directional predictive power (analysis only)

    venv\Scripts\python.exe -m backtest.predictive

Answers: "does the signal itself contain any measurable directional predictive
power, independent of the SL/TP implementation?" Every candle matching the exact
existing BUY/SELL rules (41,713 total: 19,404 BUY, 22,309 SELL) is evaluated
independently (the one-position execution rule is intentionally not applied).
For each signal the forward move to the close of `i+H` is measured for H =
1/3/5/10/20/40/80 M5 candles, in the predicted-direction sign, and reported in
pips and R (1R = 1.5×ATR at the signal candle). Reaches of +0.5R/+1R/+2R
before −1R are counted walking candles 1..H with the same conservative
adverse-first intrabar rule as the engine. No look-ahead: only bars after the
signal are used. Writes `outputs/predictive_report.md`, `predictive_BUY/SELL/ALL.csv`.

Result: the signal has **no directional predictive power**. Direction-hit rate
is below 50% at every horizon (48.2% at 1 candle → 47.1% at 80), i.e. the
signal predicts *slightly against* itself — robustly significant with ~41k
signals. Forward returns are ~0 or mildly negative (avg R ~0 at short horizons,
~−0.2R at 80 candles; worse for BUY at long horizons). The +0.5R-before-−1R
rates that rise with horizon (21% → 67%) reflect range oscillation, not edge:
the market crosses short favorable targets before −1R simply because it chops.
This confirms, independent of any SL/TP choice, that the entries carry no
usable directional information — consistent with the observed negative edge.

## Data

* `data/eurusd_m5.csv` — historical EURUSD M5 bars (open, high, low, close,
  tick_volume, spread, real_volume).
* Refreshed with `venv\Scripts\python.exe dump_mt5_data.py` (requires MT5
  connected and logged in; the actual MT5 demo server here only provides
  ~90,000 M5 bars back to mid-2025).
* The backtester only reads the CSV; it never touches MT5 or places orders.

## Required results (all produced)

The console summary and `outputs/summary.json` contain:

* Total / winning / losing / breakeven trades, win rate
* Gross profit, gross loss, net profit/loss, profit factor
* Average winning and losing trade, expectancy per trade (money + pips)
* Max drawdown (money and %), longest win and loss streaks
* Total return (%)
* Monthly performance table
* Long and short performance breakdowns

## Outputs (written to `outputs/`)

* `trade_log.csv` — every simulated trade: entry/exit time, direction, entry,
  exit, stop loss, take profit, ATR at entry, gross/cost/net pips, gross/net
  money, result, exit reason.
* `equity_curve.csv` — account balance after each closed trade.
* `equity_curve.png` — plot of that equity curve.
* `summary.json` — machine-readable metrics.

## Architecture and files

Everything lives in the `backtest/` package, fully separated from `bot.py`:

| File | Responsibility |
|------|----------------|
| `config.py` | Strategy + cost/account assumptions (all tunable via dataclasses) |
| `indicators.py` | EMA50/EMA200/RSI14/ATR14 using the same `ta` library calls as `bot.py` |
| `strategy.py` | Exact BUY/SELL rules from `bot.py` (strict inequalities) |
| `backtester.py` | Bar-by-bar engine: fills on next open, one-position rule, SL/TP resolution, costs |
| `metrics.py` | All statistics + monthly/long/short tables |
| `reporting.py` | Trade log CSV, equity CSVs + PNG, summary JSON, console report |
| `run.py` | CLI entry point (`python -m backtest.run`) |
| `diagnostics.py` | Analysis-only report (see Diagnostics section) |
| `excursion.py` | Analysis-only MAE/MFE report (see Excursion section) |
| `experiment.py` | EMA-separation experiment (see EMA-separation section) |
| `predictive.py` | Raw signal predictive-power analysis (see predictive section) |
| `validate.py` | The end-to-end validation battery described above |

The clean separation lets it be extended later for walk-forward testing, multi
symbol/timeframe, different risk models, or additional strategies without
touching the engine or the live bot.

## How the backtest works

* Signals are generated only on **closed** candles. A signal on candle `i`
  fills at the **open** of candle `i+1` (no look-ahead, no same-candle entry
  except SL/TP resolution within the fill candle).
* SL = 1.5 × ATR, TP = 3 × ATR, measured from the entry price, using the entry
  candle's ATR (mirrors `bot.py`, which uses the ATR of the last closed candle
  at fill time).
* Only one position open at a time; while one is open no new signal is queued
  (mirrors the `position_exists()` guard in `bot.py`).
* SL/TP are resolved against subsequent candles' highs/lows.

## Cost assumptions (documented)

Prices in the CSV are treated as **bid**. The `spread` column is in points.

| Cost | Value | Applied |
|------|-------|---------|
| Spread | per-entry-candle `spread` (points) | round-turn, price units |
| Slippage | 0.5 pip per side | round-turn (2 × 0.5 pip) |
| Commission | $7.00 per lot, round-turn | money per lot |

Money P&L uses a fixed `0.10` lot size on a `$10,000` starting balance
(1 lot = 100,000 base; € pip ≈ $1 at 0.10 lots). The live bot sizes by 1% risk
per trade, which depends on a live broker balance and is intentionally **not**
replicated — money figures here are illustrative; the pip/R-unit figures are
broker-independent.

Intrabar ambiguity: if a single candle touches both SL and TP, the **stop-loss
is assumed hit first** (conservative worst case, `conservative_intrabar = True`).
This avoids optimistic bias. Set it to `False` in `config.py` for the optimistic
"profit first" alternative.

## Current result and limitations

On the available dataset (90,000 M5 bars, June 2025 → Sept 2026):
~4,109 trades, 31.6% win rate, profit factor 0.57, expectancy **−$2.27/trade
(−1.6 pips)**, total return approximately **−93%** on the fixed-lot account.
The strategy does **not** show a positive statistical edge after costs on this
data.

Limitations:
* History is limited to what the MT5 demo server caches (~15 months of M5),
  so the sample is one market regime.
* No tick data: SL/TP timing within a candle is approximated (conservative rule
  above) and same-candle fills are possible when a level trades inside the fill
  candle.
* The single end-of-data open position is force-closed at the last close
  (`exit_reason = OPEN`); it is negligible here.