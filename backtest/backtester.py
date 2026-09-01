"""Bar-by-bar backtesting engine.

Walk forward through the historical candle series and simulate the strategy:

* Signals are generated on a CLOSED candle (no look-ahead).
* A signal fills at the OPEN of the next candle (realistic execution instead of
  filling inside the signal candle).
* Only one position is open at a time. While a position is open no new signal is
  queued (mirrors bot.py which skips signal checks when position_exists()).
* SL = entry +/- 1.5*ATR and TP = entry +/- 3*ATR are set from the entry price
  using the *entry candle's* ATR (bot.py uses the ATR of the last closed candle
  at the moment of entry).
* SL/TP are resolved against subsequent candles' highs/lows. If a single candle
  would touch both, the conservative rule (SL first) is applied by default.

Costs are applied round-turn per trade (spread from the entry candle + per-side
slippage converted to price, and per-lot commission in money).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import CostConfig, StrategyConfig
from .strategy import BUY, SELL, signal_at


def _cost_price(df: pd.DataFrame, i: int, cfg: CostConfig) -> float:
    """Round-turn cost (spread + both slippage sides) in price units."""
    spread_price = float(df["spread"].iat[i]) * cfg.point
    slippage_price = 2.0 * cfg.slippage_pips * cfg.pip
    return spread_price + slippage_price


@dataclass
class Trade:
    entry_time: object
    exit_time: object
    direction: str
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    atr: float
    result: str
    exit_reason: str
    net_pips: float
    gross_pips: float
    cost_pips: float
    net_money: float
    gross_money: float
    r_multiple: float = 0.0
    signal_rsi: float | None = None
    ema_sep: float | None = None
    mae_pips: float = 0.0
    mae_r: float = 0.0
    mfe_pips: float = 0.0
    signal_close: float | None = None
    signal_range: float | None = None
    signal_ema_fast: float | None = None
    signal_ema_slow: float | None = None

    def to_dict(self) -> dict:
        return {
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "direction": self.direction,
            "entry_price": round(self.entry_price, 5),
            "exit_price": round(self.exit_price, 5),
            "stop_loss": round(self.stop_loss, 5),
            "take_profit": round(self.take_profit, 5),
            "atr": round(self.atr, 5),
            "result": self.result,
            "exit_reason": self.exit_reason,
            "gross_pips": round(self.gross_pips, 1),
            "cost_pips": round(self.cost_pips, 1),
            "net_pips": round(self.net_pips, 1),
            "net_money": round(self.net_money, 2),
            "gross_money": round(self.gross_money, 2),
            "r_multiple": round(self.r_multiple, 3),
            "signal_rsi": None if self.signal_rsi is None else round(self.signal_rsi, 2),
            "ema_sep": None if self.ema_sep is None else round(self.ema_sep, 6),
            "mae_pips": round(self.mae_pips, 1),
            "mae_r": round(self.mae_r, 3),
            "mfe_pips": round(self.mfe_pips, 1),
            "signal_close": None if self.signal_close is None else round(self.signal_close, 5),
            "signal_range": None if self.signal_range is None else round(self.signal_range, 5),
            "signal_ema_fast": None if self.signal_ema_fast is None else round(self.signal_ema_fast, 6),
            "signal_ema_slow": None if self.signal_ema_slow is None else round(self.signal_ema_slow, 6),
        }


@dataclass
class _Position:
    direction: str
    entry_idx: int
    entry_price: float
    stop_loss: float
    take_profit: float
    atr: float
    cost_price: float
    signal_rsi: float | None = None
    signal_ema_fast: float | None = None
    signal_ema_slow: float | None = None
    signal_close: float | None = None
    signal_range: float | None = None
    max_adverse: float = 0.0
    max_favorable: float = 0.0

    def update_excursion(self, high: float, low: float) -> None:
        """Accumulate MAE/MFE (in price units) for an open position on a candle."""
        if self.direction == BUY:
            self.max_adverse = max(self.max_adverse, self.entry_price - low)
            self.max_favorable = max(self.max_favorable, high - self.entry_price)
        else:  # SELL
            self.max_adverse = max(self.max_adverse, high - self.entry_price)
            self.max_favorable = max(self.max_favorable, self.entry_price - low)


def _exit_at_candle(position: _Position, df: pd.DataFrame, i: int, cfg: CostConfig):
    """Return (exit_price, reason) for candle i, or None if no SL/TP touched."""
    high, low = float(df["high"].iat[i]), float(df["low"].iat[i])
    sl, tp = position.stop_loss, position.take_profit

    if position.direction == BUY:
        hit_tp = high >= tp
        hit_sl = low <= sl
    else:  # SELL
        hit_tp = low <= tp
        hit_sl = high >= sl

    if hit_sl and hit_tp:
        # Conservative default: assume the stop-loss was hit first.
        if cfg.conservative_intrabar:
            return sl, "SL"
        return tp, "TP"
    if hit_tp:
        return tp, "TP"
    if hit_sl:
        return sl, "SL"
    return None


def _finalize(
    position: _Position,
    entry_time: object,
    exit_time: object,
    exit_price: float,
    reason: str,
    c_cfg: CostConfig,
) -> Trade:
    entry = position.entry_price
    gross_price = (exit_price - entry) if position.direction == BUY else (entry - exit_price)

    gross_pips = gross_price / c_cfg.pip
    cost_pips = position.cost_price / c_cfg.pip
    net_pips = gross_pips - cost_pips

    notional = c_cfg.lot_size * c_cfg.base_contract
    gross_money = gross_price * notional
    net_money = gross_money - position.cost_price * notional - c_cfg.commission_per_lot * c_cfg.lot_size

    if net_pips > 0:
        result = "WIN"
    elif net_pips < 0:
        result = "LOSS"
    else:
        result = "BE"

    sl_dist_pips = abs(position.entry_price - position.stop_loss) / c_cfg.pip
    r_multiple = net_pips / sl_dist_pips if sl_dist_pips > 0 else 0.0

    mae_pips = position.max_adverse / c_cfg.pip
    mfe_pips = position.max_favorable / c_cfg.pip
    mae_r = position.max_adverse / (sl_dist_pips * c_cfg.pip) if sl_dist_pips > 0 else 0.0

    return Trade(
        entry_time=entry_time,
        exit_time=exit_time,
        direction=position.direction,
        entry_price=entry,
        exit_price=exit_price,
        stop_loss=position.stop_loss,
        take_profit=position.take_profit,
        atr=position.atr,
        result=result,
        exit_reason=reason,
        net_pips=net_pips,
        gross_pips=gross_pips,
        cost_pips=cost_pips,
        net_money=net_money,
        gross_money=gross_money,
        r_multiple=r_multiple,
        signal_rsi=position.signal_rsi,
        ema_sep=(
            position.signal_ema_fast - position.signal_ema_slow
            if position.signal_ema_fast is not None and position.signal_ema_slow is not None
            else None
        ),
        mae_pips=mae_pips,
        mae_r=mae_r,
        mfe_pips=mfe_pips,
        signal_close=position.signal_close,
        signal_range=position.signal_range,
        signal_ema_fast=position.signal_ema_fast,
        signal_ema_slow=position.signal_ema_slow,
    )


def run_backtest(
    df: pd.DataFrame, s_cfg: StrategyConfig, c_cfg: CostConfig
) -> tuple[list[Trade], pd.DataFrame]:
    """Run the strategy over indicator-augmented `df`.

    Returns (trades, equity_frame). `equity_frame` is a DataFrame of
    (time, balance) snapshots: the starting balance then the balance after each
    closed trade.
    """
    n = len(df)
    trades: list[Trade] = []
    balance = c_cfg.starting_balance
    position: _Position | None = None
    pending_sig: str | None = None

    equity_rows = [{"time": df["time"].iat[0], "balance": balance}]

    for i in range(1, n):
        # 1) Open a pending signal at the OPEN of candle i.
        if position is None and pending_sig is not None:
            direction = pending_sig
            entry = float(df["open"].iat[i])
            atr = float(df["atr"].iat[i])
            if direction == BUY:
                sl = entry - s_cfg.atr_sl_mult * atr
                tp = entry + s_cfg.atr_tp_mult * atr
            else:
                sl = entry + s_cfg.atr_sl_mult * atr
                tp = entry - s_cfg.atr_tp_mult * atr
            position = _Position(
                direction=direction,
                entry_idx=i,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                atr=atr,
                cost_price=_cost_price(df, i, c_cfg),
                signal_rsi=float(df["rsi"].iat[i - 1]),
                signal_ema_fast=float(df["ema_fast"].iat[i - 1]),
                signal_ema_slow=float(df["ema_slow"].iat[i - 1]),
                signal_close=float(df["close"].iat[i - 1]),
                signal_range=float(df["high"].iat[i - 1] - df["low"].iat[i - 1]),
            )
            pending_sig = None

        # 2) Manage an open position against candle i.
        if position is not None:
            position.update_excursion(float(df["high"].iat[i]), float(df["low"].iat[i]))
            hit = _exit_at_candle(position, df, i, c_cfg)
            if hit is not None:
                exit_price, reason = hit
                trade = _finalize(
                    position,
                    df["time"].iat[position.entry_idx],
                    df["time"].iat[i],
                    exit_price,
                    reason,
                    c_cfg,
                )
                balance += trade.net_money
                trades.append(trade)
                equity_rows.append({"time": df["time"].iat[i], "balance": balance})
                position = None

        # 3) Generate a signal on the closed candle i for the next bar (only if flat).
        if position is None:
            pending_sig = signal_at(df, i, s_cfg)

    # Close any position still open at the end of the dataset at the last close.
    if position is not None:
        last_idx = n - 1
        exit_price = float(df["close"].iat[last_idx])
        trade = _finalize(
            position,
            df["time"].iat[position.entry_idx],
            df["time"].iat[last_idx],
            exit_price,
            "OPEN",
            c_cfg,
        )
        balance += trade.net_money
        trades.append(trade)
        equity_rows.append({"time": df["time"].iat[last_idx], "balance": balance})
        position = None

    equity = pd.DataFrame(equity_rows)
    return trades, equity
