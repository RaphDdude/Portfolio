import pandas as pd
import numpy as np


def compute_trade_metrics(trades_df):
    # FIXED: Check for empty DataFrame
    if trades_df.empty:
        return trades_df

    trades_df = trades_df.copy()

    trades_df["pnl"] = np.where(
        trades_df["result"] == "WIN",
        abs(trades_df["tp"] - trades_df["entry"]),
        -abs(trades_df["entry"] - trades_df["sl"])
    )

    trades_df["rr"] = trades_df["pnl"] / abs(trades_df["entry"] - trades_df["sl"])

    return trades_df


def equity_curve(trades_df):
    if trades_df.empty:
        trades_df = trades_df.copy()
        trades_df["equity"] = []
        return trades_df

    trades_df = trades_df.copy()
    equity = 0
    curve = []

    for _, t in trades_df.iterrows():
        equity += t["pnl"]
        curve.append(equity)

    trades_df["equity"] = curve
    return trades_df


def max_drawdown(equity_series):
    if len(equity_series) == 0:
        return 0
    peak = equity_series.cummax()
    drawdown = equity_series - peak
    return drawdown.min()


def performance_report(trades_df):
    if trades_df.empty:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "expectancy": 0,
            "max_drawdown": 0
        }

    total = len(trades_df)
    wins = len(trades_df[trades_df["result"] == "WIN"])

    win_rate = wins / total if total else 0

    # FIXED: Proper profit_factor calculation
    gross_profit = trades_df[trades_df["pnl"] > 0]["pnl"].sum()
    gross_loss = abs(trades_df[trades_df["pnl"] < 0]["pnl"].sum())

    if gross_loss == 0:
        profit_factor = float('inf') if gross_profit > 0 else 0
    else:
        profit_factor = gross_profit / gross_loss

    expectancy = trades_df["pnl"].mean()

    return {
        "total_trades": total,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "max_drawdown": max_drawdown(trades_df["equity"])
    }


def sweep_analysis(trades_df):
    if trades_df.empty or "type" not in trades_df.columns:
        return None

    long_trades = trades_df[trades_df["type"] == "LONG"]
    short_trades = trades_df[trades_df["type"] == "SHORT"]

    return {
        "long_winrate": len(long_trades[long_trades["result"] == "WIN"]) / len(long_trades) if len(long_trades) else 0,
        "short_winrate": len(short_trades[short_trades["result"] == "WIN"]) / len(short_trades) if len(
            short_trades) else 0,
    }