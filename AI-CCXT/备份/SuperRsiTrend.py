##引入指标
from SuperRsi import rsi, supertrend
import pandas as pd
import ccxt
import datetime

class MyStrategy:
    #   初始化每一根K线运行更新 这个FROMgetData ，必须填到init 里面
    def __init__(self, df_15m, df_30m, df_1h, df_4h):
        ##定义每个策略的仓位，初始化
        self.positions_state = {i: 0 for i in range(13)}  # Initialize positions for 13 strategies
        self.positions = {}  #
        # 信号初始化
        self.buy_signal11 = 0
        self.sell_signal11 = 0
        self.buy_signal12 = 0
        self.sell_signal12 = 0
        # self.buy_signal13 = 0
        # self.sell_signal13 = 0
        # self.buy_signal14 = 0
        # self.sell_signal14 = 0
        # #   策略二
        # self.buy_signal21 = 0
        # self.sell_signal21 = 0
        # self.buy_signal22 = 0
        # self.sell_signal22 = 0
        # self.buy_signal23 = 0
        # self.sell_signal23 = 0
        # self.buy_signal24 = 0
        # self.sell_signal24 = 0
        # self.buy_signal25 = 0
        # self.sell_signal25 = 0

    #   引入时间周期
    def set_data(self, df_15m, df_30m, df_1h, df_4h):
        self.df_15m = df_15m
        self.df_30m = df_30m
        self.df_1h = df_1h
        self.df_4h = df_4h

    #   引入指标  定制数据和指标值
    def set_indicators(self):
        self.rsi_15m = rsi(self.df_15m, period=14)
        self.rsi_30m = rsi(self.df_30m, period=14)
        self.rsi_1h = rsi(self.df_1h, period=14)
        self.rsi_4h = rsi(self.df_4h, period=14)

        self.supertrend_15m = supertrend(self.df_15m, factor=3, period=14)
        self.supertrend_30m = supertrend(self.df_30m, factor=3, period=14)
        self.supertrend_1h = supertrend(self.df_1h, factor=3, period=14)
        self.supertrend_4h = supertrend(self.df_4h, factor=3, period=14)

    ## 命名 买入变量和打印
    def enter_position(self, strategy_name):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"

    #  print(f"{key}信号买入仓位：{position_size}")

    ## 命名 卖出变量和输出打印
    def exit_position(self, strategy_name, ):
        key = f"{strategy_name}_{datetime.datetime.utcnow()}"

    # print(f"{key}信号平仓仓位：{position_size}")

    ####以下是：交易策略部分calculate_signals 方法中应有相应的错误处理和日志记录

    #     交易策略1，反转策略
    # 信号第一部分：反转抄底   开仓部分，30分、60、4小时   spu突破就买
    def calculate_signals_1(self, position_size):
        #   ——————————————————————————测试————————————————————————————————————————————————
        #          #  0. 测试：买入逻辑
        #         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1]  :
        #             # # 执行买入操作,标记买入为策略1_1
        #             self.enter_position('strategy1-1')
        #             # 设置交易信号
        #             self.buy_signal11 = 1
        #             print(f"信号买入仓位：{position_size}")
        #
        #
        #         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1] :
        #             self.exit_position('strategy1-1')
        #             # 设置交易信号
        #             self.sell_signal11 = -1
        #             print(f"信号平仓仓位：{position_size}")
        #
        #         #   00. 测试：买入逻辑
        #         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1] :
        #             # # 执行买入操作,标记买入为策略1_1
        #             self.enter_position('strategy1-2')
        #             # 设置交易信号
        #             self.buy_signal12 = 1
        #             print(f"信号买入仓位：{position_size}")
        #
        #
        #         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1] :
        #             self.exit_position('strategy1-2')
        #             # 设置交易信号
        #             self.sell_signal12 = -1
        #             print(f"信号平仓仓位：{position_size}")
        #   --------------------------------测试结束--------------------------------------------------------
        #iloc[]用于基于整数位置的索引。它可以帮助你选择或操作数据。在iloc[]中，数字 -1代表最后一行(最新数据)

        print(datetime.datetime.now())
        print('最新价：', self.df_30m['close'].iloc[-2])
        print('1-1轨道值：', self.supertrend_30m.iloc[-2])  # 打印super上轨参照

        #   1. 反转，买入逻辑 30分钟super上穿  大级别仍未突破
        if self.df_30m['close'].iloc[-3] < self.supertrend_30m.iloc[-3] < self.df_30m['close'].iloc[-2]:# \
                #and self.df_30m['close'].iloc[-2] < self.df_4h['close'].iloc[-2]:
            #   执行买入操作,标记买入为策略1-1
            self.enter_position('strategy1-1')
            #   设置交易信号
            self.buy_signal11 = 1
            print("信号：1-1买入")
        #   平仓逻辑：小时图super下穿
        if self.df_30m['close'].iloc[-2] < self.supertrend_30m.iloc[-3] < self.df_30m['close'].iloc[-3]:
            self.exit_position('strategy1-1')
            # 设置交易信号
            self.sell_signal11 = -1
            print("信号：1-1平仓")

        print('1-2轨道值：', self.supertrend_1h.iloc[-2])  # 打印super上轨参照
        #   2. 买入逻辑：小时图上穿
        if self.df_1h['close'].iloc[-3] <= self.supertrend_1h.iloc[-3] < self.df_1h['close'].iloc[-2]:
            self.enter_position('strategy1-2')
            self.buy_signal12 = 1
            print("信号1-2买入")
        #   卖出逻辑：小时图下穿
        if self.df_1h['close'].iloc[-2] < self.supertrend_1h.iloc[-3]<self.df_1h['close'].iloc[-3] :
            self.exit_position('strategy1-2')
            # 设置交易信号
            self.sell_signal12 = -1
            print("信号：1-2平仓")

        # #   3. 买入逻辑：15分上穿，小时图收盘价大于sup，小时图收盘价还小于4小时
        # if (self.df_15m['close'].iloc[-2] <= self.supertrend_15m.iloc[-1] < self.df_15m['close'].iloc[-1]) \
        #         and (self.df_1h['close'].iloc[-1] > self.supertrend_1h.iloc[-1]) \
        #         and (self.df_1h['close'].iloc[-1] < self.df_4h['close'].iloc[-1]):
        #     self.enter_position('strategy1-3', position_size)
        #     self.signal13 = 1
        #     print(f"信号买入仓位：{position_size}")
        # #   卖出逻辑：按照小时图
        # if self.df_1h['close'].iloc[-1] < self.supertrend_1h.iloc[-1]:
        #     self.exit_position('strategy1-3', position_size)
        #     # 设置交易信号
        #     self.signal13 = -1
        #     print(f"信号平仓仓位：{position_size}")
        #
        # #   4. 买入逻辑: 4小时突破
        # if self.df_4h['close'].iloc[-2] <= self.supertrend_4h.iloc[-1] < self.df_4h['close'].iloc[-1]:
        #     self.enter_position('strategy1-4', position_size)
        #     self.signal14 = 1
        #     print(f"信号买入仓位：{position_size}")
        # #   卖出逻辑： 4小时跌破
        # if self.df_4h['close'].iloc[-1] < self.supertrend_4h.iloc[-1]:
        #     self.exit_position('strategy1-4', position_size)
        #     # 设置交易信号
        #     self.signal14 = -1
        #     print(f"信号平仓仓位：{position_size}")

#     # 二.趋势共振单信号
#     def calculate_signals_2(self, position_size):
#         #   5. 买入逻辑 15分顺势买
#         if (self.df_15m['close'].iloc[-2] <= self.supertrend_15m.iloc[-1] < self.df_15m['close'].iloc[-1]) and \
#                 self.df_1h['close'].iloc[-1] > self.df_4h['close'].iloc[-1]:
#             self.enter_position('strategy2-1', position_size)
#             self.signal21 = 'buy_strategy2-1'
#             print(f"信号买入仓位：{position_size}")
#         #   卖出逻辑：15分跌破
#         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1]:
#             self.exit_position('strategy2-1', position_size)
#             self.signal21 = 'sell_strategy2-1'
#             print(f"信号平仓仓位：{position_size}")
#
#         #   6. 买入逻辑：30分顺势买
#         if (self.df_30m['close'].iloc[-2] <= self.supertrend_30m.iloc[-1] < self.df_30m['close'].iloc[-1]) and \
#                 self.df_1h['close'].iloc[-1] > self.df_4h['close'].iloc[-1]:
#             self.enter_position('strategy2-2', position_size)
#             self.signal22 = 'buy_strategy2-2'
#             print(f"信号买入仓位：{position_size}")
#         #   卖出逻辑：30分跌破
#         if self.df_30m['close'].iloc[-1] < self.supertrend_30m.iloc[-1]:
#             self.exit_position('strategy2-2', position_size)
#             self.signal22 = 'sell_strategy2-2'
#             print(f"信号平仓仓位：{position_size}")
#
#         #   7. 买入逻辑：15分 RSI 超卖
#         if (self.rsi_15m .iloc[-2] < 30) and (self.df_1h['close'].iloc[-1] > self.df_1h['close'].iloc[-1]):
#             self.enter_position('strategy2-3', position_size)
#             self.signal23 = 'buy_strategy2-3'
#             print(f"信号买入仓位：{position_size}")
#         #   卖出逻辑: 15分SUPER跌破
#         if self.df_15m['close'].iloc[-1] < self.supertrend_15m.iloc[-1]:
#             self.exit_position('strategy2-3', position_size)
#             self.signal23 = 'sell_strategy2-3'
#             print(f"信号平仓仓位：{position_size}")
#
#         #   8. 买入逻辑：4小时以上，小时图突破super
#         if (self.df_1h['close'].iloc[-2] > self.supertrend_1h.iloc[-1] > self.df_1h['close'].iloc[-1]) and \
#                 (self.df_1h['close'].iloc[-1] > self.df_4h['close'].iloc[-1]):
#             self.enter_position('strategy2-4', position_size)
#             self.signal24 = 'buy_strategy2-4'
#             print(f"信号买入仓位：{position_size}")
#         #   卖出逻辑： 小时图rsi超买
#         if self.rsi_1h.iloc[-2] > 70:
#             self.exit_position('strategy2-4', position_size)
#             self.signal24 = 'sell_strategy2-4'
#             print(f"信号平仓仓位：{position_size}")
#
#         # 9. 买入逻辑：4小时以上，30分rsi超卖
#         if  (30 > self.rsi_30m.iloc[-2]) and (self.df_30m['close'].iloc[-1] > \
#                 self.df_4h['close'].iloc[-1]):
#             self.enter_position('strategy2-5', position_size)
#             self.signal25 = 'buy_strategy2-5'
#             print(f"信号买入仓位：{position_size}")
#         #   卖出逻辑 30分rsi超买
#         if self.rsi_30m.iloc[-2] > 75:
#             self.exit_position('strategy2-5', position_size)
#             self.signal25 = 'sell_strategy2-5'
#             print(f"信号平仓仓位：{position_size}")
#
# #
#
#     # 二.震荡单的信号
#     def calculate_signals_3(self, position_size):
#         # 10. 买入逻辑
#         if self.df_4h['close'].iloc[-2] <= self.supertrend_4h.iloc[-1] < self.df_4h['close'].iloc[-1]:
#             self.enter_position('strategy3-1', position_size)
#             self.signal = 'buy'
#
#         # 卖出逻辑
#         if self.df_4h['close'].iloc[-1] < self.supertrend_4h.iloc[-1]:
#             self.exit_position('strategy3-1', position_size)
#             self.signal = 'sell'
#
#         # 11. 买入逻辑
#         if self.self.rsi_15m .iloc[-1] < 30 and self.df_4h['close'].iloc[-1] > self.supertrend_4h.iloc[-1]:
#             self.enter_position('strategy3-2', position_size)
#             self.signal = 'buy'
#
#         # 卖出逻辑
#         if self.df_1h['rsi'].iloc[-1] > 70:
#             self.exit_position('strategy3-2', position_size)
#             self.signal = 'sell'
#
#         # 12. 买入逻辑：
#         if self.df_1h['rsi'].iloc[-1] < 30 and self.df_4h['close'].iloc[-1] > self.supertrend_4h.iloc[-1]:
#             self.enter_position('strategy3-3', position_size)
#             self.signal = 'buy'
#
#         # 卖出逻辑：
#         if self.df_1h['rsi'].iloc[-1] > 70:
#             self.exit_position('strategy3-3', position_size)
#             self.signal = 'sell'
