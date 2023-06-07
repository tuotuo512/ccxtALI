import ccxt
from SuperRsi import rsi, supertrend
from SuperRsiTrend import MyStrategy
import pandas as pd
import time
import math

# 创建一个空字典，用于存储每个策略的仓位大小
positions_state = {i: 0 for i in range(13)}

def run():
    # 初始化交易所
    exchange = ccxt.binance({
        'apiKey': 'da8ySe13WWUUQ1Mo2uArvD7SomJnbwLHcqbSvkLrvJubNTIbwa3FjSyCE3Nk24Y1',
        'secret': 'WSsSf12OdoConSod3tnRQYL3FQMyKl8szdLQXnTHhjDfCvO6fojM86g0iZdQp2rw',
        'enableRateLimit': True,  # 遵守交易所的API请求速率限制
        'options': {
            'defaultType': 'swap',  # swap=永续
        },
        'proxies': {
            'http': 'http://127.0.0.1:10809',
            'https': 'http://127.0.0.1:10809',
        }
    })

    while True:
        # 获取最新的K线数据
        data = exchange.fetch_ohlcv('ETH/USDT:USDT', '1m', limit=1000)

        # 转换数据到pandas DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 将timestamp列转换为日期时间格式 下一行是换成世界时间
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        #df['timestamp'] = df['timestamp'].dt.tz_localize('Asia/Shanghai').dt.tz_convert('UTC')

        # 设置timestamp列为索引
        df.set_index('timestamp', inplace=True)

        df.index = df.index.floor('1Min')
        df_1m = df.resample('1Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 将df_1m保存到CSV文件中,查看缺失和对错
        #df_1m.to_csv('df_1m.csv')

        # 暂停一段时间，比如1分钟
        time.sleep(20)

        # 生成15分钟数据
        df_15m = df.resample('1Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})


        # 生成30分钟数据
        df_30m = df.resample('1Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 生成60分钟数据
        df_1h = df.resample('5Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        # 生成240分钟数据
        df_4h = df.resample('60Min').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

        ##################################################################
        # 1. 计算交易信号：使用MyStrategy的calculate_signals方法,来根据策略,得到交易信号。
        # 2. 根据交易信号决定是否进入仓位：如果你的交易信号提示,应该进入一个新的仓位，使用enter_position方法来进入仓位。
        # 3. 根据交易信号决定是否退出仓位：如果你的交易信号提示,应该退出一个仓位，使用exit_position方法来退出仓位。
        # 创建Strategy1对象
    #   #   引入策略部分
        # 创建 MyStrategy 实例: 通过创建实例，才能实际使用这些类中定义的方法和属性。
        # 创建策略实例
        strategy = MyStrategy(df_15m, df_30m, df_1h, df_4h)

        # 设置数据
        strategy.set_data(df_15m, df_30m, df_1h, df_4h)

        # 设置指标
        strategy.set_indicators()


        #   仓位必须是0.001的整数倍，总资金/df_15m收盘价 =可下仓位。还需要添加逻辑以处理极端的市场情况
        # 获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        #print(total_capital)
        # 相当于杠杆
        r_per = 0.02  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
        # 币最新价

        close_price = df_15m['close'].iloc[-1]
        # 仓位大小
        position_size = (total_capital * r_per) / close_price
        min_position_size = 0.003  # 最小下单量

        #ETH
        # 如果资金不够只下单最小单，如果够了 保留三个小数点
        if position_size < min_position_size:
            position_size = min_position_size
        else:
            position_size = math.floor(position_size / 0.003) * 0.003
            position_size = round(position_size, 3)  # 保留小数点后三位
        print('-------多单准备开仓仓位：',position_size,'-------')
        #btc
        # # 如果资金不够只下单最小单，如果够了 保留三个小数点
        # if position_size < min_position_size:
        #     position_size = min_position_size
        # else:
        #     position_size = round(position_size, 3)  # 保留小数点后三位

        #################################

    #   # 调用Mystrategy里的calculate_signals
        strategy.calculate_signals_1(position_size)
        #strategy.calculate_signals_2(position_size)

      #  print(positions_state)  #打印仓位字典看看


        #   1.策略1 如果交易信号提示进入仓位，在创建市价订单后，应该检查交易结果。
        if strategy.buy_signal11 == 1 and positions_state[0] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ETH/USDT:USDT', side='buy', amount=position_size)
            positions_state[0] = position_size  # 更新仓位信息
            print('----------------------------------------已下单成功买入:', position_size)
            print('strategy1-1上的仓位：', positions_state[0])

        #time.sleep(5)  # 休眠xx秒

        if strategy.sell_signal11 == -1 and positions_state[0] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ETH/USDT:USDT', side='sell', amount=positions_state[0])
            print('1-1下单成功卖出:', position_size)
            positions_state[0] = 0
            print(f"1-1平仓后剩余:{positions_state[0]}")

        #time.sleep(5)  # 休眠xx秒

#       #   2.策略2
        if strategy.buy_signal12 == 1 and positions_state[1] == 0:
            # 创建市价买单
            exchange.create_market_order(symbol='ETH/USDT:USDT', side='buy', amount=position_size)
            positions_state[1] = position_size  # 更新仓位信息
            print('成功买出:',position_size)
            print(f"strategy2-1上的仓位：{positions_state[1]}")


        #time.sleep(5)  # 休眠xx秒

        if strategy.sell_signal12 == -1 and positions_state[1] > 0:
            # 创建市价卖单
            exchange.create_market_order(symbol='ETH/USDT:USDT', side='sell', amount=positions_state[1])
            print('成功卖出:',position_size)
            positions_state[1] = 0
            print('2-1平仓后剩余:',positions_state[1])

            # if order['status'] == 'closed':  # 如果订单状态为已关闭，则表示交易成功
            #     print("Sell order completed, price: {}, volume: {}".format(order['average'], order['filled']))
            # else:
            #     print("Sell order failed, status: {}".format(order['status']))

        #time.sleep(5)  # 休眠xx秒

# 运行程序
run()
