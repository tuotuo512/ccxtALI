import matplotlib.pyplot as plt
import matplotlib.dates as mdates



###绘图
# 假设已经运行了策略，结果保存在result变量中
results = cerebro.run()

# 提取15分钟数据的DataFeed
data_15m = [strategy for strategy in results if isinstance(strategy, SuperTrendATR)][0].datas[0]

# 获取15分钟数据的日期、收盘价、supertrend、RSI
dates = mdates.date2num(data_15m.datetime.array)
close_prices = data_15m.close.array
supertrend = data_15m.supertrend.array
rsi = data_15m.rsi.array

# 创建新的图形
fig, ax1 = plt.subplots()

# 绘制K线图
ax1.plot_date(dates, close_prices, '-')
# 在同一个坐标轴上绘制supertrend
ax1.plot_date(dates, supertrend, '-')

# 创建另一个坐标轴来绘制RSI
ax2 = ax1.twinx()
ax2.plot_date(dates, rsi, '-')

# 显示图形
plt.show()
