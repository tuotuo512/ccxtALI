import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator


def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)
    return tr


def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()
    return atr


def supertrend(data, period=10, factor=3):
    hl2 = (data['high'] + data['low']) / 2
    data['atr'] = atr(data, period)
    data['Upper_Band'] = hl2 + factor * data['atr']
    data['Lower_Band'] = hl2 - factor * data['atr']
    data['In_Uptrend'] = True

    for current in range(1, len(data.index)):
        previous = current - 1

        if data['close'].iloc[current] > data['Upper_Band'].iloc[previous]:
            data.at[data.index[current], 'In_Uptrend'] = True
        elif data['close'].iloc[current] < data['Lower_Band'].iloc[previous]:
            data.at[data.index[current], 'In_Uptrend'] = False
        else:
            data.at[data.index[current], 'In_Uptrend'] = data['In_Uptrend'].iloc[previous]
            if data.at[data.index[current], 'In_Uptrend'] and data['Lower_Band'].iloc[current] < data['Lower_Band'].iloc[previous]:
                data.at[data.index[current], 'Lower_Band'] = data['Lower_Band'].iloc[previous]
            if not data.at[data.index[current], 'In_Uptrend'] and data['Upper_Band'].iloc[current] > data['Upper_Band'].iloc[previous]:
                data.at[data.index[current], 'Upper_Band'] = data['Upper_Band'].iloc[previous]

    data['supertrend'] = np.where(data['In_Uptrend'], data['Lower_Band'], data['Upper_Band'])
    return data['supertrend']


    # return data_layer #画图测试时候返回data


def rsi(data: pd.DataFrame, period=14):
    rsi_indicator = RSIIndicator(data["close"], period)
    rsi = rsi_indicator.rsi()
    return rsi

#
# pd.options.mode.chained_assignment = None  # default='warn'
#
# from getData import get_data, initialize_exchange
#
# # 初始化交易所
# exchange = initialize_exchange()
#
# # 引用数据
# df, df_15m, df_30m, df_1h, df_4h = get_data(exchange)
#
#
# # 计算 Supertrend
# supertrend_data = supertrend(df_15m)
#
# # 计算 RSI
# rsi_data = rsi(df_15m)
#
#
# import mplfinance as mpf
#
# # 添加 Supertrend 到 DataFrame 用于绘图
# df_15m['Supertrend'] = supertrend_data['supertrend']
#
# # 创建一个额外的图层用于 RSI
# apds = [mpf.make_addplot(df_15m['Supertrend'], panel=0, color='g', secondary_y=False),
#         mpf.make_addplot(rsi_data, panel=1, color='r', secondary_y=True)]
#
# # 绘制K线图和RSI指标
# mpf.plot(df_15m, type='candle', style='binance', addplot=apds, volume=True, figratio=(12, 8), figscale=1.2)
