import ccxt
import time

# 实例化 Binance 交易所
exchange = ccxt.binance({
    'apiKey': 'da8ySe13WWUUQ1Mo2uArvD7SomJnbwLHcqbSvkLrvJubNTIbwa3FjSyCE3Nk24Y1',
    'secret': 'WSsSf12OdoConSod3tnRQYL3FQMyKl8szdLQXnTHhjDfCvO6fojM86g0iZdQp2rw',
    'enableRateLimit': True,  # 遵守交易所的API请求速率限制
    'options': {
        'defaultType': 'swap',  ##swap=永续
    },
    'proxies': {
        'http': 'http://127.0.0.1:10809',
        'https': 'http://127.0.0.1:10809',
    }
})

# 设置请求速率限制
exchange.enableRateLimit = True

# 获取 BTC/USDT 的 1 分钟历史数据，往前 240 根
symbol = 'BTC/USDT'
timeframe = '1m'
limit = 240

if exchange.has['fetchOHLCV']:
    while True:
        try:
            # 获取历史数据
            data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            print(symbol, data)
            break  # 如果成功获取数据，就退出循环
        except ccxt.RequestTimeout as e:
            print('Request timed out, retrying in 5 seconds...')
            time.sleep(5)  # 如果请求超时，就等待 5 秒后再试
        except ccxt.ExchangeNotAvailable as e:
            print('Exchange not available, retrying in 5 seconds...')
            time.sleep(5)  # 如果交易所不可用，就等待 5 秒后再试
