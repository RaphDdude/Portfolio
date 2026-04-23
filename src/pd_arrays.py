import pandas as pd
import numpy as np


def detect_fvg(df):
    """
    FIX: Now stores the actual FVG gap boundary price so strategy.py can
    use the real imbalance zone for entry instead of a candle midpoint.

    - bullish_fvg_top = c1["high"] (the top of the bullish gap)
    - bearish_fvg_bottom = c1["low"] (the bottom of the bearish gap)
    """
    df = df.copy()

    df["bullish_fvg"] = False
    df["bearish_fvg"] = False
    df["bullish_fvg_top"] = np.nan
    df["bearish_fvg_bottom"] = np.nan

    for i in range(2, len(df)):
        c1 = df.iloc[i - 2]
        c2 = df.iloc[i - 1]
        c3 = df.iloc[i]

        # Bullish FVG: candle 3 low > candle 1 high (gap up)
        if c3["low"] > c1["high"]:
            df.iloc[i, df.columns.get_loc("bullish_fvg")] = True
            df.iloc[i, df.columns.get_loc("bullish_fvg_top")] = c1["high"]

        # Bearish FVG: candle 3 high < candle 1 low (gap down)
        if c3["high"] < c1["low"]:
            df.iloc[i, df.columns.get_loc("bearish_fvg")] = True
            df.iloc[i, df.columns.get_loc("bearish_fvg_bottom")] = c1["low"]

    return df


def detect_order_blocks(df, lookback=5):
    """
    FIX: Order block marker is shifted to the NEXT candle (i+1) to remove
    the 1-bar lookahead. Previously, the OB was confirmed by next_c close
    but marked on the current candle, meaning a signal on candle i+1 used
    future information from candle i+1's close. Now the OB fires on i+1
    (the confirmation candle), which is the first bar you can actually
    act on with confirmed knowledge.
    """
    df = df.copy()

    df["bullish_ob"] = False
    df["bearish_ob"] = False

    df["body"] = abs(df["close"] - df["open"])
    avg_body = df["body"].rolling(lookback).mean()

    for i in range(1, len(df) - 1):
        if pd.isna(avg_body.iloc[i]):
            continue

        curr = df.iloc[i]
        next_c = df.iloc[i + 1]

        # Bullish displacement (large bearish candle followed by bullish move)
        if curr["body"] > avg_body.iloc[i]:
            if next_c["close"] > curr["close"]:
                if curr["close"] < curr["open"]:
                    # FIX: Mark on i+1 (the confirmation bar), not i
                    mark_idx = i + 1
                    df.iloc[mark_idx, df.columns.get_loc("bullish_ob")] = True

        # Bearish displacement (large bullish candle followed by bearish move)
        if curr["body"] > avg_body.iloc[i]:
            if next_c["close"] < curr["close"]:
                if curr["close"] > curr["open"]:
                    # FIX: Mark on i+1 (the confirmation bar), not i
                    mark_idx = i + 1
                    df.iloc[mark_idx, df.columns.get_loc("bearish_ob")] = True

    # Cleanup temp column
    df.drop("body", axis=1, inplace=True)

    return df
