import pandas as pd


def get_key_levels(df):
    session = df.between_time("00:00:00", "09:30:00")
    levels = {
        "buyside": session["high"].max(),
        "sellside": session["low"].min()
    }
    return levels


def apply_daily_bias(df):
    """Attaches 00:00 and 08:30 opens to the 1m candles"""
    df = df.copy()

    # Ensure we have a date column for grouping
    df['date'] = df.index.date

    # 1. Get 00:00 Open (First candle of the daily session)
    midnight_opens = df.groupby('date')['open'].first().rename('midnight_open')

    # 2. Get 08:30 Open safely using between_time (handles timezones perfectly)
    ny_830_candles = df.between_time("08:30:00", "08:30:00")

    # FALLBACK: If there's no exact 08:30:00 candle, grab 08:29 or 08:31
    if ny_830_candles.empty:
        ny_830_candles = df.between_time("08:29:00", "08:31:00")

    ny_opens = ny_830_candles.groupby(ny_830_candles.index.date)['open'].first().rename('ny_open')

    # 3. Merge them back onto the main dataframe
    df = df.join(midnight_opens, on='date')
    df = df.join(ny_opens, on='date')

    # 4. Forward fill to ensure all candles for that day have the static levels
    df['midnight_open'] = df['midnight_open'].ffill()
    df['ny_open'] = df['ny_open'].ffill()

    # Cleanup
    df.drop('date', axis=1, inplace=True)

    return df


def detect_sweep(df, buyside, sellside):
    df = df.copy()
    df['sweep_buyside'] = df['high'] > buyside
    df['sweep_sellside'] = df['low'] < sellside
    return df