import MetaTrader5 as mt5
import pandas as pd
import os
from datetime import datetime

SYMBOLS = ["EURUSD", "EURGBP", "EURJPY", "GBPUSD"]
TIMEFRAME = mt5.TIMEFRAME_M5
MAX_BARS = 1000000
FALLBACK_SIZES = [500000, 200000, 100000, 90000, 50000, 10000, 1000]
DATA_DIR = "data"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def export_symbol(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"[{symbol}] Symbol not found in MT5")
        return False

    print(f"[{symbol}] Name: {info.name}, Spread: {info.spread}")

    rates = None
    bars_used = MAX_BARS

    for attempt_size in [MAX_BARS] + FALLBACK_SIZES:
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, attempt_size)
        if rates is not None and len(rates) > 0:
            bars_used = attempt_size
            break
        print(f"[{symbol}] Failed to copy {attempt_size} bars, trying smaller...")

    if rates is None or len(rates) == 0:
        print(f"[{symbol}] No data retrieved")
        return False

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df[["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]]

    filepath = os.path.join(DATA_DIR, f"{symbol.lower()}_m5.csv")
    df.to_csv(filepath, index=False)

    print(f"[{symbol}] Exported {len(df)} bars")
    print(f"[{symbol}] First: {df['time'].iloc[0]}")
    print(f"[{symbol}] Last:  {df['time'].iloc[-1]}")
    print(f"[{symbol}] Saved to: {filepath}")

    return True


def main():
    ensure_data_dir()

    if not mt5.initialize():
        print(f"MT5 init failed: {mt5.last_error()}")
        return

    print(f"MT5 initialized: {mt5.version()}")
    print(f"Symbols to export: {SYMBOLS}")
    print("-" * 50)

    exported = []
    failed = []

    for symbol in SYMBOLS:
        try:
            if export_symbol(symbol):
                exported.append(symbol)
            else:
                failed.append(symbol)
        except Exception as e:
            print(f"[{symbol}] Error: {e}")
            failed.append(symbol)
        print("-" * 50)

    mt5.shutdown()

    print("EXPORT SUMMARY")
    print(f"  Total: {len(SYMBOLS)}")
    print(f"  Exported: {len(exported)} -> {exported}")
    if failed:
        print(f"  Failed: {len(failed)} -> {failed}")
    else:
        print("  All symbols exported successfully")


if __name__ == "__main__":
    main()
