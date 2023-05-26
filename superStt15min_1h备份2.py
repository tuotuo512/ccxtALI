import pandas as pd
import backtrader.feeds as btfeeds
import ccxt
import pandas as pd
import backtrader as bt
import time
import os

##IP代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'

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


class RSIIndicator(bt.Indicator):
    lines = ('rsi',)
    params = (('period', 14),)

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data, period=self.p.period)

    def next(self):
        self.lines.rsi[0] = self.rsi[0]

class BaseStrategy(bt.Strategy):
    params = (
        ("st_factor", 3),
        ("st_atr_period", 7),
        ('rsi_period', 14),
        ("timeframe_1min", bt.TimeFrame.Minutes),
        ("timeframe_15min", bt.TimeFrame.Minutes * 15),
        ("timeframe_30min", bt.TimeFrame.Minutes * 30),
        ("timeframe_1hour", bt.TimeFrame.Minutes * 60),
        ("timeframe_4hour", bt.TimeFrame.Minutes * 240),
        ('portfolio_frac', 0.1),  # 设置默认的资金比例为10%,
        ('leverage', 3),  # 设置默认的杠杆比例为1，表示无杠杆
    )

    ##定义变量
    def __init__(self):
        # supertrend
        self.st_1min = SuperTrendATR(self.datas[0], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_15min = SuperTrendATR(self.datas[1], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_30min = SuperTrendATR(self.datas[2], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_1hour = SuperTrendATR(self.datas[3], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        self.st_4hour = SuperTrendATR(self.datas[4], factor=self.p.st_factor, atr_period=self.p.st_atr_period)
        # self.st_daily = SuperTrendATR(self.datas[4], factor=self.p.st_factor, atr_period=self.p.st_atr_period)

        # 把supertrend绘图在主体上
        self.st_1min.plotinfo.plotmaster = self.data0
        self.st_15min.plotinfo.plotmaster = self.data1
        self.st_30min.plotinfo.plotmaster = self.data2
        self.st_1hour.plotinfo.plotmaster = self.data3
        self.st_4hour.plotinfo.plotmaster = self.data4

        # RSI
        self.rsi_15min = bt.indicators.RelativeStrengthIndex(self.datas[1], period=self.p.rsi_period)
        self.rsi_30min = bt.indicators.RelativeStrengthIndex(self.datas[2], period=self.p.rsi_period)
        self.rsi_1hour = bt.indicators.RelativeStrengthIndex(self.datas[3], period=self.p.rsi_period)
        self.rsi_4hour = bt.indicators.RelativeStrengthIndex(self.datas[4], period=self.p.rsi_period)
        # self.rsi_daily = bt.indicators.RelativeStrengthIndex(self.datas[4], period=self.p.rsi_period)

        # 定义 CrossOver indicators
        self.co_up_st_15min = bt.indicators.CrossOver(self.datas[1].close, self.st_15min.lines.supertrend)
        self.co_up_st_30min = bt.indicators.CrossOver(self.datas[2].close, self.st_30min.lines.supertrend)
        self.co_up_st_1hour = bt.indicators.CrossOver(self.datas[3].close, self.st_1hour.lines.supertrend)
        self.co_up_st_4hour = bt.indicators.CrossOver(self.datas[4].close, self.st_4hour.lines.supertrend)

        ##定义每个策略的仓位
        self.positions_state = {i: 0 for i in range(13)}  # Initialize positions for 13 strategies
        self.size = {i: 0 for i in range(13)}  # Initialize size for 13 strategies

    def next(self):
        pos = self.getposition().size
        self.log('Total position size: {}'.format(pos))

    def any_positions(self, strategy_number):
        # Return True if the position for the specified strategy is set to 1
        return self.positions_state[strategy_number] == 0

    def log(self, txt, dt=None):
        """交易日志 Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 交易日志打印
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.log('CURRENT POSITION SIZE: {}'.format(self.broker.getposition(self.data).size))
                self.log('CURRENT PORTFOLIO VALUE: %.5f' % self.broker.getvalue())

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

                self.log('CURRENT POSITION SIZE: {}'.format(self.broker.getposition(self.data).size))
                self.log('CURRENT PORTFOLIO VALUE: %.5f' % self.broker.getvalue())

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

        # 记录下已执行的交易
        self.bar_executed = len(self)
    ################开仓条件、开仓多##########################################


##策略1 反转趋势
class Strategy1(BaseStrategy):
    def next(self):

        # 获取当前杠杆后可用总资金
        cash = self.broker.getvalue() * self.params.leverage
        ##一.反转抄底开仓部分，30分、60、4小时   spu突破就买
        # 1. Buy
        if self.co_up_st_30min > 0 and (
                self.datas[2].close[-1] < self.st_4hour.lines.supertrend[0]) and self.positions_state[0] == 0:
            # 计算购买手数，使用资金的指定比例
            self.size[0] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[0])
            self.positions_state[0] = 1
        # Sell conditions
        if self.co_up_st_30min < 0 and self.positions_state[0] == 1:
            self.close(size=self.size[0])
            self.positions_state[0] = 0

        # 2
        if self.co_up_st_1hour > 0 and (
                self.datas[3].close[-1] < self.st_4hour.lines.supertrend[0]) and self.positions_state[1] == 0:
            # 计算购买手数，使用资金的指定比例
            self.size[1] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[1])
            self.positions_state[1] = 1
        if self.co_up_st_1hour < 0 and self.positions_state[1] == 1:
            self.close(size=self.size[1])
            self.positions_state[1] = 0

        # 3 小时分突破了，但4小时没突破，15分回调买
        if self.co_up_st_15min > 0 and (
                self.datas[3].close[-1] > self.st_1hour.lines.supertrend[0]) and (
                self.datas[3].close[-1] < self.st_4hour.lines.supertrend[0]) and self.positions_state[2] == 0:
            self.size[2] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[2])
            self.positions_state[2] = 1
        if self.co_up_st_1hour < 0 and self.positions_state[2] == 1:
            self.close(size=self.size[2])
            self.positions_state[2] = 0

        # 4 4小时突破
        if self.co_up_st_4hour > 0 and self.positions_state[3] == 0:
            self.size[3] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[3])
            self.positions_state[3] = 1
        if self.co_up_st_4hour < 0 and self.positions_state[3] == 1:
            self.close(size=self.size[3])
            self.positions_state[3] = 0


# 二.趋势共振单
class Strategy2(BaseStrategy):
    def next(self):
        # 获取当前杠杆后可用总资金
        cash = self.broker.getvalue() * self.params.leverage
        # 1.1-同向进场 4小时正向
        # 5.大趋势里15分钟
        if self.co_up_st_15min > 0 and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[4] == 0:
            self.size[4] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[4])
            self.positions_state[4] = 1
        if self.co_up_st_15min[0] < 0 and self.positions_state[4] == 1:
            self.close(size=self.size[4])
            self.positions_state[4] = 0

        # 6.大趋势里30分钟信号
        if (self.co_up_st_30min > 0) and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[5] == 0:
            self.size[5] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[5])
            self.positions_state[5] = 1
        if self.co_up_st_30min < 0 and self.positions_state[5] == 1:
            self.close(size=self.size[5])
            self.positions_state[5] = 0
        # 7、大趋势里，rsi超卖入场
        if self.rsi_15min[0] < 30 and (self.datas[2].close[-1] > self.st_30min.lines.supertrend[0]) and (
                self.datas[3].close[0] > self.st_4hour.lines.supertrend[0]) and self.positions_state[6] == 0:
            self.size[6] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[6])
            self.positions_state[6] = 1
        if (self.co_up_st_15min[0] < 0 <= self.co_up_st_15min[-1]) and self.positions_state[6] == 1:
            self.close(size=self.size[6])
            self.positions_state[6] = 0

        # 2.2-趋势里，sup下破，反向进场
        # 8、小时sup下去买入，小时图超买平或者
        if (self.co_up_st_1hour < 0) and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[7] == 0:
            self.size[7] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[7])
            self.positions_state[7] = 1
        if self.rsi_1hour[0] > 70 and self.positions_state[7] == 1:
            self.close(size=self.size[7])
            self.positions_state[7] = 0

        # 9、 30分钟超卖买入,小时图sup下破卖出
        if (self.rsi_30min < 30 <= self.rsi_30min[-1]) and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[8] == 0:
            self.size[8] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[8])
            self.positions_state[8] = 1
            # self.log('BUY EXECUTED, Size: %s, Price: %.2f' % (self.size[8], self.data.close[0]))
        if (self.rsi_30min > 75 >= self.rsi_30min[-1]) and self.positions_state[8] == 1:
            self.close(size=self.size[8])
            self.positions_state[8] = 0
            # self.log('SELL EXECUTED, Size: %s, Price: %.2f' % (self.size[8], self.data.close[0]))


# 三.震荡市场，买入条件   基于4小时趋势
class Strategy3(BaseStrategy):
    def next(self):
        # 获取当前杠杆后可用总资金
        cash = self.broker.getvalue() * self.params.leverage
        # 3.1-small 小周期
        # 10、4小时突破
        if (self.co_up_st_4hour > 0) and self.positions_state[9] == 0:
            self.size[9] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[9])
            self.positions_state[9] = 1
        if (self.co_up_st_4hour < 0) and self.positions_state[9] == 1:
            self.close(size=self.size[9])
            self.positions_state[9] = 0
        # 11 15分钟超卖,小时图 sup 或者rsi超买离场
        if (self.rsi_15min < 30) and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[10] == 0:
            self.size[10] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[10])
            self.positions_state[10] = 1
        if (self.rsi_1hour > 70 >= self.rsi_1hour[-1]) and self.positions_state[10] == 1:
            self.close(size=self.size[10])
            self.positions_state[10] = 0
        # 12 小时超卖进场，4小时超买或者小时图跌破spu离场
        if (self.rsi_1hour < 30) and (
                self.datas[3].close[-1] > self.st_4hour.lines.supertrend[0]) and self.positions_state[11] == 0:
            self.size[11] = int(cash * self.params.portfolio_frac / self.data.close[0])
            self.buy(size=self.size[11])
            self.positions_state[11] = 1
        if (self.rsi_1hour > 70) and self.positions_state[11] == 1:
            self.close(size=self.size[11])
            self.positions_state[11] = 0


class PandasData(btfeeds.PandasData):
    params = (
        ('datetime', None),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', None)
    )


# 创建币安交易所的api
exchange = ccxt.binance({
    'apiKey': 'da8ySe13WWUUQ1Mo2uArvD7SomJnbwLHcqbSvkLrvJubNTIbwa3FjSyCE3Nk24Y1',
    'secret': 'WSsSf12OdoConSod3tnRQYL3FQMyKl8szdLQXnTHhjDfCvO6fojM86g0iZdQp2rw',
})
for i in range(3):  # 尝试三次
    try:
        data = exchange.fetch_ohlcv('ETH/USDT', '1m')
        # 如果成功获取数据，跳出循环
        break
    except ccxt.RequestTimeout:
        print("Timeout, retrying...")
        # 等待一段时间再重试
        time.sleep(2)
else:
    print("Failed to fetch data after 3 attempts")
    data = None

if data is not None:
    # 处理数据...
    pass
# 获取以太币的1分钟数据
bars = exchange.fetch_ohlcv('ETH/USDT', '1m', limit=500)
df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
df['date'] = pd.to_datetime(df['date'], unit='ms')
df.set_index('date', inplace=True)

##装载行情数据、策略
cerebro = bt.Cerebro()
# 载入三个策略
cerebro.addstrategy(Strategy1)
cerebro.addstrategy(Strategy2)
cerebro.addstrategy(Strategy3)
cerebro.broker.setcash(1000000.0)
# 装载数据

data_1m = PandasData(dataname=df)

##数据合成  用一分钟合成 15、30、60……
data_1m = cerebro.adddata(data_1m)
data_15m = cerebro.resampledata(data_1m, timeframe=bt.TimeFrame.Minutes, compression=15)
data_30m = cerebro.resampledata(data_1m, timeframe=bt.TimeFrame.Minutes, compression=30)
data_1h = cerebro.resampledata(data_1m, timeframe=bt.TimeFrame.Minutes, compression=60)
data_4h = cerebro.resampledata(data_1m, timeframe=bt.TimeFrame.Minutes, compression=240)

# 设置保证金比例。例如，设置为0.1表示10%的保证金
cerebro.broker.setcommission(margin=0.1, commission=1.5)

# 输出初始资金
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 假设已经运行了策略，结果保存在result变量中
results = cerebro.run()

# 输出最终资金
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 绘制图表
# cerebro.plot(style='candlestick')
cerebro.plot(style='candle', barup='green', bardown='red', volume=False, plotind=[SuperTrendATR])
