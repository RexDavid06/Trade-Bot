import MetaTrader5 as mt5
import pandas as pd
import time
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
RISK_PERCENT = 1

BUY = "BUY"
SELL = "SELL"

last_candle = None


def get_data():
    # start_pos = 0 -> the LAST row is the currently-forming candle (MT5
    # semantics). signal_from_candles() only ever reads the candle BEFORE it
    # (index -2, the last COMPLETED candle), so the forming candle can never
    # influence the emitted signal.
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)
    if rates is None:
        print("Failed to get market data")
        return None

    df = pd.DataFrame(rates)
    print("Data received:", len(df))

    df['ema50'] = EMAIndicator(df['close'], 50).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], 200).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], 14).rsi()
    atr = AverageTrueRange(df['high'], df['low'], df['close'], 14)
    df['atr'] = atr.average_true_range()

    return df


def signal_from_candles(df):
    """Evaluate the V1 rules on the last COMPLETED candle (A3 fix).

    ``df`` may end with a currently-forming candle (MT5 position 0). All signal
    inputs (EMA50, EMA200, RSI, ATR) are read exclusively from ``df.iloc[-2]``,
    the last *closed* candle, never from ``df.iloc[-1]``. This guarantees the
    emitted signal cannot repaint when the forming candle's price changes, and
    makes live decisions comparable to the backtest engine, which signals only
    on closed candles.

    Returns ``(BUY|SELL|None, atr)`` where ``atr`` is the closed candle's ATR
    (used for SL/TP distances). Returns ``(None, None)`` when fewer than two
    bars are available or indicators are not yet valid.
    """
    if df is None or len(df) < 2:
        return None, None

    closed = df.iloc[-2]
    ema50 = closed['ema50']
    ema200 = closed['ema200']
    rsi = closed['rsi']
    atr = closed['atr']

    # Reject until the slow EMA has warmed up (matches backtest._valid()).
    if pd.isna(ema50) or pd.isna(ema200) or pd.isna(rsi) or pd.isna(atr):
        return None, None

    if ema50 > ema200 and 40 < rsi < 55:
        return BUY, float(atr)
    if ema50 < ema200 and 45 < rsi < 60:
        return SELL, float(atr)
    return None, None

def position_exists():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions is not None and len(positions) > 0

def calculate_lot():
    account = mt5.account_info()
    balance = account.balance
    risk = balance * (RISK_PERCENT / 100)
    lot = risk / 1000
    return max(round(lot, 2), 0.01)

def spread_ok():
    tick = mt5.symbol_info_tick(SYMBOL)
    point = mt5.symbol_info(SYMBOL).point
    spread = (tick.ask - tick.bid) / point
    print(f"Spread: {spread:.2f} points")
    return spread < 25

def place_trade(order_type, atr):
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print("No price data")
        return

    lot = calculate_lot()
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    sl_distance = atr * 1.5
    tp_distance = atr * 3

    if order_type == mt5.ORDER_TYPE_BUY:
        sl = price - sl_distance
        tp = price + tp_distance
    else:
        sl = price + sl_distance
        tp = price - tp_distance

    # Use broker-compatible filling mode
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 999,
        "comment": "TREND_PULLBACK_BOT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  # safer default for most brokers
    }

    result = mt5.order_send(request)
    print("Trade result:", result)

def check_signal():
    global last_candle
    print("Bot running...")

    df = get_data()
    if df is None:
        return

    candle_time = df.iloc[-1]['time']
    if candle_time == last_candle:
        print("Waiting for new candle...")
        return
    last_candle = candle_time

    print("New Candle Detected")
    if position_exists():
        print("Position already open")
        return
    if not spread_ok():
        print("Spread too high")
        return

    direction, atr = signal_from_candles(df)
    if direction is None:
        print("No valid closed-candle signal yet")
        return

    last = df.iloc[-2]  # the closed candle the signal was evaluated on
    ema50 = last['ema50']
    ema200 = last['ema200']
    rsi = last['rsi']

    print("EMA50:", ema50)
    print("EMA200:", ema200)
    print("RSI:", rsi)
    print("ATR:", atr)

    if direction == BUY:
        print("BUY SIGNAL")
        place_trade(mt5.ORDER_TYPE_BUY, atr)
    elif direction == SELL:
        print("SELL SIGNAL")
        place_trade(mt5.ORDER_TYPE_SELL, atr)


def main():
    if not mt5.initialize():
        print("MT5 connection failed")
        quit()

    print("Connected to MT5")

    # Ensure symbol is available
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print("Symbol not found")
        quit()

    if not symbol_info.visible:
        mt5.symbol_select(SYMBOL, True)

    try:
        while True:
            check_signal()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Bot stopped manually")
        mt5.shutdown()


if __name__ == "__main__":
    main()