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
    params = (
        ("st_factor", 3),
        ("st_atr_period", 7),
        ("timeframe_5min", bt.TimeFrame.Minutes),
        ("timeframe_15min", bt.TimeFrame.Minutes * 15),
        ("timeframe_1hour", bt.TimeFrame.Minutes * 60),
    )

    def __init__(self):
        self.st_5min = SuperTrendATR(self.data0, factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_15min = SuperTrendATR(self.datas[1], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_1hour = SuperTrendATR(self.datas[2], factor=self.p.st_factor, atr_period=self.p.st_atr_period)

        self.st_5min.plotinfo.plotmaster = self.data0
        self.st_15min.plotinfo.plotmaster = self.data1
        self.st_1hour.plotinfo.plotmaster = self.data2

        #self.st_5min.plotinfo.subplot = True
        self.st_15min.plotinfo.subplot = True
        #self.st_1hour.plotinfo.subplot = True

        self.position1 = 0
        self.position2 = 0
        self.position3 = 0
        self.opened_this_cycle = [False, False, False]  ##防止相互串

    # 检查两个时间戳是否在同一小时内
    def is_same_hour(t1, t2):
        dt1 = bt.num2date(t1).replace(minute=0, second=0, microsecond=0)
        dt2 = bt.num2date(t2).replace(minute=0, second=0, microsecond=0)
        return dt1 == dt2

#同一个回测账户中使用三种不同的进场方式，但它们之间的交易互不影响。为实现这一目标，将每种进场方式分配给不同的仓位大小
    def next(self):
        # 5分钟周期突破
        if self.data0.datetime[0] == self.data0.datetime[-1] and self.data0.close[0] > self.st_5min.supertrend[
            0] and not self.position1:
            self.order_target_percent(target=0.3, data=self.data0)
            self.position1 = 1
            self.opened_this_cycle[0] = True

        # 15分钟周期突破
        if self.data1.datetime[0] == self.data0.datetime[0] and self.data0.close[0] > self.st_15min.supertrend[
            0] and not self.position2:
            self.order_target_percent(target=0.5, data=self.data0)
            self.position2 = 1
            self.opened_this_cycle[1] = True

        # 1小时周期突破
        if self.data2.datetime[0] == self.data0.datetime[0] and self.data0.close[0] > self.st_1hour.supertrend[
            0] and not self.position3:
            self.order_target_percent(target=0.2, data=self.data0)
            self.position3 = 1
            self.opened_this_cycle[2] = True

        # 平仓逻辑
        if self.position1 and self.data0.close[0] <= self.st_5min.supertrend[0] and self.opened_this_cycle[0]:
            self.order_target_percent(target=0, data=self.data0)
            self.position1 = 0
            self.opened_this_cycle[0] = False

        if self.position2 and self.data1.datetime[0] == self.data0.datetime[0] and self.data0.close[0] <= \
                self.st_15min.supertrend[0] and self.opened_this_cycle[1]:
            self.order_target_percent(target=0, data=self.data0)
            self.position2 = 0
            self.opened_this_cycle[1] = False

        if self.position3 and self.data2.datetime[0] == self.data0.datetime[0] and self.data0.close[0] <= \
                self.st_1hour.supertrend[0] and self.opened_this_cycle[2]:
            self.order_target_percent(target=0, data=self.data0)
            self.position3 = 0
            self.opened_this_cycle[2] = False

    # 策略类order_target_percent()方法来调整仓位
    def order_target_percent(self, target, data):
        super().order_target_percent(target=target, data=data)

    ##交易日志打印，定义LOG
    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print(f'{dt.isoformat()}, {txt}')

    ##交易日志打印

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                strategy = ""
                if self.position1:
                    strategy = "5-min"
                    self.opened_this_cycle[0] = True
                elif self.position2:
                    strategy = "15-min"
                    self.opened_this_cycle[1] = True
                elif self.position3:
                    strategy = "1-hour"
                    self.opened_this_cycle[2] = True
                self.log(f'BUY EXECUTED ({strategy}), {order.executed.price:.2f}')
            elif order.issell():
                strategy = ""
                if not self.position1:
                    strategy = "5-min"
                    self.opened_this_cycle[0] = False
                elif not self.position2:
                    strategy = "15-min"
                    self.opened_this_cycle[1] = False
                elif not self.position3:
                    strategy = "1-hour"
                    self.opened_this_cycle[2] = False
                self.log(f'SELL EXECUTED ({strategy}), {order.executed.price:.2f}')

                # 在这里添加净值输出
                self.log(f'CURRENT VALUE: {self.broker.getvalue():.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            # 更新opened_this_cycle的值，如果订单被拒绝、取消等
            if order.isbuy():
                if self.position1:
                    self.opened_this_cycle[0] = False
                elif self.position2:
                    self.opened_this_cycle[1] = False
                elif self.position3:
                    self.opened_this_cycle[2] = False


# 数据文件
data_file_1m = 'ETHUSDT-5m-2023-02.csv'
data_file_15m = 'ETHUSDT-15m-2023-02.csv'
data_file_1h = 'ETHUSDT-1h-2023-02.csv'
# 数据路径
data_file_path_1m = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_file_1m)
data_file_path_15m = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_file_15m)
data_file_path_1h = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_file_1h)

# 创建将毫秒时间戳转换为datetime对象的函数
def timestamp_to_datetime(timestamp_ms):
    dt = datetime.fromtimestamp(float(timestamp_ms) / 1000)
    return dt
def preprocess_dataframe(df):
    df['datetime'] = df['datetime'].apply(lambda x: float(x))
    return df

# 加载数据
def load_data(data_file_path, timeframe, compression):
    data = bt.feeds.GenericCSVData(
        dataname=data_file_path,
        dtformat=timestamp_to_datetime,
        timeframe=timeframe,
        compression=compression,
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
    return data

data_5m = load_data(data_file_path_1m, bt.TimeFrame.Minutes, 5)

# 创建Cerebro引擎
cerebro = bt.Cerebro()

# 将数据添加到Cerebro引擎
cerebro.adddata(data_5m)
cerebro.resampledata(data_5m, timeframe=bt.TimeFrame.Minutes, compression=15)
cerebro.resampledata(data_5m, timeframe=bt.TimeFrame.Minutes, compression=60)

# 添加策略到Cerebro引擎
cerebro.addstrategy(SuperTrendStrategy)

# 设置初始资本
cerebro.broker.setcash(100000.0)

# 运行Cerebro引擎
cerebro.run()

# 绘制图表
cerebro.plot(style='candle', barup='green', bardown='red', volume=False, plotind=[SuperTrendATR])
