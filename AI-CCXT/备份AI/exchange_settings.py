import ccxt
import time

# 引入币安API设置的变量
import os

api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')


# 初始化交易所
def initialize_exchange():
    # 创建并配置交易所实例
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'},
        'proxies': {
            'http': 'http://127.0.0.1:18081',
            'https': 'http://127.0.0.1:18081',
        }
    })
    return exchange


def reconnect_exchange(exchange):
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            exchange.load_markets()
            print("连接交易所成功")
            return True
        except Exception as e:
            print("重新连接交易所失败:", str(e))
            retry_count += 1
            time.sleep(120)
    print("无法重新连接交易所，达到最大重试次数")
    return False

