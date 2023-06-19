import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from getData import  get_data

def roc(data, length=9):
    source = data['close']  # 根据数据中的列名进行调整
    roc_values = 100 * (source - source.shift(length)) / source.shift(length)
    return roc_values

# 引用-------------------------------------------------------
df_5m, df_15m, df_30m, df_1h, df_4h = get_data()

roc_values = roc(df_5m)
plt.plot(roc_values, color='#2962FF')
plt.axhline(0, color='#787B86')
plt.title('Rate Of Change')
plt.xlabel('Time')
plt.ylabel('ROC')
plt.show()
