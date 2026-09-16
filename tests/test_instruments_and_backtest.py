"""Tests for instrument configuration and backtest cost / P&L logic."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest import instruments as inst
from backtest.backtester import _cost_price
from backtest.config import CostConfig

PIP_VALUES = {
    "EURUSD": 0.0001,
    "EURGBP": 0.0001,
    "EURJPY": 0.01,
    "GBPUSD": 0.0001,
}

POINT_VALUES = {
    "EURUSD": 0.00001,
    "EURGBP": 0.00001,
    "EURJPY": 0.001,
    "GBPUSD": 0.00001,
}


PIP_VALUE_PER_LOT_USD = 10.0


def _pnl(pips: float, lots: float) -> float:
    """P&L in USD for a pip move of *pips* on *lots* at $10/pip per standard lot."""
    return pips * lots * PIP_VALUE_PER_LOT_USD


@pytest.mark.parametrize("symbol", PIP_VALUES)
def test_pip_value_per_symbol(symbol):
    assert inst.get_instrument(symbol).pip == PIP_VALUES[symbol]


@pytest.mark.parametrize("symbol", POINT_VALUES)
def test_point_value_per_symbol(symbol):
    assert inst.get_instrument(symbol).point == POINT_VALUES[symbol]


@pytest.mark.parametrize(
    ("symbol", "price_diff", "expected_pips"),
    [("EURUSD", 0.001, 10.0), ("EURJPY", 0.1, 10.0)],
)
def test_price_to_pips(symbol, price_diff, expected_pips):
    instrument = inst.get_instrument(symbol)
    assert inst.price_to_pips(price_diff, instrument) == pytest.approx(expected_pips)


@pytest.mark.parametrize(
    ("symbol", "pips", "expected_price"),
    [("EURUSD", 10.0, 0.001), ("EURJPY", 10.0, 0.1)],
)
def test_pips_to_price(symbol, pips, expected_price):
    instrument = inst.get_instrument(symbol)
    assert inst.pips_to_price(pips, instrument) == pytest.approx(expected_price)


@pytest.mark.parametrize(
    ("symbol", "spread_points", "expected_price"),
    [("EURUSD", 5, 0.00005), ("EURJPY", 10, 0.01)],
)
def test_spread_cost_points(symbol, spread_points, expected_price):
    instrument = inst.get_instrument(symbol)
    assert inst.spread_cost_points(spread_points, instrument) == pytest.approx(expected_price)


def test_instrument_lookup_is_case_insensitive():
    for symbol, config in inst.INSTRUMENTS.items():
        for spelled in (symbol.lower(), symbol.upper(), symbol.title()):
            assert inst.get_instrument(spelled) is config


def test_unknown_symbol_raises():
    with pytest.raises((KeyError, ValueError)):
        inst.get_instrument("XAUUSD")


@pytest.mark.parametrize(
    ("symbol", "entry", "exit", "expected_profit"),
    [("EURUSD", 1.1000, 1.1010, 10.0), ("EURJPY", 160.00, 160.10, 10.0)],
)
def test_pnl_buy(symbol, entry, exit, expected_profit):
    instrument = inst.get_instrument(symbol)
    gross_price = exit - entry
    pips = inst.price_to_pips(gross_price, instrument)
    profit = _pnl(pips, lots=0.1)
    assert profit == pytest.approx(expected_profit)


def test_spread_applied_once_round_turn():
    df = pd.DataFrame({"spread": [5.0]})
    cfg = CostConfig(point=0.00001, pip=0.0001, slippage_pips=0.0)
    single = 5.0 * cfg.point
    cost = _cost_price(df, 0, cfg)
    assert cost == pytest.approx(single)
    assert cost != pytest.approx(2.0 * single)


def test_eurjpy_pip_is_not_0001():
    jpy = inst.get_instrument("EURJPY")
    assert jpy.pip == pytest.approx(0.01)
    assert jpy.pip != 0.0001


@pytest.mark.parametrize("symbol", PIP_VALUES)
def test_slippage_round_turn_is_one_pip(symbol):
    instrument = inst.get_instrument(symbol)
    df = pd.DataFrame({"spread": [0.0]})
    cfg = CostConfig(
        point=instrument.point,
        pip=instrument.pip,
        slippage_pips=0.5,
    )
    cost = _cost_price(df, 0, cfg)
    assert cost / instrument.pip == pytest.approx(1.0)