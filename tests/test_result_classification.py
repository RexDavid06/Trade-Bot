"""A4 regression tests: win/loss/breakeven classification follows net_money.

Costs (spread + slippage + commission) can flip the sign between the pips-based
and the money-based result (e.g. net_pips > 0 while net_money < 0). The
authoritative classification is the financial outcome so classification and
financial metrics never disagree.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.backtester import Trade, classify_result, run_backtest
from backtest.config import CostConfig, StrategyConfig
from backtest.metrics import compute_metrics


class TestClassifyResult:
    def test_positive_is_win(self):
        assert classify_result(1.0) == "WIN"

    def test_negative_is_loss(self):
        assert classify_result(-1.0) == "LOSS"

    def test_zero_is_breakeven(self):
        assert classify_result(0.0) == "BE"


def _make_trade(net_money, net_pips, result, direction="BUY", exit_time=None):
    return Trade(
        entry_time=pd.Timestamp("2026-01-01 00:00:00"),
        exit_time=exit_time or pd.Timestamp("2026-01-01 12:00:00"),
        direction=direction,
        entry_price=1.0,
        exit_price=1.0,
        stop_loss=0.99,
        take_profit=1.01,
        atr=0.001,
        result=result,
        exit_reason="OPEN",
        net_pips=net_pips,
        gross_pips=net_pips,
        cost_pips=0.0,
        net_money=net_money,
        gross_money=net_money,
    )


def _frame(exit_close):
    n = 6
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=n, freq="5min"),
            "open": [1.00000] * n,
            "high": [1.00000, 1.00000, 1.00001, 1.00001, 1.00005, 1.00005],
            "low": [1.00000, 1.00000, 0.99999, 0.99999, 0.99995, 0.99995],
            "close": [1.00000, 1.00000, 1.00000, 1.00000, 1.00000, exit_close],
            "spread": [0.0] * n,
            "atr": [0.0001] * n,
            "rsi": [50.0] * n,
            "ema_fast": [1.0001] * n,
            "ema_slow": [1.0000] * n,
        }
    )


def _run_single_exit(exit_close, commission_per_lot):
    df = _frame(exit_close)
    s_cfg = StrategyConfig()
    c_cfg = CostConfig(
        lot_size=0.10,
        commission_per_lot=commission_per_lot,
        slippage_pips=0.0,
        point=0.00001,
        pip=0.0001,
    )
    signal = lambda df, i, cfg: "BUY" if i == 2 else None
    trades, equity = run_backtest(df, s_cfg, c_cfg, signal_fn=signal)
    assert len(trades) == 1
    return trades[0]


def test_engine_classifies_money_win_when_pips_agree():
    trade = _run_single_exit(exit_close=1.00100, commission_per_lot=7.0)
    assert trade.net_pips > 0
    assert trade.net_money > 0
    assert trade.result == "WIN"


def test_engine_labels_loss_when_pips_win_but_money_losses():
    trade = _run_single_exit(exit_close=1.00003, commission_per_lot=100.0)
    assert trade.net_pips > 0
    assert trade.net_money < 0
    assert trade.result == "LOSS"


def test_metrics_follow_money_not_stale_pips_based_field():
    trades = [
        _make_trade(net_money=-5.0, net_pips=0.5, result="WIN"),
        _make_trade(net_money=3.0, net_pips=-0.3, result="LOSS"),
        _make_trade(net_money=0.0, net_pips=0.0, result="BE"),
    ]
    equity = pd.DataFrame(
        {
            "time": pd.to_datetime(
                ["2026-01-01 00:00", "2026-01-01 12:00", "2026-01-02 12:00", "2026-01-03 12:00"]
            ),
            "balance": [10000.0, 9995.0, 9998.0, 9998.0],
        }
    )
    metrics = compute_metrics(trades, equity, starting_balance=10000.0)

    assert metrics["winning_trades"] == 1
    assert metrics["losing_trades"] == 1
    assert metrics["breakeven_trades"] == 1
    assert metrics["win_rate"] == pytest.approx(1 / 3)
    assert metrics["gross_profit"] == pytest.approx(3.0)
    assert metrics["gross_loss"] == pytest.approx(5.0)
    assert metrics["net_profit"] == pytest.approx(-2.0)
    assert metrics["longest_winning_streak"] == 1
    assert metrics["longest_losing_streak"] == 1
    monthly_wins = int(metrics["monthly"]["wins"].sum())
    monthly_losses = int(metrics["monthly"]["losses"].sum())
    assert (monthly_wins, monthly_losses) == (1, 1)


def test_metrics_consistent_with_engine_disagreement_case():
    trade = _run_single_exit(exit_close=1.00003, commission_per_lot=100.0)
    equity = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 00:25"]),
            "balance": [10000.0, 10000.0 + trade.net_money],
        }
    )
    metrics = compute_metrics([trade], equity, starting_balance=10000.0)

    assert trade.net_pips > 0
    assert metrics["winning_trades"] == 0
    assert metrics["losing_trades"] == 1
    assert metrics["expectancy_pips"] > 0
    assert metrics["net_profit"] < 0