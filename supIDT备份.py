from datetime import datetime
import os
import pandas as pd
import math
import backtrader as bt


# 创建SuperTrend指标类  基于tradingview
class SuperTrendATR(bt.Indicator):
    lines = ('supertrend', 'tsl')
    params = (('factor', 3), ('atr_period', 7),)  ##传递参数

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.p.atr_period)
        self.hl2 = (self.data.high + self.data.low) / 2
        self.up = self.hl2 - (self.p.factor * self.atr)
        self.dn = self.hl2 + (self.p.factor * self.atr)
        self.addminperiod(self.p.atr_period + 1)

    def next(self):
        t_up = max(self.up[0], self.lines.supertrend[-1]) if self.data.close[-1] > self.lines.supertrend[-1] else \
        self.up[0]
        t_down = min(self.dn[0], self.lines.supertrend[-1]) if self.data.close[-1] < self.lines.supertrend[-1] else \
        self.dn[0]

        if len(self) <= self.p.atr_period:
            self.lines.supertrend[0] = self.up[0]
            self.lines.tsl[0] = self.up[0]
        else:
            self.lines.supertrend[0] = t_up if self.data.close[0] > self.lines.supertrend[-1] else t_down
            self.lines.tsl[0] = t_up if self.data.close[0] > self.lines.supertrend[-1] else t_down


# 这里是 交易策略

class SuperTrendStrategy(bt.Strategy):
    params = (('factor', 3), ('atr_period', 7),)   ##传递参数

    def __init__(self):
        self.supertrend = SuperTrendATR(self.data, factor=self.p.factor, atr_period=self.p.atr_period)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.supertrend.supertrend[0]:
                self.buy()
        else:
            if self.data.close[0] < self.supertrend.supertrend[0]:
                self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')

                # 在这里添加净值输出
                self.log(f'CURRENT VALUE: {self.broker.getvalue():.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
         self.log('Order Canceled/Margin/Rejected')

# 数据文件和路径
data_file = 'ETHUSDT-15m-2023-02.csv'
data_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_file)

# 创建将毫秒时间戳转换为datetime对象的函数
def timestamp_to_datetime(timestamp_ms):
    dt = datetime.fromtimestamp(float(timestamp_ms) / 1000)
    return dt
def preprocess_dataframe(df):
    df['datetime'] = df['datetime'].apply(lambda x: float(x))
    return df

# 加载数据
data = bt.feeds.GenericCSVData(
    dataname=data_file_path,
    dtformat=timestamp_to_datetime,
    timeframe=bt.TimeFrame.Minutes,
    compression=15,
    datetime=0,
    high=1,
    low=2,
    open=3,
    close=4,
    volume=5,
    openinterest=-1,
    encoding='utf-8',
    preprocessor=preprocess_dataframe
)

# 创建Cerebro引擎
cerebro = bt.Cerebro()

# 将数据添加到Cerebro引擎
cerebro.adddata(data)

# 添加策略到Cerebro引擎
cerebro.addstrategy(SuperTrendStrategy)

# 设置初始资本
cerebro.broker.setcash(10000.0)

# 运行Cerebro引擎
cerebro.run()

# 绘制图表
cerebro.plot(style='candle', barup='green', bardown='red', volume=False, plotind=[SuperTrendATR])
