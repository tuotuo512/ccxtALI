##链接交易所
from ccxtbt import CCXTStore
#引入backtrader
import backtrader as bt
#时间处理
from datetime import datetime, timedelta
import json
from binance.cm_futures import CMFutures

class TestStrategy(bt.Strategy):

    def __init__(self):

        self.sma = bt.indicators.SMA(self.data,period=21)

        #self.live_data = False  # 或者其它你想要的初始值
    def next(self):

        if self.live_data:
            cash, value = self.broker.get_wallet_balance('USDT')
        else:
            return # 仍然处于历史数据回填阶段，不执行逻辑，返回

        for data in self.datas:

            print('{} - {} | Cash {} | O: {} H: {} L: {} C: {} V:{}'.format(data.datetime.datetime(),
                                                                                   data._name, cash, data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0]))
    # 处理数据状态的变化通知
    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()  # 获取了当前的日期和时间，存储在变量 dt 中。
        msg = 'Data Status: {}'.format(data._getstatusname(status))
        print(dt, dn, msg)  # 将日期、数据名和消息打印出来
        # 检查了数据的状态是否为 'LIVE'。
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False


# 创建一个 backtrader的交易大脑 Cerebro ，用于协调各个部分的工作。
# quicknotify=True 这个参数表示是否快速通知。
# 默认情况下，Cerebro 在处理数据（如价格信息，交易信号等）时，会按照固定的顺序通知各个元素（如数据源，策略，交易代理等）。
# 当 quicknotify 为 True 时，Cerebro 会尽可能快的通知各个元素，这在处理实时数据（如实盘交易）时可以提高响应速度。
# 然而，这也可能使得数据处理的顺序变得不可预测，因此在使用 quicknotify=True 时需要格外小心。
cerebro = bt.Cerebro(quicknotify=True)

# 添加策略到Cerebro
cerebro.addstrategy(TestStrategy)



# 创建了一个名为config的字典，它包含了你用来连接交易所的配置信息
config = {'apiKey': 'da8ySe13WWUUQ1Mo2uArvD7SomJnbwLHcqbSvkLrvJubNTIbwa3FjSyCE3Nk24Y1',
          'secret': 'WSsSf12OdoConSod3tnRQYL3FQMyKl8szdLQXnTHhjDfCvO6fojM86g0iZdQp2rw',
          'enableRateLimit': True,  # 遵守交易所的API请求速率限制
          'options': {
              'defaultType': 'swap',  ##swap=永续
          },
          'proxies': {
              'http': 'http://127.0.0.1:10809',
              'https': 'http://127.0.0.1:10809',
          }
          }
# 生成数据
store = CCXTStore(exchange='binance', currency='BTC/USDT:USDT', config=config, retries=5, debug=False)


# Get the broker and pass any kwargs if needed.
# ----------------------------------------------

# 这段代码是用来设置交易所的订单类型和订单状态映射
broker_mapping = {
    'order_types': {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop-loss',
        bt.Order.StopLimit: 'stop limit'
    },
    'mappings':{
        'closed_order':{
            'key': 'status',
            'value':'closed'
        },
        'canceled_order':{
            'key': 'result',
            'value':1}
    }
}
#使用定义的映射关系从交易所获取一个broker
broker = store.getbroker(broker_mapping=broker_mapping)
cerebro.setbroker(broker)

# 从交易所获取历史数据。
# hist_start_date开始时间 = 当前时间（UTC）减去50分钟;
# compression数据的压缩因子，这里为1表示不进行压缩，获取的是原始数据
# drop_newest=True 这个参数决定是否丢弃最新的未完成的蜡烛图数据，设置为True可以避免使用未完成的蜡烛图数据进行分析。
hist_start_date = datetime.utcnow() - timedelta(minutes=50)
data = store.getdata(dataname='BTC/USDT:USDT', name="BTC/USDT:USDT",
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True)#, historical=True)

# Add the feed
cerebro.adddata(data)

# Run the strategy
cerebro.run()