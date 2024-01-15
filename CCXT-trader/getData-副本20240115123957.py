import ccxt
import pandas as pd
import time
# import matplotlib.pyplot as plt
# import mplfinance as mpf

# 引入币安API设置的变量
import os

# 引入币安API设置的变量
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')


# 1. 初始化交易所
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
            print("开始：连接交易所成功")
            return True
        except Exception as e:
            print("重新连接交易所失败:", str(e))
            retry_count += 1
            time.sleep(120)
    print("无法重新连接交易所，达到最大重试次数")
    return False



# 定义获取数据的函数
def get_data(exchange):
    # 获取最新的1000根1分钟K线数据
    data = exchange.fetch_ohlcv('ARB/USDT:USDT', '1m', limit=1000)

    # 转换数据到pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 将timestamp列转换为日期时间格式
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 设置timestamp列为索引
    df.set_index('timestamp', inplace=True)

    # 暂停一段时间，比如1分钟
    time.sleep(10)

    # 生成5分钟数据
    df_5m = df.resample('3Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成15分钟数据
    df_15m = df.resample('5Min').agg({'open': 'first',
                                       'high': 'max',
                                       'low': 'min',
                                       'close': 'last',
                                       'volume': 'sum'})

    # 生成30分钟数据
    df_30m = df.resample('10Min').agg({'open': 'first',
                                       'high': 'max',
                                       'low': 'min',
                                       'close': 'last',
                                       'volume': 'sum'})

    # 生成60分钟数据
    df_1h = df.resample('30Min').agg({'open': 'first',
                                      'high': 'max',
                                      'low': 'min',
                                      'close': 'last',
                                      'volume': 'sum'})

    # 生成240分钟数据
    df_4h = df.resample('240Min').agg({'open': 'first',
                                       'high': 'max',
                                       'low': 'min',
                                       'close': 'last',
                                       'volume': 'sum'})

    return df_5m, df_15m, df_30m, df_1h, df_4h
    # 输出结果

