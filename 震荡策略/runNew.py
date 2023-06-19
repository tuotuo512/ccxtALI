import ccxt
from SuperRsi import rsi, supertrend
from NewStrategy import MyStrategy
import pandas as pd
import time
import math

#   创建一个空字典，用于存储每个策略的仓位大小
positions_state = {i: 0 for i in range(9)}

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
        'apiKey': 'TwbrGtP4y4epwunioTQwVJu1MucF3lE8cTVIKswQ1PS6FNRPwRRnJIdmVPcJHBpd',
        'secret': 'IbR2CmrZy7aisjKE9kpdFNgqTICyPi1fRyYqc14xv4XFStAeFeEpCS2nU9nRUTC7',
        'enableRateLimit': True,  # 遵守交易所的API请求速率限制
        'options': {
            'defaultType': 'swap',  # swap=永续
        },
        'proxies': {
            'http': 'http://127.0.0.1:10809',
            'https': 'http://127.0.0.1:10809',
        }
    })

    #   设置目前持有的策略仓位
    #   反转super
    positions_state[0] = 10  # 30m这里是手动填入 目前仓位持仓 1-1
    positions_state[1] = 10  # 1h                          1-2
    positions_state[2] = 10  # 15m进 30m出              1-3
    positions_state[3] = 10  # 15m进 15m出              1-4
    #   顺势super
    positions_state[4] = 10  # 这里15m图        2-1
    positions_state[5] = 10  # 这里30m图        2-2
    positions_state[6] = 10  # 这里小时图       2-3
    #  RSI  震荡
    positions_state[7] = 10  # 这里rsi15分进去，30分超买出来  2-4
    positions_state[8] = 10  # 这里30分超卖入场rsi ，30分超买出来     2-5

    #   连接异常处理====================
    max_retries = 3  # 最大重试次数

    def reconnect_exchange():
        retry_count = 0  # 当前重试次数

        while retry_count < max_retries:
            try:
                # 尝试重新连接交易所
                exchange.load_markets()
                print("连接交易所成功")
                return True  # 连接成功，返回True

            except Exception as e:
                # 处理异常情况
                print("重新连接交易所失败:", str(e))
                retry_count += 1  # 增加重试次数
                time.sleep(10)  # 暂停一段时间后再重试

        # 无法重新连接交易所，达到最大重试次数
        print("无法重新连接交易所，达到最大重试次数")
        return False

    #   开始循环
    while True:

        if not reconnect_exchange():
            # 进一步处理无法连接的情况，例如退出程序或记录日志
            break
        # =======================================
        # 获取最新的K线数据
        data = exchange.fetch_ohlcv('ARB/USDT:USDT', '5m', limit=1000)
        data1 = exchange.fetch_ohlcv('ARB/USDT:USDT', '1h', limit=1000)

        # 暂停一段时间，比如1分钟
        time.sleep(10)

        # 转换数据到pandas DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df1 = pd.DataFrame(data1, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 将timestamp列转换为日期时间格式 下一行是换成世界时间
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='ms')
        # df['timestamp'] = df['timestamp'].dt.tz_localize('Asia/Shanghai').dt.tz_convert('UTC')

        # 设置timestamp列为索引
        df.set_index('timestamp', inplace=True)
        df1.set_index('timestamp', inplace=True)

        df.index = df.index.floor('5min')
        df1.index = df1.index.floor('1H')

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
        df_1h = df1.resample('H').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 生成2H数据
        df_2h = df1.resample('2H').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 生成4h数据
        df_4h = df1.resample('4H').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

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
        strategy.set_data(df_15m, df_30m, df_1h, df_2h, df_4h)

        #   设置指标
        strategy.set_indicators()

        #       仓位设置====================================================
        #    仓位必须是0.001的整数倍，总资金/df_15m收盘价 =可下仓位。还需要添加逻辑以处理极端的市场情况
        #    获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        # print('===程序新开始===，可用总资金',total_capital)
        # 相当于杠杆
        r_per = 0.8  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
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
        #    #  调用Mystrategy里的calculate_signals
        strategy.calculate_signals_1()
        strategy.calculate_signals_2()

        #   定义交易必须大于某一个值  和小于某一个值停止
        close_price = 2.3
        stop_price = 1.1
        # 如果价格大于close_price，平掉该仓位
        if df_15m['close'].iloc[-1] > close_price:
            # 执行平仓操作
            exchange.create_order(symbol=positions_state['symbol'], type='market', side='sell',
                                  quantity=positions_state['quantity'])
            # 停止进一步执行，使用break语句跳出循环
            break

        else:
            #   信号一 ================================
            #   1.策略1 如果交易信号提示进入仓位，在创建市价订单后，应该检查交易结果。
            if strategy.buy_signal11 == 1 and positions_state[0] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[0] = position_size  # 更新仓位信息
                print('----------------------------------------成功买入1-1:', position_size)
                print('strategy1-1上的仓位：', positions_state[0])

            #      2.策略2
            if strategy.buy_signal12 == 1 and positions_state[1] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[1] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入1-2:', position_size)
                print(f"strategy1-2上的仓位：{positions_state[1]}")

            #       3.策略3
            if strategy.buy_signal13 == 1 and positions_state[2] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[2] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入1-3:', position_size)
                print('strategy1-3上的仓位：', positions_state[2])

            #       4.策略4
            if strategy.buy_signal14 == 1 and positions_state[3] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[3] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入1-4:', position_size)
                print(f"strategy1-4上的仓位：{positions_state[3]}")

            #           信号二

            #     5.策略5
            if strategy.buy_signal21 == 1 and positions_state[4] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[4] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-1:', position_size)
                print(f"strategy2-1上的仓位：{positions_state[4]}")

            #   ————————————
            #       #   6.策略6
            if strategy.buy_signal22 == 1 and positions_state[5] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[5] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-2:', position_size)
                print(f"strategy2-2上的仓位：{positions_state[5]}")

            #   ————————————
            #        7.策略7
            if strategy.buy_signal23 == 1 and positions_state[6] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[6] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-3:', position_size)
                print(f"strategy2-3上的仓位：{positions_state[6]}")

            #       8.策略8
            if strategy.buy_signal24 == 1 and positions_state[7] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[7] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-4:', position_size)
                print(f"strategy2-4上的仓位：{positions_state[7]}")

            #       #   9.策略9
            if strategy.buy_signal25 == 1 and positions_state[8] == 0:
                # 创建市价买单
                exchange.create_market_order(symbol='ARB/USDT:USDT', side='buy', amount=position_size)
                positions_state[8] = position_size  # 更新仓位信息
                print('---------------------------------------成功买入2-5:', position_size)
                print(f"strategy2-5上的仓位：{positions_state[8]}")


# 运行程序
run()
