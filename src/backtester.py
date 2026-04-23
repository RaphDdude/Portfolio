import pandas as pd


def backtest(df):
    trades = []
    in_trade = False
    trade = {}

    for i in range(len(df)):
        row = df.iloc[i]

        # -------------------------
        # ENTRY LOGIC
        # -------------------------
        if not in_trade and row.get("signal") in ["LONG", "SHORT"]:
            in_trade = True
            trade = {
                "type": row["signal"],
                "entry": row["entry"],
                "sl": row["sl"],
                "tp": row["tp"],
                "entry_index": i
            }
            continue  # FIXED: Skip exit check on entry candle

        # -------------------------
        # TRADE MANAGEMENT
        # -------------------------
        if in_trade:
            high = row["high"]
            low = row["low"]

            # LONG TRADE
            if trade["type"] == "LONG":
                if low <= trade["sl"]:
                    trade["exit"] = trade["sl"]
                    trade["result"] = "LOSS"
                    trades.append(trade.copy())
                    in_trade = False
                elif high >= trade["tp"]:
                    trade["exit"] = trade["tp"]
                    trade["result"] = "WIN"
                    trades.append(trade.copy())
                    in_trade = False

            # FIXED: Changed to elif
            elif trade["type"] == "SHORT":
                if high >= trade["sl"]:
                    trade["exit"] = trade["sl"]
                    trade["result"] = "LOSS"
                    trades.append(trade.copy())
                    in_trade = False
                elif low <= trade["tp"]:
                    trade["exit"] = trade["tp"]
                    trade["result"] = "WIN"
                    trades.append(trade.copy())
                    in_trade = False

    # FIXED: Handle empty trades case
    if not trades:
        return pd.DataFrame(columns=["type", "entry", "sl", "tp", "exit", "result", "entry_index"])

    return pd.DataFrame(trades)