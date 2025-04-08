import ccxt
import pandas as pd
import time

# Initialize Binance Futures
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future'
    }
})

# Function to fetch candlestick data
def fetch_candlestick_data(symbol, timeframe='1m', limit=30):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

# Function to detect candlestick patterns
def detect_candlestick_patterns(df):
    patterns = {
        'Dragonfly Doji': lambda x: (x['close'] == x['open']).all() and (x['high'] == x['close']).all() and (x['low'] < x['close']).all(),
        'Bullish Engulfing': lambda x: (x['close'].iloc[-1] > x['open'].iloc[-1]) and (x['close'].iloc[-2] < x['open'].iloc[-2]) and (x['close'].iloc[-1] > x['open'].iloc[-2]) and (x['open'].iloc[-1] < x['close'].iloc[-2]),
        'Piercing Pattern': lambda x: (x['close'].iloc[-1] > x['close'].iloc[-2]) and (x['open'].iloc[-1] < x['low'].iloc[-2]) and (x['close'].iloc[-1] > x['open'].iloc[-2] + (x['close'].iloc[-2] - x['open'].iloc[-2]) / 2),
        'Bullish Harami': lambda x: (x['close'].iloc[-1] > x['open'].iloc[-1]) and (x['close'].iloc[-2] < x['open'].iloc[-2]) and (x['open'].iloc[-1] > x['close'].iloc[-2]) and (x['close'].iloc[-1] < x['open'].iloc[-2]),
        'Hammer': lambda x: (x['close'].iloc[-1] > x['open'].iloc[-1]) and ((x['high'].iloc[-1] - x['low'].iloc[-1]) > 2 * (x['close'].iloc[-1] - x['open'].iloc[-1])) and ((x['close'].iloc[-1] - x['low'].iloc[-1]) > 2 * (x['open'].iloc[-1] - x['low'].iloc[-1])),
        'Morning Star': lambda x: (x['close'].iloc[-3] > x['open'].iloc[-3]) and (x['close'].iloc[-2] < x['open'].iloc[-2]) and (x['close'].iloc[-1] > x['open'].iloc[-1]) and (x['close'].iloc[-1] > x['open'].iloc[-3]),
        'Bullish Abandoned Baby': lambda x: (x['close'].iloc[-3] > x['open'].iloc[-3]) and (x['close'].iloc[-2] < x['open'].iloc[-2]) and (x['close'].iloc[-1] > x['low'].iloc[-2]) and (x['open'].iloc[-1] > x['high'].iloc[-2]),
        'Tweezer Bottom': lambda x: (x['low'].iloc[-1] == x['low'].iloc[-2]) and (x['close'].iloc[-1] > x['open'].iloc[-1]),
        'Gravestone Doji': lambda x: (x['close'] == x['open']).all() and (x['low'] == x['close']).all() and (x['high'] > x['close']).all(),
        'Bearish Engulfing': lambda x: (x['close'].iloc[-1] < x['open'].iloc[-1]) and (x['close'].iloc[-2] > x['open'].iloc[-2]) and (x['close'].iloc[-1] < x['open'].iloc[-2]) and (x['open'].iloc[-1] > x['close'].iloc[-2]),
        'Shooting Star': lambda x: (x['close'].iloc[-1] < x['open'].iloc[-1]) and ((x['high'].iloc[-1] - x['low'].iloc[-1]) > 2 * (x['open'].iloc[-1] - x['close'].iloc[-1])) and ((x['high'].iloc[-1] - x['open'].iloc[-1]) > 2 * (x['high'].iloc[-1] - x['close'].iloc[-1])),
        'Evening Star': lambda x: (x['close'].iloc[-3] < x['open'].iloc[-3]) and (x['close'].iloc[-2] > x['open'].iloc[-2]) and (x['close'].iloc[-1] < x['open'].iloc[-1]) and (x['close'].iloc[-1] < x['open'].iloc[-3]),
        'Tweezer Top': lambda x: (x['high'].iloc[-1] == x['high'].iloc[-2]) and (x['close'].iloc[-1] < x['open'].iloc[-1])
    }
    
    for pattern, condition in patterns.items():
        if condition(df):
            if 'Bullish' in pattern or 'Dragonfly Doji' in pattern or 'Hammer' in pattern or 'Morning Star' in pattern or 'Bullish Abandoned Baby' in pattern or 'Tweezer Bottom' in pattern:
                return f"{pattern}: tăng"
            elif 'Bearish' in pattern or 'Gravestone Doji' in pattern or 'Shooting Star' in pattern or 'Evening Star' in pattern or 'Tweezer Top' in pattern:
                return f"{pattern}: giảm"
    return "Không có mô hình"

# List of symbols to fetch data for
symbols = ["BTCUSDT", "BNBUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "SUIUSDT", "ADAUSDT", "LTCUSDT", "TRXUSDT", "LINKUSDT", "TRUMPUSDT", "AVAXUSDT", "AAVEUSDT"]

# Fetch data for each symbol and detect candlestick patterns every minute
while True:
    for symbol in symbols:
        df = fetch_candlestick_data(symbol.replace("USDT", "/USDT"))
        result = detect_candlestick_patterns(df)
        print(f"Kết quả dự báo cho {symbol}: {result}")
    time.sleep(60)
