##引入指标
from SuperRsi import rsi, supertrend
import datetime


#   适合震荡上行，大趋势拿着多单，2小时跌破super做多，反转做多

# 总的类，我的交易策略所有东西都在里面
class MyStrategy:
    #   初始化每一根K线运行更新 这个FROMgetData ，必须填到init 里面
    def __init__(self):

        ##定义每个策略的仓位，初始化
        self.positions_state = {i: 0 for i in range(13)}  # Initialize positions for 13 strategies
        self.positions = {}  #
        # 信号初始化
        self.buy_signal11 = 0
        self.sell_signal11 = 0
        self.buy_signal12 = 0
        self.sell_signal12 = 0
        self.buy_signal13 = 0
        self.sell_signal13 = 0
        self.buy_signal14 = 0
        self.sell_signal14 = 0
        #   策略二
        self.buy_signal21 = 0
        self.sell_signal21 = 0
        self.buy_signal22 = 0
        self.sell_signal22 = 0
        self.buy_signal23 = 0
        self.sell_signal23 = 0
        self.buy_signal24 = 0
        self.sell_signal24 = 0
        self.buy_signal25 = 0
        self.sell_signal25 = 0

    #   引入时间周期 函数
    def set_data(self, df_15m, df_30m, df_1h, df_2h, df_4h):
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.df_2h = df_2h
        self.df_4h = df_4h

    #   引入指标函数：  定制数据和指标值
    def set_indicators(self):
        self.rsi_15m = rsi(self.df_15m, period=14)
        self.rsi_30m = rsi(self.df_30m, period=14)
        self.rsi_1h = rsi(self.df_1h, period=14)
        self.rsi_2h = rsi(self.df_2h, period=14)
        self.rsi_4h = rsi(self.df_4h, period=14)

        self.supertrend_15m = supertrend(self.df_15m, factor=3, period=10)
        self.supertrend_30m = supertrend(self.df_30m, factor=3, period=10)
        self.supertrend_1h = supertrend(self.df_1h, factor=3, period=10)
        self.supertrend_2h = supertrend(self.df_2h, factor=3, period=10)
        self.supertrend_4h = supertrend(self.df_4h, factor=3, period=10)

    #   命名 买入变量和打印 函数
    def enter_position(self, strategy_name):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"

    #  print(f"{key}信号买入仓位：{position_size}")

    #   命名 卖出变量和输出打印 函数
    def exit_position(self, strategy_name):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"

    # print(f"{key}信号平仓仓位：{position_size}")

    #   以下是：交易策略部分calculate_signals 方法中应有相应的错误处理和日志记录==================================================

    #   第一部分：反转抄底信号函数：  开仓部分，30分、60、4小时   spu突破就买
    def calculate_signals_1(self):

        #   打印当下需要看的数据
        print(datetime.datetime.now())
        print('最新价：', self.df_30m['close'].iloc[-2])
        print('15分钟轨道值：', self.supertrend_15m.iloc[-2])  # 打印super上轨参照
        print('30分钟轨道值：', self.supertrend_30m.iloc[-2])  # 打印super上轨参照
        print('60分钟轨道值：', self.supertrend_1h.iloc[-2])  # 打印super上轨参照

        #   1.买入逻辑：15分钟价格低于2小时supertrend的 xx% 值，
        if self.supertrend_2h.iloc[-2] * 0.972 > self.df_15m['close'].iloc[-1]:
            # 执行买入操作，标记买入为策略1-1
            self.enter_position('strategy1-1')
            # 设置交易信号
            self.buy_signal11 = 1
            print("信号：1-1买入")

        #   2. 买入逻辑：15分钟价格低于2小时supertrend的 xx% 值，
        if self.supertrend_2h.iloc[-2] * 0.952 > self.df_15m['close'].iloc[-1]:
            self.enter_position('strategy1-2')
            self.buy_signal12 = 1
            print("信号1-2买入")

        #   3. 买入逻辑：15分低于super xx %
        if self.supertrend_2h.iloc[-2] * 0.965 > self.df_15m['close'].iloc[-1]:
            self.enter_position('strategy1-3')
            self.buy_signal13 = 1
            print("信号1-3买入仓")

        #   4. 买入逻辑: 15分低于super xx %
        if self.supertrend_2h.iloc[-2] * 0.945 > self.df_15m['close'].iloc[-1]:
            self.enter_position('strategy1-4')
            self.buy_signal14 = 1
            print("信号：1-4买入")

    #   二.趋势单信号函数
    def calculate_signals_2(self):

        #   5.  买入逻辑：顺势， 15分级别进出
        if self.df_15m['close'].iloc[-3] < self.supertrend_15m.iloc[-3] < self.df_15m['close'].iloc[-2]:
            self.enter_position('strategy2-1')
            self.buy_signal21 = 1
            print("信号：2-1买入")

        #   6.  买入逻辑：30分级别顺势
        if self.df_30m['close'].iloc[-3] < self.supertrend_30m.iloc[-3] < self.df_30m['close'].iloc[-2]:
            self.enter_position('strategy2-2')
            self.buy_signal22 = 1
            print("信号：2-2买入")

        #   7.  买入逻辑：小时级别  顺势
        if self.df_4h['close'].iloc[-3] < self.supertrend_4h.iloc[-3] < self.df_4h['close'].iloc[-2]:
            self.enter_position('strategy2-3')
            self.buy_signal23 = 1
            print("信号：2-3买入")

        # rsi
        #   8.  买入逻辑：1小时 RSI 超卖
        if (self.rsi_1h.iloc[-2] < 25) and (self.df_2h['close'].iloc[-2] > self.df_2h['close'].iloc[-3] * 0.96):
            # 这里用的小时图的值往下2%
            self.enter_position('strategy2-4')
            self.buy_signal24 = 1
            print("信号：2-4买入")

        # 9.   买入逻辑：2小时rsi超卖
        if 30 > self.rsi_2h.iloc[-3]:
            self.enter_position('strategy2-5')
            self.buy_signal25 = 1
            print("信号：2-5买入")
