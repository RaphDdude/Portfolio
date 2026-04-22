import pandas as pd


def detect_fvg(df):
    df = df.copy()

    df["bullish_fvg"] = False
    df["bearish_fvg"] = False

    for i in range(2, len(df)):
        c1 = df.iloc[i - 2]
        c2 = df.iloc[i - 1]
        c3 = df.iloc[i]

        # Bullish FVG
        if c3["low"] > c1["high"]:
            df.iloc[i, df.columns.get_loc("bullish_fvg")] = True

        # Bearish FVG
        if c3["high"] < c1["low"]:
            df.iloc[i, df.columns.get_loc("bearish_fvg")] = True

    return df


def detect_order_blocks(df, lookback=5):
    df = df.copy()

    df["bullish_ob"] = False
    df["bearish_ob"] = False

    df["body"] = abs(df["close"] - df["open"])
    avg_body = df["body"].rolling(lookback).mean()

    for i in range(1, len(df) - 1):
        if pd.isna(avg_body.iloc[i]):
            continue

        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        next_c = df.iloc[i + 1]

        # Bullish displacement (bearish candle followed by bullish move)
        if curr["body"] > avg_body.iloc[i]:
            if next_c["close"] > curr["close"]:
                if curr["close"] < curr["open"]:
                    df.iloc[i, df.columns.get_loc("bullish_ob")] = True

        # Bearish displacement (bullish candle followed by bearish move)
        if curr["body"] > avg_body.iloc[i]:
            if next_c["close"] < curr["close"]:
                if curr["close"] > curr["open"]:
                    df.iloc[i, df.columns.get_loc("bearish_ob")] = True

    # Cleanup temp column
    df.drop("body", axis=1, inplace=True)

    return df