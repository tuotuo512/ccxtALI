"""
实时数据采集模块

负责实时获取最新的市场数据，支持定时更新和数据处理
"""

import logging
import threading
import time
from datetime import datetime

import pandas as pd
from ..collectors.historical import HistoricalDataCollector
from ..config import DATA_CONFIG

# 设置日志
logger = logging.getLogger(__name__)


class RealtimeDataCollector:
    """
    实时数据采集器

    持续获取最新的市场数据，支持定时更新和数据处理回调
    """

    def __init__(self, symbol=None, timeframes=None, update_interval=60):
        """
        初始化实时数据采集器

        Args:
            symbol: 交易对，如果为None则使用配置中的默认值
            timeframes: 时间周期列表，如果为None则使用配置中的默认值
            update_interval: 更新间隔(秒)，默认60秒
        """
        self.symbol = symbol or DATA_CONFIG['default_symbol']
        self.timeframes = timeframes or DATA_CONFIG['timeframes']
        self.update_interval = update_interval

        # 用于存储历史数据的字典
        self.historical_data = {tf: pd.DataFrame() for tf in self.timeframes}

        # 创建历史数据采集器
        self.collector = HistoricalDataCollector(symbol=self.symbol)

        # 线程控制
        self.is_running = False
        self.thread = None
        self.callbacks = []  # 存储数据更新后的回调函数

    def start(self):
        """
        启动实时数据采集
        """
        if self.is_running:
            logger.warning("实时数据采集已在运行中")
            return

        # 先获取初始数据
        self._init_historical_data()

        # 启动采集线程
        self.is_running = True
        self.thread = threading.Thread(target=self._collection_loop)
        self.thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        self.thread.start()

        logger.info(f"实时数据采集已启动，更新间隔: {self.update_interval}秒")

    def stop(self):
        """
        停止实时数据采集
        """
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("实时数据采集已停止")

    def register_callback(self, callback):
        """
        注册数据更新回调函数

        Args:
            callback: 回调函数，接收更新后的数据字典作为参数
        """
        self.callbacks.append(callback)

    def _init_historical_data(self):
        """
        初始化历史数据
        """
        logger.info("初始化历史数据...")
        data_dict = self.collector.fetch_multi_timeframe_data(self.timeframes)
        for tf, data in data_dict.items():
            if not data.empty:
                self.historical_data[tf] = data
                logger.info(f"已获取{tf}周期历史数据，{len(data)}条记录")

    def _collection_loop(self):
        """
        数据采集循环
        """
        while self.is_running:
            try:
                self._update_data()

                # 调用所有注册的回调函数
                for callback in self.callbacks:
                    callback(self.historical_data)

            except Exception as e:
                logger.error(f"数据采集异常: {str(e)}")

            # 等待下次更新
            time.sleep(self.update_interval)

    def _update_data(self):
        """
        更新最新数据
        """
        logger.debug("更新最新数据...")
        for tf in self.timeframes:
            try:
                # 获取最新的一条K线数据
                latest_data = self.collector.exchange.fetch_ohlcv(self.symbol, tf, limit=1)

                if not latest_data:
                    logger.warning(f"未能获取{tf}周期的最新数据")
                    continue

                latest_df = pd.DataFrame(latest_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'], unit='ms')
                latest_df.set_index('timestamp', inplace=True)

                # 检查是否有数据重复
                if not self.historical_data[tf].empty:
                    latest_time = latest_df.index[0]

                    # 如果最新数据时间已存在，更新该条记录
                    self.historical_data[tf] = self.historical_data[tf][
                        ~self.historical_data[tf].index.isin([latest_time])]

                # 将最新数据添加到历史数据
                self.historical_data[tf] = pd.concat([self.historical_data[tf], latest_df])

                # 限制数据长度，防止内存占用过大
                if len(self.historical_data[tf]) > DATA_CONFIG['default_limit']:
                    self.historical_data[tf] = self.historical_data[tf].iloc[-DATA_CONFIG['default_limit']:]

                logger.debug(f"已更新{tf}周期数据，最新时间: {latest_df.index[0]}")

            except Exception as e:
                logger.error(f"更新{tf}周期数据失败: {str(e)}")

    def get_latest_data(self, timeframe):
        """
        获取指定时间周期的最新数据

        Args:
            timeframe: 时间周期，如'1m', '5m'等

        Returns:
            pd.DataFrame: 该时间周期的历史数据
        """
        if timeframe not in self.historical_data:
            logger.warning(f"未找到{timeframe}周期的数据")
            return pd.DataFrame()

        return self.historical_data[timeframe]

    def resample_data(self):
        """
        对1分钟数据进行重采样，生成多时间周期数据

        Returns:
            dict: 包含多个时间周期数据的字典
        """
        # 确保有1分钟数据
        if '1m' not in self.historical_data or self.historical_data['1m'].empty:
            logger.warning("没有1分钟数据，无法进行重采样")
            return {}

        df_1m = self.historical_data['1m']
        result = {'1m': df_1m}

        # 将索引设置为时间戳的分钟级别
        df_1m.index = df_1m.index.floor('1Min')

        # 重采样为不同周期
        timeframe_minutes = {
            '3m': 3,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }

        for tf, minutes in timeframe_minutes.items():
            if tf in self.timeframes:
                result[tf] = df_1m.resample(f'{minutes}Min').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()

        return result


# 使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)


    # 定义数据更新回调函数
    def on_data_update(data_dict):
        print(f"数据更新时间: {datetime.now()}")
        for tf, df in data_dict.items():
            if not df.empty:
                print(f"{tf}周期最新价格: {df['close'].iloc[-1]}")


    # 创建并启动实时数据采集器
    collector = RealtimeDataCollector(update_interval=10)  # 10秒更新一次
    collector.register_callback(on_data_update)
    collector.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        collector.stop()
        print("程序已退出")
