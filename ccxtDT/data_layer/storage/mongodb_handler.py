"""
MongoDB数据库处理模块

负责将市场数据和计算结果保存到MongoDB数据库
"""

import logging
from datetime import datetime

import pandas as pd
from ..config import DATABASE_CONFIG
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

# 设置日志
logger = logging.getLogger(__name__)


class MongoDBHandler:
    """
    MongoDB数据库处理器

    负责将数据保存到MongoDB数据库，并提供查询功能
    """

    def __init__(self, config=None):
        """
        初始化MongoDB处理器

        Args:
            config: 数据库配置，如果为None则使用默认配置
        """
        self.config = config or DATABASE_CONFIG['mongodb']
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        """
        连接到MongoDB数据库
        """
        try:
            # 创建客户端连接
            self.client = MongoClient(
                host=self.config['host'],
                port=self.config['port'],
                serverSelectionTimeoutMS=5000  # 5秒超时
            )

            # 测试连接
            self.client.admin.command('ping')

            # 获取数据库
            self.db = self.client[self.config['database']]

            # 确保创建索引
            self._ensure_indexes()

            logger.info("已连接到MongoDB数据库")

        except ConnectionFailure as e:
            logger.error(f"连接MongoDB数据库失败: {str(e)}")
            self.client = None
            self.db = None
        except Exception as e:
            logger.error(f"初始化MongoDB处理器失败: {str(e)}")
            self.client = None
            self.db = None

    def _ensure_indexes(self):
        """
        确保必要的索引存在
        """
        if not self.db:
            return

        try:
            # 为市场数据集合创建索引
            self.db['market_data'].create_index(
                [('symbol', ASCENDING), ('timeframe', ASCENDING), ('timestamp', ASCENDING)],
                unique=True
            )

            # 为技术指标集合创建索引
            self.db['technical_indicators'].create_index(
                [('symbol', ASCENDING), ('timeframe', ASCENDING), ('timestamp', ASCENDING)],
                unique=True
            )

            # 为交易信号集合创建索引
            self.db['trading_signals'].create_index(
                [('symbol', ASCENDING), ('timeframe', ASCENDING), ('timestamp', ASCENDING)]
            )

            logger.info("已创建MongoDB索引")

        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")

    def save_market_data(self, df, symbol, timeframe):
        """
        保存市场数据到MongoDB

        Args:
            df: 包含市场数据的DataFrame
            symbol: 交易对符号
            timeframe: 时间周期

        Returns:
            bool: 是否保存成功
        """
        if not self.db:
            logger.error("未连接到数据库，无法保存数据")
            return False

        if df.empty:
            logger.warning("数据为空，无需保存")
            return True

        try:
            # 准备要插入的数据
            records = []

            # 复制并重置索引，将时间作为普通列
            data_to_save = df.copy()
            data_to_save = data_to_save.reset_index()

            # 只保留基本的OHLCV列
            if 'timestamp' in data_to_save.columns:
                ohlcv_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                data_to_save = data_to_save[ohlcv_columns]

            # 将DataFrame转换为字典列表
            for _, row in data_to_save.iterrows():
                # 确保timestamp是datetime类型
                if isinstance(row['timestamp'], pd.Timestamp):
                    timestamp = row['timestamp'].to_pydatetime()
                else:
                    timestamp = row['timestamp']

                record = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': timestamp,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                }
                records.append(record)

            # 批量插入数据
            if records:
                # 使用upsert模式，避免重复插入
                for record in records:
                    self.db['market_data'].update_one(
                        {
                            'symbol': record['symbol'],
                            'timeframe': record['timeframe'],
                            'timestamp': record['timestamp']
                        },
                        {'$set': record},
                        upsert=True
                    )

                logger.info(f"已保存{len(records)}条{symbol} {timeframe}周期市场数据")
                return True
            else:
                logger.warning("没有数据需要保存")
                return False

        except Exception as e:
            logger.error(f"保存市场数据失败: {str(e)}")
            return False

    def save_technical_indicators(self, df, symbol, timeframe):
        """
        保存技术指标数据到MongoDB

        Args:
            df: 包含技术指标的DataFrame
            symbol: 交易对符号
            timeframe: 时间周期

        Returns:
            bool: 是否保存成功
        """
        if not self.db:
            logger.error("未连接到数据库，无法保存技术指标")
            return False

        if df.empty:
            logger.warning("数据为空，无需保存技术指标")
            return True

        try:
            # 准备要插入的数据
            records = []

            # 复制并重置索引
            data_to_save = df.copy()
            data_to_save = data_to_save.reset_index()

            # 将DataFrame转换为字典列表
            for _, row in data_to_save.iterrows():
                # 确保timestamp是datetime类型
                if isinstance(row['timestamp'], pd.Timestamp):
                    timestamp = row['timestamp'].to_pydatetime()
                else:
                    timestamp = row['timestamp']

                # 创建基本记录
                record = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': timestamp,
                    'indicators': {}
                }

                # 添加所有列作为指标，排除基本的OHLCV和timestamp
                exclude_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                for col in data_to_save.columns:
                    if col not in exclude_cols:
                        record['indicators'][col] = float(row[col]) if not pd.isna(row[col]) else None

                records.append(record)

            # 批量插入数据
            if records:
                for record in records:
                    self.db['technical_indicators'].update_one(
                        {
                            'symbol': record['symbol'],
                            'timeframe': record['timeframe'],
                            'timestamp': record['timestamp']
                        },
                        {'$set': record},
                        upsert=True
                    )

                logger.info(f"已保存{len(records)}条{symbol} {timeframe}周期技术指标")
                return True
            else:
                logger.warning("没有技术指标需要保存")
                return False

        except Exception as e:
            logger.error(f"保存技术指标失败: {str(e)}")
            return False

    def save_trading_signal(self, signal_data):
        """
        保存交易信号到MongoDB

        Args:
            signal_data: 包含交易信号的字典

        Returns:
            bool: 是否保存成功
        """
        if not self.db:
            logger.error("未连接到数据库，无法保存交易信号")
            return False

        try:
            # 确保timestamp是datetime类型
            if 'timestamp' in signal_data:
                if isinstance(signal_data['timestamp'], pd.Timestamp):
                    signal_data['timestamp'] = signal_data['timestamp'].to_pydatetime()
            else:
                signal_data['timestamp'] = datetime.now()

            # 添加创建时间
            signal_data['created_at'] = datetime.now()

            # 插入数据
            self.db['trading_signals'].insert_one(signal_data)

            logger.info(f"已保存交易信号: {signal_data['symbol']} {signal_data.get('signal_type', '')}")
            return True

        except Exception as e:
            logger.error(f"保存交易信号失败: {str(e)}")
            return False

    def load_market_data(self, symbol, timeframe, start_time=None, end_time=None, limit=None):
        """
        从MongoDB加载市场数据

        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            start_time: 开始时间，datetime对象
            end_time: 结束时间，datetime对象
            limit: 返回的最大记录数

        Returns:
            pd.DataFrame: 查询结果
        """
        if not self.db:
            logger.error("未连接到数据库，无法加载数据")
            return pd.DataFrame()

        try:
            # 构建查询条件
            query = {
                'symbol': symbol,
                'timeframe': timeframe
            }

            if start_time:
                query['timestamp'] = {'$gte': start_time}

            if end_time:
                if 'timestamp' in query:
                    query['timestamp']['$lte'] = end_time
                else:
                    query['timestamp'] = {'$lte': end_time}

            # 执行查询
            cursor = self.db['market_data'].find(
                query,
                {'_id': 0}  # 排除_id字段
            ).sort('timestamp', ASCENDING)

            if limit:
                cursor = cursor.limit(limit)

            # 转换为DataFrame
            data = list(cursor)
            if not data:
                logger.warning(f"未找到{symbol} {timeframe}周期的市场数据")
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # 设置timestamp为索引
            df.set_index('timestamp', inplace=True)

            logger.info(f"已加载{len(df)}条{symbol} {timeframe}周期市场数据")
            return df

        except Exception as e:
            logger.error(f"加载市场数据失败: {str(e)}")
            return pd.DataFrame()

    def load_technical_indicators(self, symbol, timeframe, start_time=None, end_time=None, limit=None):
        """
        从MongoDB加载技术指标

        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            start_time: 开始时间，datetime对象
            end_time: 结束时间，datetime对象
            limit: 返回的最大记录数

        Returns:
            pd.DataFrame: 查询结果
        """
        if not self.db:
            logger.error("未连接到数据库，无法加载技术指标")
            return pd.DataFrame()

        try:
            # 构建查询条件
            query = {
                'symbol': symbol,
                'timeframe': timeframe
            }

            if start_time:
                query['timestamp'] = {'$gte': start_time}

            if end_time:
                if 'timestamp' in query:
                    query['timestamp']['$lte'] = end_time
                else:
                    query['timestamp'] = {'$lte': end_time}

            # 执行查询
            cursor = self.db['technical_indicators'].find(
                query,
                {'_id': 0}  # 排除_id字段
            ).sort('timestamp', ASCENDING)

            if limit:
                cursor = cursor.limit(limit)

            # 转换为DataFrame
            data = list(cursor)
            if not data:
                logger.warning(f"未找到{symbol} {timeframe}周期的技术指标")
                return pd.DataFrame()

            # 转换嵌套的indicators为一级列
            flat_data = []
            for record in data:
                flat_record = {
                    'timestamp': record['timestamp'],
                    'symbol': record['symbol'],
                    'timeframe': record['timeframe']
                }

                if 'indicators' in record and isinstance(record['indicators'], dict):
                    flat_record.update(record['indicators'])

                flat_data.append(flat_record)

            df = pd.DataFrame(flat_data)

            # 设置timestamp为索引
            df.set_index('timestamp', inplace=True)

            logger.info(f"已加载{len(df)}条{symbol} {timeframe}周期技术指标")
            return df

        except Exception as e:
            logger.error(f"加载技术指标失败: {str(e)}")
            return pd.DataFrame()

    def save_all_timeframes(self, data_dict, symbol, include_indicators=False):
        """
        保存所有时间周期的数据和指标

        Args:
            data_dict: 包含多个时间周期数据的字典
            symbol: 交易对符号
            include_indicators: 是否包含技术指标

        Returns:
            bool: 是否全部保存成功
        """
        all_success = True

        for timeframe, df in data_dict.items():
            # 保存市场数据
            market_success = self.save_market_data(df, symbol, timeframe)
            if not market_success:
                all_success = False

            # 如果需要保存指标
            if include_indicators:
                # 获取除了OHLCV之外的所有列
                ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in ohlcv_cols):
                    logger.warning(f"{timeframe}周期数据缺少OHLCV列，跳过保存指标")
                    continue

                if len(df.columns) > len(ohlcv_cols):  # 有额外的列，视为指标
                    indicator_success = self.save_technical_indicators(df, symbol, timeframe)
                    if not indicator_success:
                        all_success = False

        return all_success

    def close(self):
        """
        关闭数据库连接
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("已关闭MongoDB数据库连接")


# 使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 导入历史数据和转换器
    from DT.data_layer.collectors.historical import HistoricalDataCollector
    from DT.data_layer.processors.transformer import DataTransformer

    # 获取历史数据
    collector = HistoricalDataCollector(symbol='BTC/USDT:USDT')
    data = collector.fetch_ohlcv(timeframe='1h', limit=100)

    # 计算技术指标
    transformer = DataTransformer()
    transformed_data = transformer.transform_data(data)

    # 保存到MongoDB
    handler = MongoDBHandler()

    # 保存市场数据
    handler.save_market_data(data, 'BTC/USDT:USDT', '1h')

    # 保存技术指标
    handler.save_technical_indicators(transformed_data, 'BTC/USDT:USDT', '1h')

    # 保存交易信号示例
    signal = {
        'symbol': 'BTC/USDT:USDT',
        'timeframe': '1h',
        'timestamp': datetime.now(),
        'signal_type': 'BUY',
        'price': 50000.0,
        'confidence': 0.85,
        'factors': {
            'trend': 'BULLISH',
            'momentum': 'POSITIVE',
            'volatility': 'MEDIUM'
        }
    }
    handler.save_trading_signal(signal)

    # 查询数据
    market_data = handler.load_market_data('BTC/USDT:USDT', '1h', limit=5)
    print("查询的市场数据:")
    print(market_data)

    # 查询技术指标
    indicators = handler.load_technical_indicators('BTC/USDT:USDT', '1h', limit=5)
    print("\n查询的技术指标:")
    print(indicators)

    # 关闭连接
    handler.close()
