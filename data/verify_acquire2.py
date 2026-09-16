import pandas as pd

for sym in ["eurgbp", "eurjpy"]:
    df = pd.read_csv(f"data/poc_test_v2/{sym}_m5.csv")
    print(f"\n{sym.upper()}:")
    print(f"  Bars: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Time is naive UTC: {pd.api.types.is_datetime64_any_dtype(df['time'])}")
    print(f"  Time range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
    print(f"  Monotonic: {df['time'].is_monotonic_increasing}")
    print(f"  Spread==0: {(df['spread'] == 0).sum()} | Spread>0: {(df['spread'] > 0).sum()}")
    print(f"  Spread min/mean/max: {df['spread'].min()}/{df['spread'].mean():.1f}/{df['spread'].max()}")
    print(f"  tick_volume<=0: {(df['tick_volume'] <= 0).sum()}")
    print(f"  real_volume!=0: {(df['real_volume'] != 0).sum()}")
    print(f"  OHLC ok (high>=low & close in range): "
          f"{(df['high'] >= df['low']).all()} / "
          f"{((df['close'] >= df['low']) & (df['close'] <= df['high'])).all()}")
    print(f"  dtypes: {dict(df.dtypes.astype(str))}")