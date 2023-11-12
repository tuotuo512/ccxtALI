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
            data['In_Uptrend'].iloc[current] = True
        elif data['close'].iloc[current] < data['Lower_Band'].iloc[previous]:
            data['In_Uptrend'].iloc[current] = False
        else:
            data['In_Uptrend'].iloc[current] = data['In_Uptrend'].iloc[previous]
            if data['In_Uptrend'][current] and data['Lower_Band'][current] < data['Lower_Band'][previous]:
                data['Lower_Band'].iloc[current] = data['Lower_Band'][previous]
            if not data['In_Uptrend'][current] and data['Upper_Band'][current] > data['Upper_Band'][previous]:
                data['Upper_Band'].iloc[current] = data['Upper_Band'][previous]

    data['supertrend'] = np.where(data['In_Uptrend'], data['Lower_Band'], data['Upper_Band'])
    return data


def rsi(data: pd.DataFrame, period=14):
    rsi_indicator = RSIIndicator(data["close"], period)
    rsi = rsi_indicator.rsi()
    return rsi

# pd.options.mode.chained_assignment = None  # default='warn'
# #
# # 引用
# df, df_15m, df_30m, df_1h, df_4h = get_data()

# ##防止修改原始文件
# data = df.copy()
#
# # 计算 supertrend
# supertrend(data)
#
# # 这将会删除所有'supertrend'列的值为NaN的行
# data['supertrend'].replace(0, np.nan, inplace=True)
# data.dropna(subset=['supertrend'], inplace=True)
#
# plt.figure(figsize=(12, 6))
# plt.plot(data['close'], label='close')
# plt.plot(data['supertrend'], label='supertrend', linestyle='--')
# plt.title('close Price / supertrend')
# plt.legend(loc='upper left')
# plt.grid(True)
# plt.show()
#
# # Calculate supertrend
# supertrend_values = supertrend(data)
#
# # Save as a pandas Series
# supertrend_series = pd.Series(supertrend_values, name="supertrend")
#
# # Print the last 100 values
# print(supertrend_series.tail(100))
#
# data.to_csv('df_1m.csv')
