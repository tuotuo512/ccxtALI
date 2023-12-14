import ccxt
import pandas as pd
import time
import matplotlib.pyplot as plt
import mplfinance as mpf

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


# 定义获取数据的函数
def get_data(exchange):
    # 获取最新的1000根1分钟K线数据
    data = exchange.fetch_ohlcv('ARB/USDT:USDT', '5m', limit=1000)

    # 转换数据到pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 将timestamp列转换为日期时间格式
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 设置timestamp列为索引
    df.set_index('timestamp', inplace=True)

    # # 处理缺失值
    # df.fillna(df.mean(), inplace=True)
    #
    # # 检测异常值（这里使用IQR方法，可以根据需要修改）
    # Q1 = df.quantile(0.25)
    # Q3 = df.quantile(0.75)
    # IQR = Q3 - Q1
    # df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    #
    # # 使用新数据进行一些操作，比如更新模型、做出交易决策等

    # 暂停一段时间，比如1分钟
    time.sleep(10)

    # 生成5分钟数据
    df_5m = df.resample('5Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成15分钟数据
    df_15m = df.resample('15Min').agg({'open': 'first',
                                       'high': 'max',
                                       'low': 'min',
                                       'close': 'last',
                                       'volume': 'sum'})

    # 生成30分钟数据
    df_30m = df.resample('30Min').agg({'open': 'first',
                                       'high': 'max',
                                       'low': 'min',
                                       'close': 'last',
                                       'volume': 'sum'})

    # 生成60分钟数据
    df_1h = df.resample('60Min').agg({'open': 'first',
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

# 主循环
# exchange = initialize_exchange()
# while True:
#     # 获取数据
#     df_5m, df_15m, df_30m, df_1h, df_4h = get_data(exchange)
#
#     # 打印15分钟数据的最后10组
#     print("最后10组15分钟数据:")
#     print(df_15m.tail(10))  # tail(10)将返回最后10行的数据
#
#     # 绘制15分钟的K线图
#     mpf.plot(df_15m.tail(100), type='candle', style='binance', volume=True, show_nontrading=True, mav=(3,6,9))  # 这里用tail(100)来获取最后100条数据进行绘图
#     plt.show()
#
#     time.sleep(10)  # 等待一段时间，例如60秒