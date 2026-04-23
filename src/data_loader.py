import pandas as pd


def load_data(filepath):
    # FIXED: Use the filepath parameter instead of hardcoding
    df = pd.read_csv(filepath)

    # Standardize columns
    df.columns = [col.lower() for col in df.columns]

    # Convert datetime - handle both 'time' and 'datetime' column names
    time_col = 'datetime' if 'datetime' in df.columns else 'time'
    df['datetime'] = pd.to_datetime(df[time_col])

    # Set index
    df.set_index('datetime', inplace=True)

    # Select and validate columns
    available_cols = [c for c in ['open', 'high', 'low', 'close', 'vwap'] if c in df.columns]
    df = df[available_cols]

    return df