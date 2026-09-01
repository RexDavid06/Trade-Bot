import MetaTrader5 as mt5
import pandas as pd

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
OUT = "data/eurusd_m5.csv"
MAX_BARS = 1000000

if not mt5.initialize():
    print("MT5 connection failed")
    quit()

print("Connected to MT5")

symbol_info = mt5.symbol_info(SYMBOL)
if symbol_info is None:
    print("Symbol not found")
    mt5.shutdown()
    quit()

if not symbol_info.visible:
    mt5.symbol_select(SYMBOL, True)

rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, MAX_BARS)
if rates is None or len(rates) < MAX_BARS:
    # The MT5 API caps a single copy_rates_from_pos call; retry with a
    # smaller request so the maximum available history is still fetched.
    for size in (500000, 200000, 100000, 90000, 50000, 10000, 1000):
        rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, size)
        if rates is not None and len(rates) == size:
            break
if rates is None:
    print("Failed to get market data")
    mt5.shutdown()
    quit()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']]
df.to_csv(OUT, index=False)

print("Bars written:", len(df))
print("First:", df['time'].iloc[0])
print("Last:", df['time'].iloc[-1])
print("Saved to", OUT)

mt5.shutdown()
