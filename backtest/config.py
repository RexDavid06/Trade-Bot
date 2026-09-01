"""Configuration for the EURUSD M5 backtester.

All strategy parameters, cost assumptions and paths are defined here so that the
engine, strategy and reporting code stay decoupled and reusable. Everything is
frozen dataclasses so the results are deterministic for a fixed configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StrategyConfig:
    """Parameters of the existing live strategy, copied 1:1 from bot.py."""

    symbol: str = "EURUSD"
    timeframe: str = "M5"

    ema_fast: int = 50
    ema_slow: int = 200
    rsi_period: int = 14
    atr_period: int = 14

    rsi_buy_min: float = 40.0
    rsi_buy_max: float = 55.0
    rsi_sell_min: float = 45.0
    rsi_sell_max: float = 60.0

    atr_sl_mult: float = 1.5
    atr_tp_mult: float = 3.0

    # Experiment filter (baseline = 0.0, which reproduces bot.py exactly):
    # require normalized EMA separation |EMA50 - EMA200| / ATR to EXCEED this
    # value before a BUY/SELL signal fires. Used only by the controlled
    # separation experiment; bot.py is unchanged.
    ema_sep_min: float = 0.0


@dataclass(frozen=True)
class CostConfig:
    """Trading cost and account assumptions (see README for rationale).

    Prices in the CSV are treated as bid prices. Spread and slippage are applied
    as a round-turn cost in price units. Commission is a fixed USD amount per lot
    (round-turn). Money P&L uses a fixed lot size (the live bot sizes by 1% risk,
    which depends on a live broker balance and is intentionally not replicated).
    """

    starting_balance: float = 10_000.0
    lot_size: float = 0.10
    base_contract: int = 100_000  # 1 standard lot = 100,000 base currency
    commission_per_lot: float = 7.0  # USD, round-turn
    slippage_pips: float = 0.5  # per side

    # EURUSD quoting
    point: float = 0.00001  # minimum price increment
    pip: float = 0.0001  # standard pip

    # Conservative intrabar rule: if a single candle would touch both SL and TP,
    # assume the stop-loss was hit first (worst case, avoids optimistic bias).
    conservative_intrabar: bool = True


@dataclass(frozen=True)
class PathConfig:
    """File locations. All relative to the project root."""

    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_file: Path = field(default_factory=lambda: Path("data/eurusd_m5.csv"))
    output_dir: Path = field(default_factory=lambda: Path("outputs"))

    def __post_init__(self) -> None:
        # Keep the base dir as project root; expand relative children against it.
        object.__setattr__(self, "data_file", self._abs(self.data_file))
        object.__setattr__(self, "output_dir", self._abs(self.output_dir))

    def _abs(self, p: Path) -> Path:
        if not p.is_absolute():
            return self.base_dir / p
        return p
