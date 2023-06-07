import ccxt
from SuperRsi import rsi, supertrend
from SuperRsiTrend import MyStrategy
import pandas as pd
import time
import math

#   创建一个空字典，用于存储每个策略的仓位大小
positions_state = {i: 0 for i in range(13)}

positions_state[0] = 0
positions_state[1] = 0
positions_state[2] = 0
positions_state[3] = 0
positions_state[4] = 0
positions_state[5] = 0
positions_state[6] = 0
positions_state[7] = 0
positions_state[8] = 0
positions_state[9] = 0

def run():
    # 初始化交易所
    exchange = ccxt.binance({
        'apiKey': '填api',
        'secret': '填秘钥',
        'enableRateLimit': True,  # 遵守交易所的API请求速率限制
        'options': {
            'defaultType': 'swap',  # swap=永续
        },
        'proxies': {
            'http': 'http://127.0.0.1:10809',  ## 这里改成自己的服务器地址
            'https': 'http://127.0.0.1:10809',##  这里改成自己的服务器地址
        }
    })
    #   还得引入空字典，这样可以为初始化负值
    positions_state[0] = 0      #30分钟的
    positions_state[1] = 0
    positions_state[2] = 0
    positions_state[3] = 0
    positions_state[4] = 0
    positions_state[5] = 0
    positions_state[6] = 0
    positions_state[7] = 0
    positions_state[8] = 0
    positions_state[9] = 0


    while True:

        # 获取最新的K线数据，1000根
        data = exchange.fetch_ohlcv('ARB/USDT:USDT', '1m', limit=1000)

        # 暂停一段时间，比如1分钟
        time.sleep(20)

        # 转换数据到pandas DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 将timestamp列转换为符合PD格式的日期时间
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # 设置timestamp列为索引，类似第一行 引导
        df.set_index('timestamp', inplace=True)

        #将索引值取整到最接近的1分钟，可以将具有相近时间戳的数据点归并到同一个时间段内，以便进行聚合操作
        df.index = df.index.floor('1Min')

        # 生成1分钟数据
        df_1m = df.resample('1Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 检测用：将df_1m保存到CSV文件中,查看缺失和对错
        #df_1m.to_csv('df_1m.csv')

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

        #   开始引入策略  -------------------------------------------------------------------------------------
        # 1. 计算交易信号：使用MyStrategy的calculate_signals方法,来根据策略,得到交易信号。
        # 2. 根据交易信号决定是否进入仓位：如果你的交易信号提示,应该进入一个新的仓位，使用enter_position方法来进入仓位。
        # 3. 根据交易信号决定是否退出仓位：如果你的交易信号提示,应该退出一个仓位，使用exit_position方法来退出仓位。


    #   #   引入策略部分
        #   创建策略实例：创建 MyStrategy 实例: 通过创建实例，才能实际使用这些类中定义的方法和属性。
        strategy = MyStrategy(df_15m, df_30m, df_1h, df_4h)

        #   设置要引入数据
        strategy.set_data(df_15m, df_30m, df_1h, df_4h)

        #   设置要引入指标，这意思就是都引进来
        strategy.set_indicators()

#       仓位大小管理部分--------------------------------------------------------------------
        #    仓位必须是0.001的整数倍，总资金/df_15m收盘价 =可下仓位。还需要添加逻辑以处理极端的市场情况
        #    获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        #print('===程序新开始===，可用总资金',total_capital)
        # 相当于杠杆
        r_per = 0.7  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
        #   币最新价
        close_price = df_15m['close'].iloc[-1]
        #    仓位大小
        position_size = (total_capital * r_per) / close_price
        min_position_size = 5  # 最小下单量


        print(positions_state)
        #   ARB
        #   如果资金不够只下单最小单，如果够了 保留三个小数点
        if position_size < min_position_size:
            position_size = min_position_size
        else:
            position_size = math.floor(position_size / 0.003) * 0.003
            position_size = round(position_size, 1)  # 保留小数点后三位
        print('-------多单准备开仓仓位：',position_size,'-------')


#       开始引入信号部分  ----------------------------------------------------------------------
#    #  调用Mystrategy里的calculate_signals
        strategy.calculate_signals_1(position_size)
        strategy.calculate_signals_2(position_size)
        ## 定义交易必须大于某一个值
        if df_15m['close'].iloc[-2] > 1.1:

            #   1.策略1 如果交易信号提示进入仓位，在创建市价订单后，应该检查交易结果。
            if strategy.buy_signal11 == 1 and positions_state[0] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[0] = position_size  # 更新仓位信息
                print('----------------------------------------已下单成功买入:', position_size)
                print('strategy1-1上的仓位：', positions_state[0])

            #time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal11 == -1 and positions_state[0] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[0])
                print('---------------------------------------1-1下单成功卖出:', position_size)
                positions_state[0] = 0
                print(f"1-1平仓后剩余:{positions_state[0]}")

            #time.sleep(1)  # 休眠xx秒
    #   ————————————
    #       #   2.策略2
            if strategy.buy_signal12 == 1 and positions_state[1] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[1] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入1-2:',position_size)
                print(f"strategy1-2上的仓位：{positions_state[1]}")

            #time.sleep(5)  # 休眠xx秒

            if strategy.sell_signal12 == -1 and positions_state[1] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[1])
                print('---------------------------------------成功卖出1-2:',position_size)
                positions_state[1] = 0
                print('1-2平仓后剩余:',positions_state[1])

    #   ————————————
    #       #   3.策略3
            if strategy.buy_signal13 == 1 and positions_state[2] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[2] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入1-3:', position_size)
                print('strategy1-3上的仓位：', positions_state[2])

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal13 == -1 and positions_state[2] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[2])
                print('---------------------------------------成功卖出1-3:', position_size)
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

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal14 == -1 and positions_state[3] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[3])
                print('---------------------------------------成功卖出1-4:', position_size)
                positions_state[3] = 0
                print('1-4平仓后剩余:', positions_state[3])

    ####    信号二   ··##

    #       #   5.策略5
            if strategy.buy_signal21 == 1 and positions_state[4] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[4] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-1:', position_size)
                print(f"strategy2-1上的仓位：{positions_state[4]}")

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal21 == -1 and positions_state[4] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[4])
                print('---------------------------------------成功卖出2-1:', position_size)
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

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal22 == -1 and positions_state[5] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[5])
                print('---------------------------------------成功卖出2-2:', position_size)
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

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal23 == -1 and positions_state[6] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[6])
                print('---------------------------------------成功卖出2-3:', position_size)
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

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal24 == -1 and positions_state[7] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[7])
                print('---------------------------------------成功卖出2-4:', position_size)
                positions_state[67] = 0
                print('2-4平仓后剩余:', positions_state[7])
    #   ————————————
    #       #   9.策略9
            if strategy.buy_signal25 == 1 and positions_state[8] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[8] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-5:', position_size)
                print(f"strategy2-5上的仓位：{positions_state[8]}")

            # time.sleep(1)  # 休眠xx秒

            if strategy.sell_signal25 == -1 and positions_state[8] > 0:
                # 创建市价卖单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='sell', amount=positions_state[8])
                print('---------------------------------------成功卖出2-5:', position_size)
                positions_state[8] = 0
                print('2-5平仓后剩余:', positions_state[8])


# 运行程序
run()
