from typing import List, Any

import ccxt
import time
import math

#   创建一个空字典，用于存  持仓的  每个档位的仓位大小
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

#   创建一个空字典，用于存  买《挂单》 每个档位的仓位大小
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
# 卖  《挂单》 及仓位
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

print("程序启动")


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

    # 上下区间的数值 =================================
    x = 1895  # 上区间数值，根据实际情况填写
    y = 1885  # 下区间数值，根据实际情况填写
    z = 7  # 网格数量
    # ============================================

    unfilled_orders = []
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
        #   time.sleep(15)

        #    获取账户的总资金  #加入错误处理机制
        total_capital = exchange.fetch_balance()['total']['USDT']
        print('===程序循环开始===，可用资金', total_capital)
        # 相当于杠杆
        r_per = 0.1  # 设置为0.1，表示你愿意将总资金的10%用于单个交易
        #   币最新价
        #    仓位大小
        position_size = (total_capital * r_per) / latest_price
        min_position_size = 0.003  # ETH最小下单量

        #   查看仓位字典
        # print(positions_state)

        #   如果资金不够，只下单最小单，如果够了， 则（ ETH保留1个小数点）
        if position_size < min_position_size:
            position_size = min_position_size
        else:
            position_size = math.floor(position_size / 0.003) * 0.003
            position_size = round(position_size, 3)  # 保留小数点后3位
        # print('-------多单准备开仓仓位：',position_size,'-------')

        time.sleep(30)

        # 策略逻辑  交易区间设置
        if y * 0.98 <= latest_price <= x * 1.02:

            # 第一循环，在这Z个档位里=======================
            for position_index in range(z):
                print(positions_state[position_index])
                print(positions_state_buy[position_index])
                print(positions_state_sell[position_index])
                # 第一挂多：1-7的档位上，如果没有持仓，没有挂单的请看下：轮着挂买单；有时候，价格低，直接成交了，打印成功买入。
                if positions_state[position_index] == 0 and positions_state_buy[position_index] == 0:
                    buy_price = mid - position_index * price_interval_l  # 挂单买入的价格
                    # 买开仓
                    buy_order = exchange.create_limit_order(symbol='ETH/USDT:USDT',
                                                            amount=position_size,
                                                            price=buy_price, side='buy')
                    # 买挂单的字典加仓位
                    positions_state_buy[position_index] = position_size
                    print(f"-----挂单买入档位{position_index}:", position_size)

                    # 如果买直接成交，更新持仓字典
                    if buy_order['status'] == 'closed':
                        positions_state[position_index] = position_size  # 持仓加入字典
                        positions_state_buy[position_index] = 0  # 清除买挂单的仓位
                        print(f"-----直接买入档位{position_index}:", position_size)
                    else:
                        # 买单挂单未成交，将其添加到未成交订单列表
                        unfilled_orders.append({'order': buy_order, 'position_index': position_index})
                        print(f"-----挂单买入未成交，档位{position_index}:", position_size)

                # 第二挂空：如果有多单仓位了，挂对应的空单仓位
                if positions_state[position_index] > 0 and positions_state_sell[position_index] == 0:
                    # 卖出操作、卖出网格
                    sell_price = x - position_index * price_interval_h  # 挂单买入的价格
                    # 上接刚才的如果买单成交了，立刻挂卖单
                    sell_order = exchange.create_limit_order(symbol='ETH/USDT:USDT',
                                                             amount=position_size,
                                                             price=sell_price, side='sell')
                    # 平仓的挂单字典填入
                    positions_state_sell[position_index] = position_size
                    print(f"----挂单成功卖出档位{position_index}:", position_size)

                    # 把空单填入 列表
                    unfilled_orders.append({'order': sell_order, 'position_index': position_index})

            # 跳出那7个循环，查询挂单状态
            for order_info in unfilled_orders:
                order = order_info['order']
                position_index = order_info['position_index']
                order_id = order['id']
                order_status = exchange.fetch_order_status(order_id, symbol='ETH/USDT:USDT')

                # 检查订单状态 如果挂的买成交了，
                if order_status == 'closed' and order['side'] == 'buy':
                    # 买单挂单已成交
                    positions_state[position_index] = position_size
                    positions_state_buy[position_index] = 0
                    print(f"-----挂单买入已成交，档位{position_index}:", position_size)

                if order_status == 'closed' and order['side'] == 'sell':
                    # 卖单挂单已成交
                    positions_state[position_index] = 0
                    positions_state_sell[position_index] = 0
                    print(f"-----挂单卖出已成交，档位{position_index}:", position_size)

                # 清除已经成交的单子
                if order_status == 'closed':
                    unfilled_orders.remove(order_info)


run()
