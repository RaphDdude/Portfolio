import pandas as pd


def load_data(filepath, timezone="America/New_York"):
    """
    FIX: Added explicit timezone handling.

    Many data sources (e.g., TradingView, NinjaTrader) export timestamps in UTC.
    Without converting to Eastern Time, the 08:30 NY open filter and session
    windows in strategy.py would be off by 4-5 hours depending on DST.

    Args:
        filepath: Path to CSV file.
        timezone: Target timezone (default EST for US futures).
    """
    df = pd.read_csv(filepath)

    # Standardize columns
    df.columns = [col.lower() for col in df.columns]

    # Convert datetime - handle both 'time' and 'datetime' column names
    time_col = 'datetime' if 'datetime' in df.columns else 'time'
    df['datetime'] = pd.to_datetime(df[time_col])

    # Set index
    df.set_index('datetime', inplace=True)

    # FIX: Timezone handling
    # Step 1: Check if the index already has timezone info
    if df.index.tz is None:
        # Assume UTC if no timezone info, then convert to target
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(timezone)

    # Select and validate columns
    available_cols = [c for c in ['open', 'high', 'low', 'close', 'vwap'] if c in df.columns]
    df = df[available_cols]

    # Drop any rows with NaN OHLC
    df = df.dropna(subset=['open', 'high', 'low', 'close'])

    # Sort by time (safety)
    df = df.sort_index()

    return df
