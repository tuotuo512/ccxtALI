"""
MySQL数据库处理模块

负责将市场数据保存到MySQL数据库
"""

import logging

import pandas as pd
from data_layer.config import DATABASE_CONFIG
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 设置日志
logger = logging.getLogger(__name__)

# 创建Base类
Base = declarative_base()


class OHLCVData(Base):
    """
    定义OHLCV数据表模型
    """
    __tablename__ = 'ohlcv_data'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    def __repr__(self):
        return f"<OHLCVData(symbol='{self.symbol}', timeframe='{self.timeframe}', timestamp='{self.timestamp}')>"


class MySQLHandler:
    """
    MySQL数据库处理器

    负责将数据保存到MySQL数据库，并提供查询功能
    """

    def __init__(self, config=None):
        """
        初始化MySQL处理器

        Args:
            config: 数据库配置，如果为None则使用默认配置
        """
        self.config = config or DATABASE_CONFIG['mysql']
        self.engine = None
        self.session = None
        self._connect()

    def _connect(self):
        """
        连接到MySQL数据库
        """
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}@"
                f"{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )

            self.engine = create_engine(connection_string)

            # 创建表
            Base.metadata.create_all(self.engine)

            # 创建session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            logger.info("已连接到MySQL数据库")

        except Exception as e:
            logger.error(f"连接MySQL数据库失败: {str(e)}")
            self.engine = None
            self.session = None

    def save_ohlcv_data(self, df, symbol, timeframe):
        """
        保存OHLCV数据到数据库

        Args:
            df: 包含OHLCV数据的DataFrame
            symbol: 交易对符号
            timeframe: 时间周期

        Returns:
            bool: 是否保存成功
        """
        if self.engine is None:
            logger.error("未连接到数据库，无法保存数据")
            return False

        if df.empty:
            logger.warning("数据为空，无需保存")
            return True

        try:
            # 复制数据并重置索引，将时间戳作为列
            data_to_save = df.copy()
            data_to_save = data_to_save.reset_index()

            # 只保留OHLCV列
            data_to_save = data_to_save[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

            # 添加symbol和timeframe列
            data_to_save['symbol'] = symbol
            data_to_save['timeframe'] = timeframe

            # 将数据保存到数据库
            data_to_save.to_sql(
                'ohlcv_data',
                self.engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=500  # 分批写入
            )

            logger.info(f"已保存{len(data_to_save)}条{symbol} {timeframe}周期数据")
            return True

        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False

    def load_ohlcv_data(self, symbol, timeframe, start_time=None, end_time=None, limit=None):
        """
        从数据库加载OHLCV数据

        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            start_time: 开始时间，datetime对象
            end_time: 结束时间，datetime对象
            limit: 返回的最大记录数

        Returns:
            pd.DataFrame: 查询结果
        """
        if self.engine is None:
            logger.error("未连接到数据库，无法加载数据")
            return pd.DataFrame()

        try:
            # 构建查询条件
            query = f"""
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv_data 
                WHERE symbol = '{symbol}' AND timeframe = '{timeframe}'
            """

            if start_time:
                query += f" AND timestamp >= '{start_time}'"

            if end_time:
                query += f" AND timestamp <= '{end_time}'"

            query += " ORDER BY timestamp ASC"

            if limit:
                query += f" LIMIT {limit}"

            # 执行查询
            df = pd.read_sql(query, self.engine)

            # 设置timestamp为索引
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)

            logger.info(f"已加载{len(df)}条{symbol} {timeframe}周期数据")
            return df

        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return pd.DataFrame()

    def save_all_timeframes(self, data_dict, symbol):
        """
        保存所有时间周期的数据

        Args:
            data_dict: 包含多个时间周期数据的字典
            symbol: 交易对符号

        Returns:
            bool: 是否全部保存成功
        """
        all_success = True

        for timeframe, df in data_dict.items():
            success = self.save_ohlcv_data(df, symbol, timeframe)
            if not success:
                all_success = False

        return all_success

    def close(self):
        """
        关闭数据库连接
        """
        if self.session:
            self.session.close()

        if self.engine:
            self.engine.dispose()

        logger.info("已关闭MySQL数据库连接")


# 使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 导入历史数据
    from data_layer.collectors.historical import HistoricalDataCollector

    # 获取历史数据
    collector = HistoricalDataCollector(symbol='BTC/USDT:USDT')
    data = collector.fetch_ohlcv(timeframe='1h', limit=100)

    # 保存到MySQL
    handler = MySQLHandler()
    handler.save_ohlcv_data(data, 'BTC/USDT:USDT', '1h')

    # 查询数据
    loaded_data = handler.load_ohlcv_data('BTC/USDT:USDT', '1h', limit=10)
    print("查询的数据:")
    print(loaded_data)

    # 关闭连接
    handler.close()
