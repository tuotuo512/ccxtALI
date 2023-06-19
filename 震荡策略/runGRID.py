import ccxt
import time
import math

#   创建一个空字典，用于存《挂单》每个档位的仓位大小
positions_state = {
    0: 0,  # 初始仓位大小，
    1: 0,  # 初始仓位大小，
    2: 0,  # 初始仓位大小
    3: 0,  # 初始仓位大小
    4: 0,  # 初始仓位大小
    5: 0,  # 初始仓位大小
    6: 0,  # 初始仓位大小
    7: 0,  # 初始仓位大小

    # ... 继续添加其他仓位大小，默认为0
}

#   创建一个空字典，用于存《成交单》每个档位的仓位大小
positions_state_buy = {
    0: 0,  # 初始仓位大小，
    1: 0,  # 初始仓位大小，
    2: 0,  # 初始仓位大小
    3: 0,  # 初始仓位大小
    4: 0,  # 初始仓位大小
    5: 0,  # 初始仓位大小
    6: 0,  # 初始仓位大小
    7: 0,  # 初始仓位大小
}

positions_state_sell = {
    0: 0,  # 初始仓位大小，
    1: 0,  # 初始仓位大小，
    2: 0,  # 初始仓位大小
    3: 0,  # 初始仓位大小
    4: 0,  # 初始仓位大小
    5: 0,  # 初始仓位大小
    6: 0,  # 初始仓位大小
    7: 0,  # 初始仓位大小
}


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

    # 上下区间的数值
    x = 1750  # 上区间数值，根据实际情况填写
    y = 1700  # 下区间数值，根据实际情况填写
    z = 7  # 网格数量

    #   开始循环
    while True:

        if not reconnect_exchange():
            # 进一步处理无法连接的情况，例如退出程序或记录日志
            break
        # =======================================
        # 获取最新的K线数据
        data = exchange.fetch_ohlcv('ETH/USDT:USDT', '1m', limit=100)
        latest_price = data[-1][4]  # 获取最新收盘价，根据实际情况选择索引

        # 计算每个价格区间的间隔
        mid = (x + y) / 2
        # 计算每个价格区间的间隔 (上下可以不等距)
        price_interval_l = (mid - y) / z
        price_interval_h = (x - mid) / z

        # 暂停一段时间，比如1分钟
        time.sleep(20)

        #    获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        # print('===程序新开始===，可用总资金',total_capital)
        # 相当于杠杆
        r_per = 0.3  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
        #   币最新价
        #    仓位大小
        position_size = (total_capital * r_per) / latest_price
        min_position_size = 0.03  # ETH最小下单量

        #   查看仓位字典
        print(positions_state)

        #   如果资金不够，只下单最小单，如果够了， 则（ ETH保留1个小数点）
        if position_size < min_position_size:
            position_size = min_position_size
        else:
            position_size = math.floor(position_size / 0.003) * 0.003
            position_size = round(position_size, 3)  # 保留小数点后3位
        # print('-------多单准备开仓仓位：',position_size,'-------')

        # 策略逻辑
        if y <= latest_price <= x:

            # 在这几个档位里
            for position_index in range(z):

                #  如果买单的 ’挂单字典仓位‘ 没有， 挂满
                if positions_state[position_index] == 0:
                    buy_price = mid - position_index * price_interval_l  # 挂单买入的价格
                    # 执行开仓操作，根据实际情况调用交易所的平仓接口
                    order = exchange.create_limit_buy_order(symbol='ETH/USDT:USDT', amount=position_size, price=buy_price)
                    # 挂单字典仓位 填入仓位
                    positions_state[position_index] = position_size

                    # <挂单>完成后，就把 ”buy持仓字典“ 改了
                    print(f"-----成功挂单买入档位{position_index}:", position_size)

                    # 如果成交
                    if order['status'] == 'closed':
                        # 如果成交，更新已经买入的仓位字典
                        positions_state_buy[position_index] = position_size
                        print(f"-----成功买入档位{position_index}:", position_size)
# 平仓逻辑

                        # 卖出操作、卖出网格
                        sell_price = x - position_index * price_interval_h  # 挂单买入的价格
                        # 上接刚才的如果买单成交了，立刻挂卖单
                        order = exchange.create_limit_sell_order(symbol='ETH/USDT:USDT', amount=positions_state[position_index],
                                                         price=sell_price)
                        positions_state_sell[position_index] = position_size
                        print(f"----成功挂单卖出档位{position_index}:", position_size)

                        # 执行平仓操作，根据实际情况调用交易所的买入接口
                        if order['status'] == 'closed':
                            # 更新仓位字典
                            positions_state[position_index] = 0
                            positions_state_buy[position_index] = 0
                            print(f"-----成功平仓卖出档位{position_index}:",
                                  position_size)


# 运行程序
run()
