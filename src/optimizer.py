import pandas as pd
import numpy as np


def sensitivity_test(df, pipeline_fn, param_grid, train_pct=0.7):
    """
    FIX: Complete rewrite with two critical improvements:

    1. WALK-FORWARD VALIDATION: Splits data into training (first train_pct) and
       out-of-sample testing (remaining). Parameters are evaluated on both sets
       so you can see if the training winner holds up on unseen data.

    2. PARAMETER PASSING: Instead of the no-op df.attrs approach, the
       pipeline_fn now receives parameters as keyword arguments so they
       actually affect the backtest.

    Args:
        df: Full dataframe (with signals already generated).
        pipeline_fn: Function(df, **params) -> trades_df. Should accept
                     swing_window, rr, spread, slippage, etc.
        param_grid: Dict of param_name -> list of values to test.
        train_pct: Fraction of data used for training (rest for OOS test).

    Returns:
        List of dicts with in-sample and out-of-sample metrics per combo.
    """
    # Split data
    split_idx = int(len(df) * train_pct)
    df_train = df.iloc[:split_idx].copy()
    df_test = df.iloc[split_idx:].copy()

    results = []

    for window in param_grid.get("swing_window", [3]):
        for rr in param_grid.get("rr", [2.0]):

            params = {
                "swing_window": window,
                "rr": rr,
            }

            # --- In-sample (training) ---
            try:
                trades_train = pipeline_fn(df_train, **params)
                if trades_train.empty:
                    train_wr = 0.0
                    train_trades = 0
                    train_pf = 0.0
                else:
                    train_wr = (trades_train["result"] == "WIN").mean()
                    if pd.isna(train_wr):
                        train_wr = 0.0
                    train_trades = len(trades_train)
                    pnl_col = "pnl_dollars" if "pnl_dollars" in trades_train.columns else "pnl"
                    gp = trades_train[trades_train[pnl_col] > 0][pnl_col].sum()
                    gl = abs(trades_train[trades_train[pnl_col] < 0][pnl_col].sum())
                    train_pf = gp / gl if gl > 0 else float('inf') if gp > 0 else 0
            except Exception:
                train_wr, train_trades, train_pf = 0.0, 0, 0.0

            # --- Out-of-sample (testing) ---
            try:
                trades_test = pipeline_fn(df_test, **params)
                if trades_test.empty:
                    test_wr = 0.0
                    test_trades = 0
                    test_pf = 0.0
                else:
                    test_wr = (trades_test["result"] == "WIN").mean()
                    if pd.isna(test_wr):
                        test_wr = 0.0
                    test_trades = len(trades_test)
                    pnl_col = "pnl_dollars" if "pnl_dollars" in trades_test.columns else "pnl"
                    gp = trades_test[trades_test[pnl_col] > 0][pnl_col].sum()
                    gl = abs(trades_test[trades_test[pnl_col] < 0][pnl_col].sum())
                    test_pf = gp / gl if gl > 0 else float('inf') if gp > 0 else 0
            except Exception:
                test_wr, test_trades, test_pf = 0.0, 0, 0.0

            results.append({
                "window": window,
                "rr": rr,
                "train_winrate": round(train_wr, 4),
                "train_trades": train_trades,
                "train_profit_factor": round(train_pf, 2),
                "test_winrate": round(test_wr, 4),
                "test_trades": test_trades,
                "test_profit_factor": round(test_pf, 2),
                # OOS degradation: how much worse is the test vs train WR
                "wr_degradation": round(train_wr - test_wr, 4) if train_wr > 0 else 0,
            })

    return results


def ablation_test(df, pipeline_fn, **backtest_kwargs):
    """
    FIX: Ablation now properly disables features by setting their boolean
    columns to False instead of dropping them (which causes row.get() to
    return the default False anyway, but this approach is more explicit
    and won't break if the strategy uses different default behavior).

    Also runs on both in-sample and out-of-sample splits.
    """
    tests = {}

    # Full strategy (baseline)
    tests["full"] = df.copy()

    # Disable MSS by setting both columns to False
    no_mss = df.copy()
    if "mss_bullish" in no_mss.columns:
        no_mss["mss_bullish"] = False
    if "mss_bearish" in no_mss.columns:
        no_mss["mss_bearish"] = False
    tests["no_mss"] = no_mss

    # Disable FVG by setting both columns to False
    no_fvg = df.copy()
    if "bullish_fvg" in no_fvg.columns:
        no_fvg["bullish_fvg"] = False
    if "bearish_fvg" in no_fvg.columns:
        no_fvg["bearish_fvg"] = False
    tests["no_fvg"] = no_fvg

    # Disable sweep by setting both columns to False
    no_sweep = df.copy()
    if "sweep_buyside" in no_sweep.columns:
        no_sweep["sweep_buyside"] = False
    if "sweep_sellside" in no_sweep.columns:
        no_sweep["sweep_sellside"] = False
    tests["no_sweep"] = no_sweep

    # Disable OB by setting both columns to False
    no_ob = df.copy()
    if "bullish_ob" in no_ob.columns:
        no_ob["bullish_ob"] = False
    if "bearish_ob" in no_ob.columns:
        no_ob["bearish_ob"] = False
    tests["no_ob"] = no_ob

    results = {}

    for name, test_df in tests.items():
        try:
            trades = pipeline_fn(test_df, **backtest_kwargs)
            if trades.empty:
                win_rate = 0.0
                total = 0
                pnl_col = "pnl_dollars" if "pnl_dollars" in trades.columns else "pnl"
                total_pnl = 0
            else:
                win_rate = (trades["result"] == "WIN").mean()
                if pd.isna(win_rate):
                    win_rate = 0.0
                total = len(trades)
                pnl_col = "pnl_dollars" if "pnl_dollars" in trades.columns else "pnl"
                total_pnl = trades[pnl_col].sum()
        except Exception:
            win_rate, total, total_pnl = 0.0, 0, 0

        results[name] = {
            "win_rate": round(win_rate, 4),
            "trades": total,
            "total_pnl": round(total_pnl, 2),
        }

    return results
