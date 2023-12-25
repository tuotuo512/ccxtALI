# 交易策略逻辑部分

from SuperRsi import rsi, supertrend
import datetime


class MyStrategy:
    def __init__(self):
        # 初始化指标和数据框架

        self.indicators = {}
        self.dataframes = {}
        self.positions = {}
        self.signals = {}  # 初始化为空字典

    def set_data(self, df_15m, df_30m, df_1h):
        self.dataframes = {
            '15m': df_15m,
            '30m': df_30m,
            '1h': df_1h
        }

    def set_indicators(self):
        for timeframe in ['15m', '30m', '1h']:
            self.indicators[f"rsi_{timeframe}"] = rsi(self.dataframes[timeframe], period=14)
            self.indicators[f"supertrend_{timeframe}"] = supertrend(self.dataframes[timeframe], factor=3, period=10)

    # 修改 update_position 方法来更新 self.signals 字典，直接使用策略名称作为键：
    def update_position(self, strategy_name, signal_type):
        self.signals[strategy_name] = signal_type
        # print(f"信号更新: {strategy_name} = {signal_type}")

    #   以下是：交易策略部分calculate_signals 方法中应有相应的错误处理和日志记录==================================================

    #   第一部分：反转抄底信号函数：  开仓部分，30分、60、4小时   spu突破就买
    def calculate_signals_1(self):
        # 在 calculate_signals_1 中调用数据和指标
        df_15m = self.dataframes['15m']
        df_30m = self.dataframes['30m']
        df_1h = self.dataframes['1h']
        supertrend_15m = self.indicators['supertrend_15m']
        supertrend_30m = self.indicators['supertrend_30m']
        supertrend_1h = self.indicators['supertrend_1h']

        # iloc[]用于基于整数位置的索引。它可以帮助你选择或操作数据。在iloc[]中，数字 -1代表最后一行(最新数据)
        #   打印当下需要看的数据
        print(datetime.datetime.now())
        print('最新价：', df_15m['close'].iloc[-1])
        print('15分钟轨道值：', supertrend_15m.iloc[-2])  # 打印super上轨参照
        print('30分钟轨道值：', supertrend_30m.iloc[-2])  # 打印super上轨参照
        print('60分钟轨道值：', supertrend_1h.iloc[-2])  # 打印super上轨参照

        #   第一套.策略……
        #   1. 反转，买入逻辑 30分进，30分出
        # # 测试
        # if df_15m['close'].iloc[-3] > supertrend_1h.iloc[-3]:
        #     # 更新打印语句以匹配新的策略命名规则
        #     strategy_name = "1_1"  # 根据update_position中的参数来构造策略名称
        #     self.update_position(strategy_name, 1)  # 买入信号
        #     print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认

        # 1_1开仓逻辑：15分图进 15分出
        if df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]:
            strategy_name = "1_1"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, 1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认
        #   卖出逻辑： 15m跌破
        if df_15m['close'].iloc[-2] < supertrend_15m.iloc[-3] < df_15m['close'].iloc[-3]:
            strategy_name = "1_1"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, -1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认

        #   1_2. 买入逻辑: 30m进30m出
        if df_30m['close'].iloc[-3] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-2]:
            strategy_name = "1_2"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, 1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认
            # 1_4平仓逻辑：半小时图super下穿
        if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3]:
            strategy_name = "1_2"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, -1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认

        #   1_3. 买入逻辑：15分进，30分出，小时图收盘价大于sup，小时图收盘价还小于4小时
        if (df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]) \
                and (df_1h['close'].iloc[-2] > supertrend_1h.iloc[-2]):
            strategy_name = "1_3"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, 1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认
        #   卖出逻辑：按照半小时图
        if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3] \
                or (df_15m['close'].iloc[-2] < (0.98 * supertrend_15m.iloc[-3])):  # 小于suer止损
            strategy_name = "1_3"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, -1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认

        #   1_4. 买入逻辑：1小时图进 1小时图出
        if df_1h['close'].iloc[-3] <= supertrend_1h.iloc[-3] < df_1h['close'].iloc[-2]:
            strategy_name = "1_4"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, 1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认
        #   卖出逻辑：小时图下穿
        if df_1h['close'].iloc[-2] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-3]:
            strategy_name = "1_4"  # 根据update_position中的参数来构造策略名称
            self.update_position(strategy_name, -1)  # 买入信号
            print(f"更新了信号 {strategy_name}: {self.signals[strategy_name]}")  # 打印以确认

    # #   第二套.趋势共振单信号函数
    # def calculate_signals_2(self):
    #     # 在 calculate_signals_1 中使用数据和指标
    #     df_15m = self.dataframes['15m']
    #     df_30m = self.dataframes['30m']
    #     df_1h = self.dataframes['1h']
    #     supertrend_15m = self.indicators['supertrend_15m']
    #     supertrend_30m = self.indicators['supertrend_30m']
    #     supertrend_1h = self.indicators['supertrend_1h']
    #     rsi_15m = self.indicators['rsi_15m']
    #     rsi_30m = self.indicators['rsi_30m']
    #     # rsi_1h = self.indicators['rsi_1h']
    #
    #     #   5.  买入逻辑：顺势， 15分级别进出
    #     if (df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]) and \
    #             (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
    #         self.update_position('strategy2-1', 1)
    #     #   卖出逻辑：15分跌破
    #     if df_15m['close'].iloc[-2] < supertrend_15m.iloc[-3] < df_15m['close'].iloc[-3]:
    #         self.update_position('strategy2-1', -1)
    #
    #     #   6.  买入逻辑：30分级别顺势
    #     if (df_30m['close'].iloc[-3] <= supertrend_30m.iloc[-3] < df_30m['close'].iloc[-2]) and \
    #             (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
    #         self.update_position('strategy2-2', 1)
    #     #   卖出逻辑：30分跌破
    #     if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3]:
    #         self.update_position('strategy2-2', -1)
    #
    #     #   7.  买入逻辑：小时级别  顺势
    #     if (df_1h['close'].iloc[-3] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-2]) and \
    #             (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
    #         self.update_position('strategy2-3', 1)
    #         #   卖出逻辑: SUPER跌破
    #         if df_1h['close'].iloc[-2] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-3]:
    #             self.update_position('strategy2-3', -1)
    #
    #     # 第三套策略. rsi  震荡
    #     #   8.  买入逻辑：15分 RSI 超卖 和大趋势向上
    #     if (rsi_15m.iloc[-3] < 30) and (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.96):
    #         # 这里用的小时图的值往下2%
    #         self.update_position('strategy3-1', 1)
    #     #   卖出逻辑： 30分super跌破
    #     if rsi_30m.iloc[-3] > 80:
    #         self.update_position('strategy3-1', -1)
    #
    #     # 9.   买入逻辑：4小时以上，30分rsi超卖 和大趋势向上
    #     if (30 > rsi_30m.iloc[-3]) and (
    #             df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.96):  # 这里用的小时图的值往下2%
    #         self.update_position('strategy3-2', 1)
    #     #   卖出逻辑 30分rsi超买
    #     if rsi_30m.iloc[-3] > 80:
    #         self.update_position('strategy3-2', -1)
