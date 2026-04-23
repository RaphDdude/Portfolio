import numpy as np
import pandas as pd
from datetime import time


# ICT trading windows (EST) — only trade during these sessions
TRADING_WINDOWS = [
    (time(2, 0), time(5, 0)),      # London session
    (time(8, 0), time(11, 0)),     # NY morning session
    (time(12, 30), time(14, 30)),  # NY afternoon
]


def _in_trading_window(dt_index_value):
    """Check if the current bar falls within a valid ICT trading window."""
    if not hasattr(dt_index_value, "time"):
        return True  # Skip filter if index is not datetime
    t = dt_index_value.time()
    return any(start <= t <= end for start, end in TRADING_WINDOWS)


def _premium_discount(close, mid_open, ny_open, threshold_pct=0.001):
    """
    FIX: Added equilibrium zone.
    If close is within threshold_pct of the midpoint between mid_open and ny_open,
    it's considered NEUTRAL (no bias). This prevents low-conviction signals
    when price is hovering around fair value.
    """
    if pd.isna(mid_open) or pd.isna(ny_open):
        return False, False

    midpoint = (mid_open + ny_open) / 2
    range_size = abs(ny_open - mid_open)
    # If range is tiny, use a fixed threshold to avoid division issues
    zone = max(range_size * threshold_pct, 0.5)

    if close > midpoint + zone:
        return True, False  # Premium
    elif close < midpoint - zone:
        return False, True  # Discount
    return False, False  # Neutral


def generate_signals(df, atr_col="atr"):
    """
    FIX: Complete rewrite with:
      - Session/time-of-day filter
      - Equilibrium zone for premium/discount
      - Dynamic SL based on structure (sweep candle extreme) + ATR buffer
      - FVG entry uses stored gap boundaries instead of candle midpoint
    """
    df = df.copy()

    df["signal"] = None
    df["entry"] = np.nan
    df["sl"] = np.nan
    df["tp"] = np.nan

    for i in range(len(df)):
        row = df.iloc[i]

        # ---- TIME-OF-DAY FILTER ----
        if not _in_trading_window(df.index[i]):
            continue

        # Grab daily levels
        mid_open = row.get("midnight_open")
        ny_open = row.get("ny_open")

        # ---- PREMIUM / DISCOUNT (with equilibrium zone) ----
        is_premium, is_discount = _premium_discount(
            row["close"], mid_open, ny_open
        )

        # Dynamic ATR-based buffer for SL
        atr_val = row.get(atr_col, 5.0)
        if pd.isna(atr_val):
            atr_val = 5.0
        sl_buffer = max(atr_val * 0.3, 2.0)  # min 2 ticks

        # -------------------------
        # SHORT SETUP (Premium Bias)
        # -------------------------
        if (
                is_premium
                and row.get("sweep_buyside", False)
                and row.get("mss_bearish", False)
                and (row.get("bearish_fvg", False) or row.get("bearish_ob", False))
        ):
            entry = calculate_fvg_entry(row)
            if entry is None:
                entry = row["close"]

            # FIX: Dynamic SL — beyond sweep candle high + ATR buffer
            sl = row["high"] + sl_buffer
            tp = entry - (sl - entry) * 2

            df.at[i, "signal"] = "SHORT"
            df.iloc[i, df.columns.get_loc("entry")] = entry
            df.iloc[i, df.columns.get_loc("sl")] = sl
            df.iloc[i, df.columns.get_loc("tp")] = tp

        # -------------------------
        # LONG SETUP (Discount Bias)
        # -------------------------
        elif (
                is_discount
                and row.get("sweep_sellside", False)
                and row.get("mss_bullish", False)
                and (row.get("bullish_fvg", False) or row.get("bullish_ob", False))
        ):
            entry = calculate_fvg_entry(row)
            if entry is None:
                entry = row["close"]

            # FIX: Dynamic SL — below sweep candle low - ATR buffer
            sl = row["low"] - sl_buffer
            tp = entry + (entry - sl) * 2

            df.at[i, "signal"] = "LONG"
            df.iloc[i, df.columns.get_loc("entry")] = entry
            df.iloc[i, df.columns.get_loc("sl")] = sl
            df.iloc[i, df.columns.get_loc("tp")] = tp

    return df


def calculate_fvg_entry(row):
    """
    FIX: Now uses the stored FVG gap boundaries (bearish_fvg_bottom / bullish_fvg_top)
    instead of the meaningless candle midpoint. Falls back to candle midpoint only
    if the boundary columns don't exist yet (backward compatibility).
    """
    # Prefer stored FVG boundary columns
    bearish_boundary = row.get("bearish_fvg_bottom")
    bullish_boundary = row.get("bullish_fvg_top")

    # Use boundary if available and valid
    if pd.notna(bearish_boundary):
        return bearish_boundary
    if pd.notna(bullish_boundary):
        return bullish_boundary

    # Fallback: check boolean flags + use candle midpoint (backward compat)
    if row.get("bullish_fvg", False) or row.get("bullish_ob", False):
        return (row["high"] + row["low"]) / 2
    if row.get("bearish_fvg", False) or row.get("bearish_ob", False):
        return (row["high"] + row["low"]) / 2

    return None