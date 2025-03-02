import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
import mplfinance as mpf

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from getData import  get_data


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
    """Calculate supertrend given a DataFrame, period and factor"""
    hl2 = (data['high'] + data['low']) / 2
    data['atr'] = atr(data, period)

    data['Upper_Band'] = hl2 + factor * data['atr']
    data['Lower_Band'] = hl2 - factor * data['atr']

    data['In_Uptrend'] = True
    for current in range(1, len(data.index)):
        previous = current - 1

        if data['close'][current] > data['Upper_Band'][previous]:
            data['In_Uptrend'][current] = True
        elif data['close'][current] < data['Lower_Band'][previous]:
            data['In_Uptrend'][current] = False
        else:
            data['In_Uptrend'][current] = data['In_Uptrend'][previous]
            if data['In_Uptrend'][current] and data['Lower_Band'][current] < data['Lower_Band'][previous]:
                data['Lower_Band'][current] = data['Lower_Band'][previous]
            if not data['In_Uptrend'][current] and data['Upper_Band'][current] > data['Upper_Band'][previous]:
                data['Upper_Band'][current] = data['Upper_Band'][previous]

    data['supertrend'] = np.where(data['In_Uptrend'], data['Lower_Band'], data['Upper_Band'])
    return data['supertrend']


# RSI Indicator
def rsi(data: pd.DataFrame, period=14):
    """
    Function to compute RSI

    Args:
    data_layer : pandas DataFrame with close data_layer
    period : Period for RSI
    """
    rsi_indicator = RSIIndicator(data["close"], period)
    rsi = rsi_indicator.rsi()
    return rsi

pd.options.mode.chained_assignment = None  # default='warn'


# 引用-------------------------------------------------------
df_5m, df_15m, df_30m, df_1h, df_4h = get_data()



##防止修改原始文件
df_15m = df_15m.copy()

# 生成15分钟数据
data = df_15m.resample('15Min').agg({'open': 'first',
                                     'high': 'max',
                                     'low': 'min',
                                     'close': 'last',
                                     'volume': 'sum'})

# supertrend(data_layer) 是调用一个函数来计算超趋势指标，并返回一个结果
supertrend(data)


# 创建一个新的图表----------------------------------------------------
fig, ax = plt.subplots()

# 绘制K线图
mpf.plot(data, type='candle', ax=ax,volume=False, show_nontrading=True)

# 绘制supertrend
ax.plot(data.index, data['supertrend'], color='purple', linewidth=2, label='Supertrend')


# 设置图例
ax.legend()
# 显示图表
plt.show()


# Calculate supertrend
supertrend_values = data['supertrend']

# Save as a pandas Series
supertrend_series = pd.Series(supertrend_values  , name="supertrend")


# Print the last 100 values
print(supertrend_series.tail(100))
