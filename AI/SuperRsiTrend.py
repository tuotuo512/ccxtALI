from SuperRsi import rsi, supertrend
import datetime


class MyStrategy:
    def __init__(self):
        # 初始化指标和数据框架

        self.indicators = {}
        self.dataframes = {}
        self.positions_state = {i: 0 for i in range(13)}
        self.positions = {}
        self.signals = {f"signal{i}": 0 for i in range(1, 26)}

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

    def enter_position(self, strategy_name):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"
        # 记录买入操作
        # 例如，可以将key和其他相关信息添加到self.positions中
        # self.positions[key] = {"type": "entry", "strategy": strategy_name, ...}

    def exit_position(self, strategy_name):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"
        # 记录卖出操作

    #   做一个函数，用来更新交易位置和信号
    def update_position(self, strategy_name, signal_type):
        """
        更新交易位置和信号，并打印信号信息
        :param strategy_name: 策略名称
        :param signal_type: 信号类型，1表示买入，-1表示卖出
        """
        # 根据信号类型执行相应的操作
        if signal_type == 1:
            self.enter_position(strategy_name)
            action = "买入"
        elif signal_type == -1:
            self.exit_position(strategy_name)
            action = "平仓"
        else:
            return  # 如果信号类型不是1或-1，则不执行任何操作

        # 更新信号并打印信息
        signal_key = f"signal{strategy_name[-2:]}"  # 提取信号编号
        self.signals[signal_key] = signal_type
        print(f"信号：{strategy_name} {action}")

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
        print('最新价：', df_30m['close'].iloc[-2])
        print('15分钟轨道值：', supertrend_15m.iloc[-2])  # 打印super上轨参照
        print('30分钟轨道值：', supertrend_30m.iloc[-2])  # 打印super上轨参照
        print('60分钟轨道值：', supertrend_1h.iloc[-2])  # 打印super上轨参照

        #   第一套策略……
        #   1. 反转，买入逻辑 30分进，30分出
        if df_30m['close'].iloc[-3] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-2]:
            self.update_position('strategy1-1', 1)  # 买入
        #   平仓逻辑：小时图super下穿
        if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3]:
            self.update_position('strategy1-1', -1)

        #   2. 买入逻辑：小时图进小时图出
        if df_1h['close'].iloc[-3] <= supertrend_1h.iloc[-3] < df_1h['close'].iloc[-2]:
            self.update_position('strategy1-2', 1)
        #   卖出逻辑：小时图下穿
        if df_1h['close'].iloc[-2] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-3]:
            self.update_position('strategy1-2', -1)

        #   3. 买入逻辑：15分进，30分出，小时图收盘价大于sup，小时图收盘价还小于4小时
        if (df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]) \
                and (df_1h['close'].iloc[-2] > supertrend_1h.iloc[-2]):
            self.update_position('strategy1-3', 1)

        #   卖出逻辑：按照半小时图
        if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3] \
                or (df_15m['close'].iloc[-2] < (0.98 * supertrend_15m.iloc[-3])):  # 小于suer止损
            self.update_position('strategy1-3', -1)

        #   4. 买入逻辑: 15m进15m出
        if df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]:
            self.update_position('strategy1-4', 1)

        #   卖出逻辑： 15m跌破
        if df_15m['close'].iloc[-2] < supertrend_15m.iloc[-3] < df_15m['close'].iloc[-3]:
            self.update_position('strategy1-4', -1)

    #   二.趋势共振单信号函数
    def calculate_signals_2(self):
        # 在 calculate_signals_1 中使用数据和指标
        df_15m = self.dataframes['15m']
        df_30m = self.dataframes['30m']
        df_1h = self.dataframes['1h']
        supertrend_15m = self.indicators['supertrend_15m']
        supertrend_30m = self.indicators['supertrend_30m']
        supertrend_1h = self.indicators['supertrend_1h']
        rsi_15m = self.indicators['rsi_15m']
        rsi_30m = self.indicators['rsi_30m']
        # rsi_1h = self.indicators['rsi_1h']

        #   5.  买入逻辑：顺势， 15分级别进出
        if (df_15m['close'].iloc[-3] <= supertrend_15m.iloc[-3] < df_15m['close'].iloc[-2]) and \
                (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
            self.update_position('strategy2-1', 1)
        #   卖出逻辑：15分跌破
        if df_15m['close'].iloc[-2] < supertrend_15m.iloc[-3] < df_15m['close'].iloc[-3]:
            self.update_position('strategy2-1', -1)

        #   6.  买入逻辑：30分级别顺势
        if (df_30m['close'].iloc[-3] <= supertrend_30m.iloc[-3] < df_30m['close'].iloc[-2]) and \
                (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
            self.update_position('strategy2-2', 1)
        #   卖出逻辑：30分跌破
        if df_30m['close'].iloc[-2] < supertrend_30m.iloc[-3] < df_30m['close'].iloc[-3]:
            self.update_position('strategy2-2', -1)

        #   7.  买入逻辑：小时级别  顺势
        if (df_1h['close'].iloc[-3] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-2]) and \
                (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.98):  # 这里用的小时图的值往下2%
            self.update_position('strategy2-3', 1)
            #   卖出逻辑: SUPER跌破
            if df_1h['close'].iloc[-2] < supertrend_1h.iloc[-3] < df_1h['close'].iloc[-3]:
                self.update_position('strategy2-3', -1)

        # rsi
        #   8.  买入逻辑：15分 RSI 超卖 和大趋势向上
        if (rsi_15m.iloc[-3] < 30) and (df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.96):
            # 这里用的小时图的值往下2%
            self.update_position('strategy3-1', 1)
        #   卖出逻辑： 30分super跌破
        if rsi_30m.iloc[-3] > 80:
            self.update_position('strategy3-1', -1)

        # 9.   买入逻辑：4小时以上，30分rsi超卖 和大趋势向上
        if (30 > rsi_30m.iloc[-3]) and (
                df_1h['close'].iloc[-2] > df_1h['close'].iloc[-3] * 0.96):  # 这里用的小时图的值往下2%
            self.update_position('strategy3-2', 1)
        #   卖出逻辑 30分rsi超买
        if rsi_30m.iloc[-3] > 80:
            self.update_position('strategy3-2', -1)
