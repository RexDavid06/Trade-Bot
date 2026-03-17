import MetaTrader5 as mt5
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import time

SYMBOL = "EURUSD"
LOT = 0.01
TIMEFRAME = mt5.TIMEFRAME_M5

# connect to MT5
if not mt5.initialize():
    print("MT5 Initialization Failed")
    quit()

print("Connected to MT5")

def get_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)
    df = pd.DataFrame(rates)

    df['sma_fast'] = SMAIndicator(df['close'], window=50).sma_indicator()
    df['sma_slow'] = SMAIndicator(df['close'], window=200).sma_indicator()
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()

    return df


def place_trade(order_type):

    price = mt5.symbol_info_tick(SYMBOL).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT,
        "type": order_type,
        "price": price,
        "sl": price - 0.005 if order_type == mt5.ORDER_TYPE_BUY else price + 0.005,
        "tp": price + 0.010 if order_type == mt5.ORDER_TYPE_BUY else price - 0.010,
        "deviation": 20,
        "magic": 100,
        "comment": "MA_RSI_BOT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    print(result)


def check_signal():
    df = get_data()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # BUY SIGNAL
    if prev.sma_fast < prev.sma_slow and last.sma_fast > last.sma_slow and last.rsi < 70:
        print("BUY SIGNAL")
        place_trade(mt5.ORDER_TYPE_BUY)

    # SELL SIGNAL
    elif prev.sma_fast > prev.sma_slow and last.sma_fast < last.sma_slow and last.rsi > 30:
        print("SELL SIGNAL")
        place_trade(mt5.ORDER_TYPE_SELL)


while True:
    check_signal()
    time.sleep(60)