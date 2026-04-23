from src.data_loader import load_data
from src.liquidity import detect_sweep, get_key_levels, apply_daily_bias  # <-- Import new function
from src.structure import detect_swings, detect_bos, detect_mss
from src.pd_arrays import detect_fvg, detect_order_blocks
from src.strategy import generate_signals
from src.backtester import backtest
from src.analytics import compute_trade_metrics, equity_curve, performance_report

# 1. Load data
df = load_data("datan1.csv")

# 2. Apply Daily Bias (00:00 and 08:30 opens)
df = apply_daily_bias(df)  # <-- NEW STEP

# 3. Liquidity
levels = get_key_levels(df)
df = detect_sweep(df, levels["buyside"], levels["sellside"])

# 4. Structure
df = detect_swings(df)
df = detect_bos(df)
df = detect_mss(df)

# 5. PD Arrays
df = detect_fvg(df)
df = detect_order_blocks(df)

# 6. Generate Signals
df = generate_signals(df)

# DEBUG CHECK
print(df[["midnight_open", "ny_open", "signal"]].head(10))  # Check if levels attached
print(df["signal"].value_counts())

# 7. Backtest
trades = backtest(df)

# 8. Analytics
if not trades.empty:
    trades = compute_trade_metrics(trades)
    trades = equity_curve(trades)
    report = performance_report(trades)
    print(report)
else:
    print("No trades generated.")
