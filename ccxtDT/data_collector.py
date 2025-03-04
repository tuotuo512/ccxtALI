import logging
from time import sleep

import ccxt
import pandas as pd


class DataCollector:
    def __init__(self, config):
        self.exchange = self._init_exchange(config)
        self.symbols = config.SYMBOLS
        self.timeframes = config.TIMEFRAMES
        self.logger = logging.getLogger('data_collector')

    def _init_exchange(self, config):
        """初始化交易所连接"""
        exchange_class = config.EXCHANGE['class']
        return exchange_class(config.EXCHANGE['config'])

    def _handle_rate_limit(self):
        """处理交易所API限速"""
        sleep(self.exchange.rateLimit / 1000)

    def fetch_historical_data(self, symbol, timeframe, limit=1000):
        """获取历史K线数据"""
        try:
            data = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                params={'price': 'mark'}  # 获取标记价格
            )
            self._handle_rate_limit()
            return self._convert_to_dataframe(data, symbol, timeframe)
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error: {str(e)}")
            return None
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error: {str(e)}")
            return None

    def _convert_to_dataframe(self, data, symbol, timeframe):
        """转换原始数据为DataFrame"""
        df = pd.DataFrame(
            data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def realtime_stream(self, callback):
        """WebSocket实时数据流"""
        # 建议使用ccxt.pro或独立的WebSocket实现
        # 此处为示例伪代码
        self.exchange.websocket_subscribe(...)
        while True:
            data = self.exchange.websocket_recv()
            callback(data)
