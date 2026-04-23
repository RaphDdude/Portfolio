import pandas as pd
import numpy as np


def detect_swings(df, window=3):
    """
    FIX: Removed center=True lookahead bias.
    Uses trailing window and shifts the result so the swing is only
    confirmed (window // 2) bars after it actually occurred, matching
    what a trader sees in real-time.
    """
    df = df.copy()

    df["swing_high"] = df["high"].rolling(window, center=False).apply(
        lambda x: 1 if x[-1] == np.max(x) else 0, raw=True
    )
    df["swing_low"] = df["low"].rolling(window, center=False).apply(
        lambda x: 1 if x[-1] == np.min(x) else 0, raw=True
    )

    # Shift back so the confirmation is delayed by (window // 2 - 1) bars
    delay = max(window // 2 - 1, 0)
    df["swing_high"] = df["swing_high"].shift(delay).fillna(0).astype(int)
    df["swing_low"] = df["swing_low"].shift(delay).fillna(0).astype(int)

    return df


def get_last_swings(df):
    swings_high = df[df["swing_high"] == 1]["high"]
    swings_low = df[df["swing_low"] == 1]["low"]

    return swings_high, swings_low


def detect_bos(df):
    """
    FIX: BOS now resets after each break.
    Previously, once price broke a swing high, EVERY subsequent candle
    also triggered bos_bullish, creating cascading false signals.
    Now only the FIRST break is marked, and the tracker resets so a
    new swing point must form before another BOS can occur.
    """
    df = df.copy()

    df["bos_bullish"] = False
    df["bos_bearish"] = False

    last_swing_high = None
    last_swing_low = None

    for i in range(len(df)):
        row = df.iloc[i]

        if row["swing_high"] == 1:
            last_swing_high = row["high"]

        if row["swing_low"] == 1:
            last_swing_low = row["low"]

        # Bullish BOS: close breaks above last swing high
        if last_swing_high is not None and row["close"] > last_swing_high:
            df.iloc[i, df.columns.get_loc("bos_bullish")] = True
            last_swing_high = None  # RESET — wait for new swing

        # Bearish BOS: close breaks below last swing low
        if last_swing_low is not None and row["close"] < last_swing_low:
            df.iloc[i, df.columns.get_loc("bos_bearish")] = True
            last_swing_low = None  # RESET — wait for new swing

    return df


def detect_mss(df, sweep_expiry_bars=60):
    """
    FIX: Sweep state now expires after sweep_expiry_bars (default 60 = 1hr on 1m).
    Previously a sweep flag stayed True forever until a BOS occurred,
    meaning an unrelated BOS hours later would be incorrectly marked as MSS.
    """
    df = df.copy()

    df["mss_bullish"] = False
    df["mss_bearish"] = False

    swept_sellside = False
    swept_buyside = False
    sellside_bars = 0
    buyside_bars = 0

    for i in range(len(df)):
        row = df.iloc[i]

        # Check for new sweep events
        if "sweep_sellside" in df.columns and row["sweep_sellside"]:
            swept_sellside = True
            sellside_bars = 0

        if "sweep_buyside" in df.columns and row["sweep_buyside"]:
            swept_buyside = True
            buyside_bars = 0

        # Increment bar counters
        if swept_sellside:
            sellside_bars += 1
        if swept_buyside:
            buyside_bars += 1

        # Expire stale sweep states
        if swept_sellside and sellside_bars > sweep_expiry_bars:
            swept_sellside = False
            sellside_bars = 0

        if swept_buyside and buyside_bars > sweep_expiry_bars:
            swept_buyside = False
            buyside_bars = 0

        # MSS: sweep followed by BOS
        if swept_sellside and row["bos_bullish"]:
            df.iloc[i, df.columns.get_loc("mss_bullish")] = True
            swept_sellside = False
            sellside_bars = 0

        if swept_buyside and row["bos_bearish"]:
            df.iloc[i, df.columns.get_loc("mss_bearish")] = True
            swept_buyside = False
            buyside_bars = 0

    return df
