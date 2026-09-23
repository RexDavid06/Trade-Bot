"""A5 regression tests: explicit sizing model and risk_fraction parity.

The frozen default (lot_size_mode="fixed") must reproduce exactly the original
fixed-lot book. The additive "risk_fraction" mode re-derives the lot per trade
from the running balance using bot.py's live formula:
    lot = max(round(balance * 0.01 / 1000, 2), 0.01)
documented as explicit parameters (100 pips assumed SL * $10/pip/lot = 1000).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.backtester import run_backtest
from backtest.config import CostConfig, StrategyConfig, lot_for_balance
from backtest.strategy import signal_at


class TestLotForBalance:
    def test_fixed_defaults_unchanged(self):
        cfg = CostConfig()
        assert cfg.lot_size_mode == "fixed"
        assert lot_for_balance(10_000.0, cfg) == pytest.approx(0.10)

    def test_fixed_ignores_balance(self):
        cfg = CostConfig()
        assert lot_for_balance(1.0, cfg) == pytest.approx(0.10)
        assert lot_for_balance(1_000_000.0, cfg) == pytest.approx(0.10)

    def test_risk_fraction_reproduces_bot_formula_at_10k(self):
        cfg = CostConfig(lot_size_mode="risk_fraction")
        # bot.py: lot = max(round(10000 * 0.01 / 1000, 2), 0.01) = 0.10
        assert lot_for_balance(10_000.0, cfg) == pytest.approx(0.10)

    def test_risk_fraction_scales_with_balance(self):
        cfg = CostConfig(lot_size_mode="risk_fraction")
        # 20k balance -> risk $200 / 1000 = 0.20 lots
        assert lot_for_balance(20_000.0, cfg) == pytest.approx(0.20)
        # 5k balance -> risk $50 / 1000 = 0.05 lots
        assert lot_for_balance(5_000.0, cfg) == pytest.approx(0.05)

    def test_min_lot_floor(self):
        cfg = CostConfig(lot_size_mode="risk_fraction")
        assert lot_for_balance(100.0, cfg) == pytest.approx(0.01)

    def test_max_lot_cap(self):
        cfg = CostConfig(lot_size_mode="risk_fraction", maximum_lot=0.5)
        assert lot_for_balance(100_000.0, cfg) == pytest.approx(0.5)

    def test_rounding_to_lot_step(self):
        cfg = CostConfig(lot_size_mode="risk_fraction")
        # 12600 balance -> 0.126 rounds to 0.13 (0.01 step)
        assert lot_for_balance(12_600.0, cfg) == pytest.approx(0.13)

    def test_risk_percent_scaling(self):
        cfg = CostConfig(lot_size_mode="risk_fraction", risk_percent=2.0)
        assert lot_for_balance(10_000.0, cfg) == pytest.approx(0.20)


def _frame():
    n = 220
    rng = np.random.default_rng(7)
    close = 1.1000 + np.cumsum(rng.normal(0, 0.0001, n))
    # Steady uptrend so V1 fires BUY signals on many closed candles.
    close += np.linspace(0, 0.001, n)
    # high far enough above close to reach TP (entry + 3*atr = +0.0009),
    # low far enough below close to miss SL (entry - 1.5*atr = -0.00045).
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=n, freq="5min"),
            "open": close,
            "high": close + 0.0010,
            "low": close - 0.0001,
            "close": close,
            "spread": np.full(n, 5.0),
            "ema_fast": np.full(n, 1.1010),
            "ema_slow": np.full(n, 1.1000),
            "rsi": np.full(n, 48.0),
            "atr": np.full(n, 0.0003),
        }
    )


class TestRiskFractionEngineParity:
    def test_fixed_and_risk_fraction_differ_only_in_money(self):
        df = _frame()
        s_cfg = StrategyConfig()
        fixed = CostConfig(lot_size_mode="fixed")
        risk = CostConfig(lot_size_mode="risk_fraction")

        trades_fixed, eq_fixed = run_backtest(df, s_cfg, fixed, signal_fn=signal_at, max_hold_bars=5)
        trades_risk, eq_risk = run_backtest(df, s_cfg, risk, signal_fn=signal_at, max_hold_bars=5)

        assert len(trades_fixed) == len(trades_risk) > 0
        for t_f, t_r in zip(trades_fixed, trades_risk):
            for attr in (
                "entry_time", "exit_time", "direction", "entry_price", "exit_price",
                "result", "exit_reason", "net_pips", "gross_pips", "cost_pips",
            ):
                assert getattr(t_f, attr) == getattr(t_r, attr), attr
        assert eq_fixed["balance"].iloc[-1] == pytest.approx(10_000.0 + sum(t.net_money for t in trades_fixed))
        assert eq_risk["balance"].iloc[-1] == pytest.approx(10_000.0 + sum(t.net_money for t in trades_risk))

    def test_risk_fraction_is_deterministic(self):
        df = _frame()
        s_cfg = StrategyConfig()
        risk = CostConfig(lot_size_mode="risk_fraction")
        t1, e1 = run_backtest(df, s_cfg, risk, signal_fn=signal_at, max_hold_bars=5)
        t2, e2 = run_backtest(df, s_cfg, risk, signal_fn=signal_at, max_hold_bars=5)
        assert t1 == t2
        assert e1.equals(e2)

    def test_risk_fraction_first_lot_matches_fixed(self):
        df = _frame()
        s_cfg = StrategyConfig()
        fixed = CostConfig(lot_size_mode="fixed")
        risk = CostConfig(lot_size_mode="risk_fraction", slippage_pips=0.0, commission_per_lot=0.0)
        trades_fixed, _ = run_backtest(df, s_cfg, fixed, signal_fn=signal_at, max_hold_bars=5)
        trades_risk, _ = run_backtest(df, s_cfg, risk, signal_fn=signal_at, max_hold_bars=5)
        assert len(trades_risk) >= 2
        # $10k start, 1% risk: first lot is exactly 0.10 (same as fixed default).
        assert trades_fixed[0].lot == pytest.approx(0.10)
        assert trades_risk[0].lot == pytest.approx(0.10)

    def test_risk_fraction_equity_grows_after_winning_streak(self):
        df = _frame()
        s_cfg = StrategyConfig()
        risk = CostConfig(lot_size_mode="risk_fraction", slippage_pips=0.0, commission_per_lot=0.0)
        trades, eq = run_backtest(df, s_cfg, risk, signal_fn=signal_at, max_hold_bars=5)
        assert len(trades) >= 2
        net = sum(t.net_money for t in trades)
        # In a sustained uptrend with zero costs, net is positive.
        assert net > 0
        # Later trades in a winning streak size larger than the first 0.10 lot.
        assert trades[-1].lot > trades[0].lot
        assert eq["balance"].iloc[-1] == pytest.approx(10_000.0 + net)