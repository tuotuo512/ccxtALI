"""
历史数据采集模块

负责从交易所获取历史K线数据
"""

import os
import pandas as pd
import time
import ccxt
from datetime import datetime, timedelta
import pytz
import logging

# 导入配置
from DT.data_layer.config import EXCHANGE_CONFIG, DATA_CONFIG

# 设置日志
logger = logging.getLogger(__name__)


class HistoricalDataCollector:
    """
    历史数据采集器

    用于从交易所获取历史K线数据，支持多种时间周期
    """

    def __init__(self, exchange_name='binance', symbol=None):
        """
        初始化历史数据采集器

        Args:
            exchange_name: 交易所名称，默认为'binance'
            symbol: 交易对，如果为None则使用配置中的默认值
        """
        self.exchange_name = exchange_name
        self.symbol = symbol or DATA_CONFIG['default_symbol']
        self.exchange = self._initialize_exchange()

    def _initialize_exchange(self):
        """
        初始化交易所连接

        Returns:
            ccxt交易所实例
        """
        # 创建并配置交易所实例
        if self.exchange_name not in EXCHANGE_CONFIG:
            raise ValueError(f"不支持的交易所: {self.exchange_name}")

        # 复制配置以避免修改原始配置
        config = EXCHANGE_CONFIG[self.exchange_name].copy()

        # 如果配置中包含代理设置相关的选项
        if 'use_proxy' in EXCHANGE_CONFIG and EXCHANGE_CONFIG['use_proxy']:
            config['proxies'] = EXCHANGE_CONFIG['proxy_settings']

        exchange_class = getattr(ccxt, self.exchange_name)
        exchange = exchange_class(config)

        # 尝试连接交易所
        self._reconnect_exchange(exchange)
        return exchange

    def _reconnect_exchange(self, exchange):
        """
        尝试重新连接交易所

        Args:
            exchange: 交易所实例

        Returns:
            bool: 连接是否成功
        """
        max_retries = DATA_CONFIG['max_retries']
        retry_delay = DATA_CONFIG['retry_delay']

        retry_count = 0
        while retry_count < max_retries:
            try:
                exchange.load_markets()
                logger.info("连接交易所成功")
                return True
            except ccxt.RequestTimeout:
                logger.warning(f"请求超时，正在重试... ({retry_count + 1}/{max_retries})")
                retry_count += 1
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"重新连接交易所失败: {str(e)}")
                retry_count += 1
                time.sleep(retry_delay * 2)  # 对于非超时错误，等待时间延长

        logger.error("无法重新连接交易所，达到最大重试次数")
        return False

    def fetch_ohlcv(self, timeframe='1m', limit=None):
        """
        获取K线数据

        Args:
            timeframe: 时间周期，如'1m', '5m', '1h'等
            limit: 获取的K线数量，默认使用配置中的值

        Returns:
            pd.DataFrame: K线数据DataFrame
        """
        limit = limit or DATA_CONFIG['default_limit']

        try:
            # 获取K线数据
            data = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=limit)

            # 转换为DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # 转换时间戳为日期时间格式
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            # 尝试重新连接
            if self._reconnect_exchange(self.exchange):
                # 重试一次
                data = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=limit)
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            return pd.DataFrame()  # 返回空DataFrame

    def fetch_multi_timeframe_data(self, timeframes=None):
        """
        获取多个时间周期的数据

        Args:
            timeframes: 时间周期列表，如果为None则使用配置中的默认值

        Returns:
            dict: 包含不同时间周期数据的字典
        """
        timeframes = timeframes or DATA_CONFIG['timeframes']
        results = {}

        for tf in timeframes:
            logger.info(f"获取{tf}周期数据...")
            df = self.fetch_ohlcv(timeframe=tf)
            if not df.empty:
                results[tf] = df

        return results


# 简单使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    collector = HistoricalDataCollector()
    data = collector.fetch_multi_timeframe_data()
    for tf, df in data.items():
        print(f"{tf}周期数据行数: {len(df)}")
        print(df.head())