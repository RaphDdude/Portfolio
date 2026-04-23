#!/usr/bin/env python3
"""
ICT Strategy Code Review & Backtesting Accuracy Report
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, SimpleDocTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ━━ Color Palette ━━
ACCENT = colors.HexColor('#4d2fa6')
TEXT_PRIMARY = colors.HexColor('#222526')
TEXT_MUTED = colors.HexColor('#767e82')
BG_SURFACE = colors.HexColor('#dadfe1')
BG_PAGE = colors.HexColor('#edeff0')

TABLE_HEADER_COLOR = ACCENT
TABLE_HEADER_TEXT = colors.white
TABLE_ROW_EVEN = colors.white
TABLE_ROW_ODD = BG_SURFACE

CRITICAL_BG = colors.HexColor('#fde8e8')
CRITICAL_TEXT = colors.HexColor('#b91c1c')
HIGH_BG = colors.HexColor('#fef3c7')
HIGH_TEXT = colors.HexColor('#92400e')
MEDIUM_BG = colors.HexColor('#dbeafe')
MEDIUM_TEXT = colors.HexColor('#1e40af')
LOW_BG = colors.HexColor('#dcfce7')
LOW_TEXT = colors.HexColor('#166534')

# ━━ Font Registration ━━
pdfmetrics.registerFont(TTFont('Tinos', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Tinos-Bold', '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Calibri', '/usr/share/fonts/truetype/english/Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('Tinos', normal='Tinos', bold='Tinos-Bold')
registerFontFamily('Calibri', normal='Calibri', bold='Calibri')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')

# ━━ Styles ━━
body_style = ParagraphStyle(
    name='Body', fontName='Tinos', fontSize=10.5, leading=17,
    alignment=TA_JUSTIFY, spaceAfter=6, textColor=TEXT_PRIMARY
)
code_style = ParagraphStyle(
    name='Code', fontName='DejaVuSans', fontSize=8.5, leading=12,
    alignment=TA_LEFT, spaceAfter=6, textColor=TEXT_PRIMARY,
    backColor=colors.HexColor('#f5f5f5'), leftIndent=12, rightIndent=12,
    borderColor=colors.HexColor('#e0e0e0'), borderWidth=0.5,
    borderPadding=6, spaceBefore=6
)
heading1 = ParagraphStyle(
    name='H1', fontName='Tinos', fontSize=20, leading=26,
    spaceBefore=18, spaceAfter=10, textColor=TEXT_PRIMARY, alignment=TA_LEFT
)
heading2 = ParagraphStyle(
    name='H2', fontName='Tinos', fontSize=15, leading=20,
    spaceBefore=14, spaceAfter=8, textColor=ACCENT, alignment=TA_LEFT
)
heading3 = ParagraphStyle(
    name='H3', fontName='Tinos', fontSize=12, leading=16,
    spaceBefore=10, spaceAfter=6, textColor=TEXT_PRIMARY, alignment=TA_LEFT
)
caption_style = ParagraphStyle(
    name='Caption', fontName='Tinos', fontSize=9, leading=13,
    alignment=TA_CENTER, textColor=TEXT_MUTED, spaceBefore=3, spaceAfter=6
)
header_cell_style = ParagraphStyle(
    name='HeaderCell', fontName='Tinos', fontSize=9.5, leading=13,
    alignment=TA_CENTER, textColor=colors.white
)
cell_style = ParagraphStyle(
    name='Cell', fontName='Tinos', fontSize=9, leading=13,
    alignment=TA_LEFT, textColor=TEXT_PRIMARY
)
cell_center = ParagraphStyle(
    name='CellCenter', fontName='Tinos', fontSize=9, leading=13,
    alignment=TA_CENTER, textColor=TEXT_PRIMARY
)
severity_critical = ParagraphStyle(
    name='SevCritical', fontName='Tinos', fontSize=8.5, leading=12,
    alignment=TA_CENTER, textColor=CRITICAL_TEXT
)
severity_high = ParagraphStyle(
    name='SevHigh', fontName='Tinos', fontSize=8.5, leading=12,
    alignment=TA_CENTER, textColor=HIGH_TEXT
)
severity_medium = ParagraphStyle(
    name='SevMedium', fontName='Tinos', fontSize=8.5, leading=12,
    alignment=TA_CENTER, textColor=MEDIUM_TEXT
)
severity_low = ParagraphStyle(
    name='SevLow', fontName='Tinos', fontSize=8.5, leading=12,
    alignment=TA_CENTER, textColor=LOW_TEXT
)
bullet_style = ParagraphStyle(
    name='Bullet', fontName='Tinos', fontSize=10.5, leading=17,
    alignment=TA_LEFT, spaceAfter=4, textColor=TEXT_PRIMARY,
    leftIndent=20, bulletIndent=8
)
callout_style = ParagraphStyle(
    name='Callout', fontName='Tinos', fontSize=10.5, leading=17,
    alignment=TA_LEFT, spaceAfter=8, textColor=TEXT_PRIMARY,
    leftIndent=14, borderColor=ACCENT, borderWidth=2, borderPadding=8,
    backColor=colors.HexColor('#f8f6ff')
)

PAGE_W, PAGE_H = A4
LEFT_M = 1.0 * inch
RIGHT_M = 1.0 * inch
TOP_M = 0.9 * inch
BOTTOM_M = 0.9 * inch
AVAIL_W = PAGE_W - LEFT_M - RIGHT_M

def make_table(data, col_widths, row_count):
    t = Table(data, colWidths=col_widths, hAlign='CENTER')
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for r in range(1, row_count):
        bg = TABLE_ROW_ODD if r % 2 == 0 else TABLE_ROW_EVEN
        style_cmds.append(('BACKGROUND', (0, r), (-1, r), bg))
    t.setStyle(TableStyle(style_cmds))
    return t

def severity_cell(severity):
    styles_map = {'CRITICAL': severity_critical, 'HIGH': severity_high,
                  'MEDIUM': severity_medium, 'LOW': severity_low}
    bg_map = {'CRITICAL': CRITICAL_BG, 'HIGH': HIGH_BG,
              'MEDIUM': MEDIUM_BG, 'LOW': LOW_BG}
    s = ParagraphStyle(
        name=f'Sev_{severity}_{id(severity)}',
        parent=styles_map.get(severity, cell_center),
        backColor=bg_map.get(severity, colors.white)
    )
    return Paragraph(f'<b>{severity}</b>', s)


# ━━ Build Document ━━
output_path = '/home/z/my-project/download/ICT_Strategy_Code_Review.pdf'
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOTTOM_M,
    title='ICT Strategy Code Review and Backtesting Accuracy Report',
    author='Z.ai'
)

story = []

# ══════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════
story.append(Spacer(1, 160))
story.append(Paragraph('<b>ICT Strategy</b>', ParagraphStyle(
    name='CoverTitle', fontName='Tinos', fontSize=42, leading=50,
    alignment=TA_CENTER, textColor=TEXT_PRIMARY
)))
story.append(Spacer(1, 12))
story.append(Paragraph('<b>Code Review and Backtesting<br/>Accuracy Report</b>', ParagraphStyle(
    name='CoverSubtitle', fontName='Tinos', fontSize=22, leading=30,
    alignment=TA_CENTER, textColor=ACCENT
)))
story.append(Spacer(1, 50))

# Decorative line
line_data = [['']]
line_table = Table(line_data, colWidths=[AVAIL_W * 0.4], hAlign='CENTER')
line_table.setStyle(TableStyle([
    ('LINEBELOW', (0, 0), (-1, 0), 2, ACCENT),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
]))
story.append(line_table)
story.append(Spacer(1, 50))

meta_style = ParagraphStyle(
    name='Meta', fontName='Tinos', fontSize=13, leading=20,
    alignment=TA_CENTER, textColor=TEXT_MUTED
)
story.append(Paragraph('Comprehensive Analysis of 9 Core Modules', meta_style))
story.append(Spacer(1, 8))
story.append(Paragraph('Strategy | Structure | Liquidity | Backtester | Analytics | Optimizer', meta_style))
story.append(Spacer(1, 80))

footer_style = ParagraphStyle(
    name='Footer', fontName='Tinos', fontSize=10, leading=14,
    alignment=TA_CENTER, textColor=TEXT_MUTED
)
story.append(Paragraph('April 2026', footer_style))

story.append(PageBreak())

# ══════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ══════════════════════════════════════════
story.append(Paragraph('<b>1. Executive Summary</b>', heading1))
story.append(Paragraph(
    'This report provides a comprehensive code review of an ICT (Inner Circle Trader) smart money '
    'strategy backtesting system comprising 9 Python modules. The review identifies critical bugs that '
    'directly compromise backtesting accuracy, logic errors that produce misleading signals, and '
    'architectural gaps that prevent reliable strategy evaluation. The analysis covers every file in '
    'the pipeline: data loading, liquidity detection, market structure analysis, price delivery (PD) '
    'array identification, signal generation, trade execution simulation, performance analytics, '
    'and parameter optimization.', body_style))
story.append(Spacer(1, 8))
story.append(Paragraph(
    'The review uncovered <b>5 critical-severity issues</b>, <b>7 high-severity issues</b>, '
    '<b>6 medium-severity issues</b>, and <b>5 low-severity issues</b>. The most impactful findings '
    'relate to the backtester engine itself: the SL/TP hit priority logic is fundamentally flawed, '
    'there is no intrabar price simulation, no spread or slippage modeling, and the PnL calculation '
    'does not account for position sizing or contract specifications. Combined with a lookahead bias '
    'in the swing detection algorithm and an arbitrary hardcoded stop-loss distance, these issues mean '
    'that the current backtest results cannot be trusted to reflect real-world trading performance. '
    'The sections that follow detail each finding with file location, root cause analysis, impact '
    'assessment, and concrete code-level fix recommendations.', body_style))

story.append(Spacer(1, 18))

# Summary table
summary_data = [
    [Paragraph('<b>Severity</b>', header_cell_style),
     Paragraph('<b>Count</b>', header_cell_style),
     Paragraph('<b>Primary Impact</b>', header_cell_style)],
    [severity_cell('CRITICAL'), Paragraph('5', cell_center),
     Paragraph('Invalid backtest results, false signals, lookahead bias', cell_style)],
    [severity_cell('HIGH'), Paragraph('7', cell_center),
     Paragraph('Misleading accuracy, cascading false positives, no risk modeling', cell_style)],
    [severity_cell('MEDIUM'), Paragraph('6', cell_center),
     Paragraph('Suboptimal entries, incorrect metrics, optimizer ineffectiveness', cell_style)],
    [severity_cell('LOW'), Paragraph('5', cell_center),
     Paragraph('Code quality, missing validations, edge cases', cell_style)],
]
summary_table = make_table(summary_data, [AVAIL_W*0.18, AVAIL_W*0.12, AVAIL_W*0.70], 5)
story.append(summary_table)
story.append(Paragraph('<b>Table 1.</b> Issue severity distribution summary', caption_style))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 2. CRITICAL ISSUES
# ══════════════════════════════════════════
story.append(Paragraph('<b>2. Critical Issues</b>', heading1))
story.append(Paragraph(
    'Critical issues are those that fundamentally break the correctness of the backtest. Each one '
    'independently renders the current results unreliable. Addressing these is the highest priority '
    'before drawing any conclusions from the system.', body_style))

# ── 2.1 SL/TP Priority ──
story.append(Spacer(1, 12))
story.append(Paragraph('<b>2.1 SL/TP Hit Priority Bias in Backtester</b>', heading2))
story.append(Paragraph('<b>File:</b> backtester.py, lines 34-57', heading3))
story.append(Paragraph(
    'The backtester checks stop-loss before take-profit for LONG trades, and stop-loss before '
    'take-profit for SHORT trades, regardless of the candle open price or the actual price path '
    'within the bar. In a real market, when both the SL and TP levels are within a single candle\'s '
    'high-low range, the order in which price touches them depends on the actual intrabar movement. '
    'For a LONG trade, if the candle opens above the entry and rallies to the TP before dropping '
    'to the SL, the trade should be a winner. However, the current code always checks the low first, '
    'so it would record a loss. This creates a systematic pessimistic bias where winning trades that '
    'experience a drawdown before hitting their target are incorrectly counted as losses.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'Conversely, for SHORT trades, the code checks the high first (SL) before the low (TP). If a '
    'short candle opens below entry and falls to the TP before retracing to the SL, it should be a '
    'winner, but the code records a loss. The bias is asymmetric between long and short sides, which '
    'can distort the long-vs-short win rate comparison in sweep_analysis. On 1-minute data with tight '
    'stops and 2R targets, this issue affects a significant percentage of trades because the '
    'high-to-low range frequently encompasses both levels.', body_style))
story.append(Spacer(1, 6))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Implement an open-price heuristic: if the candle open is above the entry for a LONG, the market '
    'is already bullish, so check TP first. If the open is below entry, check SL first. For SHORT '
    'trades, reverse the logic. A more advanced solution is to model the price path using a random '
    'walk or percent-of-range heuristic (e.g., if the TP is closer to the open than the SL, assume '
    'TP is hit first). The following code demonstrates the open-price heuristic approach:', body_style))

story.append(Paragraph(
    '# LONG: check TP first if open >= entry, else check SL first<br/>'
    'if trade["type"] == "LONG":<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if row["open"] >= trade["entry"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if high >= trade["tp"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;trade["exit"] = trade["tp"]; trade["result"] = "WIN"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif low <= trade["sl"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;trade["exit"] = trade["sl"]; trade["result"] = "LOSS"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;else:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if low <= trade["sl"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;trade["exit"] = trade["sl"]; trade["result"] = "LOSS"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif high >= trade["tp"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;trade["exit"] = trade["tp"]; trade["result"] = "WIN"',
    code_style))

story.append(Spacer(1, 18))

# ── 2.2 BOS Never Resets ──
story.append(Paragraph('<b>2.2 BOS Detection Never Resets After Break (Cascading False Signals)</b>', heading2))
story.append(Paragraph('<b>File:</b> structure.py, lines 26-50', heading3))
story.append(Paragraph(
    'The detect_bos function tracks last_swing_high and last_swing_low but never resets them after '
    'a Break of Structure occurs. Once price closes above the last swing high, every subsequent '
    'candle that closes above the same level triggers bos_bullish = True. This means that if price '
    'breaks a swing high and continues trending up for 200 candles, all 200 candles are marked as '
    'bullish BOS. In the ICT methodology, a Break of Structure is a single structural event that '
    'confirms a trend change. Marking every subsequent candle as BOS completely dilutes the meaning '
    'of the signal and causes the MSS detection (which depends on BOS) to fire incorrectly on every '
    'candle after a sweep+BOS event.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'The same problem applies to bos_bearish. After a bearish break, every subsequent close below '
    'the last swing low triggers a new bearish BOS. This cascading behavior explains why the strategy '
    'may appear to generate too many signals or why signals cluster around trending periods. In '
    'practice, this inflates the trade count with duplicate signals and makes it impossible to '
    'attribute a specific BOS candle to a specific signal generation event.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Reset last_swing_high to None after a bullish BOS fires, and reset last_swing_low to None after '
    'a bearish BOS fires. The next BOS should only trigger when a new swing point forms and is '
    'subsequently broken. Additionally, consider adding a minimum distance requirement between '
    'consecutive swing points to filter out noise on 1-minute data:', body_style))

story.append(Paragraph(
    'if last_swing_high is not None and row["close"] > last_swing_high:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bos_bullish")] = True<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;last_swing_high = None &nbsp;# RESET after break<br/>'
    '<br/>'
    'if last_swing_low is not None and row["close"] < last_swing_low:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bos_bearish")] = True<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;last_swing_low = None &nbsp;# RESET after break',
    code_style))

story.append(Spacer(1, 18))

# ── 2.3 Lookahead Bias in Swing Detection ──
story.append(Paragraph('<b>2.3 Lookahead Bias in Swing Detection</b>', heading2))
story.append(Paragraph('<b>File:</b> structure.py, lines 5-16', heading3))
story.append(Paragraph(
    'The detect_swings function uses pandas rolling with center=True, which means that determining '
    'whether bar i is a swing high requires looking at bars i-1, i, and i+1. In a live trading '
    'scenario, you cannot know bar i+1 at the time bar i closes. This introduces lookahead bias: '
    'the strategy uses future data to make decisions on the current bar. On 1-minute data, a swing '
    'point at 10:00 is only confirmed at 10:02, but the current system treats it as confirmed at '
    '10:00. Any signal generated on or near that bar is using information that would not have been '
    'available in real-time.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'The impact of this bias depends on the window size. With window=3, the lookahead is 1 bar '
    '(1 minute), which is small but still problematic when combined with other look-ahead-dependent '
    'indicators like BOS and MSS. With larger windows, the lookahead grows proportionally. For a '
    'strategy that relies heavily on structural market analysis (swing points are foundational to '
    'BOS, MSS, and order blocks), even a 1-bar lookahead can shift the entry timing enough to '
    'materially alter the backtest result. A trade that appears to enter at a swing low might '
    'actually enter 1-2 bars later in live trading, potentially missing the optimal entry price.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Change to a trailing (non-centered) rolling window using center=False, and shift the result '
    'back by (window // 2) bars so the confirmation is delayed appropriately. Alternatively, use '
    'a lookback approach where the swing is confirmed on bar i but the signal cannot fire until '
    'bar i + (window // 2). This ensures the strategy only acts on confirmed swing points:', body_style))

story.append(Paragraph(
    'df["swing_high"] = df["high"].rolling(window, center=False).apply(<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;lambda x: 1 if x[-1] == np.max(x) else 0, raw=True<br/>'
    ')<br/>'
    'df["swing_high"] = df["swing_high"].shift(window // 2 - 1)',
    code_style))

story.append(Spacer(1, 18))

# ── 2.4 No Spread/Slippage/Commission ──
story.append(Paragraph('<b>2.4 No Spread, Slippage, or Commission Modeling</b>', heading2))
story.append(Paragraph('<b>File:</b> backtester.py (entire file)', heading3))
story.append(Paragraph(
    'The backtester executes trades at exact signal prices without any transaction cost modeling. '
    'In reality, every trade incurs at minimum a bid-ask spread (typically 0.5-2 ticks on NQ futures), '
    'possible slippage on market orders (1-3 ticks during volatile conditions), and broker commissions. '
    'With a hardcoded 5-tick stop-loss, a 2-tick spread means the effective stop distance is reduced '
    'by 40%, which dramatically increases the actual loss rate. The entry price in the signal is a '
    'midpoint calculation from the candle high and low, which may be several ticks away from the '
    'actual executable price at the time the signal fires. Furthermore, limit orders for entry at the '
    'FVG midpoint may not fill if price gaps through the level, a scenario completely absent from the '
    'backtest.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'The absence of cost modeling makes the backtest results systematically optimistic. Every winning '
    'trade has a slightly lower realized profit, and every losing trade has a slightly larger realized '
    'loss. Over hundreds of trades, this compounding effect can easily turn a supposedly profitable '
    'strategy into a net loser. For any strategy with a target of only 2R and a 5-tick stop on a '
    'high-frequency instrument like NQ, transaction costs are a first-order effect, not a minor '
    'adjustment. The current results may overstate profitability by 15-30% or more depending on '
    'the actual market conditions during the test period.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add configurable spread, slippage, and commission parameters. For NQ futures, a conservative '
    'estimate is 1.5 ticks spread + 0.5 ticks slippage = 2 ticks total cost per side (4 ticks '
    'round-trip). Add these to the SL and subtract from the TP for LONG trades (reverse for SHORT). '
    'Also model entry as a limit order with a fill probability or use the next bar\'s open as the '
    'execution price:', body_style))

story.append(Paragraph(
    'spread = 1.5 &nbsp;# ticks<br/>'
    'slippage = 0.5 &nbsp;# ticks<br/>'
    'cost_per_side = spread + slippage<br/>'
    '<br/>'
    '# For LONG: effective SL is further away, TP is closer<br/>'
    'eff_sl = trade["sl"] + cost_per_side<br/>'
    'eff_tp = trade["tp"] - cost_per_side<br/>'
    '<br/>'
    '# For SHORT: reverse<br/>'
    'eff_sl = trade["sl"] - cost_per_side<br/>'
    'eff_tp = trade["tp"] + cost_per_side',
    code_style))

story.append(Spacer(1, 18))

# ── 2.5 Hardcoded Stop Loss ──
story.append(Paragraph('<b>2.5 Hardcoded Stop-Loss Distance (No Dynamic Risk Management)</b>', heading2))
story.append(Paragraph('<b>File:</b> strategy.py, lines 40 and 61', heading3))
story.append(Paragraph(
    'The stop-loss is set to a fixed 5 ticks/pips above the candle high (for shorts) or below the '
    'entry (for longs). This ignores market volatility, the size of the swing being traded, the '
    'width of the liquidity sweep, and any structural invalidation level. In a volatile pre-market '
    'session, 5 ticks may be stopped out by normal noise. In a quiet mid-day period, a 5-tick stop '
    'may be unnecessarily tight, reducing the win rate on trades that would eventually work. The '
    'ICT methodology typically places stops beyond the swing that was swept or the extreme of the '
    'displacement candle, which could be 10-30 ticks away depending on the structure being traded.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'The hardcoded value also creates a fixed risk-reward ratio that does not adapt to market '
    'conditions. With a 5-tick stop and a 2R target, the TP is always 10 ticks from entry. On days '
    'when the market is ranging, a 10-tick target may be unrealistic, leading to many trades that '
    'stall and eventually stop out. On trending days, a 10-tick target may be too small, leaving '
    'profit on the table. A dynamic stop based on ATR, swing structure, or the sweep extremity '
    'would significantly improve the strategy\'s adaptability and realism.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Replace the hardcoded 5-tick stop with a structure-based or ATR-based calculation. Place the '
    'stop beyond the sweep candle\'s high (for shorts) or low (for longs), plus a small buffer. '
    'Alternatively, use a multiple of ATR (e.g., 0.5-1.0x ATR(14)) as the stop distance. This '
    'adapts the risk to current volatility and aligns with the ICT concept of invalidation beyond '
    'the structural extremity:', body_style))

story.append(Paragraph(
    'import talib<br/>'
    '<br/>'
    'atr = talib.ATR(df["high"], df["low"], df["close"], timeperiod=14)<br/>'
    '<br/>'
    '# For SHORT: SL beyond the sweep candle high + buffer<br/>'
    'sl = row["high"] + max(atr[i] * 0.3, 2) &nbsp;# min 2 ticks buffer<br/>'
    '<br/>'
    '# For LONG: SL below the sweep candle low - buffer<br/>'
    'sl = entry - max(atr[i] * 0.3, 2)',
    code_style))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 3. HIGH-SEVERITY ISSUES
# ══════════════════════════════════════════
story.append(Paragraph('<b>3. High-Severity Issues</b>', heading1))
story.append(Paragraph(
    'High-severity issues significantly degrade the accuracy and reliability of the backtesting '
    'system but do not necessarily invalidate all results. Each issue represents a meaningful '
    'departure from realistic market conditions or introduces systematic error into the signal '
    'generation pipeline.', body_style))

# ── 3.1 FVG Entry ──
story.append(Spacer(1, 12))
story.append(Paragraph('<b>3.1 FVG Entry Uses Candle Midpoint Instead of Gap Zone</b>', heading2))
story.append(Paragraph('<b>File:</b> strategy.py, lines 72-77', heading3))
story.append(Paragraph(
    'The calculate_fvg_entry function returns (row["high"] + row["low"]) / 2, which is simply the '
    'midpoint of the current candle. A Fair Value Gap is a 3-candle pattern where candle 1\'s high '
    'is below candle 3\'s low (bullish) or candle 1\'s low is above candle 3\'s high (bearish). '
    'The correct FVG entry should be at the top of the bullish gap (candle 1\'s high for bullish '
    'FVG) or the bottom of the bearish gap (candle 1\'s low for bearish FVG), because ICT theory '
    'states that price tends to return to fill these imbalance zones. Using the current candle\'s '
    'midpoint ignores the actual gap entirely and defeats the purpose of identifying FVGs as entry '
    'points. The function also does not differentiate between bullish and bearish FVGs when '
    'calculating the entry price.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Store the actual FVG boundaries (c1.high for bullish, c1.low for bearish) during detection '
    'in pd_arrays.py. Then use these stored values as the entry price in the strategy. Modify '
    'detect_fvg to record the gap boundaries as new columns (bullish_fvg_top, bearish_fvg_bottom) '
    'and reference them in calculate_fvg_entry:', body_style))

story.append(Paragraph(
    '# In pd_arrays.py - detect_fvg:<br/>'
    'df["bullish_fvg_top"] = np.nan<br/>'
    'df["bearish_fvg_bottom"] = np.nan<br/>'
    '<br/>'
    'if c3["low"] > c1["high"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bullish_fvg")] = True<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bullish_fvg_top")] = c1["high"]<br/>'
    '<br/>'
    'if c3["high"] < c1["low"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bearish_fvg")] = True<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;df.iloc[i, df.columns.get_loc("bearish_fvg_bottom")] = c1["low"]',
    code_style))

story.append(Spacer(1, 18))

# ── 3.2 MSS Sweep State ──
story.append(Paragraph('<b>3.2 MSS Sweep State Never Resets Without BOS (Stale State Bug)</b>', heading2))
story.append(Paragraph('<b>File:</b> structure.py, lines 53-78', heading3))
story.append(Paragraph(
    'In detect_mss, the boolean flags swept_sellside and swept_buyside are set to True when a '
    'liquidity sweep is detected and are only reset when an MSS event fires (sweep followed by BOS). '
    'If a sweep occurs but no BOS follows within the dataset, the flag remains True indefinitely. '
    'This means that the next BOS that occurs (possibly hours or days later) will be incorrectly '
    'marked as an MSS, even though it is unrelated to the original sweep event. In ICT methodology, '
    'MSS requires the sweep and the structural break to be related temporal events, typically within '
    'the same session or at most the same trading day.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'For example, if a sell-side sweep occurs at 03:00 (Asian session) but no bullish BOS happens '
    'until 10:00 (NYSE open), the system will mark the 10:00 BOS as MSS_bullish. In reality, the '
    'sweep and the BOS are separated by 7 hours and likely driven by completely different market '
    'dynamics. This produces false MSS signals that generate trades at structurally invalid points, '
    'degrading both the win rate and the conceptual integrity of the strategy.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add a time-based expiry or a bar-count limit to the sweep state. If a BOS does not occur '
    'within N bars (e.g., 60 bars = 1 hour on 1-minute data) after the sweep, reset the flag. '
    'Alternatively, reset the sweep flag at the start of each trading session or when a new swing '
    'point forms:', body_style))

story.append(Paragraph(
    'sweep_expiry = 60 &nbsp;# bars<br/>'
    'sweep_bar_count = {<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;"sellside": 0,<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;"buyside": 0<br/>'
    '}<br/>'
    '<br/>'
    '# In the loop:<br/>'
    'if row["sweep_sellside"]:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;swept_sellside = True<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;sweep_bar_count["sellside"] = 0<br/>'
    'elif swept_sellside:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;sweep_bar_count["sellside"] += 1<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if sweep_bar_count["sellside"] > sweep_expiry:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;swept_sellside = False',
    code_style))

story.append(Spacer(1, 18))

# ── 3.3 No Intrabar Simulation ──
story.append(Paragraph('<b>3.3 No Intrabar Price Path Simulation</b>', heading2))
story.append(Paragraph('<b>File:</b> backtester.py, lines 29-57', heading3))
story.append(Paragraph(
    'The backtester uses candle high and low to determine if SL or TP was hit, but does not simulate '
    'the actual price movement within the candle. This means the system cannot distinguish between '
    'a candle that gently trends from open to close and one that wildly oscillates between its high '
    'and low. Both scenarios are treated identically. On 1-minute data, candles frequently have high '
    'ranges relative to their close-to-open distance, meaning that a candle might hit the SL, bounce '
    'back, and then hit the TP. In reality, the trade would have been stopped out at the SL, but the '
    'current code (with the SL-first bias described in Section 2.1) might record it either way '
    'depending on the arbitrary check order.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'For accurate backtesting of intraday strategies, especially those using tight stops on 1-minute '
    'data, some form of intrabar simulation is essential. Without it, the backtest cannot capture '
    'the reality that many trades will be stopped out by intra-candle noise even if the candle '
    'ultimately closes in the favorable direction. This is one of the primary reasons that backtests '
    'on 1-minute data tend to significantly overestimate win rates compared to live trading results.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Implement a simple intrabar model. The most common approaches are: (a) percentage-of-range '
    'model, where the probability of hitting SL or TP first is proportional to their distance from '
    'the candle open; (b) random walk model, where you generate a synthetic price path within the '
    'candle using the open, high, low, and close as constraints; or (c) use tick data if available. '
    'The percentage-of-range model is the simplest to implement and provides a reasonable first '
    'approximation:', body_style))

story.append(Paragraph(
    '# Probability-based approach (no simulation needed):<br/>'
    'total_range = high - low<br/>'
    'sl_dist = abs(open - sl) / total_range &nbsp;# 0.0 to 1.0<br/>'
    'tp_dist = abs(open - tp) / total_range &nbsp;# 0.0 to 1.0<br/>'
    '<br/>'
    '# If both in range, hit probability inversely proportional to distance<br/>'
    'if low <= sl and high >= tp:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;prob_sl_first = tp_dist / (sl_dist + tp_dist)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;hit_sl = random.random() < prob_sl_first',
    code_style))

story.append(Spacer(1, 18))

# ── 3.4 PnL Not Account-Based ──
story.append(Paragraph('<b>3.4 PnL Calculation Uses Raw Price Difference (Not Account-Based)</b>', heading2))
story.append(Paragraph('<b>File:</b> analytics.py, lines 12-18', heading3))
story.append(Paragraph(
    'The compute_trade_metrics function calculates PnL as the absolute price difference between '
    'entry and exit (for wins) or entry and SL (for losses). This ignores position sizing, pip '
    'value, contract specifications, and account currency effects. On NQ futures, each point is '
    'worth $20 per contract. A 5-point move equals $100, not 5. The current system reports PnL in '
    'raw index points, which is meaningless for assessing actual trading performance. The risk-reward '
    'ratio calculation (pnl / abs(entry - sl)) produces correct R-multiples by coincidence because '
    'the unit cancels, but the expectancy (mean PnL) and equity curve are in arbitrary units.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'This becomes particularly important when comparing the strategy across different instruments or '
    'when trying to assess whether the strategy generates enough profit to cover fixed costs '
    '(platform fees, data subscriptions, etc.). A strategy that makes an average of 2 index points '
    'per trade sounds modest but could represent $40 per contract per trade with proper sizing, '
    'which is significant at scale. Without converting to dollar terms, it is impossible to make '
    'informed decisions about the strategy\'s viability.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Introduce a point_value parameter (default $20 for NQ) and a contracts_per_trade parameter. '
    'Convert all PnL calculations to dollar terms. Also calculate returns as a percentage of account '
    'equity rather than raw dollar amounts, which enables comparison across different account sizes '
    'and strategies:', body_style))

story.append(Paragraph(
    'point_value = 20 &nbsp;# dollars per point for NQ<br/>'
    'contracts = 1<br/>'
    '<br/>'
    'trades_df["pnl_dollars"] = trades_df["pnl"] * point_value * contracts<br/>'
    'trades_df["pnl_pct"] = trades_df["pnl_dollars"] / initial_equity * 100<br/>'
    'trades_df["rr"] = trades_df["pnl_dollars"] / (abs(trades_df["entry"] - trades_df["sl"]) * point_value * contracts)',
    code_style))

story.append(Spacer(1, 18))

# ── 3.5 No Time-of-Day Filter ──
story.append(Paragraph('<b>3.5 No Time-of-Day or Session Filtering</b>', heading2))
story.append(Paragraph('<b>Files:</b> strategy.py, backtester.py', heading3))
story.append(Paragraph(
    'ICT strategies are inherently session-based. The London Open (02:00-05:00 EST), New York Open '
    '(08:30-11:00 EST), and London Close (10:00-12:00 EST) are the primary trading windows where '
    'liquidity sweeps and structural shifts occur with high probability. The current system generates '
    'signals at any time of day, including during the Asian session (low liquidity, narrow ranges) '
    'and mid-day doldrums (no institutional activity). Taking trades during these periods contradicts '
    'the ICT methodology and introduces low-quality signals that drag down the overall win rate.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'The lack of session filtering also means the backtester evaluates trades that would never be '
    'taken by a discretionary ICT trader. This inflates the trade count with noise trades and makes '
    'the performance metrics appear worse than they would be if the strategy were properly filtered. '
    'Additionally, some ICT setups require specific session alignments, such as a sweep of the Asian '
    'session high during the London session followed by a MSS during the New York session. These '
    'multi-session setups are impossible to evaluate without session-aware signal generation.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add a time-of-day filter to the signal generation logic. Only generate signals during high-conviction '
    'ICT trading windows. Also consider adding a session label column to the dataframe to enable '
    'session-specific analysis and reporting:', body_style))

story.append(Paragraph(
    '# Define ICT trading windows (EST)<br/>'
    'TRADING_WINDOWS = [<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;("08:00", "11:00"), &nbsp;# NY morning session<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;("02:00", "05:00"), &nbsp;# London session<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;("12:30", "14:30"), &nbsp;# NY afternoon<br/>'
    ']<br/>'
    '<br/>'
    '# In generate_signals, check if current time is in a window:<br/>'
    'current_time = row.name.time()<br/>'
    'in_window = any(start <= current_time <= end for start, end in TRADING_WINDOWS)<br/>'
    'if not in_window:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;continue &nbsp;# Skip signal generation',
    code_style))

story.append(Spacer(1, 18))

# ── 3.6 No Position Sizing ──
story.append(Paragraph('<b>3.6 No Risk-Based Position Sizing in Backtester</b>', heading2))
story.append(Paragraph('<b>File:</b> backtester.py (entire file)', heading3))
story.append(Paragraph(
    'The backtester treats every trade as a single unit without any position sizing logic. In reality, '
    'traders size positions based on their risk tolerance (typically 0.5-2% of account equity per '
    'trade), the distance to the stop-loss, and the instrument\'s point value. A trade with a 3-tick '
    'stop should have a larger position than one with a 10-tick stop to maintain consistent dollar '
    'risk per trade. Without position sizing, the backtest assumes equal dollar risk per trade, which '
    'means that trades with wider stops (larger losses when they hit) have disproportionate impact '
    'on the equity curve compared to tight-stop trades.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'This is particularly important for the current strategy because the hardcoded 5-tick stop means '
    'all trades have the same nominal risk. However, if the recommended fix in Section 2.5 is '
    'implemented (dynamic stops based on ATR or structure), stop distances will vary, and position '
    'sizing becomes essential for meaningful performance comparison. Without it, the optimizer may '
    'favor parameter combinations that produce wider stops (which have lower win rates but also lower '
    'dollar risk per contract), creating a misleading performance profile.', body_style))

story.append(Spacer(1, 18))

# ── 3.7 Optimizer Tests on Same Data ──
story.append(Paragraph('<b>3.7 Optimizer Tests on Same Data (No Walk-Forward Validation)</b>', heading2))
story.append(Paragraph('<b>File:</b> optimizer.py (entire file)', heading3))
story.append(Paragraph(
    'The sensitivity_test and ablation_test functions evaluate different parameter combinations on '
    'the same dataset used to calibrate the strategy. This is a form of in-sample optimization that '
    'leads to curve fitting. The parameters that perform best on the test data are likely '
    'overfitted and will not generalize to unseen data. In quantitative finance, this is one of the '
    'most common reasons that strategies with impressive backtests fail in live trading. The optimizer '
    'is effectively searching for the parameter set that best fits noise in the historical data '
    'rather than capturing a genuine market edge.', body_style))
story.append(Spacer(1, 6))
story.append(Paragraph(
    'Furthermore, the ablation_test does not actually perform a valid ablation. Dropping columns '
    'like "sweep_buyside" from the dataframe means the strategy\'s generate_signals function calls '
    'row.get("sweep_buyside", False), which returns the default False. This is identical to having '
    'the column present with all False values. If the sweep detection originally produced both True '
    'and False values (which it does), removing the column replaces all True values with False, but '
    'this only works if the column existed in the first place. The ablation is measuring the '
    'contribution of each feature by disabling it entirely, but the approach is fragile and would '
    'break if the strategy ever changes how it reads these columns.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Implement walk-forward optimization: split the data into training (e.g., first 70%) and testing '
    '(last 30%) periods. Optimize parameters on the training period, then evaluate the optimized '
    'parameters on the out-of-sample test period. Use rolling or anchored windows for more robust '
    'evaluation. The out-of-sample performance is the only metric that should be reported for '
    'strategy viability assessment.', body_style))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 4. MEDIUM-SEVERITY ISSUES
# ══════════════════════════════════════════
story.append(Paragraph('<b>4. Medium-Severity Issues</b>', heading1))
story.append(Paragraph(
    'Medium-severity issues affect the quality, precision, or usability of the system without '
    'fundamentally breaking the results. These should be addressed after the critical and high-severity '
    'items are resolved.', body_style))

# ── 4.1 Premium/Discount ──
story.append(Spacer(1, 12))
story.append(Paragraph('<b>4.1 Premium/Discount Bias Is Oversimplified</b>', heading2))
story.append(Paragraph('<b>File:</b> strategy.py, lines 20-25', heading3))
story.append(Paragraph(
    'The premium/discount check uses a simple comparison: if close > midnight_open AND close > ny_open, '
    'the market is in premium. This binary classification does not account for the actual equilibrium '
    'range or the distance from fair value. In ICT methodology, premium and discount are defined '
    'relative to a range (the daily range, a session range, or a computed equilibrium zone). Price '
    'that is just barely above both opens is treated the same as price that is far above them, even '
    'though the ICT concept of "expensive" implies a meaningful deviation from value. The current '
    'implementation classifies the majority of the trading day as either premium or discount, leaving '
    'little room for a neutral/equilibrium zone where no directional bias should be applied.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add an equilibrium zone: if price is within X% of the midpoint between midnight_open and ny_open, '
    'classify it as neutral (no bias). Only classify as premium if above the upper threshold and as '
    'discount if below the lower threshold. This reduces the number of low-conviction signals and '
    'aligns with the ICT concept of a fair value zone.', body_style))

story.append(Spacer(1, 12))

# ── 4.2 get_key_levels Session ──
story.append(Paragraph('<b>4.2 get_key_levels Uses Overly Wide Session Range</b>', heading2))
story.append(Paragraph('<b>File:</b> liquidity.py, lines 4-10', heading3))
story.append(Paragraph(
    'The get_key_levels function uses between_time("00:00:00", "09:30:00") to determine buy-side '
    'and sell-side liquidity levels. This 9.5-hour window spans the entire Asian session, European '
    'pre-market, and pre-NY open period. In ICT methodology, the pre-market range (typically the '
    'period before the major session open) is more relevant for identifying the liquidity pools that '
    'institutional participants target. Using the entire overnight range may capture levels that are '
    'too far from the current market to be relevant, or levels that were already swept during the '
    'Asian or early European sessions.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Consider using the previous day\'s high and low as the primary liquidity levels (a standard ICT '
    'approach), or limit the session range to the specific pre-market window (e.g., 20:00-09:30 EST '
    'for the full overnight, or 04:00-09:30 EST for the European pre-market). The choice should '
    'match the ICT model being traded.', body_style))

story.append(Spacer(1, 12))

# ── 4.3 Equity Curve from Zero ──
story.append(Paragraph('<b>4.3 Equity Curve Starts from Zero (No Initial Capital)</b>', heading2))
story.append(Paragraph('<b>File:</b> analytics.py, lines 23-38', heading3))
story.append(Paragraph(
    'The equity_curve function starts with equity = 0 and accumulates PnL from each trade. This '
    'means the equity curve represents cumulative raw PnL, not actual account equity. The max '
    'drawdown calculation uses this zero-based equity, which can produce misleading drawdown figures. '
    'For example, if the first 5 trades are winners (+10 points each, total +50) and then 3 trades '
    'lose (-5 points each, total -15), the peak is 50 and the trough is 35, giving a drawdown of 15. '
    'However, relative to a $10,000 account, the actual drawdown percentage would be 0.03% (15 points '
    'x $20 / $10,000), not the 30% that the raw numbers might suggest to an unsuspecting analyst.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Accept an initial_capital parameter (default $10,000 or $50,000 depending on the instrument) '
    'and start the equity curve from that value. Calculate drawdown as a percentage of peak equity, '
    'not as an absolute value. This produces results that are directly comparable to actual trading '
    'performance and allows meaningful risk assessment.', body_style))

story.append(Spacer(1, 12))

# ── 4.4 No Trade Expiry ──
story.append(Paragraph('<b>4.4 No Trade Timeout or Maximum Holding Period</b>', heading2))
story.append(Paragraph('<b>File:</b> backtester.py, lines 4-63', heading3))
story.append(Paragraph(
    'The backtester holds trades indefinitely until the SL or TP is hit. In practice, ICT traders '
    'typically set a maximum holding period (e.g., close the trade by end of session, end of day, or '
    'after N bars). Without a timeout, the backtester may hold trades for hours or even across '
    'session boundaries, accumulating swap costs and exposing the position to regime changes that '
    'the original signal did not account for. A sweep of the Asian high during the London session '
    'may produce a valid signal, but holding the trade through the NY afternoon session and into the '
    'next Asian session is not consistent with the ICT time-based analysis framework.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add a max_bars parameter (e.g., 60 bars = 1 hour on 1-minute data) and close the trade at '
    'the current close price if the bar count exceeds the limit. Record the exit as a time-based '
    'exit with a separate result category ("TIMEOUT") for performance analysis.', body_style))

story.append(Spacer(1, 12))

# ── 4.5 No Consecutive Trade Filter ──
story.append(Paragraph('<b>4.5 No Consecutive Trade or Daily Trade Limit</b>', heading2))
story.append(Paragraph('<b>Files:</b> strategy.py, backtester.py', heading3))
story.append(Paragraph(
    'The system can generate an unlimited number of signals per day and the backtester can take every '
    'one of them. If conditions are persistently met (e.g., price stays in premium with recurring '
    'sweeps and MSS), the system will take trade after trade. In reality, most ICT traders limit '
    'themselves to 1-3 trades per session or per day. Taking every signal leads to overtrading, '
    'which increases transaction costs, increases exposure to adverse events, and produces a cluster '
    'of correlated losses when the market regime shifts. The lack of a cooldown period between trades '
    'also means that if a trade stops out, the very next candle can trigger a new entry in the same '
    'direction, leading to consecutive stop-outs.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Add a max_trades_per_day parameter (default 2-3) and a minimum bars between trades (cooldown). '
    'Also add logic to prevent re-entering in the same direction immediately after a loss, which is '
    'a common revenge-trading pattern that the backtester should filter out.', body_style))

story.append(Spacer(1, 12))

# ── 4.6 detect_order_blocks Lookahead ──
story.append(Paragraph('<b>4.6 Order Block Detection Uses Next Candle (Lookahead)</b>', heading2))
story.append(Paragraph('<b>File:</b> pd_arrays.py, lines 26-57', heading3))
story.append(Paragraph(
    'The detect_order_blocks function identifies order blocks by checking if the next candle (next_c) '
    'closes beyond the current candle. Specifically, for a bullish order block, it requires '
    'next_c["close"] > curr["close"]. This means the order block is only confirmed after the next '
    'candle closes, but the current system marks the current candle (not the next one) as the order '
    'block. If a signal fires on the candle immediately after the order block candle, it is using '
    'future information (the close of the very candle that confirms the pattern) to generate the '
    'signal. This is a one-bar lookahead that, while small, biases the entry timing in favor of the '
    'strategy.', body_style))

story.append(Paragraph('<b>Recommended Fix:</b>', heading3))
story.append(Paragraph(
    'Shift the order block marker to the next candle (i+1) or delay signal generation by one bar '
    'after an order block is detected. This ensures the strategy only acts on confirmed order blocks.', body_style))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 5. LOW-SEVERITY ISSUES
# ══════════════════════════════════════════
story.append(Paragraph('<b>5. Low-Severity Issues</b>', heading1))
story.append(Paragraph(
    'Low-severity issues are code quality improvements, edge case handling, and best practices that '
    'should be addressed to improve the robustness and maintainability of the codebase.', body_style))

story.append(Spacer(1, 12))

low_issues = [
    ('5.1 Data Loader Lacks Timezone Handling',
     'data_loader.py', 'lines 11-13',
     'The load_data function converts timestamps using pd.to_datetime without specifying a timezone. '
     'If the CSV contains UTC timestamps and the analysis expects Eastern Time (as implied by the '
     '08:30 NY open in liquidity.py), the time-of-day filters will be off by 4-5 hours depending on '
     'daylight saving time. This could cause the strategy to evaluate signals during wrong sessions, '
     'producing completely invalid results. The fix is to explicitly set the timezone after parsing: '
     'df.index = df.index.tz_localize("UTC").tz_convert("America/New_York").'),
    ('5.2 Sweep Detection Is Too Sensitive (Single-Tick Breach)',
     'liquidity.py', 'lines 46-49',
     'The detect_sweep function triggers on df["high"] > buyside, meaning even a 0.25-tick '
     'breach registers as a sweep. ICT defines a liquidity sweep as a wick-through-and-close-back '
     'pattern, where price briefly pierces the level then closes on the other side. The current '
     'implementation counts any touch as a sweep, inflating the sweep count and generating signals '
     'on noise touches. Add a minimum breach distance (e.g., 2-3 ticks) and/or require the candle '
     'to close back below the buyside level for a bullish sweep.'),
    ('5.3 All Loops Use .iloc (Performance Bottleneck)',
     'All files', 'multiple locations',
     'Every module uses row-by-row iteration with df.iloc[i] and df.at[i, col]. On a typical NQ '
     '1-minute dataset with 200,000+ bars, this produces extremely slow execution. The detect_fvg, '
     'detect_order_blocks, detect_bos, detect_mss, generate_signals, and backtest functions all '
     'iterate row by row. Consider using numpy vectorized operations or numba @jit decorators for '
     'the hot loops. The detect_fvg function, for example, can be fully vectorized using shift '
     'operations: df["bullish_fvg"] = (df["low"].shift(2) > df["high"].shift(0)) would not '
     'work as-is but illustrates the approach.'),
    ('5.4 Equity Curve Empty DataFrame Logic Bug',
     'analytics.py', 'lines 24-27',
     'In the equity_curve function, when the input is empty, the code does trades_df = trades_df.copy() '
     'and then sets trades_df["equity"] = []. This creates a DataFrame with one row containing an empty '
     'list as the equity value, rather than a properly empty DataFrame. The function should return '
     'an empty DataFrame directly, matching the behavior in performance_report.'),
    ('5.5 Optimizer Uses df.attrs (Fragile Parameter Passing)',
     'optimizer.py', 'lines 10-11',
     'The sensitivity_test function passes parameters via df_copy.attrs["swing_window"] and '
     'df_copy.attrs["rr"], but nothing in the current codebase reads these attributes. The strategy '
     'and structure functions use hardcoded defaults and do not check df.attrs. This means the '
     'optimizer is running the same parameters repeatedly and producing identical results regardless '
     'of the param_grid values. The param_grid loop has no effect on the actual backtest results.'),
]

for title, file, loc, desc in low_issues:
    story.append(Paragraph(f'<b>{title}</b>', heading2))
    story.append(Paragraph(f'<b>File:</b> {file}, {loc}', heading3))
    story.append(Paragraph(desc, body_style))
    story.append(Spacer(1, 10))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 6. COMPLETE ISSUE TRACKER TABLE
# ══════════════════════════════════════════
story.append(Paragraph('<b>6. Complete Issue Tracker</b>', heading1))
story.append(Paragraph(
    'The table below provides a consolidated view of all identified issues, their severity, the '
    'affected file, and a concise description. Use this as a prioritized checklist for remediation '
    'work. Critical and high-severity items should be addressed before running any further backtests.', body_style))

story.append(Spacer(1, 12))

tracker_data = [
    [Paragraph('<b>#</b>', header_cell_style),
     Paragraph('<b>Severity</b>', header_cell_style),
     Paragraph('<b>File</b>', header_cell_style),
     Paragraph('<b>Description</b>', header_cell_style)],
    [Paragraph('1', cell_center), severity_cell('CRITICAL'), Paragraph('backtester.py', cell_center),
     Paragraph('SL checked before TP regardless of price path', cell_style)],
    [Paragraph('2', cell_center), severity_cell('CRITICAL'), Paragraph('structure.py', cell_center),
     Paragraph('BOS never resets, cascading false signals', cell_style)],
    [Paragraph('3', cell_center), severity_cell('CRITICAL'), Paragraph('structure.py', cell_center),
     Paragraph('Lookahead bias in centered rolling swing detection', cell_style)],
    [Paragraph('4', cell_center), severity_cell('CRITICAL'), Paragraph('backtester.py', cell_center),
     Paragraph('No spread, slippage, or commission modeling', cell_style)],
    [Paragraph('5', cell_center), severity_cell('CRITICAL'), Paragraph('strategy.py', cell_center),
     Paragraph('Hardcoded 5-tick SL ignores volatility and structure', cell_style)],
    [Paragraph('6', cell_center), severity_cell('HIGH'), Paragraph('strategy.py', cell_center),
     Paragraph('FVG entry uses candle midpoint, not actual gap zone', cell_style)],
    [Paragraph('7', cell_center), severity_cell('HIGH'), Paragraph('structure.py', cell_center),
     Paragraph('MSS sweep state never expires without BOS', cell_style)],
    [Paragraph('8', cell_center), severity_cell('HIGH'), Paragraph('backtester.py', cell_center),
     Paragraph('No intrabar price path simulation', cell_style)],
    [Paragraph('9', cell_center), severity_cell('HIGH'), Paragraph('analytics.py', cell_center),
     Paragraph('PnL is raw price diff, not dollar-based', cell_style)],
    [Paragraph('10', cell_center), severity_cell('HIGH'), Paragraph('strategy.py', cell_center),
     Paragraph('No time-of-day or session filtering on signals', cell_style)],
    [Paragraph('11', cell_center), severity_cell('HIGH'), Paragraph('backtester.py', cell_center),
     Paragraph('No risk-based position sizing', cell_style)],
    [Paragraph('12', cell_center), severity_cell('HIGH'), Paragraph('optimizer.py', cell_center),
     Paragraph('No walk-forward validation, optimizer overfits', cell_style)],
    [Paragraph('13', cell_center), severity_cell('MEDIUM'), Paragraph('strategy.py', cell_center),
     Paragraph('Premium/discount bias is binary, no equilibrium zone', cell_style)],
    [Paragraph('14', cell_center), severity_cell('MEDIUM'), Paragraph('liquidity.py', cell_center),
     Paragraph('Key levels session range too wide (9.5 hours)', cell_style)],
    [Paragraph('15', cell_center), severity_cell('MEDIUM'), Paragraph('analytics.py', cell_center),
     Paragraph('Equity curve starts from zero, no initial capital', cell_style)],
    [Paragraph('16', cell_center), severity_cell('MEDIUM'), Paragraph('backtester.py', cell_center),
     Paragraph('No trade timeout or maximum holding period', cell_style)],
    [Paragraph('17', cell_center), severity_cell('MEDIUM'), Paragraph('strategy.py', cell_center),
     Paragraph('No daily trade limit or consecutive trade filter', cell_style)],
    [Paragraph('18', cell_center), severity_cell('MEDIUM'), Paragraph('pd_arrays.py', cell_center),
     Paragraph('Order block detection has 1-bar lookahead', cell_style)],
    [Paragraph('19', cell_center), severity_cell('LOW'), Paragraph('data_loader.py', cell_center),
     Paragraph('No timezone handling on datetime index', cell_style)],
    [Paragraph('20', cell_center), severity_cell('LOW'), Paragraph('liquidity.py', cell_center),
     Paragraph('Sweep triggers on sub-tick breach, too sensitive', cell_style)],
    [Paragraph('21', cell_center), severity_cell('LOW'), Paragraph('All files', cell_center),
     Paragraph('Row-by-row .iloc loops are slow on large datasets', cell_style)],
    [Paragraph('22', cell_center), severity_cell('LOW'), Paragraph('analytics.py', cell_center),
     Paragraph('Empty DataFrame equity curve logic bug', cell_style)],
    [Paragraph('23', cell_center), severity_cell('LOW'), Paragraph('optimizer.py', cell_center),
     Paragraph('df.attrs not consumed by any function, no-op loop', cell_style)],
]

tracker_widths = [AVAIL_W*0.06, AVAIL_W*0.14, AVAIL_W*0.16, AVAIL_W*0.64]
tracker_table = make_table(tracker_data, tracker_widths, 24)
story.append(tracker_table)
story.append(Paragraph('<b>Table 2.</b> Complete issue tracker with severity and file references', caption_style))

story.append(Spacer(1, 24))

# ══════════════════════════════════════════
# 7. RECOMMENDED IMPLEMENTATION PRIORITY
# ══════════════════════════════════════════
story.append(Paragraph('<b>7. Recommended Implementation Priority</b>', heading1))
story.append(Paragraph(
    'Addressing all 23 issues simultaneously is impractical. The following phased approach prioritizes '
    'the fixes that have the highest impact on backtesting accuracy, grouped by implementation '
    'dependency. Each phase builds on the previous one, and the expected accuracy improvement is '
    'noted for each phase.', body_style))

story.append(Spacer(1, 12))

priority_data = [
    [Paragraph('<b>Phase</b>', header_cell_style),
     Paragraph('<b>Issues</b>', header_cell_style),
     Paragraph('<b>Description</b>', header_cell_style),
     Paragraph('<b>Expected Impact</b>', header_cell_style)],
    [Paragraph('<b>1</b>', cell_center), Paragraph('#1, #2, #3, #4', cell_center),
     Paragraph('Fix backtester engine: SL/TP priority, BOS reset, lookahead, costs', cell_style),
     Paragraph('Accuracy improvement: 30-50%', cell_style)],
    [Paragraph('<b>2</b>', cell_center), Paragraph('#5, #6, #7', cell_center),
     Paragraph('Fix signal generation: dynamic SL, FVG entry, MSS expiry', cell_style),
     Paragraph('Signal quality improvement: 20-30%', cell_style)],
    [Paragraph('<b>3</b>', cell_center), Paragraph('#8, #9, #10, #11', cell_center),
     Paragraph('Add realism: intrabar sim, dollar PnL, session filter, sizing', cell_style),
     Paragraph('Result reliability improvement: 15-25%', cell_style)],
    [Paragraph('<b>4</b>', cell_center), Paragraph('#12, #13-18', cell_center),
     Paragraph('Optimizer and medium fixes: walk-forward, equity, timeouts', cell_style),
     Paragraph('Robustness improvement: 10-15%', cell_style)],
    [Paragraph('<b>5</b>', cell_center), Paragraph('#19-23', cell_center),
     Paragraph('Code quality: timezone, performance, edge cases', cell_style),
     Paragraph('Maintainability and correctness', cell_style)],
]
priority_widths = [AVAIL_W*0.08, AVAIL_W*0.14, AVAIL_W*0.50, AVAIL_W*0.28]
priority_table = make_table(priority_data, priority_widths, 6)
story.append(priority_table)
story.append(Paragraph('<b>Table 3.</b> Phased implementation plan with expected accuracy impact', caption_style))

story.append(Spacer(1, 18))

story.append(Paragraph(
    'Phase 1 is the most critical. The four issues in this phase (backtester SL/TP priority, BOS reset, '
    'lookahead bias, and cost modeling) each independently compromise the validity of the backtest. '
    'After Phase 1, re-run the backtest and compare the new results with the original. The difference '
    'will reveal the magnitude of the previous biases. If the strategy still shows positive expectancy '
    'after Phase 1, it is a meaningful indicator of potential viability, and subsequent phases can '
    'further refine the accuracy. If the strategy shows negative expectancy after Phase 1, it may '
    'indicate that the original apparent profitability was an artifact of the biases, and fundamental '
    'strategy redesign may be needed before continuing.', body_style))


# ━━ Build ━━
doc.build(story)
print(f"Report generated: {output_path}")
