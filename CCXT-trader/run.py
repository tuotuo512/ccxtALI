import ccxt
from SuperRsiTrend import MyStrategy
import pandas as pd
import time
import math

# 引入币安API设置的变量
import os

# 引入币安API设置的变量
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')


#   创建一个空字典，用于存储每个策略的仓位大小
def initialize_positions():
    # 初始化仓位状态字典，假设有10个策略（从0到9）
    positions_state = {i: 0 for i in range(10)}

    return positions_state


#  1. 初始化交易所
def initialize_exchange():
    # 创建并配置交易所实例
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,  # 遵守交易所的API请求速率限制
        'options': {'defaultType': 'swap'},  # swap=永续
        'proxies': {
            'http': 'http://127.0.0.1:18081',
            'https': 'http://127.0.0.1:18081',
        }
    })
    return exchange


# 2. 重连交易所
def reconnect_exchange(exchange):
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            exchange.load_markets()
            print("连接交易所成功")
            return True
        except Exception as e:
            print("重新连接交易所失败:", str(e))
            retry_count += 1
            time.sleep(60)
    print("无法重新连接交易所，达到最大重试次数")
    return False


# 3. 获取和处理市场数据

def fetch_and_process_market_data(exchange):
    data = exchange.fetch_ohlcv('ARB/USDT:USDT', '5m', limit=1000)

    # 暂停一段时间，比如1分钟
    time.sleep(20)

    # 转换数据到pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 将timestamp列转换为日期时间格式 下一行是换成世界时间
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df['timestamp'] = df['timestamp'].dt.tz_localize('Asia/Shanghai').dt.tz_convert('UTC')

    # 设置timestamp列为索引
    df.set_index('timestamp', inplace=True)

    df.index = df.index.floor('5min')
    df_5m = df.resample('5min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 将df_5m保存到CSV文件中,查看缺失和对错
    # df_5m.to_csv('df_5m.csv')

    # 生成15分钟数据
    df_15m = df.resample('15Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成30分钟数据
    df_30m = df.resample('30Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成60分钟数据
    df_1h = df.resample('60Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成240分钟数据
    df_4h = df.resample('60Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    return df_15m, df_30m, df_1h, df_4h


# 4. 计算交易信号和执行交易

def calculate_and_execute_trades(positions_state, exchange, df_15m, df_30m, df_1h):
    # 计算交易信号和执行交易的逻辑

    #  引入仓位
    # positions_state = initialize_positions()
    #  设置目前持有的策略仓位
    #  1、纯super
    positions_state[0] = 0  # 30m这里是手动填入 目前仓位持仓 1-1
    positions_state[1] = 0  # 1h                          1-2
    positions_state[2] = 0  # 15m进 30m出              1-3
    positions_state[3] = 0  # 15m进 15m出              1-4
    #   2、顺势super
    positions_state[4] = 0  # 这里15m图        2-1
    positions_state[5] = 0  # 这里30m图        2-2
    positions_state[6] = 0  # 这里小时图       2-3
    #  3、RSI  震荡
    positions_state[7] = 0  # 这里rsi15分进去，30分超买出来  2-4
    positions_state[8] = 0  # 这里30分超卖入场rsi ，30分超买出来     2-5

    # ====================================================================
    # 1. 计算交易信号：使用MyStrategy的calculate_signals方法,来根据策略,得到交易信号。
    # 2. 根据交易信号决定是否进入仓位：如果你的交易信号提示,应该进入一个新的仓位，使用enter_position方法来进入仓位。
    # 3. 根据交易信号决定是否退出仓位：如果你的交易信号提示,应该退出一个仓位，使用exit_position方法来退出仓位。
    # 创建Strategy1对象
    #   #   引入策略部分
    #   创建 MyStrategy 实例: 通过创建实例，才能实际使用这些类中定义的方法和属性。
    #   创建策略实例
    strategy = MyStrategy()

    #   设置数据
    strategy.set_data(df_15m, df_30m, df_1h)

    #   设置指标
    strategy.set_indicators()

    #       仓位设置====================================================
    #    仓位必须是0.001的整数倍，总资金/df_15m收盘价 =可下仓位。还需要添加逻辑以处理极端的市场情况
    #    获取账户的总资金  #加入错误处理机制
    total_capital = exchange.fetch_balance()['total']['USDT']
    # print('===程序新开始===，可用总资金',total_capital)
    # 相当于杠杆
    r_per = 0.1  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
    #   币最新价
    close_price = df_15m['close'].iloc[-1]
    #    仓位大小
    position_size = (total_capital * r_per) / close_price
    min_position_size = 5  # arb最小下单量

    #   查看仓位字典
    print(positions_state)

    #   如果资金不够，只下单最小单，如果够了， 则（ ARB保留1个小数点）
    if position_size < min_position_size:
        position_size = min_position_size
    else:
        position_size = math.floor(position_size / 0.003) * 0.003
        position_size = round(position_size, 1)  # 保留小数点后1位
    # print('-------多单准备开仓仓位：',position_size,'-------')

    # ----------------------------------------------------------------------------------
    #  调用MyStrategy里的calculate_signals
    strategy.calculate_signals_1()
    strategy.calculate_signals_2()

    #   定义交易必须大于某一个值
    if 4.3 > df_15m['close'].iloc[-1] > 1.1:
        #   信号一
        #   1.策略1 如果交易信号提示进入仓位，在创建市价订单后，应该检查交易结果。
        if strategy.buy_signal11 == 1 and positions_state[0] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[0] = position_size  # 更新仓位信息
            print('----------------------------------------成功买入1-1:', position_size)
            print('strategy1-1上的仓位：', positions_state[0])

        if strategy.sell_signal11 == -1 and positions_state[0] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[0])
            print('---------------------------------------成功卖出1-1:', positions_state[0])
            positions_state[0] = 0
            print(f"1-1平仓后剩余:{positions_state[0]}")

        #   ————————————
        #       #   2.策略2
        if strategy.buy_signal12 == 1 and positions_state[1] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[1] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入1-2:', position_size)
            print(f"strategy1-2上的仓位：{positions_state[1]}")

        if strategy.sell_signal12 == -1 and positions_state[1] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[1])
            print('---------------------------------------成功卖出1-2:', positions_state[1])
            positions_state[1] = 0
            print('1-2平仓后剩余:', positions_state[1])

        #   ————————————
        #       #   3.策略3
        if strategy.buy_signal13 == 1 and positions_state[2] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[2] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入1-3:', position_size)
            print('strategy1-3上的仓位：', positions_state[2])

        if strategy.sell_signal13 == -1 and positions_state[2] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[2])
            print('---------------------------------------成功卖出1-3:', positions_state[2])
            positions_state[2] = 0
            print('1-3平仓后剩余:', positions_state[2])
        #   ————————————
        #       #   4.策略4
        if strategy.buy_signal14 == 1 and positions_state[3] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[3] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入1-4:', position_size)
            print(f"strategy1-4上的仓位：{positions_state[3]}")

        if strategy.sell_signal14 == -1 and positions_state[3] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[3])
            print('---------------------------------------成功卖出1-4:', positions_state[3])
            positions_state[3] = 0
            print('1-4平仓后剩余:', positions_state[3])

        #           信号二   ··##

        #       #   5.策略5
        if strategy.buy_signal21 == 1 and positions_state[4] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[4] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入2-1:', position_size)
            print(f"strategy2-1上的仓位：{positions_state[4]}")

        if strategy.sell_signal21 == -1 and positions_state[4] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[4])
            print('---------------------------------------成功卖出2-1:', positions_state[4])
            positions_state[4] = 0
            print('2-1平仓后剩余:', positions_state[4])
        #   ————————————
        #       #   6.策略6
        if strategy.buy_signal22 == 1 and positions_state[5] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[5] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入2-2:', position_size)
            print(f"strategy2-2上的仓位：{positions_state[5]}")

        if strategy.sell_signal22 == -1 and positions_state[5] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[5])
            print('---------------------------------------成功卖出2-2:', positions_state[5])
            positions_state[5] = 0
            print('2-2平仓后剩余:', positions_state[5])
        #   ————————————
        #       #   7.策略7
        if strategy.buy_signal23 == 1 and positions_state[6] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[6] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入2-3:', position_size)
            print(f"strategy2-3上的仓位：{positions_state[6]}")

        if strategy.sell_signal23 == -1 and positions_state[6] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[6])
            print('---------------------------------------成功卖出2-3:', positions_state[6])
            positions_state[6] = 0
            print('2-3平仓后剩余:', positions_state[6])
        #   ————————————
        #       #   8.策略8
        if strategy.buy_signal24 == 1 and positions_state[7] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[7] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入2-4:', position_size)
            print(f"strategy2-4上的仓位：{positions_state[7]}")

        if strategy.sell_signal24 == -1 and positions_state[7] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[7])
            print('---------------------------------------成功卖出2-4:', positions_state[7])
            positions_state[7] = 0
            print('2-4平仓后剩余:', positions_state[7])
        #   ————————————
        #       #   9.策略9
        if strategy.buy_signal25 == 1 and positions_state[8] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
            positions_state[8] = position_size  # 更新仓位信息
            print('---------------------------------------成功买入2-5:', position_size)
            print(f"strategy2-5上的仓位：{positions_state[8]}")

        if strategy.sell_signal25 == -1 and positions_state[8] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[8])
            print('---------------------------------------成功卖出2-5:', positions_state[8])
            positions_state[8] = 0
            print('2-5平仓后剩余:', positions_state[8])


# 5.主运行函数
def run():
    exchange = initialize_exchange()
    positions_state = initialize_positions()

    while True:
        if not reconnect_exchange(exchange):
            break

        df_15m, df_30m, df_1h, df_4h = fetch_and_process_market_data(exchange)
        strategy = MyStrategy()
        strategy.set_data(df_15m, df_30m, df_1h)
        strategy.set_indicators()
        calculate_and_execute_trades(strategy, positions_state, exchange, df_15m, df_30m, df_1h)

        time.sleep(60)  # 等待一段时间


# 运行程序
run()
