import numpy as np
import pandas as pd

def generate_signals(df):
    df = df.copy()

    df["signal"] = None
    df["entry"] = np.nan
    df["sl"] = np.nan
    df["tp"] = np.nan

    for i in range(len(df)):
        row = df.iloc[i]

        # Grab daily levels safely (returns None if column doesn't exist or is NaN)
        mid_open = row.get("midnight_open")
        ny_open = row.get("ny_open")

        # Calculate if we are in Premium or Discount
        # (If ny_open is NaN, default to False so we don't accidentally take bad trades)
        is_premium = (pd.notna(mid_open) and pd.notna(ny_open) and
                      row["close"] > mid_open and row["close"] > ny_open)

        is_discount = (pd.notna(mid_open) and pd.notna(ny_open) and
                       row["close"] < mid_open and row["close"] < ny_open)

        # -------------------------
        # SHORT SETUP (Premium Bias)
        # -------------------------
        if (
                is_premium  # <-- NEW CONFLUENCE
                and row.get("sweep_buyside", False)
                and row.get("mss_bearish", False)
                and (row.get("bearish_fvg", False) or row.get("bearish_ob", False))
        ):
            entry = calculate_fvg_entry(row)
            if entry is None:
                entry = row["close"]

            sl = row["high"] + 5
            tp = entry - (sl - entry) * 2

            df.at[i, "signal"] = "SHORT"
            df.iloc[i, df.columns.get_loc("entry")] = entry
            df.iloc[i, df.columns.get_loc("sl")] = sl
            df.iloc[i, df.columns.get_loc("tp")] = tp

        # -------------------------
        # LONG SETUP (Discount Bias)
        # -------------------------
        elif (
                is_discount  # <-- NEW CONFLUENCE
                and row.get("sweep_sellside", False)
                and row.get("mss_bullish", False)
                and (row.get("bullish_fvg", False) or row.get("bullish_ob", False))
        ):
            entry = calculate_fvg_entry(row)
            if entry is None:
                entry = row["close"]

            sl = entry - 5
            tp = entry + (entry - sl) * 2

            df.at[i, "signal"] = "LONG"
            df.iloc[i, df.columns.get_loc("entry")] = entry
            df.iloc[i, df.columns.get_loc("sl")] = sl
            df.iloc[i, df.columns.get_loc("tp")] = tp

    return df


def calculate_fvg_entry(row):
    if row.get("bullish_fvg", False) or row.get("bullish_ob", False):
        return (row["high"] + row["low"]) / 2
    if row.get("bearish_fvg", False) or row.get("bearish_ob", False):
        return (row["high"] + row["low"]) / 2
    return None
