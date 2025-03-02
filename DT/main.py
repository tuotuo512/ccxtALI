"""
数字货币交易系统 - 主入口文件

整合数据层的各个组件，实现数据采集、处理和存储流程
"""

import logging
import time
from datetime import datetime

# 导入数据层组件
from data_layer.collectors.historical import HistoricalDataCollector
from data_layer.collectors.realtime import RealtimeDataCollector
from data_layer.processors.cleaner import DataCleaner
from data_layer.processors.transformer import DataTransformer
from data_layer.storage.mongodb_handler import MongoDBHandler

# 导入配置
from data_layer.config import DATA_CONFIG

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_data_layer(symbol=None):
    """
    初始化数据层

    Args:
        symbol: 交易对，如果为None则使用配置中的默认值

    Returns:
        dict: 包含各个组件的字典
    """
    symbol = symbol or DATA_CONFIG['default_symbol']
    logger.info(f"初始化数据层，交易对: {symbol}")

    # 初始化各个组件
    historical_collector = HistoricalDataCollector(symbol=symbol)
    realtime_collector = RealtimeDataCollector(symbol=symbol, update_interval=60)
    data_cleaner = DataCleaner()
    data_transformer = DataTransformer()
    db_handler = MongoDBHandler()

    components = {
        'historical_collector': historical_collector,
        'realtime_collector': realtime_collector,
        'data_cleaner': data_cleaner,
        'data_transformer': data_transformer,
        'db_handler': db_handler
    }

    return components


def process_historical_data(components, symbol, timeframes=None):
    """
    处理历史数据

    Args:
        components: 数据层组件字典
        symbol: 交易对
        timeframes: 时间周期列表

    Returns:
        dict: 处理后的历史数据
    """
    timeframes = timeframes or DATA_CONFIG['timeframes']
    logger.info(f"处理{symbol}的历史数据，时间周期: {timeframes}")

    # 获取历史数据
    data_dict = components['historical_collector'].fetch_multi_timeframe_data(timeframes)

    # 清理数据
    cleaned_data = components['data_cleaner'].clean_all_timeframes(data_dict)

    # 转换数据，添加技术指标
    transformed_data = components['data_transformer'].transform_all_timeframes(cleaned_data)

    # 保存数据到数据库
    components['db_handler'].save_all_timeframes(transformed_data, symbol, include_indicators=True)

    return transformed_data


def setup_realtime_data_processing(components, symbol):
    """
    设置实时数据处理

    Args:
        components: 数据层组件字典
        symbol: 交易对

    Returns:
        RealtimeDataCollector: 实时数据采集器
    """
    logger.info(f"设置{symbol}的实时数据处理")

    # 定义数据更新回调函数
    def on_data_update(data_dict):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"收到数据更新: {current_time}")

        # 清洗数据
        cleaned_data = components['data_cleaner'].clean_all_timeframes(data_dict)

        # 转换数据，添加技术指标
        transformed_data = components['data_transformer'].transform_all_timeframes(cleaned_data)

        # 保存到数据库
        components['db_handler'].save_all_timeframes(transformed_data, symbol, include_indicators=True)

        # 打印最新价格信息
        for tf, df in transformed_data.items():
            if not df.empty:
                latest_close = df['close'].iloc[-1]
                latest_time = df.index[-1]
                logger.info(f"{tf}周期最新价格: {latest_close:.2f} @ {latest_time}")

    # 注册回调函数
    components['realtime_collector'].register_callback(on_data_update)

    # 启动实时数据采集
    components['realtime_collector'].start()

    return components['realtime_collector']


def main():
    """
    主函数
    """
    logger.info("启动数字货币交易系统 - 数据层")

    # 选择交易对
    symbol = DATA_CONFIG['default_symbol']

    # 初始化数据层组件
    components = initialize_data_layer(symbol)

    # 处理历史数据
    historical_data = process_historical_data(components, symbol)

    # 设置实时数据处理
    realtime_collector = setup_realtime_data_processing(components, symbol)

    logger.info("系统已启动，按Ctrl+C停止")

    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("接收到停止信号")
    finally:
        # 清理资源
        realtime_collector.stop()
        components['db_handler'].close()
        logger.info("系统已停止")


if __name__ == "__main__":
    main()