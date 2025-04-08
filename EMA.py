import ccxt.async_support as ccxt  # Use the asynchronous version of ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import asyncio
import time
from queue import Queue
from threading import Thread
import platform

# Khởi tạo đối tượng Binance Futures
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future',
    },
})

# Hàm để lấy dữ liệu nến từ Binance Futures
async def fetch_binance_futures_data(symbol, timeframe='1m', since=None, limit=500):
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)  # Ensure the timestamps are timezone-aware
    return df

# Hàm để tính toán EMA
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

# Hàm để xác định xu hướng
def determine_trend(ema_series):
    if len(ema_series) < 2:
        return "Không rõ ràng"  # Không đủ dữ liệu để xác định xu hướng
    current_ema = ema_series.iloc[-1]
    previous_ema = ema_series.iloc[-2]
    if current_ema > previous_ema:
        return "Tăng"
    elif current_ema < previous_ema:
        return "Giảm"
    else:
        return "Không rõ ràng"

# Hàm để xử lý một symbol
async def process_symbol(symbol, result_queue):
    since_1min = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000)  # Lấy dữ liệu trong 1 giờ qua
    since_2hours = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp() * 1000)  # Lấy dữ liệu trong 2 giờ qua
    since_3hours = int((datetime.now(timezone.utc) - timedelta(hours=3)).timestamp() * 1000)  # Lấy dữ liệu trong 3 giờ qua

    data_1min = await fetch_binance_futures_data(symbol, timeframe='1m', since=since_1min)
    data_5min = await fetch_binance_futures_data(symbol, timeframe='5m', since=since_2hours)
    data_15min = await fetch_binance_futures_data(symbol, timeframe='15m', since=since_3hours)

    ema_1min = calculate_ema(data_1min, 1)
    ema_5min = calculate_ema(data_5min, 5)
    ema_15min = calculate_ema(data_15min, 15)

    trend_1min = determine_trend(ema_1min)
    trend_5min = determine_trend(ema_5min)
    trend_15min = determine_trend(ema_15min)

    if trend_1min == trend_5min == trend_15min:
        combined_trend = trend_1min
    else:
        combined_trend = "Không rõ ràng"

    result_queue.put(f"Kết quả chung ({symbol}): {combined_trend}")

# Hàm tổng hợp kết quả
def aggregate_results(result_queue):
    while True:
        result = result_queue.get()
        if result is None:
            break
        print(result)

# Chương trình chính
def main():
    symbols = ["BTCUSDT", "BNBUSDT", "ETHUSDT", "XRPUSDT",  "SOLUSDT", "DOGEUSDT", "SUIUSDT", "ADAUSDT", "LTCUSDT", "TRXUSDT", "LINKUSDT", "TRUMPUSDT", "AVAXUSDT", "AAVEUSDT"]  # Danh sách các cặp symbol
    result_queue = Queue()

    aggregator_thread = Thread(target=aggregate_results, args=(result_queue,))
    aggregator_thread.start()

    async def job():
        tasks = [process_symbol(symbol, result_queue) for symbol in symbols]
        await asyncio.gather(*tasks)

    async def scheduler():
        while True:
            await job()
            await asyncio.sleep(60)  # Wait for 1 minute before running the job again

    # Set the event loop policy to use ProactorEventLoop on Windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Set the newly created event loop as the current event loop
    try:
        loop.run_until_complete(scheduler())
    except KeyboardInterrupt:
        result_queue.put(None)  # Dừng luồng tổng hợp
        aggregator_thread.join()
    finally:
        loop.close()

if __name__ == "__main__":
    main()
