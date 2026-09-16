import pandas as pd

for sym in ["eurgbp", "eurjpy"]:
    df = pd.read_csv(f"data/poc_test/{sym}_m5.csv")
    print(f"\n{sym.upper()}:")
    print(f"  Bars: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Time range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
    print(f"  Spread > 0: {(df['spread'] > 0).sum()} ({(df['spread'] > 0).mean()*100:.1f}%)")
    print(f"  Spread == 0: {(df['spread'] == 0).sum()}")
    print(
        f"  Spread min: {df['spread'].min()}, mean: {df['spread'].mean():.1f}, max: {df['spread'].max()}"
    )
    print(f"  tick_volume > 0: {(df['tick_volume'] > 0).sum()}")
    print(f"  OHLC valid (high >= low): {(df['high'] >= df['low']).all()}")
    print(f"  Time monotonic: {df['time'].is_monotonic_increasing}")
    print(f"  Dtypes: time={df['time'].dtype}, spread={df['spread'].dtype}")