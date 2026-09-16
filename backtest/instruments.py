"""
Centralized instrument configuration for all supported symbols.

This module replaces the hardcoded ``pip = 0.0001`` values scattered across
``config.py`` and other modules, providing a single source of truth for
per-symbol trading parameters such as pip size, point value, price digits,
and contract size.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentConfig:
    """Immutable configuration for a single tradable instrument.

    Attributes:
        symbol: The trading symbol, e.g. ``"EURUSD"``.
        pip: The size of one pip in price units (e.g. 0.0001 for a 5-digit
            pair, 0.01 for a 3-digit JPY pair).
        point: The smallest price increment, i.e. one ``1/pow(10, digits)``.
            Typically pip / 10 for 5-digit pairs.
        price_digits: Number of decimal places used for price quotes.
        contract_size: Units of base currency per one standard lot.
        spread_interpretation: How the broker reports the spread column.
            ``"points"`` means the value is in points (multiply by ``point``
            to get price units). ``"pips"`` means the value is already in
            pips.
        description: Human-readable name, e.g. ``"Euro / US Dollar"``.
    """

    symbol: str
    pip: float
    point: float
    price_digits: int
    contract_size: int
    spread_interpretation: str
    description: str


INSTRUMENTS: dict[str, InstrumentConfig] = {
    "EURUSD": InstrumentConfig(
        symbol="EURUSD",
        pip=0.0001,
        point=0.00001,
        price_digits=5,
        contract_size=100_000,
        spread_interpretation="points",
        description="Euro / US Dollar",
    ),
    "EURGBP": InstrumentConfig(
        symbol="EURGBP",
        pip=0.0001,
        point=0.00001,
        price_digits=5,
        contract_size=100_000,
        spread_interpretation="points",
        description="Euro / British Pound",
    ),
    "EURJPY": InstrumentConfig(
        symbol="EURJPY",
        pip=0.01,
        point=0.001,
        price_digits=3,
        contract_size=100_000,
        spread_interpretation="points",
        description="Euro / Japanese Yen",
    ),
    "GBPUSD": InstrumentConfig(
        symbol="GBPUSD",
        pip=0.0001,
        point=0.00001,
        price_digits=5,
        contract_size=100_000,
        spread_interpretation="points",
        description="British Pound / US Dollar",
    ),
}


def get_instrument(symbol: str) -> InstrumentConfig:
    """Return the :class:`InstrumentConfig` for *symbol* (case-insensitive).

    Raises:
        KeyError: If the symbol is not found in the registry.
    """
    key = symbol.upper()
    return INSTRUMENTS[key]


def price_to_pips(price_diff: float, instrument: InstrumentConfig) -> float:
    """Convert a raw price difference to pips for the given instrument.

    For example, a ``price_diff`` of ``0.0054`` on EURUSD (pip = 0.0001)
    yields ``54.0`` pips.
    """
    return price_diff / instrument.pip


def pips_to_price(pips: float, instrument: InstrumentConfig) -> float:
    """Convert a pip count to a raw price difference for the given instrument.

    For example, ``72.5`` pips on EURJPY (pip = 0.01) yields ``0.725``.
    """
    return pips * instrument.pip


def spread_cost_points(
    spread_column_value: float, instrument: InstrumentConfig
) -> float:
    """Convert the broker's spread column value to a price-unit cost.

    If the instrument's ``spread_interpretation`` is ``"points"``, the raw
    column value is multiplied by the instrument's ``point`` size.  If it is
    ``"pips"``, the value is multiplied by the instrument's ``pip`` size
    instead.
    """
    if instrument.spread_interpretation == "pips":
        return spread_column_value * instrument.pip
    return spread_column_value * instrument.point
