from src.data_loader import load_data
from src.liquidity import detect_sweep, get_key_levels, apply_daily_bias
from src.structure import detect_swings, detect_bos, detect_mss
from src.pd_arrays import detect_fvg, detect_order_blocks
from src.strategy import generate_signals
from src.backtester import backtest
from src.analytics import compute_trade_metrics, equity_curve, performance_report, sweep_analysis
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================
DATA_FILE = "testData.csv"
TIMEZONE = "America/New_York"

# Backtester settings
SPREAD = 1.5            # ticks
SLIPPAGE = 0.5          # ticks
POINT_VALUE = 20.0      # dollars per point (NQ futures)
CONTRACTS = 1
INITIAL_EQUITY = 10000.0
MAX_BARS_HELD = 60      # 1 hour on 1m data
MAX_TRADES_PER_DAY = 3

# Structure settings
SWING_WINDOW = 3
MSS_SWEEP_EXPIRY = 60   # bars (1 hour)

# Liquidity settings
SWEEP_SESSION_START = "00:00:00"
SWEEP_SESSION_END = "09:30:00"
SWEEP_MIN_BREACH = 2.0  # ticks
SWEEP_REQUIRE_WICK = True

# Analytics
REPORT_INITIAL_EQUITY = INITIAL_EQUITY


# ============================================================
# 1. LOAD DATA (with timezone conversion)
# ============================================================
print("Loading data...")
df = load_data(DATA_FILE, timezone=TIMEZONE)
print(f"  Loaded {len(df)} bars | Range: {df.index[0]} to {df.index[-1]}")

# ============================================================
# 2. APPLY DAILY BIAS (00:00 and 08:30 opens)
# ============================================================
print("Applying daily bias...")
df = apply_daily_bias(df)

# ============================================================
# 3. COMPUTE ATR (needed by strategy for dynamic SL)
# ============================================================
print("Computing ATR...")
df["atr"] = df["high"].rolling(14).apply(
    lambda x: max(x[0] - x[3], x[1] - x[0], x[2] - x[1]),
    raw=True
).ewm(span=14, adjust=False).mean()

# ============================================================
# 4. LIQUIDITY
# ============================================================
print("Detecting liquidity levels...")
levels = get_key_levels(df, session_start=SWEEP_SESSION_START, session_end=SWEEP_SESSION_END)
print(f"  Buyside: {levels['buyside']:.2f} | Sellside: {levels['sellside']:.2f}")

df = detect_sweep(
    df,
    levels["buyside"],
    levels["sellside"],
    min_breach=SWEEP_MIN_BREACH,
    require_wick=SWEEP_REQUIRE_WICK,
)
print(f"  Buyside sweeps: {df['sweep_buyside'].sum()} | Sellside sweeps: {df['sweep_sellside'].sum()}")

# ============================================================
# 5. STRUCTURE
# ============================================================
print("Detecting market structure...")
df = detect_swings(df, window=SWING_WINDOW)
df = detect_bos(df)
df = detect_mss(df, sweep_expiry_bars=MSS_SWEEP_EXPIRY)
print(f"  Bullish BOS: {df['bos_bullish'].sum()} | Bearish BOS: {df['bos_bearish'].sum()}")
print(f"  Bullish MSS: {df['mss_bullish'].sum()} | Bearish MSS: {df['mss_bearish'].sum()}")

# ============================================================
# 6. PD ARRAYS
# ============================================================
print("Detecting PD arrays...")
df = detect_fvg(df)
df = detect_order_blocks(df)
print(f"  Bullish FVG: {df['bullish_fvg'].sum()} | Bearish FVG: {df['bearish_fvg'].sum()}")
print(f"  Bullish OB:  {df['bullish_ob'].sum()} | Bearish OB:  {df['bearish_ob'].sum()}")

# ============================================================
# 7. GENERATE SIGNALS
# ============================================================
print("Generating signals...")
df = generate_signals(df, atr_col="atr")
signal_counts = df["signal"].value_counts()
print(f"  Signals: {dict(signal_counts)}")

# ============================================================
# 8. BACKTEST
# ============================================================
print("Running backtest...")
trades = backtest(
    df,
    spread=SPREAD,
    slippage=SLIPPAGE,
    point_value=POINT_VALUE,
    contracts=CONTRACTS,
    initial_equity=INITIAL_EQUITY,
    max_bars=MAX_BARS_HELD,
    max_trades_per_day=MAX_TRADES_PER_DAY,
)
print(f"  Total trades: {len(trades)}")

# ============================================================
# 9. ANALYTICS
# ============================================================
if not trades.empty:
    trades = compute_trade_metrics(trades, point_value=POINT_VALUE, contracts=CONTRACTS)
    trades = equity_curve(trades, initial_equity=REPORT_INITIAL_EQUITY)
    report = performance_report(trades, initial_equity=REPORT_INITIAL_EQUITY)
    sweep = sweep_analysis(trades)

    print("\n" + "=" * 50)
    print("PERFORMANCE REPORT")
    print("=" * 50)
    print(f"  Total Trades:      {report['total_trades']}")
    print(f"  Win Rate:          {report['win_rate']:.1%}")
    print(f"  Profit Factor:     {report['profit_factor']:.2f}")
    print(f"  Expectancy:        ${report['expectancy_dollars']:.2f}")
    print(f"  Total PnL:         ${report['total_pnl_dollars']:.2f}")
    print(f"  Max Drawdown:      ${report['max_drawdown']:.2f} ({report['max_drawdown_pct']:.1f}%)")
    print(f"  Timeout Trades:    {report['timeout_count']}")

    if sweep:
        print(f"\n  Long  Win Rate:     {sweep['long_winrate']:.1%} ({sweep['long_count']} trades)")
        print(f"  Short Win Rate:     {sweep['short_winrate']:.1%} ({sweep['short_count']} trades)")
        print(f"  Long  PnL:          ${sweep['long_pnl']:.2f}")
        print(f"  Short PnL:          ${sweep['short_pnl']:.2f}")

    print("=" * 50)
else:
    print("No trades generated.")
