# 主程序运行
import time
import math
from SuperRsiTrend import MyStrategy
from getData import initialize_exchange, reconnect_exchange,fetch_and_process_market_data

# 引入交易所设置
exchange = initialize_exchange()

# 初始化仓位状态字典
initialize_positions = {f"{i}_{j}": (0, 0) for i in range(1, 4) for j in range(1, 6)}

# 假设信号从其他地方获得
signals = {}  # 这将被设置为包含策略信号的字典


# 2. 手动设置特定策略的仓位状态
def manual_update_positions():
    global initialize_positions
    # 示例：手动设置策略 '1_1' 的仓位为某个值，信号保持不变

    initialize_positions['1_1'] = (0, 0)  # 3m这里是手动填入 目前仓位持仓 1-1
    initialize_positions['1_2'] = (0, 0)  # 50m                   1-2
    initialize_positions['1_3'] = (0, 0)  # 15m进 15m出            1-3
    initialize_positions['1_4'] = (0, 0)  # 5进 30m出              1-4
    initialize_positions['1_5'] = (0, 0)  # 30进 30m出              1-4
    #   2、顺势super
    initialize_positions['2_1'] = (0, 0)  # 这里15m图        2-1
    initialize_positions['2_2'] = (0, 0)  # 这里30m图        2-2
    initialize_positions['2_3'] = (0, 0)  # 这里小时图       2-3
    #  3、RSI  震荡
    initialize_positions['3_1'] = (0, 0)  # 这里rsi15分进去，30分超买出来  2-4
    initialize_positions['3_2'] = (0, 0)  # 这里30分超卖入场rsi ，30分超买出来


# 更新一下仓位手动的
manual_update_positions()


# 3. 更新信号和仓位
def update_positions(signals):
    global initialize_positions

    for strategy_name in signals:
        if strategy_name in initialize_positions:
            _, current_position = initialize_positions[strategy_name]
            new_signal = signals[strategy_name]
            initialize_positions[strategy_name] = (new_signal, current_position)


# 4.主函数
def run():
    global initialize_positions
    # 获取数据
    historical_df = None  # 初始化历史数据DataFrame

    while True:
        if not reconnect_exchange(exchange):
            break

        # 每次循环时获取最新数据
        df_1m, df_3m, df_5m, df_15m, df_30m = fetch_and_process_market_data(exchange, historical_df)

        # print(df_15m.tail(5))

        strategy = MyStrategy()
        strategy.set_data(df_1m, df_3m, df_5m, df_15m, df_30m)  # 设置策略数据
        strategy.set_indicators()  # 计算指标

        # 执行策略计算信号
        strategy.calculate_signals_1()

        #   仓位设置管理部分====================================================
        #    仓位必须是0.001的整数倍，总资金/df_15m收盘价 =可下仓位。还需要添加逻辑以处理极端的市场情况
        #    获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        # print('===程序新开始===，可用总资金',total_capital)
        # 相当于杠杆
        r_per = 3  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
        #   币最新价
        close_price = df_1m['close'].iloc[-1]
        #    仓位大小
        position_size = (total_capital * r_per) / close_price
        min_position_size = 0.009  # ETH最小下单量

        #   如果资金不够，只下单最小单，如果够了， 则（ ETH保留1个小数点）
        if position_size < min_position_size:
            position_size = min_position_size
        else:
            position_size = math.floor(position_size / 0.009) * 0.009
            position_size = round(position_size, 1)  # 保留小数点后1位
        print('-------多单准备开仓仓位：', position_size, '-------')

        # 更新仓位状态
        update_positions(strategy.signals)

        #   查看仓位字典
        print(initialize_positions)

        # 在此处添加打印语句以查看signals的当前状态
        # print("当前信号状态：")
        # 执行交易
        for strategy_name in strategy.signals:
            execute_trade(exchange, strategy, strategy_name, initialize_positions, position_size)

        time.sleep(10)


# 6. 定义执行交易的函数

def execute_trade(exchange, strategy, strategy_name, positions_state, position_size):
    signal, position = positions_state.get(strategy_name, (0, 0))  # 获取信号和仓位

    print(f"准备执行交易 - 策略名称: {strategy_name}, 信号: {signal}, 仓位: {position}")
    time.sleep(5)
    if signal == 1 and position == 0:
        # 买入逻辑
        exchange.create_market_order(symbol='ETH/USDT:USDT', side='buy', amount=position_size)
        positions_state[strategy_name] = (signal, position_size)  # 更新仓位状态
        print(f'----------------------------------------成功买入{strategy_name}:', position_size)
        print(f'{strategy_name}上的仓位：', positions_state[strategy_name])

    elif signal == -1 and position > 0:
        # 卖出逻辑
        exchange.create_market_order(symbol='ETH/USDT:USDT', side='sell', amount=position)
        print(f'---------------------------------------成功卖出{strategy_name}:', position)
        positions_state[strategy_name] = (signal, 0)  # 清空仓位
        print(f'{strategy_name}平仓后剩余:', positions_state[strategy_name])


# 运行程序
run()
