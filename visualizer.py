import matplotlib.pyplot as plt


def plot_trades(df, trades, start=0, end=500):
    subset = df.iloc[start:end]

    plt.figure(figsize=(15, 6))
    plt.plot(subset.index, subset["close"], label="Price")

    for _, trade in trades.iterrows():
        entry_idx = trade["entry_index"]

        if entry_idx < start or entry_idx > end:
            continue

        entry_time = df.index[entry_idx]
        color = "green" if trade["type"] == "LONG" else "red"

        # Entry point
        plt.scatter(entry_time, trade["entry"], color=color)

        # TP / SL lines
        end_idx = min(entry_idx + 20, len(df) - 1)
        plt.hlines(trade["tp"], entry_time, df.index[end_idx], colors="green")
        plt.hlines(trade["sl"], entry_time, df.index[end_idx], colors="red")

    plt.title("Trades Visualization")
    plt.legend()
    plt.show()


def plot_equity(trades_df):
    if trades_df.empty or "equity" not in trades_df.columns:
        print("No equity data to plot")
        return

    plt.figure(figsize=(12, 5))
    plt.plot(trades_df["equity"])
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("PnL")
    plt.show()