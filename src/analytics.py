import pandas as pd
import numpy as np


def compute_trade_metrics(trades_df, point_value=20.0, contracts=1):
    """
    FIX: PnL now includes dollar conversion and handles TIMEOUT results.
    Uses the actual exit price (eff_sl/eff_tp) when available, falling back
    to the original sl/tp for backward compatibility.
    """
    if trades_df.empty:
        return trades_df

    trades_df = trades_df.copy()

    # Determine effective exit price (prefer eff levels from improved backtester)
    if "exit" in trades_df.columns:
        exit_price = trades_df["exit"]
    else:
        # Backward compat: derive exit from result
        exit_price = np.where(
            trades_df["result"] == "WIN", trades_df["tp"],
            np.where(
                trades_df["result"] == "LOSS", trades_df["sl"],
                trades_df["close"]  # TIMEOUT
            )
        )

    entry = trades_df["entry"]

    # Raw PnL in points
    if "point_value" in trades_df.columns:
        pv = trades_df["point_value"]
    else:
        pv = point_value

    if "contracts" in trades_df.columns:
        con = trades_df["contracts"]
    else:
        con = contracts

    # Direction-aware PnL calculation
    is_long = trades_df["type"] == "LONG"
    is_short = ~is_long

    raw_pnl_points = np.where(
        is_long,
        exit_price - entry,      # LONG: buy low, sell high
        entry - exit_price        # SHORT: sell high, buy low
    )

    trades_df["pnl"] = raw_pnl_points
    trades_df["pnl_dollars"] = raw_pnl_points * pv * con

    # R-multiple: pnl / risk (risk = abs(entry - sl) * point_value * contracts)
    risk = np.abs(trades_df["entry"] - trades_df["sl"]) * pv * con
    trades_df["rr"] = np.where(risk > 0, trades_df["pnl_dollars"] / risk, 0.0)

    return trades_df


def equity_curve(trades_df, initial_equity=10000.0):
    """
    FIX: Equity curve now starts from initial_equity instead of zero.
    Also fixed the empty DataFrame bug that created a row with [].
    """
    if trades_df.empty:
        empty = pd.DataFrame(columns=list(trades_df.columns) + ["equity"])
        return empty

    trades_df = trades_df.copy()
    equity = initial_equity
    curve = []

    for _, t in trades_df.iterrows():
        pnl_dol = t.get("pnl_dollars", t["pnl"] * 20.0)  # fallback
        equity += pnl_dol
        curve.append(equity)

    trades_df["equity"] = curve
    return trades_df


def max_drawdown(equity_series, as_pct=False):
    """
    FIX: Now returns drawdown as a percentage of peak equity (more meaningful).
    Set as_pct=False to get the old absolute value behavior.
    """
    if len(equity_series) == 0:
        return 0.0
    peak = equity_series.cummax()
    drawdown = equity_series - peak
    dd_min = drawdown.min()

    if as_pct:
        # Percentage of peak equity
        peak_at_dd = peak[drawdown.idxmin()]
        if peak_at_dd > 0:
            return (dd_min / peak_at_dd) * 100
        return 0.0
    return dd_min


def performance_report(trades_df, initial_equity=10000.0):
    """
    FIX: Report now includes dollar-based metrics, timeout stats, and
    percentage drawdown alongside absolute drawdown.
    """
    if trades_df.empty:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "expectancy": 0,
            "expectancy_dollars": 0,
            "max_drawdown": 0,
            "max_drawdown_pct": 0,
            "total_pnl_dollars": 0,
            "timeout_count": 0,
        }

    total = len(trades_df)
    wins = len(trades_df[trades_df["result"] == "WIN"])
    timeouts = len(trades_df[trades_df["result"] == "TIMEOUT"])

    win_rate = wins / total if total else 0

    # Use dollar PnL if available, else raw points
    pnl_col = "pnl_dollars" if "pnl_dollars" in trades_df.columns else "pnl"
    gross_profit = trades_df[trades_df[pnl_col] > 0][pnl_col].sum()
    gross_loss = abs(trades_df[trades_df[pnl_col] < 0][pnl_col].sum())

    if gross_loss == 0:
        profit_factor = float('inf') if gross_profit > 0 else 0
    else:
        profit_factor = gross_profit / gross_loss

    expectancy = trades_df[pnl_col].mean()

    # Drawdown (both formats)
    dd_abs = max_drawdown(trades_df["equity"]) if "equity" in trades_df.columns else 0
    dd_pct = max_drawdown(trades_df["equity"], as_pct=True) if "equity" in trades_df.columns else 0

    total_pnl = trades_df[pnl_col].sum()

    return {
        "total_trades": total,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "expectancy_dollars": expectancy if pnl_col == "pnl_dollars" else expectancy * 20.0,
        "max_drawdown": dd_abs,
        "max_drawdown_pct": dd_pct,
        "total_pnl_dollars": total_pnl if pnl_col == "pnl_dollars" else total_pnl * 20.0,
        "timeout_count": timeouts,
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
        "long_count": len(long_trades),
        "short_count": len(short_trades),
        "long_pnl": long_trades["pnl_dollars"].sum() if "pnl_dollars" in long_trades.columns else 0,
        "short_pnl": short_trades["pnl_dollars"].sum() if "pnl_dollars" in short_trades.columns else 0,
    }
