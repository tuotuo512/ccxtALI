from datetime import datetime
import os
import pandas as pd
import backtrader as bt
from superStt15min import CustomStrategy15
from superStt15min_1h import CustomStrategy15_60

class MainStrategy(bt.Strategy):
    params = (
        ('strategy1', CustomStrategy15),
        ('strategy2', CustomStrategy15_60),
    )

    def __init__(self):
        self.strat1 = self.p.strategy1(self.data)
        self.strat2 = self.p.strategy2(self.data)

    def next(self):
        self.strat1.next()
        self.strat2.next()

    def notify_order(self, order):
        self.strat1.notify_order(order)
        self.strat2.notify_order(order)

cerebro = bt.Cerebro()

cerebro.addstrategy(MainStrategy)

cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.001)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot(style='candlestick')
