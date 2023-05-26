from datetime import datetime
import os
import pandas as pd
import backtrader as bt

class SuperTrendATR(bt.Indicator):
    lines = ('supertrend', 'tsl')
    params = (('factor', 3), ('atr_period', 7),)

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

class CustomStrategy60_Day(bt.Strategy):
    params = (
        ("st_factor", 3),
        ("st_atr_period", 7),
    )

    def __init__(self):
        self.st_15min = SuperTrendATR(self.datas[0], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_1hour = SuperTrendATR(self.datas[1], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.position1 = 0

        # Plot Supertrend on the main chart
        self.st_15min.plotinfo.plotmaster = self.datas[0]
        self.st_1hour.plotinfo.plotmaster = self.datas[1]

    #开仓条件，以及手数
    def next(self):
        if self.data1.close[0] > self.st_15min.lines.supertrend[0] and not self.position1:
            self.buy(size=10)
            self.position1 = 1
        #分批平仓  收盘价要同时低于两个周期，否则容易交易频繁
        if (self.data1.close[0] < self.st_1hour.lines.supertrend[0] and self.data1.close[0] < self.st_15min.lines.supertrend[0])\
            and self.position1:
            self.sell(size=10)
            self.position1 = 0


    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'Buy executed at {order.executed.price:.2f}')
            elif order.issell():
                print(f'Sell executed at {order.executed.price:.2f}')

cerebro = bt.Cerebro()

data_15m = bt.feeds.GenericCSVData(
    dataname='ETHUSDT-15m-2023-02.csv',
    dtformat=lambda x: datetime.fromtimestamp(float(x) / 1000),
    timeframe=bt.TimeFrame.Minutes,
    compression=15,
    datetime=0,
    high=1,
    low=2,
    open=3,
    close=4,
    volume=5,
    openinterest=-1
)

data_1h = bt.feeds.GenericCSVData(
    dataname='ETHUSDT-1h-2023-02.csv',
    dtformat=lambda x: datetime.fromtimestamp(float(x) / 1000),
    timeframe=bt.TimeFrame.Minutes,
    compression=60,
    datetime=0,
    high=1,
    low=2,
    open=3,
    close=4,
    volume=5,
    openinterest=-1
)

cerebro.adddata(data_1h)
cerebro.adddata(data_15m)

cerebro.addstrategy(CustomStrategy60_Day)

cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.001)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot(style='candlestick')
