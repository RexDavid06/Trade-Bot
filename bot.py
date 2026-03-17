import MetaTrader5 as mt5
import pandas as pd
import time
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
RISK_PERCENT = 1

last_candle = None

# CONNECT TO MT5
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

def get_data():
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

    last = df.iloc[-1]
    ema50 = last['ema50']
    ema200 = last['ema200']
    rsi = last['rsi']
    atr = last['atr']

    print("EMA50:", ema50)
    print("EMA200:", ema200)
    print("RSI:", rsi)
    print("ATR:", atr)

    if ema50 > ema200 and 40 < rsi < 55:
        print("BUY SIGNAL")
        place_trade(mt5.ORDER_TYPE_BUY, atr)
    elif ema50 < ema200 and 45 < rsi < 60:
        print("SELL SIGNAL")
        place_trade(mt5.ORDER_TYPE_SELL, atr)
    else:
        print("No trade signal")

try:
    while True:
        check_signal()
        time.sleep(10)
except KeyboardInterrupt:
    print("Bot stopped manually")
    mt5.shutdown()