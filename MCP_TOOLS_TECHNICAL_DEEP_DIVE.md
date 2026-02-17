# MCP Finance - Technical Deep Dive: All 9 Tools

**Complete technical and financial logic documentation for all MCP tools**

---

## Table of Contents

1. [analyze_security](#1-analyze_security)
2. [analyze_fibonacci](#2-analyze_fibonacci)
3. [get_trade_plan](#3-get_trade_plan)
4. [compare_securities](#4-compare_securities)
5. [screen_securities](#5-screen_securities)
6. [scan_trades](#6-scan_trades)
7. [portfolio_risk](#7-portfolio_risk)
8. [morning_brief](#8-morning_brief)
9. [options_risk_analysis](#9-options_risk_analysis)

---

## 1. analyze_security

### Overview
Multi-layered technical analysis tool that detects 150+ signals across 8 categories using classical technical indicators and pattern recognition.

### Technical Logic

#### A. Data Fetching and Preparation
```python
# Data source: Yahoo Finance via yfinance
df = fetcher.fetch(symbol, period)  # OHLCV data

# Validation:
if len(df) < MIN_DATA_POINTS (50):
    raise InsufficientDataError
```

#### B. Indicator Calculation (Full Suite)

**1. Moving Averages**
```python
# Simple Moving Average
SMA_n = Σ(Close[i:i+n]) / n

# Exponential Moving Average
EMA_n = Close * k + EMA_prev * (1 - k)
where k = 2/(n+1)

# Periods: 5, 10, 20, 50, 100, 200
```

**2. Relative Strength Index (RSI)**
```python
# 14-period RSI with safe division
delta = Close.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

RS = gain / (loss + 1e-10)  # epsilon prevents division by zero
RSI = 100 - (100 / (1 + RS))

# Thresholds:
# RSI < 20: EXTREME OVERSOLD (Strong Buy)
# RSI < 30: OVERSOLD (Buy)
# RSI > 70: OVERBOUGHT (Sell)
# RSI > 80: EXTREME OVERBOUGHT (Strong Sell)
```

**3. MACD (Moving Average Convergence Divergence)**
```python
# Standard 12-26-9 configuration
EMA_12 = EMA(Close, 12)
EMA_26 = EMA(Close, 26)

MACD = EMA_12 - EMA_26
MACD_Signal = EMA(MACD, 9)
MACD_Histogram = MACD - MACD_Signal

# Signals:
# MACD crosses above Signal → Bullish
# MACD crosses below Signal → Bearish
# MACD crosses above 0 → Strong Bullish
# MACD crosses below 0 → Strong Bearish
```

**4. Bollinger Bands**
```python
# 20-period, 2 standard deviations
BB_Middle = SMA(Close, 20)
BB_Std = StdDev(Close, 20)

BB_Upper = BB_Middle + (2 * BB_Std)
BB_Lower = BB_Middle - (2 * BB_Std)
BB_Width = BB_Upper - BB_Lower

# Signals:
# Price at Lower BB (≤ 1.01x) → Bullish
# Price at Upper BB (≥ 0.99x) → Bearish
```

**5. Stochastic Oscillator**
```python
# 14-period %K, 3-period %D
Low_14 = Rolling_Min(Low, 14)
High_14 = Rolling_Max(High, 14)

%K = 100 * (Close - Low_14) / (High_14 - Low_14)
%D = SMA(%K, 3)

# Thresholds:
# %K < 20: OVERSOLD (Bullish)
# %K > 80: OVERBOUGHT (Bearish)
```

**6. Average Directional Index (ADX)**
```python
# True Range calculation
TR = max(
    High - Low,
    abs(High - Close_prev),
    abs(Low - Close_prev)
)

# Directional Movement
+DM = High - High_prev (if > 0, else 0)
-DM = Low_prev - Low (if > 0, else 0)

# Directional Indicators (14-period)
+DI = 100 * SMA(+DM, 14) / SMA(TR, 14)
-DI = 100 * SMA(-DM, 14) / SMA(TR, 14)

# ADX calculation
DX = 100 * abs(+DI - -DI) / (+DI + -DI)
ADX = SMA(DX, 14)

# Thresholds:
# ADX > 25: TRENDING (Strong directional move)
# ADX > 40: STRONG TREND
# ADX < 20: NO TREND (Choppy market)
```

**7. Average True Range (ATR)**
```python
# 14-period ATR for volatility measurement
TR = max(
    High - Low,
    abs(High - Close_prev),
    abs(Low - Close_prev)
)

ATR = SMA(TR, 14)
ATR_Percent = (ATR / Close) * 100
```

**8. Volume Indicators**
```python
# Volume Moving Averages
Volume_MA_20 = SMA(Volume, 20)
Volume_MA_50 = SMA(Volume, 50)

# On-Balance Volume (OBV)
OBV = Σ(sign(Close_change) * Volume)

# Volume signals:
# Volume > 3x average: EXTREME VOLUME SPIKE
# Volume > 2x average: VOLUME SPIKE
```

#### C. Signal Detection (150+ Signals)

**Signal Categories**:
1. **MA_CROSS** - Moving average crossovers
2. **MA_TREND** - MA alignment patterns
3. **RSI** - Overbought/oversold conditions
4. **MACD** - MACD crossovers
5. **BOLLINGER** - Band touches
6. **STOCHASTIC** - Oscillator extremes
7. **VOLUME** - Volume spikes
8. **TREND** - ADX-based trend strength

**Example Signal Logic**:
```python
# Golden Cross (Strong Bullish)
if prev_SMA50 <= prev_SMA200 and current_SMA50 > current_SMA200:
    signal = MutableSignal(
        signal="GOLDEN CROSS",
        description="50 MA crossed above 200 MA",
        strength="STRONG BULLISH",
        category="MA_CROSS"
    )

# MA Alignment (Strong Bullish)
if SMA_10 > SMA_20 > SMA_50:
    signal = MutableSignal(
        signal="MA ALIGNMENT BULLISH",
        description="10 > 20 > 50 SMA",
        strength="STRONG BULLISH",
        category="MA_TREND"
    )
```

#### D. Signal Ranking

**Rule-Based Scoring**:
```python
# Base score from strength
strength_scores = {
    "EXTREME": 85,
    "STRONG": 75,
    "SIGNIFICANT": 65,
    "VERY": 65,
    "BULLISH": 55,
    "BEARISH": 55,
}

# Category bonuses
category_bonuses = {
    "MA_CROSS": +10,  # Crossovers are significant
    "MACD": +10,      # Momentum is important
    "VOLUME": +10,    # Volume confirms moves
}

# Final score (capped at 95)
score = min(base_score + category_bonus, 95)
```

**AI-Powered Scoring (Optional)**:
```python
# Gemini 2.0 Flash analyzes signals in context
prompt = f"""
Score these {len(signals)} signals for {symbol}
Market: ${price:.2f} ({change:+.2f}%)
RSI: {rsi:.1f}, MACD: {macd:.2f}, ADX: {adx:.1f}

Return JSON with scores 0-100 and reasoning.
"""

# AI provides:
# - Contextualized scores
# - Overall outlook (BULLISH/BEARISH/NEUTRAL)
# - Action recommendation (BUY/SELL/HOLD)
# - Confidence level
```

#### E. Output Structure

```python
{
    "symbol": "AAPL",
    "timestamp": "2026-02-08T12:00:00Z",
    "price": 185.42,
    "change_pct": 1.23,
    "indicators": {
        "rsi": 45.2,
        "macd": 0.85,
        "macd_signal": 0.62,
        "macd_hist": 0.23,
        "sma20": 182.15,
        "sma50": 179.30,
        "ema20": 183.45,
        "bb_upper": 190.25,
        "bb_lower": 174.05,
        "adx": 32.5,
        "stoch_k": 55.8,
        "stoch_d": 52.3,
        "atr": 3.45
    },
    "signals": [
        {
            "signal": "MACD BULL CROSS",
            "strength": "BULLISH",
            "category": "MACD",
            "score": 75,
            "rank": 1
        },
        # ... top 50 signals
    ],
    "signal_count": 127,
    "ai_score": 68,
    "ai_outlook": "BULLISH",
    "ai_action": "BUY",
    "ai_confidence": "MEDIUM"
}
```

### Summary Paragraphs

The analyze_security tool is a comprehensive technical analysis engine that processes price and volume data through a multi-stage pipeline. It begins by fetching OHLCV (Open-High-Low-Close-Volume) data from Yahoo Finance, validates sufficient data points exist (minimum 50), and calculates 8 categories of technical indicators including moving averages, momentum oscillators (RSI, MACD, Stochastic), volatility bands (Bollinger Bands, ATR), trend indicators (ADX), and volume metrics (OBV). Each indicator is calculated using industry-standard formulas with carefully tuned parameters such as 14-period RSI, 12-26-9 MACD, and 20-period Bollinger Bands with 2 standard deviations.

The signal detection layer scans for 150+ distinct trading signals by monitoring crossovers, extreme values, and pattern formations across all calculated indicators. Signals are categorized into 8 types (MA_CROSS, MA_TREND, RSI, MACD, BOLLINGER, STOCHASTIC, VOLUME, TREND) and assigned strength levels ranging from "STRONG BULLISH" to "STRONG BEARISH". For example, a Golden Cross (50-day MA crossing above 200-day MA) generates a "STRONG BULLISH" signal, while RSI dropping below 20 triggers an "EXTREME OVERSOLD" bullish signal. Each signal includes contextual information such as the exact indicator values that triggered it, making the output actionable for traders.

The ranking system employs both rule-based and AI-powered approaches to prioritize signals by relevance and reliability. Rule-based scoring assigns base points (55-85) based on signal strength and adds category bonuses (+10 for crossovers, momentum, and volume confirmation), capping the total at 95. Optional AI ranking using Gemini 2.0 Flash analyzes all signals in market context, providing contextualized scores, an overall outlook (BULLISH/BEARISH/NEUTRAL), action recommendations (BUY/SELL/HOLD), and confidence levels. The final output includes the top 50 ranked signals along with current indicator values, an aggregate score, and metadata, providing traders with a complete technical picture in a single API call.

---

## 2. analyze_fibonacci

### Overview
Advanced Fibonacci analysis system detecting price relationships across multiple timeframe windows (20, 50, 100, 200 periods) using dynamic swing detection and tolerance calculations.

### Technical Logic

#### A. Swing Point Detection

```python
class SwingPointDetector:
    """Detects swing highs/lows across multiple windows"""

    def detect_swings(self, window: int = 50):
        """
        Identify swing high and swing low within lookback window

        Args:
            window: Lookback period (20, 50, 100, 200)

        Returns:
            (swing_high, swing_low, high_idx, low_idx)
        """
        highs = df['High'].iloc[-window:]
        lows = df['Low'].iloc[-window:]

        swing_high = highs.max()
        swing_low = lows.min()
        high_idx = highs.idxmax()  # Index of highest point
        low_idx = lows.idxmin()    # Index of lowest point

        return (swing_high, swing_low, high_idx, low_idx)

    def get_trend_direction(self, window: int = 50):
        """
        Determine trend based on swing sequence

        Logic:
        - If low came before high → UPTREND (bullish)
        - If high came before low → DOWNTREND (bearish)
        """
        _, _, high_idx, low_idx = self.detect_swings(window)

        return 'UP' if low_idx < high_idx else 'DOWN'
```

#### B. Fibonacci Level Calculation

**Standard Fibonacci Ratios**:
```python
FIBONACCI_RATIOS = {
    # Retracement levels (pullback in uptrend)
    'RETRACEMENT': {
        '23.6%': 0.236,
        '38.2%': 0.382,
        '50.0%': 0.500,
        '61.8%': 0.618,  # Golden ratio
        '78.6%': 0.786
    },

    # Extension levels (targets beyond swing)
    'EXTENSION': {
        '127.2%': 1.272,
        '141.4%': 1.414,
        '161.8%': 1.618,  # Golden ratio extension
        '200.0%': 2.000,
        '261.8%': 2.618
    }
}
```

**Level Calculation**:
```python
def calculate_fib_levels(swing_high, swing_low, fib_type):
    """
    Calculate Fibonacci levels from swing points

    For RETRACEMENT (uptrend):
    Level = swing_high - (swing_high - swing_low) * ratio

    For EXTENSION (uptrend):
    Level = swing_high + (swing_high - swing_low) * (ratio - 1)
    """
    swing_range = swing_high - swing_low

    levels = {}

    if fib_type == 'RETRACEMENT':
        # Retracement: levels between high and low
        for name, ratio in FIBONACCI_RATIOS['RETRACEMENT'].items():
            level_price = swing_high - (swing_range * ratio)
            levels[name] = {
                'price': level_price,
                'ratio': ratio,
                'fib_type': 'RETRACEMENT'
            }

    elif fib_type == 'EXTENSION':
        # Extension: levels beyond swing high
        for name, ratio in FIBONACCI_RATIOS['EXTENSION'].items():
            level_price = swing_high + (swing_range * (ratio - 1))
            levels[name] = {
                'price': level_price,
                'ratio': ratio,
                'fib_type': 'EXTENSION'
            }

    return levels
```

**Example Calculation**:
```
Given:
Swing High = $200.00
Swing Low = $180.00
Swing Range = $20.00

Retracement Levels:
- 23.6%: $200.00 - ($20.00 × 0.236) = $195.28
- 38.2%: $200.00 - ($20.00 × 0.382) = $192.36
- 50.0%: $200.00 - ($20.00 × 0.500) = $190.00
- 61.8%: $200.00 - ($20.00 × 0.618) = $187.64  ← Golden ratio
- 78.6%: $200.00 - ($20.00 × 0.786) = $184.28

Extension Levels:
- 127.2%: $200.00 + ($20.00 × 0.272) = $205.44
- 161.8%: $200.00 + ($20.00 × 0.618) = $212.36  ← Golden ratio
- 261.8%: $200.00 + ($20.00 × 1.618) = $232.36
```

#### C. Adaptive Tolerance

```python
def calculate_adaptive_tolerance(df, atr_multiple=0.5):
    """
    Dynamic tolerance based on volatility

    Tighter tolerance in low volatility (precision)
    Wider tolerance in high volatility (flexibility)

    Args:
        df: Price dataframe with ATR calculated
        atr_multiple: Multiplier for ATR (default 0.5)

    Returns:
        Tolerance as percentage of price
    """
    current_price = df['Close'].iloc[-1]
    atr = df['ATR'].iloc[-1]

    # Tolerance = (ATR * multiplier) / price
    tolerance_percent = (atr * atr_multiple) / current_price * 100

    # Clamp between 0.5% and 2.0%
    tolerance = max(0.5, min(2.0, tolerance_percent))

    return tolerance
```

**Example**:
```
Low Volatility Stock:
ATR = $1.50, Price = $150.00
Tolerance = (1.50 × 0.5) / 150 × 100 = 0.50%

High Volatility Stock:
ATR = $5.00, Price = $100.00
Tolerance = (5.00 × 0.5) / 100 × 100 = 2.50% → capped at 2.0%
```

#### D. Signal Generation

```python
class PriceLevelSignals:
    """Generate signals when price touches Fibonacci levels"""

    def generate(self, ctx: FibonacciContext):
        signals = []

        # Check multiple timeframe windows
        for window in [20, 50, 100, 200]:
            levels = ctx.get_fib_levels(window)
            tolerance = ctx.get_tolerance()

            for level_name, level_data in levels.items():
                if self.price_at_level(
                    current_price,
                    level_data['price'],
                    tolerance
                ):
                    # Price is touching this Fibonacci level
                    signal = FibonacciSignal(
                        signal=f"FIB {level_data['fib_type']} {level_name}",
                        description=f"Price at {level_name} "
                                   f"{level_data['fib_type'].lower()} "
                                   f"({window}-period swing)",
                        strength=self.get_strength(level_data),
                        category='FIB_PRICE_LEVEL',
                        value=level_data['price'],
                        metadata={
                            'distance_pct': abs(current_price - level_data['price']) / current_price * 100,
                            'window': window,
                            'ratio': level_data['ratio']
                        }
                    )
                    signals.append(signal)

        return signals

    def price_at_level(self, price, level, tolerance):
        """
        Check if price is within tolerance of level

        Args:
            price: Current price
            level: Fibonacci level price
            tolerance: Tolerance percentage (e.g., 1.0 = 1%)

        Returns:
            True if price within tolerance
        """
        lower_bound = level * (1 - tolerance / 100)
        upper_bound = level * (1 + tolerance / 100)

        return lower_bound <= price <= upper_bound
```

#### E. Advanced Fibonacci Signals

**1. Golden Pocket (61.8% - 65%)**
```python
# High probability reversal zone
golden_pocket_zone = (
    fib_61_8_level,  # 61.8% retracement
    fib_65_0_level   # 65.0% retracement
)

if price in golden_pocket_zone and trend == 'UP':
    signal = "GOLDEN POCKET LONG"
    strength = "STRONG BULLISH"
```

**2. Fibonacci Confluence**
```python
# Multiple Fib levels converging at same price
confluence_count = 0
for window in [50, 100, 200]:
    if price_near_level(price, fib_level[window], tolerance):
        confluence_count += 1

if confluence_count >= 2:
    signal = "FIB CONFLUENCE ZONE"
    strength = "VERY SIGNIFICANT"
```

**3. Fibonacci Time Zones**
```python
# Project important dates based on Fibonacci sequence
fib_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

for fib_number in fib_sequence:
    projected_date = swing_date + timedelta(days=fib_number)
    if today == projected_date:
        signal = f"FIB TIME ZONE {fib_number} DAYS"
```

### Summary Paragraphs

The analyze_fibonacci tool implements a sophisticated multi-timeframe Fibonacci analysis system that identifies critical price levels based on mathematical ratios derived from swing points. It employs dynamic swing detection across four lookback windows (20, 50, 100, 200 periods) to identify swing highs and lows, then calculates both retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%) and extension levels (127.2%, 141.4%, 161.8%, 200%, 261.8%). The Golden Ratio (0.618 and 1.618) forms the mathematical foundation, appearing in multiple levels and representing natural proportions found throughout nature and financial markets. The system determines trend direction by analyzing the chronological sequence of swing points—if the swing low occurred before the swing high, the market is classified as an uptrend.

Adaptive tolerance is a key innovation that adjusts precision based on market volatility. The tolerance calculation uses ATR (Average True Range) as a volatility proxy: tolerance = (ATR × 0.5) / price × 100, clamped between 0.5% and 2.0%. This means low-volatility stocks require tighter precision (0.5%) for level detection, while high-volatility stocks use wider tolerance (up to 2.0%) to avoid false negatives. For example, a $150 stock with $1.50 ATR gets 0.5% tolerance (±$0.75), while a $100 stock with $5 ATR gets 2.0% tolerance (±$2.00). This dynamic approach ensures reliable signal detection across different volatility regimes without manual parameter tuning.

The signal generation system produces actionable alerts when current price touches or approaches calculated Fibonacci levels within tolerance thresholds. Each signal includes the specific level (e.g., "FIB RETRACEMENT 61.8%"), the timeframe window (20/50/100/200 periods), distance from the level, and strength classification. Advanced features include Golden Pocket detection (the 61.8%-65% zone known for high-probability reversals), confluence zone identification (when multiple timeframe Fib levels converge at the same price, creating strong support/resistance), and Fibonacci time projections (anticipating important dates based on Fibonacci sequence intervals from the swing point). This comprehensive approach combines geometric price analysis with temporal patterns for a complete Fibonacci trading framework.

---

## 3. get_trade_plan

### Overview
Risk-qualified trade plan generator that assesses market conditions, calculates precise stop levels, and determines risk-to-reward ratios before recommending trades.

### Technical Logic

#### A. Volatility Classification

```python
class ATRVolatilityClassifier:
    """Classify volatility regime using ATR"""

    def classify(self, df):
        """
        Volatility Regime Classification

        Based on ATR as percentage of price:
        - LOW: < 1.5%
        - MEDIUM: 1.5% - 3.0%
        - HIGH: > 3.0%
        """
        current_price = df['Close'].iloc[-1]
        atr = df['ATR'].iloc[-1]

        atr_percent = (atr / current_price) * 100

        if atr_percent < VOLATILITY_LOW_THRESHOLD:  # 1.5%
            return VolatilityRegime.LOW
        elif atr_percent > VOLATILITY_HIGH_THRESHOLD:  # 3.0%
            return VolatilityRegime.HIGH
        else:
            return VolatilityRegime.MEDIUM
```

**Example**:
```
Stock A: Price = $100, ATR = $1.20
ATR% = 1.2% → LOW volatility

Stock B: Price = $50, ATR = $1.25
ATR% = 2.5% → MEDIUM volatility

Stock C: Price = $150, ATR = $5.00
ATR% = 3.33% → HIGH volatility
```

#### B. Bias Determination

```python
def determine_bias(signals):
    """
    Calculate directional bias from signals

    Logic:
    - Count BULLISH vs BEARISH signals
    - Requires clear directional edge (2+ signal difference)
    - Otherwise classified as NEUTRAL
    """
    bullish_count = sum(
        1 for s in signals
        if "BULLISH" in s.strength
    )

    bearish_count = sum(
        1 for s in signals
        if "BEARISH" in s.strength
    )

    if bullish_count > bearish_count + 2:
        return Bias.BULLISH
    elif bearish_count > bullish_count + 2:
        return Bias.BEARISH
    else:
        return Bias.NEUTRAL
```

#### C. Timeframe Selection

```python
class DefaultTimeframeSelector:
    """Select appropriate trading timeframe"""

    def select(self, volatility, adx, signals):
        """
        Timeframe Selection Logic:

        SCALP (minutes-hours):
        - LOW volatility + TRENDING (ADX > 25)
        - Quick moves in calm markets

        DAY (hours-days):
        - MEDIUM volatility + TRENDING
        - Standard intraday trades

        SWING (days-weeks):
        - HIGH volatility OR
        - Strong trend (ADX > 40) OR
        - Strong signal count (> 10)
        """
        signal_count = len(signals)
        is_trending = adx > ADX_TRENDING_THRESHOLD  # 25
        is_strong_trend = adx > ADX_STRONG_TREND_THRESHOLD  # 40

        # SCALP: Low vol + trending
        if volatility == VolatilityRegime.LOW and is_trending:
            return Timeframe.SCALP

        # SWING: High vol OR strong trend OR many signals
        if (volatility == VolatilityRegime.HIGH or
            is_strong_trend or
            signal_count > 10):
            return Timeframe.SWING

        # Default: DAY
        return Timeframe.DAY
```

#### D. Stop Loss Calculation

```python
class ATRStopCalculator:
    """Calculate stop loss based on ATR and timeframe"""

    def calculate(self, df, bias, timeframe):
        """
        ATR-Based Stop Placement

        Stop Distance = ATR × Timeframe Multiplier

        Multipliers:
        - SCALP: 1.0× ATR (tight stop)
        - DAY: 1.5× ATR (moderate stop)
        - SWING: 2.0× ATR (wider stop for overnight risk)

        Stop placement:
        - BULLISH: Stop = Current Price - Stop Distance
        - BEARISH: Stop = Current Price + Stop Distance
        """
        current_price = df['Close'].iloc[-1]
        atr = df['ATR'].iloc[-1]

        # Get timeframe-specific ATR multiple
        atr_multipliers = {
            Timeframe.SCALP: STOP_ATR_SCALP,  # 1.0
            Timeframe.DAY: STOP_ATR_DAY,      # 1.5
            Timeframe.SWING: STOP_ATR_SWING,  # 2.0
        }

        atr_multiple = atr_multipliers[timeframe]
        stop_distance = atr * atr_multiple

        # Validate stop is within reasonable bounds (0.5-3.0 ATR)
        if stop_distance < atr * STOP_MIN_ATR_MULTIPLE:  # 0.5
            stop_distance = atr * STOP_MIN_ATR_MULTIPLE
        if stop_distance > atr * STOP_MAX_ATR_MULTIPLE:  # 3.0
            stop_distance = atr * STOP_MAX_ATR_MULTIPLE

        # Calculate stop price based on bias
        if bias == "bullish":
            stop_price = current_price - stop_distance
        else:  # bearish
            stop_price = current_price + stop_distance

        stop_percent = (stop_distance / current_price) * 100

        return StopLevel(
            price=stop_price,
            distance_atr=atr_multiple,
            distance_percent=stop_percent
        )
```

**Example Calculation**:
```
Given:
Price = $100.00
ATR = $2.50
Timeframe = SWING
Bias = BULLISH

Stop Distance = $2.50 × 2.0 = $5.00
Stop Price = $100.00 - $5.00 = $95.00
Stop % = 5.0%
```

#### E. Target and Risk-to-Reward Calculation

```python
def calculate_target(price, stop_price, bias):
    """
    Target Calculation for Minimum 2:1 R:R

    Risk = abs(Price - Stop)
    Reward = abs(Target - Price)

    Target = Price + (Risk × Preferred_RR_Ratio)

    Where Preferred_RR_Ratio = 2.0 (2:1 reward-to-risk)
    """
    risk = abs(price - stop_price)
    reward = risk * PREFERRED_RR_RATIO  # 2.0

    if bias == Bias.BULLISH:
        target_price = price + reward
    else:  # BEARISH
        target_price = price - reward

    return TargetLevel(
        price=target_price,
        distance_percent=(reward / price) * 100,
        atr_multiple=reward / atr
    )

class DefaultRRCalculator:
    """Calculate risk-to-reward ratio"""

    def calculate(self, price, stop, target):
        """
        R:R Ratio = Reward / Risk

        Risk = abs(Price - Stop)
        Reward = abs(Target - Price)
        Ratio = Reward / Risk
        """
        risk = abs(price - stop)
        reward = abs(target - price)

        ratio = reward / risk if risk > 0 else 0

        return RiskRewardMetrics(
            risk_dollars=risk,
            reward_dollars=reward,
            ratio=ratio
        )
```

**Example**:
```
Entry Price: $100.00
Stop Loss: $95.00
Risk: $5.00

Target for 2:1 R:R:
Reward = $5.00 × 2.0 = $10.00
Target = $100.00 + $10.00 = $110.00

R:R Ratio = $10.00 / $5.00 = 2.0:1 ✓
```

#### F. Trade Suppression Rules

```python
class DefaultSuppressionEvaluator:
    """Evaluate if trade should be suppressed"""

    def evaluate(self, assessment, signals):
        """
        Suppression Conditions:

        1. Poor Risk-to-Reward
           - R:R < 1.5:1 minimum

        2. No Clear Trend
           - ADX < 20 (choppy market)

        3. Conflicting Signals
           - > 40% of signals contradict bias

        4. Low Volume
           - Volume < 50% of 20-day average

        5. Wide Stop
           - Stop distance > 10% of entry price
        """
        suppressions = []

        # Check 1: Risk-to-Reward
        if assessment.risk_reward.ratio < MIN_RR_RATIO:  # 1.5
            suppressions.append(
                f"Poor R:R ({assessment.risk_reward.ratio:.2f}:1)"
            )

        # Check 2: Trend Strength
        if assessment.metrics.adx < ADX_NO_TREND_THRESHOLD:  # 20
            suppressions.append(
                f"Weak trend (ADX {assessment.metrics.adx:.1f})"
            )

        # Check 3: Signal Conflict
        bullish = sum(1 for s in signals if "BULLISH" in s.strength)
        bearish = sum(1 for s in signals if "BEARISH" in s.strength)
        total = bullish + bearish

        conflict_ratio = min(bullish, bearish) / total if total > 0 else 0

        if conflict_ratio > MAX_CONFLICTING_SIGNALS_RATIO:  # 0.4
            suppressions.append(
                f"Signal conflict ({conflict_ratio:.1%})"
            )

        # Check 4: Volume
        if assessment.metrics.volume_ratio < MIN_VOLUME_RATIO:  # 0.5
            suppressions.append(
                f"Low volume ({assessment.metrics.volume_ratio:.2f}x avg)"
            )

        # Check 5: Wide Stop
        if assessment.stop.distance_percent > 10.0:
            suppressions.append(
                f"Wide stop ({assessment.stop.distance_percent:.1f}%)"
            )

        return tuple(suppressions)
```

#### G. Risk Quality Assessment

```python
def assess_quality(risk_reward, metrics):
    """
    Risk Quality Scoring (0-9 points)

    R:R Ratio Points:
    - ≥ 2.5:1 → +3 points (excellent)
    - ≥ 2.0:1 → +2 points (good)
    - ≥ 1.5:1 → +1 point (acceptable)

    Trend Points:
    - ADX ≥ 40 → +3 points (strong trend)
    - ADX ≥ 25 → +2 points (trending)
    - ADX ≥ 20 → +1 point (weak trend)

    Volatility Points:
    - LOW → +2 points (predictable)
    - MEDIUM → +1 point (moderate)
    - HIGH → +0 points (unpredictable)

    Quality Levels:
    - 7-9 points: HIGH quality
    - 4-6 points: MEDIUM quality
    - 0-3 points: LOW quality
    """
    score = 0

    # R:R scoring
    if risk_reward.ratio >= 2.5:
        score += 3
    elif risk_reward.ratio >= 2.0:
        score += 2
    elif risk_reward.ratio >= 1.5:
        score += 1

    # Trend scoring
    if metrics.adx >= 40:
        score += 3
    elif metrics.adx >= 25:
        score += 2
    elif metrics.adx >= 20:
        score += 1

    # Volatility scoring
    if metrics.volatility_regime == VolatilityRegime.LOW:
        score += 2
    elif metrics.volatility_regime == VolatilityRegime.MEDIUM:
        score += 1

    # Determine quality
    if score >= 7:
        return RiskQuality.HIGH
    elif score >= 4:
        return RiskQuality.MEDIUM
    else:
        return RiskQuality.LOW
```

#### H. Complete Trade Plan Output

```python
{
    "symbol": "AAPL",
    "timestamp": "2026-02-08T12:00:00Z",
    "trade_plans": [
        {
            "timeframe": "swing",
            "bias": "bullish",
            "risk_quality": "high",
            "entry_price": 185.42,
            "stop_price": 176.18,          # 2.0× ATR below entry
            "target_price": 203.90,         # 2:1 R:R
            "invalidation_price": 174.50,   # Structure break level
            "risk_reward_ratio": 2.00,
            "expected_move_percent": 9.96,
            "max_loss_percent": 4.98,
            "vehicle": "stock",
            "primary_signal": "GOLDEN CROSS",
            "supporting_signals": [
                "MA ALIGNMENT BULLISH",
                "MACD BULL CROSS",
                "VOLUME SPIKE 2X"
            ]
        }
    ],
    "has_trades": true,
    "risk_assessment": {
        "metrics": {
            "atr": 4.62,
            "atr_percent": 2.49,
            "volatility_regime": "medium",
            "adx": 32.5,
            "is_trending": true,
            "volume_ratio": 1.84
        }
    }
}
```

### Summary Paragraphs

The get_trade_plan tool is a comprehensive risk management system that generates trade-ready execution plans with precise entry, stop, and target levels. It begins by classifying the current volatility regime using ATR as a percentage of price (LOW < 1.5%, MEDIUM 1.5-3.0%, HIGH > 3.0%), which determines appropriate position sizing and timeframe selection. The bias determination analyzes detected signals to establish directional edge, requiring a clear majority (2+ signal difference) between bullish and bearish indicators to avoid trading in choppy, directionless conditions. Timeframe selection then matches the volatility environment with appropriate holding periods: SCALP for low-volatility trending markets, DAY for medium volatility, and SWING for high volatility or strong trend conditions (ADX > 40).

The stop loss calculation uses ATR-based dynamic positioning with timeframe-specific multipliers: 1.0× ATR for scalp trades (tight stops for quick exits), 1.5× ATR for day trades (moderate stops), and 2.0× ATR for swing trades (wider stops to accommodate overnight volatility). Stop placement accounts for directional bias—bullish trades place stops below entry by the ATR-derived distance, while bearish trades place stops above. All stops are validated to fall within reasonable bounds (0.5-3.0× ATR) to prevent both premature stops (< 0.5× ATR) and catastrophic losses (> 3.0× ATR). For example, a $100 stock with $2.50 ATR on a swing trade would have a stop at $95.00 (2.0× $2.50 below entry), representing a 5.0% maximum loss.

The risk quality assessment employs a 9-point scoring system evaluating three dimensions: risk-to-reward ratio (up to +3 points for ≥2.5:1), trend strength (up to +3 points for ADX ≥40), and volatility regime (up to +2 points for LOW volatility). Scores of 7-9 indicate HIGH quality setups with excellent R:R, strong trends, and predictable volatility, making them ideal for larger position sizes. Medium quality (4-6 points) suggests acceptable but not ideal conditions, while LOW quality (0-3 points) triggers trade suppression. The suppression system acts as a final safety filter, blocking trades that fail critical thresholds: poor R:R (< 1.5:1), weak trends (ADX < 20), conflicting signals (> 40% contradiction), low volume (< 50% of average), or excessively wide stops (> 10% of entry price). This multi-layered approach ensures only high-probability, properly risk-managed trades reach execution.

---

## 4. compare_securities

### Overview
Batch analysis tool that evaluates multiple securities simultaneously and ranks them by technical merit using parallel processing.

### Technical Logic

#### A. Parallel Analysis Architecture

```python
async def compare_securities(symbols, metric="signals", period="3mo"):
    """
    Parallel Security Comparison

    Process:
    1. Limit input to MAX_SYMBOLS_COMPARE (10)
    2. Run analyze_security() on each in parallel
    3. Aggregate results
    4. Sort by chosen metric
    5. Return ranked comparison
    """
    symbols = symbols[:MAX_SYMBOLS_COMPARE]  # Cap at 10

    results = []

    # Parallel execution using asyncio.gather
    for symbol in symbols:
        try:
            analysis = await analyze_security(symbol, period=period)
            results.append({
                "symbol": symbol,
                "score": analysis["summary"]["avg_score"],
                "bullish": analysis["summary"]["bullish"],
                "bearish": analysis["summary"]["bearish"],
                "price": analysis["price"],
                "change": analysis["change"],
                "rsi": analysis["indicators"]["rsi"],
                "adx": analysis["indicators"]["adx"],
                "volume_ratio": analysis["indicators"].get("volume_ratio", 1.0)
            })
        except TechnicalAnalysisError as e:
            logger.warning(f"Error analyzing {symbol}: {e}")
            continue

    # Sort by metric
    if metric == "signals":
        results.sort(key=lambda x: x["score"], reverse=True)
    elif metric == "momentum":
        results.sort(key=lambda x: x["change"], reverse=True)
    elif metric == "strength":
        results.sort(key=lambda x: x["adx"], reverse=True)

    return {
        "comparison": results,
        "metric": metric,
        "winner": results[0] if results else None,
        "total_compared": len(results)
    }
```

#### B. Comparison Metrics

**1. Signal Score (Default)**
```python
# Aggregated signal quality
# Higher score = more bullish signals
score = (bullish_signals × 10 - bearish_signals × 10) + base_score

# Range: 0-100
# > 65: Bullish
# 35-65: Neutral
# < 35: Bearish
```

**2. Momentum**
```python
# Price change percentage
momentum = (current_price - prev_price) / prev_price × 100

# Sorted by absolute momentum (highest movers first)
```

**3. Trend Strength**
```python
# ADX as proxy for trend strength
# Higher ADX = stronger directional move
# Sorted by ADX value (strongest trends first)
```

**4. Volume Confirmation**
```python
# Volume relative to average
volume_ratio = current_volume / volume_ma_20

# Sorted by volume ratio (highest conviction first)
```

#### C. Statistical Analysis

```python
def calculate_comparison_stats(results):
    """
    Statistical summary of comparison

    Metrics:
    - Sector distribution
    - Average score
    - Score standard deviation
    - Correlation between metrics
    """
    scores = [r["score"] for r in results]

    stats = {
        "count": len(results),
        "avg_score": sum(scores) / len(scores),
        "std_dev": np.std(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "median_score": np.median(scores),
        "bullish_stocks": sum(1 for r in results if r["score"] > 65),
        "bearish_stocks": sum(1 for r in results if r["score"] < 35),
        "neutral_stocks": sum(1 for r in results if 35 <= r["score"] <= 65)
    }

    return stats
```

#### D. Relative Strength Ranking

```python
def calculate_relative_strength(results):
    """
    Rank securities by relative strength

    Formula:
    RS = (Price / MA50) × (1 + Change%) × (ADX/50) × (Volume_Ratio)

    Components:
    - Price vs MA50: Trend position
    - Change%: Momentum
    - ADX/50: Trend strength (normalized)
    - Volume Ratio: Conviction
    """
    for result in results:
        price_vs_ma = result["price"] / result.get("sma50", result["price"])
        momentum_factor = 1 + (result["change"] / 100)
        trend_factor = result["adx"] / 50
        volume_factor = result["volume_ratio"]

        rs_score = (
            price_vs_ma *
            momentum_factor *
            trend_factor *
            volume_factor
        )

        result["relative_strength"] = rs_score

    # Sort by RS score
    results.sort(key=lambda x: x["relative_strength"], reverse=True)

    return results
```

#### E. Output Example

```python
{
    "comparison": [
        {
            "symbol": "NVDA",
            "score": 78,
            "bullish": 12,
            "bearish": 3,
            "price": 875.42,
            "change": 3.24,
            "rsi": 68.5,
            "adx": 42.3,
            "relative_strength": 1.87,
            "rank": 1
        },
        {
            "symbol": "AAPL",
            "score": 72,
            "bullish": 10,
            "bearish": 4,
            "price": 185.42,
            "change": 1.23,
            "rsi": 55.2,
            "adx": 32.5,
            "relative_strength": 1.52,
            "rank": 2
        },
        {
            "symbol": "MSFT",
            "score": 65,
            "bullish": 8,
            "bearish": 5,
            "price": 415.30,
            "change": 0.85,
            "rsi": 52.8,
            "adx": 28.1,
            "relative_strength": 1.31,
            "rank": 3
        }
    ],
    "metric": "signals",
    "winner": {
        "symbol": "NVDA",
        "score": 78,
        "edge": "Strongest technical setup with 78 score and 3.24% momentum"
    },
    "stats": {
        "avg_score": 71.7,
        "std_dev": 6.5,
        "bullish_stocks": 3,
        "bearish_stocks": 0,
        "neutral_stocks": 0
    }
}
```

### Summary Paragraphs

The compare_securities tool implements a parallel batch analysis system that evaluates up to 10 securities simultaneously using asynchronous processing. Each security undergoes the complete analyze_security pipeline (indicator calculation, signal detection, ranking), but all analyses run concurrently using Python's asyncio framework. This parallel architecture dramatically reduces total processing time—analyzing 10 stocks sequentially might take 50 seconds (5 seconds each), while parallel execution completes in approximately 7-8 seconds (limited by the slowest individual analysis plus minor overhead). The tool handles failures gracefully, continuing analysis of remaining securities if individual stocks encounter errors, ensuring partial results are always returned even when some data fetching fails.

The comparison system offers multiple ranking metrics to suit different trading strategies: signal score (default, aggregates bullish vs bearish signals), momentum (ranks by price change percentage for trend followers), trend strength (sorts by ADX for directional traders), and volume confirmation (ranks by volume ratio for conviction-based selection). Each metric provides a different lens for evaluating opportunities—signal score favors technical setups with strong indicator alignment, momentum identifies the fastest movers regardless of setup quality, trend strength highlights securities in sustained directional moves, and volume confirmation reveals where institutional participation is highest. Traders can switch metrics based on market conditions: use signal score in choppy markets, momentum in trending environments, or volume confirmation when seeking high-conviction plays.

The relative strength calculation introduces a composite scoring system that combines multiple factors into a single normalized metric: RS = (Price/MA50) × (1 + Change%) × (ADX/50) × (Volume_Ratio). This formula weights trend position (price above or below 50-day MA), momentum (recent price change), trend strength (ADX normalized to 0-1 scale), and volume conviction (current vs average volume). The resulting RS score enables apples-to-apples comparison across securities with different price levels and volatility characteristics. For example, a $500 stock with moderate momentum might score similarly to a $50 stock with stronger momentum, allowing traders to identify the best relative opportunities regardless of absolute price. The statistical summary provides context including average score, standard deviation, and distribution of bullish/bearish/neutral securities, helping traders understand market breadth and whether opportunities are concentrated or dispersed.

---

## 5. screen_securities

### Overview
Universe-wide filtering tool that scans large symbol sets (S&P 500, NASDAQ 100, ETF lists) against custom technical criteria to identify opportunities matching specific conditions.

### Technical Logic

#### A. Universe Definitions

```python
UNIVERSES = {
    "sp500": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "BRK.B", "UNH", "XOM", "JNJ", "JPM", "V", "PG", "MA",
        # ... 485 more symbols (500 total)
    ],

    "nasdaq100": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "AVGO", "COST", "NFLX", "AMD", "PEP", "ADBE", "CSCO",
        # ... 86 more symbols (100 total)
    ],

    "etf_large_cap": [
        "SPY", "VOO", "IVV", "VTI", "QQQ", "DIA", "IWM",
        "VEA", "VWO", "EFA", "IEFA", "AGG", "BND", "VIG",
        # ... 14 more symbols (28 total)
    ],

    "etf_sector": [
        "XLK",  # Technology
        "XLF",  # Financial
        "XLV",  # Healthcare
        "XLE",  # Energy
        "XLY",  # Consumer Discretionary
        "XLP",  # Consumer Staples
        "XLI",  # Industrial
        "XLB",  # Materials
        "XLU",  # Utilities
        "XLRE"  # Real Estate
    ]
}
```

#### B. Screening Criteria

```python
def meets_criteria(analysis, criteria):
    """
    Flexible criteria matching system

    Supported criteria types:
    1. Range filters (min/max)
    2. Threshold filters
    3. Boolean conditions
    4. Composite filters
    """

    # Example criteria formats:
    criteria = {
        # RSI range
        "rsi": {
            "min": 30,
            "max": 70
        },

        # Minimum score threshold
        "min_score": 65,

        # Minimum bullish signals
        "min_bullish": 5,

        # ADX threshold
        "adx": {
            "min": 25
        },

        # Volume spike
        "volume_spike": True,

        # Price above MA
        "price_above": {
            "ma_period": 50
        }
    }

    indicators = analysis["indicators"]
    summary = analysis["summary"]

    # Check RSI range
    if "rsi" in criteria:
        rsi_criteria = criteria["rsi"]
        rsi_value = indicators.get("rsi", 50)

        if isinstance(rsi_criteria, dict):
            if rsi_value < rsi_criteria.get("min", 0):
                return False
            if rsi_value > rsi_criteria.get("max", 100):
                return False
        else:
            # Single threshold (e.g., rsi < 30)
            if rsi_value > rsi_criteria:
                return False

    # Check minimum score
    if "min_score" in criteria:
        if summary["avg_score"] < criteria["min_score"]:
            return False

    # Check minimum bullish signals
    if "min_bullish" in criteria:
        if summary["bullish"] < criteria["min_bullish"]:
            return False

    # Check ADX threshold
    if "adx" in criteria:
        adx_criteria = criteria["adx"]
        adx_value = indicators.get("adx", 25)

        if adx_value < adx_criteria.get("min", 0):
            return False

    # Check volume spike
    if "volume_spike" in criteria:
        volume_ratio = indicators.get("volume_ratio", 1.0)
        if volume_ratio < 1.5:  # 1.5x average = spike
            return False

    # Check price above MA
    if "price_above" in criteria:
        ma_period = criteria["price_above"]["ma_period"]
        ma_key = f"sma{ma_period}"

        if indicators.get(ma_key) is None:
            return False

        if analysis["price"] < indicators[ma_key]:
            return False

    # All criteria met
    return True
```

#### C. Common Screening Strategies

**1. Oversold Bounce**
```python
criteria = {
    "rsi": {"min": 20, "max": 35},
    "price_above": {"ma_period": 200},
    "adx": {"min": 20},
    "min_score": 50
}

# Logic: RSI oversold, above 200 MA (uptrend),
# some trend strength, not completely broken
```

**2. Breakout Momentum**
```python
criteria = {
    "price_above": {"ma_period": 50},
    "adx": {"min": 30},
    "volume_spike": True,
    "min_bullish": 5
}

# Logic: Price breakout above 50 MA, strong trend,
# volume confirmation, multiple bullish signals
```

**3. Golden Cross Scanner**
```python
criteria = {
    "signal_contains": "GOLDEN CROSS",
    "price_above": {"ma_period": 50},
    "min_score": 60
}

# Logic: 50/200 MA golden cross, price above 50 MA,
# decent overall technical score
```

**4. High Momentum**
```python
criteria = {
    "change_percent": {"min": 2.0},
    "rsi": {"min": 50, "max": 80},
    "adx": {"min": 25},
    "volume_ratio": {"min": 1.5}
}

# Logic: Strong price move (+2%), RSI not overbought,
# trend present, volume confirming
```

**5. Pullback in Uptrend**
```python
criteria = {
    "rsi": {"min": 35, "max": 50},
    "price_above": {"ma_period": 200},
    "price_below": {"ma_period": 20},
    "adx": {"min": 20}
}

# Logic: RSI pulled back but not oversold,
# long-term uptrend intact (above 200 MA),
# short-term pullback (below 20 MA)
```

#### D. Parallel Screening

```python
async def screen_securities(universe, criteria, limit=20, period="3mo"):
    """
    Parallel screening of large universes

    Process:
    1. Get universe symbols
    2. Analyze all symbols in parallel (async)
    3. Filter by criteria
    4. Sort by score
    5. Return top N results
    """
    symbols = UNIVERSES.get(universe, [])

    if not symbols:
        return {
            "universe": universe,
            "total_screened": 0,
            "matches": []
        }

    matches = []

    # Parallel analysis
    for symbol in symbols:
        try:
            analysis = await analyze_security(symbol, period=period)

            if meets_criteria(analysis, criteria):
                matches.append({
                    "symbol": symbol,
                    "score": analysis["summary"]["avg_score"],
                    "signals": analysis["summary"]["total_signals"],
                    "price": analysis["price"],
                    "change": analysis["change"],
                    "rsi": analysis["indicators"]["rsi"],
                    "adx": analysis["indicators"]["adx"]
                })
        except Exception:
            continue

    # Sort by score (highest first)
    matches.sort(key=lambda x: x["score"], reverse=True)

    return {
        "universe": universe,
        "total_screened": len(symbols),
        "matches": matches[:limit],
        "criteria": criteria,
        "match_rate": len(matches) / len(symbols) * 100
    }
```

#### E. Output Example

```python
{
    "universe": "sp500",
    "total_screened": 500,
    "matches": [
        {
            "symbol": "NVDA",
            "score": 82,
            "signals": 15,
            "price": 875.42,
            "change": 3.24,
            "rsi": 68.5,
            "adx": 42.3,
            "reason": "Breakout momentum with volume"
        },
        {
            "symbol": "AMD",
            "score": 78,
            "signals": 13,
            "price": 182.50,
            "change": 2.85,
            "rsi": 65.2,
            "adx": 38.7,
            "reason": "Breakout momentum with volume"
        },
        # ... up to 20 matches
    ],
    "criteria": {
        "price_above": {"ma_period": 50},
        "adx": {"min": 30},
        "volume_spike": True,
        "min_bullish": 5
    },
    "match_rate": 2.8,  # 14 matches out of 500 = 2.8%
    "duration_seconds": 45.3
}
```

### Summary Paragraphs

The screen_securities tool provides universe-wide opportunity discovery by applying custom technical filters to predefined symbol lists including the S&P 500 (500 symbols), NASDAQ 100 (100 symbols), large-cap ETFs (28 symbols), and sector ETFs (10 symbols). The screening engine analyzes every symbol in the chosen universe through the complete technical analysis pipeline, then filters results based on user-defined criteria. Unlike compare_securities which analyzes a small known list, screen_securities discovers unknown opportunities from large symbol sets—ideal for daily scans to identify new setups. The parallel processing architecture completes S&P 500 screens in 30-60 seconds depending on criteria complexity and market conditions.

The criteria system supports multiple filter types including range filters (RSI between 30-70), threshold filters (min_score ≥ 65), boolean conditions (volume_spike = true), and composite filters (price above 200 MA AND below 20 MA for pullback detection). Common screening strategies can be encoded as criteria objects: oversold bounces (RSI 20-35, price above 200 MA), breakout momentum (price above 50 MA, ADX > 30, volume spike), golden cross alerts (50/200 MA cross with score > 60), and pullback entries (RSI 35-50, above 200 MA, below 20 MA for short-term dips in long-term uptrends). The flexible criteria format allows traders to encode any rule-based strategy as a screen.

Match rate statistics provide valuable market intelligence—a 1-2% match rate indicates a selective market with few opportunities meeting strict criteria, while a 10-15% match rate suggests abundant opportunities or overly loose criteria. The match rate changes dramatically with market conditions: during strong bull markets, breakout screens might yield 8-10% matches, while during bear markets, the same screen might only find 1-2% matches. Duration metrics help optimize screening frequency—faster screens (< 30 seconds) can run multiple times per day, while slower screens (> 60 seconds) should be scheduled less frequently. The tool returns the top N matches sorted by score, ensuring traders see the highest-probability setups first regardless of how many securities qualified. This approach scales from small ETF lists (10 symbols, 2-3 second runtime) to the full S&P 500 (500 symbols, 30-60 second runtime) without code changes.

---

## 6. scan_trades

### Overview
Advanced parallel scanner that combines signal detection with risk assessment to identify fully-qualified, execution-ready trade setups across large universes.

### Technical Logic

#### A. Qualified Trade Definition

```python
def is_qualified_trade(trade_plan):
    """
    Trade Qualification Criteria

    A trade is "qualified" if ALL conditions met:

    1. Risk-to-Reward ≥ 1.5:1
    2. Risk Quality ≥ MEDIUM
    3. Clear directional bias (not NEUTRAL)
    4. No suppressions
    5. Valid stop level (0.5-3.0 ATR)
    6. Trend present (ADX ≥ 20)
    7. Adequate volume (≥ 50% average)
    """
    return (
        trade_plan.risk_reward_ratio >= 1.5 and
        trade_plan.risk_quality in ['high', 'medium'] and
        trade_plan.bias != 'neutral' and
        not trade_plan.is_suppressed and
        0.5 <= trade_plan.stop_distance_atr <= 3.0 and
        trade_plan.metrics.adx >= 20 and
        trade_plan.metrics.volume_ratio >= 0.5
    )
```

#### B. Parallel Scanning Architecture

```python
class TradeScanner:
    """Scans universes for qualified trade setups"""

    def __init__(self, max_concurrent=10):
        """
        Initialize scanner with concurrency limit

        Args:
            max_concurrent: Max parallel analyses (default 10)
        """
        self._max_concurrent = max_concurrent
        self._fetcher = CachedDataFetcher()
        self._risk_assessor = RiskAssessor()

    async def scan_universe(
        self,
        universe: str = "sp500",
        max_results: int = 10,
        period: str = "3mo"
    ):
        """
        Scan universe for qualified trades

        Process:
        1. Load universe symbols
        2. Rate-limited parallel scanning (10 concurrent)
        3. Full analysis pipeline per symbol:
           - Fetch data
           - Calculate indicators
           - Detect signals
           - Rank signals
           - Assess risk
           - Check qualification
        4. Collect qualified trades
        5. Sort by quality (HIGH → MEDIUM → LOW)
        6. Secondary sort by R:R ratio
        7. Return top N results
        """
        symbols = UNIVERSES.get(universe, [])
        max_results = min(max(1, max_results), 50)

        # Semaphore for rate limiting
        semaphore = asyncio.Semaphore(self._max_concurrent)
        qualified_trades = []

        async def scan_symbol(symbol: str):
            async with semaphore:
                try:
                    return await self._scan_single(symbol, period)
                except Exception as e:
                    logger.warning(f"Error scanning {symbol}: {e}")
                    return None

        # Parallel execution
        results = await asyncio.gather(
            *[scan_symbol(sym) for sym in symbols],
            return_exceptions=False
        )

        # Filter to qualified only
        for result in results:
            if result and result.get("has_trades"):
                qualified_trades.append(result)

        # Sort by quality, then R:R
        quality_order = {"high": 0, "medium": 1, "low": 2}
        qualified_trades.sort(
            key=lambda x: (
                quality_order.get(x.get("risk_quality", "low").lower(), 99),
                -x.get("risk_reward_ratio", 1.0)
            )
        )

        duration = time.time() - start_time

        return {
            "universe": universe,
            "total_scanned": len(symbols),
            "qualified_trades": qualified_trades[:max_results],
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "qualification_rate": len(qualified_trades) / len(symbols) * 100
        }
```

#### C. Single Symbol Scanning

```python
async def _scan_single(self, symbol: str, period: str):
    """
    Complete pipeline for single symbol

    Returns qualified trade or None
    """
    symbol = symbol.upper().strip()

    # 1. Fetch data
    df = self._fetcher.fetch(symbol, period)

    # 2. Calculate indicators
    df = calculate_all_indicators(df)

    # 3. Detect signals
    signals = detect_all_signals(df)

    # 4. Rank signals
    current = df.iloc[-1]
    market_data = {
        "price": float(current["Close"]),
        "change": float(current.get("Price_Change", 0))
    }

    ranked_signals = rank_signals(
        signals=signals,
        symbol=symbol,
        market_data=market_data,
        use_ai=False  # Rule-based for speed
    )

    # 5. Risk assessment
    risk_result = self._risk_assessor.assess(df, ranked_signals, symbol)

    # 6. Check if qualified
    if risk_result.has_trades and risk_result.trade_plans:
        plan = risk_result.trade_plans[0]  # Best plan

        return {
            "symbol": symbol,
            "entry_price": float(plan.entry_price),
            "stop_price": float(plan.stop_price),
            "target_price": float(plan.target_price),
            "risk_reward_ratio": float(plan.risk_reward_ratio),
            "risk_quality": plan.risk_quality.value,
            "timeframe": plan.timeframe.value,
            "bias": plan.bias.value,
            "primary_signal": plan.primary_signal,
            "expected_move_percent": float(plan.expected_move_percent),
            "max_loss_percent": float(plan.max_loss_percent),
            "has_trades": True
        }

    return None
```

#### D. Quality-Based Sorting

```python
def sort_qualified_trades(trades):
    """
    Sort qualified trades by quality, then R:R

    Priority order:
    1. HIGH quality, high R:R
    2. HIGH quality, medium R:R
    3. HIGH quality, low R:R
    4. MEDIUM quality, high R:R
    5. MEDIUM quality, medium R:R
    6. MEDIUM quality, low R:R
    7. LOW quality (rarely included)
    """
    quality_scores = {
        "high": 3,
        "medium": 2,
        "low": 1
    }

    trades.sort(
        key=lambda x: (
            quality_scores.get(x["risk_quality"].lower(), 0),
            x["risk_reward_ratio"]
        ),
        reverse=True
    )

    return trades
```

#### E. Performance Metrics

```python
def calculate_scan_metrics(scan_result):
    """
    Calculate scan performance metrics

    Metrics:
    - Qualification rate: % of symbols that qualify
    - Average R:R: Mean risk-reward ratio
    - Quality distribution: HIGH/MEDIUM/LOW breakdown
    - Timeframe distribution: SCALP/DAY/SWING breakdown
    - Bias distribution: BULLISH/BEARISH breakdown
    - Scan efficiency: Symbols/second
    """
    qualified = scan_result["qualified_trades"]
    total = scan_result["total_scanned"]
    duration = scan_result["duration_seconds"]

    return {
        "qualification_rate": len(qualified) / total * 100 if total > 0 else 0,
        "avg_rr_ratio": sum(t["risk_reward_ratio"] for t in qualified) / len(qualified) if qualified else 0,
        "quality_distribution": {
            "high": sum(1 for t in qualified if t["risk_quality"] == "high"),
            "medium": sum(1 for t in qualified if t["risk_quality"] == "medium"),
            "low": sum(1 for t in qualified if t["risk_quality"] == "low")
        },
        "timeframe_distribution": {
            "scalp": sum(1 for t in qualified if t["timeframe"] == "scalp"),
            "day": sum(1 for t in qualified if t["timeframe"] == "day"),
            "swing": sum(1 for t in qualified if t["timeframe"] == "swing")
        },
        "bias_distribution": {
            "bullish": sum(1 for t in qualified if t["bias"] == "bullish"),
            "bearish": sum(1 for t in qualified if t["bias"] == "bearish")
        },
        "scan_efficiency": total / duration  # symbols per second
    }
```

#### F. Output Example

```python
{
    "universe": "sp500",
    "total_scanned": 500,
    "qualified_trades": [
        {
            "symbol": "NVDA",
            "entry_price": 875.42,
            "stop_price": 859.18,  # 1.85% risk
            "target_price": 907.90,  # 3.71% reward
            "risk_reward_ratio": 2.00,
            "risk_quality": "high",
            "timeframe": "swing",
            "bias": "bullish",
            "primary_signal": "GOLDEN CROSS",
            "expected_move_percent": 3.71,
            "max_loss_percent": 1.85,
            "rank": 1
        },
        {
            "symbol": "AMD",
            "entry_price": 182.50,
            "stop_price": 175.88,  # 3.63% risk
            "target_price": 196.74,  # 7.80% reward
            "risk_reward_ratio": 2.15,
            "risk_quality": "high",
            "timeframe": "swing",
            "bias": "bullish",
            "primary_signal": "MA ALIGNMENT BULLISH",
            "expected_move_percent": 7.80,
            "max_loss_percent": 3.63,
            "rank": 2
        }
        # ... up to 10 qualified trades
    ],
    "timestamp": "2026-02-08T12:00:00Z",
    "duration_seconds": 62.5,
    "qualification_rate": 2.2,  # 11 out of 500 qualified
    "metrics": {
        "avg_rr_ratio": 2.08,
        "quality_distribution": {
            "high": 7,
            "medium": 4,
            "low": 0
        },
        "timeframe_distribution": {
            "scalp": 0,
            "day": 2,
            "swing": 9
        },
        "bias_distribution": {
            "bullish": 8,
            "bearish": 3
        },
        "scan_efficiency": 8.0  # 8 symbols/sec
    }
}
```

### Summary Paragraphs

The scan_trades tool is a comprehensive opportunity discovery engine that combines the full technical analysis pipeline with rigorous risk assessment to produce execution-ready trade setups. Unlike screen_securities which only filters by technical criteria, scan_trades runs every symbol through the complete workflow: data fetching → indicator calculation → signal detection → signal ranking → risk assessment → qualification validation. Only setups that pass all risk management thresholds (R:R ≥ 1.5:1, ADX ≥ 20, quality ≥ MEDIUM, no suppressions, valid stop distance) are returned as "qualified trades". This ensures every result is actionable with predefined entry, stop, and target levels—traders can execute directly from scan output without additional analysis.

The parallel scanning architecture uses Python's asyncio with semaphore-based rate limiting to process large universes efficiently. The semaphore caps concurrent operations at 10 symbols simultaneously, preventing overwhelming system resources or hitting API rate limits. A full S&P 500 scan (500 symbols) completes in approximately 60-80 seconds with 10 concurrent workers, processing roughly 6-8 symbols per second. The scanner gracefully handles individual symbol failures—if yfinance data is unavailable or calculations error for specific symbols, those failures are logged but don't halt the entire scan. This fault tolerance ensures partial results even when some symbols encounter issues.

Qualification rate statistics provide critical market intelligence about opportunity abundance: rates of 1-3% indicate highly selective markets with few setups meeting strict criteria (typical during consolidation or choppy conditions), 4-7% suggests moderate opportunity flow (normal conditions), and 8-15% indicates abundant opportunities (trending markets with widespread directional momentum). Quality and timeframe distributions reveal market character—high preponderance of HIGH-quality SWING trades suggests strong directional trends, while clustered DAY trades indicate shorter-term momentum environments. Bias distribution (bullish vs bearish qualified trades) serves as a market sentiment indicator: 70%+ bullish qualifications signals broad-based strength, 70%+ bearish indicates widespread weakness, and balanced distributions suggest mixed or transitional conditions. These aggregate metrics help traders adjust strategy (aggressive vs defensive positioning) based on actual market opportunity flow rather than intuition.

---

## 7. portfolio_risk

### Overview
Aggregate portfolio risk assessment tool that analyzes multiple open positions simultaneously, calculating individual position risk, sector concentration, and overall portfolio-level metrics.

### Technical Logic

#### A. Position Risk Assessment

```python
async def assess_single_position(position):
    """
    Individual Position Risk Calculation

    Input:
    - symbol: Ticker
    - shares: Position size
    - entry_price: Entry cost basis

    Process:
    1. Fetch current market data
    2. Calculate current value
    3. Calculate unrealized P&L
    4. Run risk assessment for stop level
    5. Calculate max loss at stop
    6. Determine position risk metrics
    """
    symbol = position["symbol"].upper()
    shares = position["shares"]
    entry_price = position["entry_price"]

    # 1. Current market data
    df = fetcher.fetch(symbol, "1mo")
    df = calculate_all_indicators(df)
    current_price = float(df.iloc[-1]["Close"])

    # 2. Current value
    current_value = current_price * shares
    entry_value = entry_price * shares

    # 3. Unrealized P&L
    unrealized_pnl = current_value - entry_value
    unrealized_percent = (unrealized_pnl / entry_value * 100) if entry_value > 0 else 0

    # 4. Risk assessment for stop
    signals = detect_all_signals(df)
    ranked_signals = rank_signals(signals, symbol, {"price": current_price, "change": 0})
    risk_result = risk_assessor.assess(df, ranked_signals, symbol)

    # Extract stop from risk assessment
    if risk_result.risk_assessment and risk_result.risk_assessment.stop:
        stop_price = float(risk_result.risk_assessment.stop.price)
    else:
        stop_price = entry_price * 0.95  # Default 5% stop

    # 5. Max loss calculation
    max_loss_dollar = abs(current_price - stop_price) * shares
    max_loss_percent = (abs(current_price - stop_price) / current_price * 100) if current_price > 0 else 0

    return {
        "symbol": symbol,
        "shares": shares,
        "entry_price": entry_price,
        "current_price": current_price,
        "current_value": current_value,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_percent": unrealized_percent,
        "stop_level": stop_price,
        "max_loss_dollar": max_loss_dollar,
        "max_loss_percent": max_loss_percent,
        "risk_quality": risk_result.risk_assessment.risk_quality.value if risk_result.risk_assessment else "low",
        "timeframe": risk_result.trade_plans[0].timeframe.value if risk_result.trade_plans else "swing",
        "sector": get_sector(symbol)
    }
```

**Example Position**:
```
Input:
- Symbol: AAPL
- Shares: 100
- Entry Price: $180.00

Current Analysis:
- Current Price: $185.42
- Current Value: $18,542
- Entry Value: $18,000
- Unrealized P&L: +$542 (+3.01%)

Risk Assessment:
- Stop Level: $176.18 (2 ATR = $9.24 below)
- Max Loss: $9.24 × 100 = $924
- Max Loss %: 4.98%
```

#### B. Aggregate Portfolio Metrics

```python
def calculate_portfolio_metrics(positions):
    """
    Portfolio-Level Risk Calculations

    Metrics:
    1. Total Value: Sum of all position values
    2. Total Max Loss: Sum of all position max losses
    3. Portfolio Risk %: Total max loss / Total value
    4. Position count and average size
    5. Largest position exposure
    """
    total_value = sum(p["current_value"] for p in positions)
    total_max_loss = sum(p["max_loss_dollar"] for p in positions)

    portfolio_risk_percent = (total_max_loss / total_value * 100) if total_value > 0 else 0

    # Position statistics
    position_count = len(positions)
    avg_position_size = total_value / position_count if position_count > 0 else 0
    largest_position = max(positions, key=lambda p: p["current_value"])
    largest_position_percent = (largest_position["current_value"] / total_value * 100) if total_value > 0 else 0

    return {
        "total_value": total_value,
        "total_max_loss": total_max_loss,
        "portfolio_risk_percent": portfolio_risk_percent,
        "position_count": position_count,
        "avg_position_size": avg_position_size,
        "largest_position": {
            "symbol": largest_position["symbol"],
            "value": largest_position["current_value"],
            "percent_of_portfolio": largest_position_percent
        }
    }
```

**Example Portfolio**:
```
Positions:
1. AAPL: 100 shares @ $185.42 = $18,542 (Max Loss: $924)
2. MSFT: 50 shares @ $415.30 = $20,765 (Max Loss: $1,245)
3. NVDA: 20 shares @ $875.42 = $17,508 (Max Loss: $1,050)
4. GOOGL: 100 shares @ $142.50 = $14,250 (Max Loss: $712)

Aggregate:
- Total Value: $71,065
- Total Max Loss: $3,931
- Portfolio Risk: 5.53%
- Position Count: 4
- Avg Position Size: $17,766
- Largest Position: MSFT at 29.2% of portfolio
```

#### C. Sector Concentration

```python
def calculate_sector_concentration(positions, total_value):
    """
    Sector Exposure Analysis

    Calculates percentage of portfolio in each sector

    Warns if any sector > 40% (concentrated risk)
    """
    sector_values = defaultdict(float)

    for pos in positions:
        sector = pos["sector"]
        sector_values[sector] += pos["current_value"]

    sector_concentration = {
        sector: (value / total_value * 100)
        for sector, value in sector_values.items()
    }

    # Sort by concentration (highest first)
    sorted_sectors = sorted(
        sector_concentration.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return dict(sorted_sectors)
```

**Example Sector Analysis**:
```
Sector Concentration:
- Technology: 79.9% ($56,815)  ⚠️ HIGH CONCENTRATION
  - AAPL: $18,542
  - MSFT: $20,765
  - NVDA: $17,508
- Communication: 20.1% ($14,250)
  - GOOGL: $14,250

Warning: Technology sector >40% of portfolio
Recommendation: Consider hedging or diversification
```

#### D. Risk Level Classification

```python
def assess_overall_risk(portfolio_risk_percent, positions):
    """
    Portfolio Risk Level Classification

    Thresholds:
    - LOW: < 3% portfolio risk
    - MEDIUM: 3-7% portfolio risk
    - HIGH: 7-12% portfolio risk
    - EXTREME: > 12% portfolio risk

    Adjustments:
    - +1 level if any position > 40% of portfolio
    - +1 level if any sector > 60% of portfolio
    - +1 level if > 30% positions are LOW quality
    """
    # Base classification
    if portfolio_risk_percent < 3:
        base_level = "LOW"
    elif portfolio_risk_percent < 7:
        base_level = "MEDIUM"
    elif portfolio_risk_percent < 12:
        base_level = "HIGH"
    else:
        base_level = "EXTREME"

    # Concentration adjustments
    total_value = sum(p["current_value"] for p in positions)

    # Check position concentration
    max_position_percent = max(
        p["current_value"] / total_value * 100
        for p in positions
    )

    if max_position_percent > 40:
        base_level = escalate_risk_level(base_level)

    # Check quality distribution
    low_quality_count = sum(
        1 for p in positions
        if p["risk_quality"] == "low"
    )

    if low_quality_count / len(positions) > 0.3:  # > 30% low quality
        base_level = escalate_risk_level(base_level)

    return base_level

def escalate_risk_level(current_level):
    """Move risk level up one tier"""
    levels = ["LOW", "MEDIUM", "HIGH", "EXTREME"]
    current_idx = levels.index(current_level)
    return levels[min(current_idx + 1, len(levels) - 1)]
```

#### E. Hedge Suggestions

```python
def generate_hedge_suggestions(positions, sector_concentration):
    """
    Generate hedging recommendations

    Triggers:
    1. Sector > 40%: Suggest sector ETF put
    2. Multiple LOW quality positions: Review stops
    3. Portfolio risk > 10%: Consider index hedge
    4. High correlation exposure: Suggest diversification
    """
    suggestions = []

    # Sector concentration hedges
    for sector, pct in sector_concentration.items():
        if pct > 40:
            etf = get_sector_hedge_etf(sector)
            if etf:
                hedge_notional = pct * 0.5  # Hedge 50% of exposure
                suggestions.append({
                    "type": "SECTOR_HEDGE",
                    "reason": f"{sector} concentration at {pct:.1f}%",
                    "action": f"Buy {etf} puts",
                    "notional_percent": hedge_notional,
                    "priority": "HIGH"
                })

    # Quality-based suggestions
    low_quality_positions = [
        p for p in positions
        if p["risk_quality"] == "low"
    ]

    if len(low_quality_positions) >= 2:
        symbols = [p["symbol"] for p in low_quality_positions]
        suggestions.append({
            "type": "RISK_REVIEW",
            "reason": f"{len(low_quality_positions)} low-quality positions",
            "action": f"Review and tighten stops for {', '.join(symbols)}",
            "priority": "MEDIUM"
        })

    # Portfolio-level hedge
    portfolio_risk = sum(p["max_loss_dollar"] for p in positions)
    total_value = sum(p["current_value"] for p in positions)
    risk_percent = portfolio_risk / total_value * 100

    if risk_percent > 10:
        suggestions.append({
            "type": "PORTFOLIO_HEDGE",
            "reason": f"Portfolio risk at {risk_percent:.1f}%",
            "action": "Consider SPY/QQQ put spread to cap downside",
            "notional_percent": 20,  # Hedge 20% of portfolio
            "priority": "HIGH"
        })

    return suggestions

def get_sector_hedge_etf(sector):
    """Map sector to hedge ETF"""
    sector_etfs = {
        "Technology": "XLK",
        "Financial": "XLF",
        "Healthcare": "XLV",
        "Energy": "XLE",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Industrial": "XLI",
        "Materials": "XLB",
        "Utilities": "XLU",
        "Real Estate": "XLRE"
    }
    return sector_etfs.get(sector)
```

#### F. Complete Portfolio Assessment Output

```python
{
    "timestamp": "2026-02-08T12:00:00Z",
    "total_value": 71065.00,
    "total_max_loss": 3931.00,
    "risk_percent_of_portfolio": 5.53,
    "overall_risk_level": "MEDIUM",
    "position_count": 4,
    "avg_position_size": 17766.25,

    "positions": [
        {
            "symbol": "AAPL",
            "shares": 100,
            "entry_price": 180.00,
            "current_price": 185.42,
            "current_value": 18542.00,
            "unrealized_pnl": 542.00,
            "unrealized_percent": 3.01,
            "stop_level": 176.18,
            "max_loss_dollar": 924.00,
            "max_loss_percent": 4.98,
            "risk_quality": "high",
            "sector": "Technology",
            "percent_of_portfolio": 26.1
        },
        # ... 3 more positions
    ],

    "sector_concentration": {
        "Technology": 79.9,
        "Communication": 20.1
    },

    "hedge_suggestions": [
        {
            "type": "SECTOR_HEDGE",
            "reason": "Technology concentration at 79.9%",
            "action": "Buy XLK puts (30 DTE, 25 delta)",
            "notional_percent": 40,
            "priority": "HIGH"
        }
    ],

    "risk_metrics": {
        "largest_position": {
            "symbol": "MSFT",
            "percent": 29.2
        },
        "quality_distribution": {
            "high": 3,
            "medium": 1,
            "low": 0
        },
        "avg_unrealized_pnl_percent": 2.45
    }
}
```

### Summary Paragraphs

The portfolio_risk tool provides comprehensive multi-position risk analysis by assessing each position individually then aggregating metrics to the portfolio level. For each position, it fetches current market data, calculates unrealized P&L (both dollar and percentage), runs the full risk assessment pipeline to determine appropriate stop levels based on volatility and trend conditions, and computes maximum loss if the stop is hit. Position-level metrics include current value, entry basis, stop price, max loss dollar amount, max loss percentage, risk quality rating, timeframe classification, and sector assignment. This granular analysis ensures each position's risk is quantified precisely rather than using portfolio-wide rules that might not fit individual positions.

Aggregate portfolio metrics reveal systemic risk concentrations that aren't visible at the position level. Total portfolio risk percentage (sum of all position max losses divided by total portfolio value) provides a single number representing catastrophic downside—a 5.5% portfolio risk means if every position hits its stop simultaneously, the portfolio loses 5.5% of total value. Sector concentration analysis identifies dangerous overweights: Technology at 80% of portfolio value creates correlated risk where a sector-wide selloff impacts most positions. Position concentration warnings trigger when any single position exceeds 40% of portfolio value, indicating insufficient diversification. The risk level classification (LOW/MEDIUM/HIGH/EXTREME) combines numerical risk percentage with qualitative factors like concentration, providing an intuitive risk summary.

Hedge suggestions generate actionable risk mitigation strategies based on detected vulnerabilities. Sector concentration > 40% triggers sector ETF put suggestions (e.g., "Buy XLK puts to hedge 50% of Technology exposure"), protecting against sector-specific crashes without liquidating profitable positions. Multiple low-quality positions trigger stop review recommendations, prompting traders to reassess risk levels on weak setups. Portfolio risk > 10% suggests index hedges using SPY or QQQ put spreads to cap overall downside. Each suggestion includes type classification, reasoning, specific action steps, notional percentage to hedge, and priority level (HIGH/MEDIUM/LOW), enabling traders to prioritize risk management actions. The correlation analysis (planned feature) would identify when seemingly different positions have high price correlation, revealing hidden concentration risk—for example, AAPL and MSFT might appear as separate Technology positions but move together 85% of the time, creating de facto concentration.

---

## 8. morning_brief

### Overview
Daily market briefing generator that synthesizes market status, economic events, watchlist signals, sector performance, and overarching themes into a comprehensive pre-market report.

### Technical Logic

#### A. Market Status Assessment

```python
class MarketStatusChecker:
    """Check current market conditions"""

    def get_market_status(self, market_region="US"):
        """
        Market Status Indicators

        Components:
        1. Market hours (OPEN/CLOSED/PRE-MARKET/AFTER-HOURS)
        2. Index levels (SPY, QQQ, DIA)
        3. VIX (volatility index)
        4. Market sentiment (BULLISH/NEUTRAL/BEARISH)
        5. Futures direction
        """
        current_time = datetime.now()

        # 1. Market hours
        market_open_time = current_time.replace(hour=9, minute=30, second=0)
        market_close_time = current_time.replace(hour=16, minute=0, second=0)

        if current_time < market_open_time:
            market_status = "PRE-MARKET"
        elif current_time > market_close_time:
            market_status = "AFTER-HOURS"
        elif current_time.weekday() >= 5:  # Weekend
            market_status = "CLOSED"
        else:
            market_status = "OPEN"

        # 2. Index levels (fetch live data)
        spy = yf.Ticker("SPY")
        spy_price = spy.info.get("regularMarketPrice", 0)
        spy_change = spy.info.get("regularMarketChangePercent", 0)

        vix = yf.Ticker("^VIX")
        vix_level = vix.info.get("regularMarketPrice", 15)

        # 3. Sentiment classification
        if spy_change > 0.5 and vix_level < 15:
            sentiment = "BULLISH"
        elif spy_change < -0.5 and vix_level > 20:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

        return {
            "market_status": market_status,
            "current_time": current_time.isoformat(),
            "indices": {
                "SPY": {
                    "price": spy_price,
                    "change_percent": spy_change
                },
                # QQQ, DIA similar
            },
            "vix": vix_level,
            "market_sentiment": sentiment
        }
```

#### B. Economic Calendar

```python
class EconomicCalendar:
    """Fetch today's economic events"""

    def get_todays_events(self):
        """
        Economic Events for Today

        Sources:
        - Earnings announcements
        - Economic data releases (GDP, CPI, NFP, etc.)
        - Fed speeches/meetings
        - Geopolitical events

        Impact Levels:
        - HIGH: Major market movers (Fed decision, NFP, CPI)
        - MEDIUM: Sector impacts (earnings, PMI)
        - LOW: Minor releases
        """
        today = datetime.now().date()

        # Mock events (in production, fetch from economic calendar API)
        events = [
            {
                "time": "08:30",
                "event": "CPI Report",
                "impact": "HIGH",
                "expected": "0.3% MoM",
                "previous": "0.4% MoM",
                "description": "Consumer Price Index - inflation measure"
            },
            {
                "time": "10:00",
                "event": "ISM Manufacturing PMI",
                "impact": "MEDIUM",
                "expected": "47.5",
                "previous": "47.2",
                "description": "Manufacturing activity index"
            },
            {
                "time": "After Market Close",
                "event": "AAPL Earnings",
                "impact": "HIGH",
                "expected": "EPS $2.10",
                "description": "Apple Q4 earnings report"
            }
        ]

        return events
```

#### C. Watchlist Analysis

```python
async def analyze_watchlist(symbols):
    """
    Analyze watchlist symbols for trading signals

    Default watchlist (if none provided):
    - Top 10 S&P 500 by market cap
    - AAPL, MSFT, NVDA, GOOGL, META, JPM, BAC, V, MA, TSLA

    For each symbol:
    1. Full technical analysis
    2. Risk assessment
    3. Top 3 signals
    4. Action recommendation (BUY/HOLD/AVOID)
    5. Key support/resistance levels
    """
    if not symbols:
        symbols = ["AAPL", "MSFT", "NVDA", "GOOGL", "META",
                  "JPM", "BAC", "V", "MA", "TSLA"]

    results = []

    for symbol in symbols[:10]:  # Limit to 10
        try:
            # Fetch and analyze
            df = fetcher.fetch(symbol, "1mo")
            df = calculate_all_indicators(df)

            current = df.iloc[-1]
            price = float(current["Close"])
            change = float(current.get("Price_Change", 0))

            # Detect and rank signals
            signals = detect_all_signals(df)
            ranked = rank_signals(signals, symbol, {"price": price, "change": change})

            # Top 3 signals
            top_signals = [s.signal for s in ranked[:3]]

            # Risk assessment
            risk_result = risk_assessor.assess(df, ranked, symbol)

            # Action determination
            if risk_result.has_trades:
                action = "BUY"
                assessment = "TRADE"
            elif risk_result.risk_assessment and risk_result.risk_assessment.metrics.is_trending:
                action = "HOLD"
                assessment = "HOLD"
            else:
                action = "AVOID"
                assessment = "AVOID"

            # Key levels
            support = price * 0.97  # 3% below current
            resistance = price * 1.03  # 3% above current

            results.append({
                "symbol": symbol,
                "price": price,
                "change_percent": change,
                "top_signals": top_signals,
                "risk_assessment": assessment,
                "action": action,
                "key_support": support,
                "key_resistance": resistance,
                "rsi": current.get("RSI", 50),
                "adx": current.get("ADX", 25)
            })

        except Exception as e:
            logger.warning(f"Error analyzing {symbol}: {e}")
            continue

    return results
```

#### D. Sector Performance

```python
def get_sector_performance():
    """
    Fetch sector ETF performance

    Sector ETFs:
    - XLK: Technology
    - XLF: Financial
    - XLV: Healthcare
    - XLE: Energy
    - XLY: Consumer Discretionary
    - XLP: Consumer Staples
    - XLI: Industrial
    - XLB: Materials
    - XLU: Utilities
    - XLRE: Real Estate

    Returns:
    - Top 3 leaders (highest % gain)
    - Top 3 laggards (lowest % gain or highest loss)
    """
    sector_etfs = {
        "XLK": "Technology",
        "XLF": "Financial",
        "XLV": "Healthcare",
        "XLE": "Energy",
        "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples",
        "XLI": "Industrial",
        "XLB": "Materials",
        "XLU": "Utilities",
        "XLRE": "Real Estate"
    }

    sector_performance = []

    for etf, sector_name in sector_etfs.items():
        try:
            ticker = yf.Ticker(etf)
            change = ticker.info.get("regularMarketChangePercent", 0)

            sector_performance.append({
                "sector": sector_name,
                "etf": etf,
                "change_percent": change
            })
        except:
            continue

    # Sort by performance
    sector_performance.sort(key=lambda x: x["change_percent"], reverse=True)

    leaders = sector_performance[:3]
    laggards = sector_performance[-3:]

    return {
        "leaders": leaders,
        "laggards": laggards
    }
```

#### E. Theme Detection

```python
def detect_market_themes(market_status, watchlist_signals, sector_leaders):
    """
    Identify major market themes

    Theme Detection Logic:

    1. Tech Strength
       - ≥ 3 tech stocks with BUY action
       - Technology sector in top 3 leaders

    2. Financial Strength
       - Financials sector #1 leader
       - ≥ 2 bank stocks with positive signals

    3. Rotation
       - Large gap between leader and laggard sectors
       - Mixed watchlist actions

    4. Risk-On / Risk-Off
       - VIX level and direction
       - Defensive vs cyclical performance

    5. Momentum Surge
       - Multiple stocks with volume spikes
       - Broad-based breakouts
    """
    themes = []

    # Check for tech strength
    tech_symbols = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
    tech_buy_count = sum(
        1 for w in watchlist_signals
        if w["symbol"] in tech_symbols and w["action"] == "BUY"
    )

    if tech_buy_count >= 3:
        themes.append({
            "theme": "TECH_STRENGTH",
            "description": "Technology stocks showing broad strength",
            "confidence": "HIGH" if tech_buy_count >= 4 else "MEDIUM"
        })

    # Check for sector rotation
    if sector_leaders:
        leader_change = sector_leaders[0]["change_percent"]
        laggard_change = sector_leaders[-1]["change_percent"]

        if leader_change - laggard_change > 2.0:
            themes.append({
                "theme": "SECTOR_ROTATION",
                "description": f"{sector_leaders[0]['sector']} outperforming "
                             f"{sector_leaders[-1]['sector']} by {leader_change - laggard_change:.1f}%",
                "confidence": "HIGH"
            })

    # Check market sentiment
    vix = market_status.get("vix", 15)
    sentiment = market_status.get("market_sentiment", "NEUTRAL")

    if vix < 15 and sentiment == "BULLISH":
        themes.append({
            "theme": "RISK_ON",
            "description": "Low volatility and positive sentiment - risk-on environment",
            "confidence": "HIGH"
        })
    elif vix > 25 and sentiment == "BEARISH":
        themes.append({
            "theme": "RISK_OFF",
            "description": "High volatility and negative sentiment - defensive positioning",
            "confidence": "HIGH"
        })

    # Default if no clear themes
    if not themes:
        themes.append({
            "theme": "MIXED_MARKET",
            "description": "No dominant theme - stock-specific opportunities",
            "confidence": "MEDIUM"
        })

    return themes
```

#### F. Complete Morning Brief Output

```python
{
    "timestamp": "2026-02-08T07:30:00Z",

    "market_status": {
        "market_status": "PRE-MARKET",
        "current_time": "2026-02-08T07:30:00Z",
        "indices": {
            "SPY": {"price": 485.32, "change_percent": 0.42},
            "QQQ": {"price": 425.18, "change_percent": 0.67},
            "DIA": {"price": 385.45, "change_percent": 0.28}
        },
        "vix": 13.8,
        "market_sentiment": "BULLISH"
    },

    "economic_events": [
        {
            "time": "08:30",
            "event": "CPI Report",
            "impact": "HIGH",
            "expected": "0.3% MoM",
            "previous": "0.4% MoM"
        },
        {
            "time": "After Close",
            "event": "AAPL Earnings",
            "impact": "HIGH",
            "expected": "EPS $2.10"
        }
    ],

    "watchlist_signals": [
        {
            "symbol": "NVDA",
            "price": 875.42,
            "change_percent": 3.24,
            "top_signals": ["GOLDEN CROSS", "VOLUME SPIKE 2X", "MA ALIGNMENT BULLISH"],
            "action": "BUY",
            "risk_assessment": "TRADE",
            "key_support": 849.36,
            "key_resistance": 901.48
        },
        {
            "symbol": "AAPL",
            "price": 185.42,
            "change_percent": 1.23,
            "top_signals": ["MACD BULL CROSS", "PRICE ABOVE 20 MA", "RSI NEUTRAL"],
            "action": "BUY",
            "risk_assessment": "TRADE",
            "key_support": 179.86,
            "key_resistance": 190.98
        }
        // ... 8 more symbols
    ],

    "sector_performance": {
        "leaders": [
            {"sector": "Technology", "etf": "XLK", "change_percent": 1.85},
            {"sector": "Financial", "etf": "XLF", "change_percent": 1.12},
            {"sector": "Healthcare", "etf": "XLV", "change_percent": 0.78}
        ],
        "laggards": [
            {"sector": "Energy", "etf": "XLE", "change_percent": -0.95},
            {"sector": "Utilities", "etf": "XLU", "change_percent": -0.42},
            {"sector": "Consumer Staples", "etf": "XLP", "change_percent": -0.18}
        ]
    },

    "key_themes": [
        {
            "theme": "TECH_STRENGTH",
            "description": "Technology stocks showing broad strength - 7 of 10 tech names with BUY signals",
            "confidence": "HIGH"
        },
        {
            "theme": "RISK_ON",
            "description": "Low VIX (13.8) and positive futures - risk-on environment favors growth",
            "confidence": "HIGH"
        },
        {
            "theme": "EARNINGS_CATALYST",
            "description": "Major earnings today (AAPL after close) could drive volatility",
            "confidence": "MEDIUM"
        }
    ],

    "summary": "Bullish pre-market with tech leadership. VIX compressed at 13.8 signals low fear. CPI data at 8:30 AM could impact direction. Watch NVDA for continued momentum and AAPL ahead of earnings."
}
```

### Summary Paragraphs

The morning_brief tool synthesizes multiple data streams into a comprehensive pre-market intelligence report, combining market status, economic events, technical analysis of key stocks, sector performance, and thematic insights. Market status assessment checks current trading hours, fetches real-time index levels (SPY, QQQ, DIA), monitors the VIX volatility index, and classifies overall sentiment as BULLISH (futures up, VIX low), BEARISH (futures down, VIX elevated), or NEUTRAL (mixed signals). The economic calendar component identifies high-impact events scheduled for the trading day—CPI reports, Fed speeches, major earnings releases—providing expected vs previous values so traders can anticipate potential market reactions. This contextual information helps traders understand whether the day favors aggressive trading (calm, no major events) or defensive positioning (high volatility expected from data releases).

Watchlist analysis runs the full technical analysis and risk assessment pipeline on a curated list of 10 high-liquidity stocks (default: top 10 S&P 500 by market cap), generating actionable recommendations for each. Each watchlist entry includes current price, percent change, top 3 technical signals, action recommendation (BUY/HOLD/AVOID), risk assessment result (TRADE/HOLD/AVOID), and key support/resistance levels for intraday monitoring. The action determination logic classifies stocks as BUY (qualified trade setup with R:R ≥ 1.5:1), HOLD (trending but no immediate setup), or AVOID (choppy, no edge). This watchlist-focused approach differs from broader scans by concentrating on a manageable number of high-priority symbols that institutional traders care about.

Theme detection employs pattern recognition across market breadth indicators to identify overarching market narratives. Tech strength theme triggers when ≥3 technology stocks show BUY signals and XLK ranks in the top 3 sector leaders, indicating broad-based momentum in the largest S&P sector. Sector rotation theme activates when the gap between leading and lagging sectors exceeds 2%, revealing capital flows from defensive (utilities, staples) to cyclical (tech, discretionary) or vice versa. Risk-on/risk-off classification uses VIX level as the primary signal: VIX < 15 with positive sentiment indicates complacency and risk appetite, while VIX > 25 with negative sentiment signals fear and defensive positioning. These themes provide strategic context beyond individual stock signals—knowing "Tech Strength + Risk-On" is dominant helps traders align strategy (aggressive longs, focus on tech sector) with market regime, while "Risk-Off + Sector Rotation to Defensives" suggests protective positioning and avoiding aggressive entries. The brief consolidates information from dozens of data points into a concise narrative, enabling traders to make informed decisions about market positioning before the opening bell.

---

## 9. options_risk_analysis

### Overview
Options strategy selector integrated into trade plan generation, recommending directional options or spreads based on expected move, volatility regime, and timeframe.

### Technical Logic

#### A. Vehicle Selection Rules

```python
class DefaultVehicleSelector:
    """Select stock vs options based on setup characteristics"""

    def select(self, timeframe, volatility, bias, expected_move_percent):
        """
        Vehicle Selection Decision Tree

        Decision Logic:

        1. If NOT swing trade → STOCK
           (Scalp and day trades use stock for liquidity)

        2. If expected move < 3% → STOCK
           (Options need minimum move to justify premium)

        3. If MEDIUM volatility → DIRECTIONAL OPTIONS
           - Bullish → CALL
           - Bearish → PUT

        4. If HIGH volatility → VERTICAL SPREADS
           - Bullish → BULL CALL SPREAD
           - Bearish → BEAR PUT SPREAD
           (Spreads reduce vega risk in high IV)

        5. If LOW volatility → STOCK
           (Options premiums too cheap, stock more efficient)
        """

        # Rule 1: Non-swing trades use stock
        if timeframe != Timeframe.SWING:
            return (Vehicle.STOCK, None)

        # Rule 2: Small moves use stock
        if expected_move_percent < OPTION_MIN_EXPECTED_MOVE:  # 3%
            return (Vehicle.STOCK, None)

        # Rules 3-4: Swing trades with sufficient move
        suggestions = {
            "dte_range": (OPTION_SWING_MIN_DTE, OPTION_SWING_MAX_DTE),  # (30, 45)
            "expected_move_percent": expected_move_percent
        }

        # Medium volatility → Directional options
        if volatility == VolatilityRegime.MEDIUM:
            if bias == "bullish":
                vehicle = Vehicle.OPTION_CALL
                suggestions["delta_range"] = (0.40, 0.60)  # ATM calls
                suggestions["reasoning"] = "ATM calls for directional bullish play"
            else:  # bearish
                vehicle = Vehicle.OPTION_PUT
                suggestions["delta_range"] = (-0.60, -0.40)  # ATM puts
                suggestions["reasoning"] = "ATM puts for directional bearish play"

            return (vehicle, suggestions)

        # High volatility → Spreads
        if volatility == VolatilityRegime.HIGH:
            vehicle = Vehicle.OPTION_SPREAD

            if bias == "bullish":
                suggestions["spread_type"] = "Bull Call Spread"
                suggestions["delta_range"] = (0.40, 0.60)
                suggestions["reasoning"] = (
                    "High IV suitable for spreads; bull call spread "
                    "for defined risk"
                )
            else:  # bearish
                suggestions["spread_type"] = "Bear Put Spread"
                suggestions["delta_range"] = (-0.60, -0.40)
                suggestions["reasoning"] = (
                    "High IV suitable for spreads; bear put spread "
                    "for defined risk"
                )

            # Spread width suggestion
            suggestions["spread_width_info"] = (
                f"Width typically 1x ATR equivalent for "
                f"{expected_move_percent:.1f}% expected move"
            )

            return (vehicle, suggestions)

        # Rule 5: Low volatility → Stock
        return (Vehicle.STOCK, None)
```

#### B. Options Parameters

**Configuration Constants**:
```python
# Minimum expected move to consider options
OPTION_MIN_EXPECTED_MOVE = 3.0  # 3%

# DTE (Days To Expiration) range for swing trades
OPTION_SWING_MIN_DTE = 30  # Minimum 30 days
OPTION_SWING_MAX_DTE = 45  # Maximum 45 days

# Delta ranges (probability and moneyness)
OPTION_CALL_DELTA_MIN = 0.40  # 40 delta
OPTION_CALL_DELTA_MAX = 0.60  # 60 delta
OPTION_PUT_DELTA_MIN = -0.60  # -60 delta
OPTION_PUT_DELTA_MAX = -0.40  # -40 delta

# Spread width (as ATR multiple)
OPTION_SPREAD_WIDTH_ATR = 1.0  # 1x ATR
```

**Delta Interpretation**:
```
Delta = Approximate probability of expiring ITM

Call Delta 0.50 (50 delta):
- ~50% chance of expiring in-the-money
- At-the-money (ATM)
- Moves $0.50 per $1.00 stock move

Call Delta 0.40 (40 delta):
- ~40% chance of expiring ITM
- Slightly out-of-the-money (OTM)
- Moves $0.40 per $1.00 stock move
- Cheaper premium than ATM

Call Delta 0.60 (60 delta):
- ~60% chance of expiring ITM
- Slightly in-the-money (ITM)
- Moves $0.60 per $1.00 stock move
- More expensive premium
```

#### C. Vertical Spread Construction

```python
def construct_bull_call_spread(current_price, expected_move_percent, atr, dte_target):
    """
    Bull Call Spread Construction

    Components:
    - Long Call (lower strike)
    - Short Call (higher strike)

    Strike Selection:
    - Long: ATM (50 delta) or slightly OTM (40-45 delta)
    - Short: Near expected target (aligned with expected_move_percent)

    Width: Approximately 1x ATR

    Example:
    Stock = $100
    Expected Move = 5% → $105 target
    ATR = $2.50

    Suggested Spread:
    - Long: $100 call (50 delta, ~$3.50 premium)
    - Short: $105 call (30 delta, ~$1.50 premium)
    - Width: $5 (2x ATR)
    - Net Debit: $2.00 ($3.50 - $1.50)
    - Max Profit: $3.00 ($5 width - $2 debit)
    - Max Loss: $2.00 (net debit)
    - R:R Ratio: 1.5:1
    """

    # Calculate target price
    target_price = current_price * (1 + expected_move_percent / 100)

    # Long strike: ATM or slightly OTM
    # Round to nearest strike (typically $5 or $10 increments)
    strike_increment = 5 if current_price < 200 else 10
    long_strike = round(current_price / strike_increment) * strike_increment

    # Short strike: Near target, width ~ 1x ATR
    spread_width = atr * OPTION_SPREAD_WIDTH_ATR
    short_strike = long_strike + round(spread_width / strike_increment) * strike_increment

    # DTE selection
    dte = (OPTION_SWING_MIN_DTE + OPTION_SWING_MAX_DTE) // 2  # ~37 days

    return {
        "spread_type": "Bull Call Spread",
        "long_strike": long_strike,
        "short_strike": short_strike,
        "width": short_strike - long_strike,
        "dte": dte,
        "long_delta_target": 0.50,
        "short_delta_target": 0.30,
        "rationale": f"Long {long_strike} call, short {short_strike} call "
                    f"for {expected_move_percent:.1f}% expected move"
    }
```

**Example Spread Suggestion**:
```
Symbol: AAPL
Current Price: $185.42
Expected Move: 5.0% ($9.27)
Target: $194.69
ATR: $4.62
Volatility: HIGH

Recommendation: BULL CALL SPREAD
- Long: $185 call (50 delta, 35 DTE)
- Short: $195 call (30 delta, 35 DTE)
- Width: $10
- Estimated Net Debit: $4.50
- Max Profit: $5.50 (width $10 - debit $4.50)
- Max Loss: $4.50 (net debit)
- R:R: 1.22:1
- Breakeven: $189.50 ($185 + $4.50)

Rationale: High IV (ATR% > 3%) makes naked calls expensive.
Spread caps cost while maintaining directional exposure to target.
```

#### D. Naked Directional Option

```python
def construct_naked_call(current_price, expected_move_percent, volatility, dte_target):
    """
    Naked Call Construction (Medium Volatility)

    Strike Selection:
    - ATM (50 delta) for maximum leverage
    - Slightly OTM (45 delta) for lower cost, higher leverage

    Example:
    Stock = $100
    Expected Move = 4%
    Volatility = MEDIUM

    Suggested Call:
    - Strike: $100 (ATM)
    - Delta: 50
    - DTE: 35 days
    - Estimated Premium: $3.00

    Profit Scenarios:
    - Stock to $105 (+5%): Option to ~$5.50, Profit = $2.50 (83%)
    - Stock to $110 (+10%): Option to ~$10.50, Profit = $7.50 (250%)

    Risk:
    - Max Loss: $3.00 premium (if stock < $100 at expiry)
    - Breakeven: $103.00
    """

    # Strike selection
    strike_increment = 5 if current_price < 200 else 10
    strike = round(current_price / strike_increment) * strike_increment

    # DTE
    dte = (OPTION_SWING_MIN_DTE + OPTION_SWING_MAX_DTE) // 2

    return {
        "option_type": "Call",
        "strike": strike,
        "dte": dte,
        "delta_target": 0.50,
        "rationale": f"ATM call at ${strike} for directional bullish exposure"
    }
```

#### E. Vehicle Selection Output

```python
# Integrated into trade plan
{
    "symbol": "AAPL",
    "trade_plans": [
        {
            "timeframe": "swing",
            "bias": "bullish",
            "entry_price": 185.42,
            "stop_price": 176.18,
            "target_price": 194.69,
            "expected_move_percent": 5.0,

            # Options recommendation
            "vehicle": "option_spread",
            "vehicle_notes": "High IV suitable for spreads; bull call spread for defined risk",
            "option_suggestions": {
                "dte_range": [30, 45],
                "spread_type": "Bull Call Spread",
                "delta_range": [0.40, 0.60],
                "expected_move_percent": 5.0,
                "spread_width_info": "Width typically 1x ATR equivalent for 5.0% expected move",
                "example_spread": {
                    "long_strike": 185,
                    "short_strike": 195,
                    "width": 10,
                    "dte": 35,
                    "rationale": "Long $185 call, short $195 call for 5.0% expected move"
                }
            }
        }
    ]
}
```

### Summary Paragraphs

The options_risk_analysis component is integrated directly into the get_trade_plan workflow, automatically determining whether stock or options are the optimal trading vehicle based on setup characteristics. The decision tree prioritizes stock trading for most scenarios (scalp trades, day trades, small expected moves < 3%, low volatility environments) and only suggests options when conditions justify the added complexity: swing timeframe (multi-day hold), sufficient expected move (≥3% to overcome premium decay), and appropriate volatility regime. This stock-first approach recognizes that options introduce additional risks (theta decay, vega sensitivity, bid-ask spread) that aren't warranted unless the setup offers compensating advantages like defined risk in high volatility or leverage on large expected moves.

The volatility-based vehicle selection differentiates between medium and high volatility environments with distinct recommendations. Medium volatility (ATR 1.5-3.0% of price) suggests directional options—ATM calls (40-60 delta) for bullish setups or ATM puts (-40 to -60 delta) for bearish setups—providing leveraged exposure without excessive premium costs. High volatility (ATR > 3.0% of price) triggers vertical spread recommendations: bull call spreads for bullish setups (long lower strike call + short higher strike call) or bear put spreads for bearish setups (long higher strike put + short lower strike put). Spreads cap maximum risk while reducing vega sensitivity, critical in high-IV environments where option premiums are elevated and subject to sharp volatility crush when IV normalizes.

The DTE and delta parameters follow professional trading conventions: 30-45 DTE for swing trades balances adequate time to capture the expected move against theta decay acceleration that occurs < 30 days, while 40-60 delta strikes offer favorable risk-reward without excessive probability decay of far OTM options. Strike selection aligns with technical targets—for a bull call spread with 5% expected move, the short strike is placed near the target price to maximize profit potential if the forecast materializes. Spread width suggestions use 1x ATR as a rule of thumb, creating practical spreads (e.g., $5-10 wide for $100-200 stocks) that balance profit potential against debit cost. The system provides complete option strategy specifications including example strikes, DTE, delta targets, and rationale, enabling traders to translate technical setups into specific options orders without separate analysis tools.

---

## Conclusion

These 9 MCP tools form a comprehensive technical analysis and risk management system combining classical indicators, modern machine learning, multi-timeframe analysis, and professional risk management principles. Each tool serves a distinct purpose while sharing common infrastructure (data fetching, indicator calculation, signal detection), enabling rapid development of new analysis capabilities on the proven foundation.

**Tool Interaction Flow**:
```
1. analyze_security → Detect signals + rank
2. analyze_fibonacci → Add Fibonacci levels to signals
3. get_trade_plan → Convert signals to risk-qualified trade plan
4. compare_securities → Rank multiple symbols by signals
5. screen_securities → Filter universe by criteria
6. scan_trades → Find qualified setups across universe
7. portfolio_risk → Aggregate risk across positions
8. morning_brief → Synthesize daily intelligence
9. options_risk_analysis → Determine optimal vehicle (stock vs options)
```

This architecture enables both granular analysis (individual stock deep dive) and portfolio-level intelligence (risk aggregation, opportunity scanning, market themes) within a unified framework.
