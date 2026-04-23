import pandas as pd
import numpy as np


def detect_swings(df, window=3):
    df = df.copy()

    df["swing_high"] = df["high"].rolling(window, center=True).apply(
        lambda x: 1 if x[window // 2] == np.max(x) else 0, raw=True
    )

    df["swing_low"] = df["low"].rolling(window, center=True).apply(
        lambda x: 1 if x[window // 2] == np.min(x) else 0, raw=True
    )

    return df


def get_last_swings(df):
    swings_high = df[df["swing_high"] == 1]["high"]
    swings_low = df[df["swing_low"] == 1]["low"]

    return swings_high, swings_low


def detect_bos(df):
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

        if last_swing_high is not None and row["close"] > last_swing_high:
            df.iloc[i, df.columns.get_loc("bos_bullish")] = True

        if last_swing_low is not None and row["close"] < last_swing_low:
            df.iloc[i, df.columns.get_loc("bos_bearish")] = True

    return df


def detect_mss(df):
    df = df.copy()

    df["mss_bullish"] = False
    df["mss_bearish"] = False

    swept_sellside = False
    swept_buyside = False

    for i in range(len(df)):
        row = df.iloc[i]

        if "sweep_sellside" in df.columns and row["sweep_sellside"]:
            swept_sellside = True

        if "sweep_buyside" in df.columns and row["sweep_buyside"]:
            swept_buyside = True

        if swept_sellside and row["bos_bullish"]:
            df.iloc[i, df.columns.get_loc("mss_bullish")] = True
            swept_sellside = False

        if swept_buyside and row["bos_bearish"]:
            df.iloc[i, df.columns.get_loc("mss_bearish")] = True
            swept_buyside = False

    return df