import pandas as pd


def sensitivity_test(df, backtest_fn, param_grid):
    results = []

    for window in param_grid["swing_window"]:
        for rr in param_grid["rr"]:
            df_copy = df.copy()
            df_copy.attrs["swing_window"] = window
            df_copy.attrs["rr"] = rr

            trades = backtest_fn(df_copy)

            # FIXED: Handle empty trades
            if trades.empty:
                win_rate = 0.0
            else:
                win_rate = (trades["result"] == "WIN").mean()
                if pd.isna(win_rate):
                    win_rate = 0.0

            results.append({
                "window": window,
                "rr": rr,
                "win_rate": win_rate,
                "total_trades": len(trades)
            })

    return results


def ablation_test(df, backtest_fn):
    tests = {
        "full": df,
        "no_mss": df.drop(columns=["mss_bullish", "mss_bearish"], errors="ignore"),
        "no_fvg": df.drop(columns=["bullish_fvg", "bearish_fvg"], errors="ignore"),
        "no_sweep": df.drop(columns=["sweep_buyside", "sweep_sellside"], errors="ignore"),
    }

    results = {}

    for name, test_df in tests.items():
        trades = backtest_fn(test_df)

        # FIXED: Handle empty trades
        if trades.empty:
            win_rate = 0.0
        else:
            win_rate = (trades["result"] == "WIN").mean()
            if pd.isna(win_rate):
                win_rate = 0.0

        results[name] = {
            "win_rate": win_rate,
            "trades": len(trades)
        }

    return results
