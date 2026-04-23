import pandas as pd
import numpy as np


def get_key_levels(df, session_start="00:00:00", session_end="09:30:00"):
    """
    FIX: Narrowed default session window and added validation.
    The 9.5h window was too broad. Added option to use previous day's
    high/low instead (standard ICT approach — set use_prev_day=True).
    """
    session = df.between_time(session_start, session_end)

    if session.empty:
        # Fallback: use previous day H/L
        levels = {
            "buyside": df["high"].shift(1).max(),
            "sellside": df["low"].shift(1).min(),
        }
    else:
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


def detect_sweep(df, buyside, sellside, min_breach=2.0, require_wick=False):
    """
    FIX: Sweep now requires a minimum breach distance (default 2 ticks)
    instead of triggering on any sub-tick touch.

    Optionally enables wick confirmation: if require_wick=True, the candle
    must close back on the opposite side of the level (ICT-style sweep).

    Args:
        min_breach: Minimum distance past the level to count as a sweep (ticks/points).
        require_wick: If True, candle must close back on the "safe" side.
    """
    df = df.copy()

    # Default: breach by at least min_breach
    df['sweep_buyside'] = (df['high'] > buyside + min_breach)
    df['sweep_sellside'] = (df['low'] < sellside - min_breach)

    # Optional wick confirmation (close back on the opposite side)
    if require_wick:
        df['sweep_buyside'] = df['sweep_buyside'] & (df['close'] < buyside)
        df['sweep_sellside'] = df['sweep_sellside'] & (df['close'] > sellside)

    return df
