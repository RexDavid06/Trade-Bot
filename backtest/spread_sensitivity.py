"""Spread sensitivity analysis framework for execution cost assumptions.

Tests how a strategy's backtest performance changes under different execution
cost profiles (spread, slippage, and commission). Every scenario re-runs the
same strategy with identical signals; only the cost model varies, isolating the
impact of execution-cost assumptions on reported performance.

The scenarios feed the :class:`~backtest.config.CostConfig` fields
``spread_multiplier``, ``min_spread_pips`` and ``extra_slippage_pips``, which
are applied to the per-candle observed spread in the backtester.

Usage:
    from backtest.spread_sensitivity import (
        CostScenario, OBSERVED, STRESSED_2X, MINIMUM_1PIP, REALISTIC, HIGH_COST,
        make_cost_config, run_cost_sensitivity, print_sensitivity_report,
    )

    results = run_cost_sensitivity(
        df, signal_fn, add_indicators, s_cfg,
        [OBSERVED, STRESSED_2X, MINIMUM_1PIP, REALISTIC, HIGH_COST],
        get_instrument("EURUSD"),
    )
    print_sensitivity_report(results)

Run with:
    python -m backtest.spread_sensitivity
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

import pandas as pd

from .backtester import SignalFn, run_backtest
from .config import CostConfig, StrategyConfig
from .instruments import InstrumentConfig
from .metrics import compute_metrics


@dataclass
class CostScenario:
    """An execution cost profile for sensitivity testing.

    Attributes:
        name: Unique identifier used as the key in results and the report table.
        spread_multiplier: Scales the observed spread column (1.0 = raw data).
        min_spread_pips: Floor applied to the resulting spread, in pips.
        extra_slippage_pips: Extra slippage per side, on top of the base
            ``CostConfig.slippage_pips``.
        commission_per_lot: Round-turn commission in USD per standard lot.
    """

    name: str
    spread_multiplier: float = 1.0
    min_spread_pips: float = 0.0
    extra_slippage_pips: float = 0.0
    commission_per_lot: float = 7.0


OBSERVED = CostScenario(
    name="OBSERVED",
    spread_multiplier=1.0,
    min_spread_pips=0.0,
    extra_slippage_pips=0.0,
    commission_per_lot=7.0,
)
"""Baseline: observed spreads, base slippage, standard commission."""

STRESSED_2X = CostScenario(
    name="STRESSED_2X",
    spread_multiplier=2.0,
    min_spread_pips=0.0,
    extra_slippage_pips=0.0,
    commission_per_lot=7.0,
)
"""Doubles observed spreads to simulate adverse liquidity conditions."""

MINIMUM_1PIP = CostScenario(
    name="MINIMUM_1PIP",
    spread_multiplier=0.0,
    min_spread_pips=1.0,
    extra_slippage_pips=0.0,
    commission_per_lot=7.0,
)
"""Ignores observed spread entirely and uses a flat 1-pip minimum."""

REALISTIC = CostScenario(
    name="REALISTIC",
    spread_multiplier=1.0,
    min_spread_pips=0.5,
    extra_slippage_pips=0.2,
    commission_per_lot=7.0,
)
"""Adds a small minimum spread and per-side slippage for live-market realism."""

HIGH_COST = CostScenario(
    name="HIGH_COST",
    spread_multiplier=2.0,
    min_spread_pips=1.0,
    extra_slippage_pips=0.5,
    commission_per_lot=14.0,
)
"""Aggressive stress test: widened spread, extra slippage, doubled commission."""


def make_cost_config(
    scenario: CostScenario,
    instrument_config: InstrumentConfig,
    starting_balance: float = 10_000.0,
    lot_size: float = 0.10,
) -> CostConfig:
    """Build a :class:`CostConfig` from a scenario and an instrument config.

    Spread/slippage/commission values come from the scenario; quoting sizes
    (pip, point, contract size) and account assumptions come from the
    instrument and the default cost config.

    Args:
        scenario: The cost scenario to apply.
        instrument_config: Per-symbol quoting and contract-size settings.
        starting_balance: Account balance used for equity-curve metrics.
        lot_size: Position size in lots used for money P&L.

    Returns:
        A frozen CostConfig encoding the scenario's cost assumptions.
    """
    base = CostConfig()
    return replace(
        base,
        starting_balance=starting_balance,
        lot_size=lot_size,
        base_contract=instrument_config.contract_size,
        commission_per_lot=scenario.commission_per_lot,
        slippage_pips=base.slippage_pips + scenario.extra_slippage_pips,
        spread_multiplier=scenario.spread_multiplier,
        min_spread_pips=scenario.min_spread_pips,
        point=instrument_config.point,
        pip=instrument_config.pip,
    )


def run_cost_sensitivity(
    df: pd.DataFrame,
    signal_fn: SignalFn | None,
    setup_fn: Callable[[pd.DataFrame, StrategyConfig], pd.DataFrame],
    s_cfg: StrategyConfig,
    scenarios: list[CostScenario],
    instrument_config: InstrumentConfig,
    starting_balance: float = 10_000.0,
    lot_size: float = 0.10,
) -> dict[str, dict[str, Any]]:
    """Run a backtest under each cost scenario and collect performance metrics.

    The dataframe is prepared once (indicators added) and each scenario is
    backtested with identical signals; only the cost model changes. This makes
    any performance difference attributable to execution-cost assumptions.

    Args:
        df: Raw OHLCV dataframe (must contain an open/high/low/close and a
            ``spread`` column). Prepared with ``setup_fn`` before backtesting.
        signal_fn: Model function ``signal_fn(df, i, cfg) -> "BUY" | "SELL" |
            None`` evaluated on closed candles. ``None`` uses the default V1
            strategy from ``backtest.strategy``.
        setup_fn: Function that augments the dataframe with the indicators the
            strategy needs (e.g. ``backtest.indicators.add_indicators``).
        s_cfg: Strategy configuration passed to ``setup_fn`` and the backtester.
        scenarios: Cost scenarios to evaluate, one backtest each.
        instrument_config: Quoting/contract settings for the instrument.
        starting_balance: Account starting balance for equity metrics.
        lot_size: Position size in lots for money P&L.

    Returns:
        Mapping of scenario name to the metrics dict returned by
        :func:`backtest.metrics.compute_metrics`.
    """
    prepared = setup_fn(df, s_cfg)
    results: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        c_cfg = make_cost_config(scenario, instrument_config, starting_balance, lot_size)
        trades, equity = run_backtest(prepared, s_cfg, c_cfg, signal_fn)
        results[scenario.name] = compute_metrics(trades, equity, c_cfg.starting_balance)
    return results


_METRIC_COLUMNS = [
    ("total_return_pct", "Ret %", "{:>.2f}"),
    ("net_profit", "Net P/L", "${:,.0f}"),
    ("max_drawdown_pct", "Max DD %", "{:>.2f}"),
    ("profit_factor", "PF", "{:>.2f}"),
    ("win_rate", "Win %", "{:>.1%}"),
    ("expectancy_per_trade", "Exp / T", "${:,.2f}"),
    ("total_trades", "Trades", "{:d}"),
]


def print_sensitivity_report(results: dict[str, dict[str, Any]]) -> None:
    """Print a comparison table of metrics across cost scenarios.

    Each row is a scenario; each column is a performance metric. The observed-
    spread baseline is expected to be included in ``results`` so differences
    can be read directly.

    Args:
        results: Output of :func:`run_cost_sensitivity` mapping scenario names
            to metrics dicts.
    """
    if not results:
        print("No results to display.")
        return

    cols = [entry for entry in _METRIC_COLUMNS if any(entry[0] in m for m in results.values())]
    name_width = max(len(name) for name in results)

    header = f"{'Scenario':<{name_width}}  " + "  ".join(label for _, label, _ in cols)
    print(header)
    print("-" * len(header))

    for name, metrics in results.items():
        row = f"{name:<{name_width}}  "
        cells = []
        for key, _, fmt in cols:
            val = metrics.get(key)
            if val is None:
                cells.append("N/A")
            elif isinstance(val, float) and (val != val or val in (float("inf"), float("-inf"))):
                cells.append("inf" if val > 0 else "-inf")
            else:
                cells.append(fmt.format(val))
        print(row + "  ".join(cells))


if __name__ == "__main__":
    from .config import PathConfig
    from .indicators import add_indicators
    from .instruments import get_instrument

    pcfg = PathConfig()
    if not pcfg.data_file.exists():
        raise SystemExit(f"Data file not found: {pcfg.data_file}")

    data = pd.read_csv(pcfg.data_file)
    if "time" in data.columns:
        data["time"] = pd.to_datetime(data["time"])

    sensitivity_results = run_cost_sensitivity(
        data,
        None,
        add_indicators,
        StrategyConfig(),
        [OBSERVED, STRESSED_2X, MINIMUM_1PIP, REALISTIC, HIGH_COST],
        get_instrument("EURUSD"),
    )
    print_sensitivity_report(sensitivity_results)