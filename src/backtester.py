import pandas as pd
import numpy as np


def backtest(
    df,
    spread=1.5,
    slippage=0.5,
    point_value=20.0,
    contracts=1,
    initial_equity=10000.0,
    max_bars=60,
    max_trades_per_day=3,
):
    """
    Improved backtester with:
      - Open-price SL/TP priority heuristic
      - Spread + slippage modelling
      - Time-based trade timeout
      - Position sizing (fixed contracts)
      - Daily trade limit
    """
    trades = []
    in_trade = False
    trade = {}
    bars_in_trade = 0
    daily_trade_count = 0
    last_trade_date = None

    cost_per_side = spread + slippage

    for i in range(len(df)):
        row = df.iloc[i]

        # Track daily trade count
        current_date = row.name.date() if hasattr(row.name, "date") else str(i)
        if last_trade_date != current_date:
            daily_trade_count = 0
            last_trade_date = current_date

        # -------------------------
        # ENTRY LOGIC
        # -------------------------
        if not in_trade and row.get("signal") in ["LONG", "SHORT"]:
            if daily_trade_count >= max_trades_per_day:
                continue

            in_trade = True
            bars_in_trade = 0

            entry = row["entry"]
            sl = row["sl"]
            tp = row["tp"]

            # Apply spread/slippage to effective levels
            if row["signal"] == "LONG":
                eff_sl = sl - cost_per_side
                eff_tp = tp - cost_per_side
            else:  # SHORT
                eff_sl = sl + cost_per_side
                eff_tp = tp + cost_per_side

            trade = {
                "type": row["signal"],
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "eff_sl": eff_sl,
                "eff_tp": eff_tp,
                "entry_index": i,
                "point_value": point_value,
                "contracts": contracts,
            }
            continue

        # -------------------------
        # TRADE MANAGEMENT
        # -------------------------
        if in_trade:
            bars_in_trade += 1
            high = row["high"]
            low = row["low"]
            open_price = row["open"]

            eff_sl = trade["eff_sl"]
            eff_tp = trade["eff_tp"]

            # ---- Trade timeout check ----
            if bars_in_trade >= max_bars:
                trade["exit"] = row["close"]
                trade["result"] = "TIMEOUT"
                trade["bars_held"] = bars_in_trade
                trades.append(trade.copy())
                in_trade = False
                daily_trade_count += 1
                continue

            # ---- LONG TRADE ----
            if trade["type"] == "LONG":
                sl_hit = low <= eff_sl
                tp_hit = high >= eff_tp

                if sl_hit and tp_hit:
                    # Both in range: use open-price heuristic
                    if open_price >= trade["entry"]:
                        # Open above entry -> bullish, assume TP hit first
                        trade["exit"] = eff_tp
                        trade["result"] = "WIN"
                    else:
                        # Open below entry -> bearish, assume SL hit first
                        trade["exit"] = eff_sl
                        trade["result"] = "LOSS"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

                elif sl_hit:
                    trade["exit"] = eff_sl
                    trade["result"] = "LOSS"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

                elif tp_hit:
                    trade["exit"] = eff_tp
                    trade["result"] = "WIN"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

            # ---- SHORT TRADE ----
            elif trade["type"] == "SHORT":
                sl_hit = high >= eff_sl
                tp_hit = low <= eff_tp

                if sl_hit and tp_hit:
                    # Both in range: use open-price heuristic
                    if open_price <= trade["entry"]:
                        # Open below entry -> bearish, assume TP hit first
                        trade["exit"] = eff_tp
                        trade["result"] = "WIN"
                    else:
                        # Open above entry -> bullish, assume SL hit first
                        trade["exit"] = eff_sl
                        trade["result"] = "LOSS"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

                elif sl_hit:
                    trade["exit"] = eff_sl
                    trade["result"] = "LOSS"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

                elif tp_hit:
                    trade["exit"] = eff_tp
                    trade["result"] = "WIN"
                    trade["bars_held"] = bars_in_trade
                    trades.append(trade.copy())
                    in_trade = False
                    daily_trade_count += 1

    if not trades:
        return pd.DataFrame(
            columns=[
                "type", "entry", "sl", "tp", "exit", "result",
                "entry_index", "bars_held", "point_value", "contracts",
            ]
        )

    return pd.DataFrame(trades)
