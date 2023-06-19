import ccxt
import pandas as pd
import time
import matplotlib.pyplot as plt
import mplfinance as mpf


def get_data():
    # 初始化交易所
    exchange = ccxt.binance({
        'apiKey': 'TwbrGtP4y4epwunioTQwVJu1MucF3lE8cTVIKswQ1PS6FNRPwRRnJIdmVPcJHBpd',
        'secret': 'IbR2CmrZy7aisjKE9kpdFNgqTICyPi1fRyYqc14xv4XFStAeFeEpCS2nU9nRUTC7',
        'enableRateLimit': True,  # 遵守交易所的API请求速率限制
        'options': {
            'defaultType': 'swap',  # swap=永续
        },
        'proxies': {
            'http': 'http://127.0.0.1:10809',
            'https': 'http://127.0.0.1:10809',
        }
    })

    while True:
        # 获取最新的1000根1分钟K线数据
        data = exchange.fetch_ohlcv('ETH/USDT:USDT', '5m', limit=1000)

        # 转换数据到pandas DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 将timestamp列转换为日期时间格式
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # 设置timestamp列为索引
        df.set_index('timestamp', inplace=True)

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

#定义了一个名为get_data的函数。在Python中，定义一个函数不会自动执行它，需要明确地调用函数以便执行它
df_5m, df_15m, df_30m, df_1h, df_4h = get_data()


#print(df_15m)#
#
# 绘制带时间的K线图
# mpf.plot(df_1m, type='candle', style='binance')
# mpf.plot(df_4h, type='candle', style='binance')
# plt.show()
