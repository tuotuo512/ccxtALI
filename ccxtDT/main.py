"""
数字货币交易系统 - 主入口文件

整合数据层和策略层的各个组件，实现一个完整的数据分析和交易信号生成流程
"""

import logging
import time
from datetime import datetime

# 导入数据层组件
from data_layer.collectors.historical import HistoricalDataCollector
from data_layer.collectors.realtime import RealtimeDataCollector
# 导入配置
from data_layer.config import DATA_CONFIG
from data_layer.processors.cleaner import DataCleaner
from data_layer.processors.transformer import DataTransformer
from data_layer.storage.mongodb_handler import MongoDBHandler
from strategy_layer.backtest.evaluator import StrategyEvaluator
from strategy_layer.backtest.visualizer import StrategyVisualizer
# 导入策略层组件
from strategy_layer.factors.technical_factors import TechnicalFactors
from strategy_layer.signals.reversal_signals import ReversalSignalGenerator
from strategy_layer.signals.trend_signals import TrendSignalGenerator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_system(symbol=None):
    """
    初始化交易系统的数据层和策略层

    Args:
        symbol: 交易对，如果为None则使用配置中的默认值

    Returns:
        dict: 包含各个组件的字典
    """
    symbol = symbol or DATA_CONFIG['default_symbol']
    logger.info(f"初始化交易系统，交易对: {symbol}")

    # 初始化数据层组件
    historical_collector = HistoricalDataCollector(symbol=symbol)
    realtime_collector = RealtimeDataCollector(symbol=symbol, update_interval=60)
    data_cleaner = DataCleaner()
    data_transformer = DataTransformer()
    db_handler = MongoDBHandler()

    # 初始化策略层组件
    tech_factors = TechnicalFactors()
    trend_signal_generator = TrendSignalGenerator(lookback_period=20)
    reversal_signal_generator = ReversalSignalGenerator(rsi_overbought=70, rsi_oversold=30)
    strategy_evaluator = StrategyEvaluator(initial_capital=10000, position_size=0.1)
    strategy_visualizer = StrategyVisualizer()

    components = {
        # 数据层组件
        'historical_collector': historical_collector,
        'realtime_collector': realtime_collector,
        'data_cleaner': data_cleaner,
        'data_transformer': data_transformer,
        'db_handler': db_handler,

        # 策略层组件
        'tech_factors': tech_factors,
        'trend_signal_generator': trend_signal_generator,
        'reversal_signal_generator': reversal_signal_generator,
        'strategy_evaluator': strategy_evaluator,
        'strategy_visualizer': strategy_visualizer
    }

    return components


def process_historical_data(components, symbol, timeframes=None):
    """
    处理历史数据并生成交易信号

    Args:
        components: 系统组件字典
        symbol: 交易对
        timeframes: 时间周期列表

    Returns:
        dict: 包含处理后的历史数据和交易信号的字典
    """
    timeframes = timeframes or DATA_CONFIG['timeframes']
    logger.info(f"处理{symbol}的历史数据，时间周期: {timeframes}")

    # 获取历史数据
    data_dict = components['historical_collector'].fetch_multi_timeframe_data(timeframes)

    # 清理数据
    cleaned_data = components['data_cleaner'].clean_all_timeframes(data_dict)

    # 转换数据，添加基础技术指标
    transformed_data = components['data_transformer'].transform_all_timeframes(cleaned_data)

    # 保存基本处理后的数据到数据库
    components['db_handler'].save_all_timeframes(transformed_data, symbol, include_indicators=True)

    # 为每个时间周期添加策略层的技术因子和交易信号
    result_dict = {}
    for tf, df in transformed_data.items():
        if df.empty:
            logger.warning(f"{tf}周期数据为空，跳过")
            continue

        # 添加高级技术因子
        df_with_factors = components['tech_factors'].add_basic_factors(df)
        df_with_custom = components['tech_factors'].add_custom_factors(df_with_factors)

        # 生成趋势信号
        df_with_trend = components['trend_signal_generator'].generate_signals(df_with_custom)

        # 生成反转信号
        df_with_signals = components['reversal_signal_generator'].generate_signals(df_with_trend)

        # 生成组合信号 (趋势和反转结合)
        df_with_signals['combined_signal'] = 0
        # 当趋势与反转信号一致时，采用该信号
        df_with_signals.loc[(df_with_signals['trend_signal'] == 1) &
                            (df_with_signals['reversal_signal'] == 1), 'combined_signal'] = 1
        df_with_signals.loc[(df_with_signals['trend_signal'] == -1) &
                            (df_with_signals['reversal_signal'] == -1), 'combined_signal'] = -1

        # 保存到结果字典
        result_dict[tf] = df_with_signals

        # 记录最新信号
        latest_row = df_with_signals.iloc[-1]
        logger.info(f"{tf}周期最新信号 - 趋势: {latest_row['trend_signal']}, "
                    f"反转: {latest_row['reversal_signal']}, "
                    f"组合: {latest_row['combined_signal']}")

    # 将带有信号的数据保存到数据库的单独集合中
    for tf, df in result_dict.items():
        collection_name = f"{symbol.replace('/', '_')}_{tf}_signals"
        components['db_handler'].save_dataframe(df, collection_name)

    logger.info("历史数据处理和信号生成完成")
    return result_dict


def backtest_strategy(components, signal_data, timeframe='1h', signal_column='trend_signal'):
    """
    回测特定时间周期和信号类型的策略

    Args:
        components: 系统组件字典
        signal_data: 包含信号的数据字典
        timeframe: 要回测的时间周期
        signal_column: 使用的信号列名

    Returns:
        tuple: (回测结果DataFrame, 指标字典)
    """
    logger.info(f"回测{timeframe}周期的{signal_column}策略")

    if timeframe not in signal_data:
        logger.error(f"找不到{timeframe}周期的数据")
        return None, None

    df = signal_data[timeframe]

    # 回测策略
    backtest_results = components['strategy_evaluator'].backtest_signals(df, signal_column=signal_column)
    metrics = components['strategy_evaluator'].calculate_metrics(backtest_results)

    # 打印关键指标
    logger.info(f"策略回测结果 - 总收益率: {metrics['总收益率']:.2f}%, "
                f"夏普比率: {metrics['夏普比率']:.2f}, "
                f"最大回撤: {metrics['最大回撤']:.2f}%")

    return backtest_results, metrics


def setup_realtime_strategy(components, symbol):
    """
    设置实时数据处理和策略信号生成

    Args:
        components: 系统组件字典
        symbol: 交易对

    Returns:
        RealtimeDataCollector: 实时数据采集器
    """
    logger.info(f"设置{symbol}的实时数据处理和策略信号生成")

    # 定义数据更新回调函数
    def on_data_update(data_dict):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"收到数据更新: {current_time}")

        # 清洗数据
        cleaned_data = components['data_cleaner'].clean_all_timeframes(data_dict)

        # 转换数据，添加基础技术指标
        transformed_data = components['data_transformer'].transform_all_timeframes(cleaned_data)

        # 为每个时间周期生成交易信号
        for tf, df in transformed_data.items():
            if df.empty:
                continue

            # 添加技术因子
            df_with_factors = components['tech_factors'].add_basic_factors(df)
            df_with_custom = components['tech_factors'].add_custom_factors(df_with_factors)

            # 生成信号
            df_with_trend = components['trend_signal_generator'].generate_signals(df_with_custom)
            df_with_signals = components['reversal_signal_generator'].generate_signals(df_with_trend)

            # 计算组合信号
            df_with_signals['combined_signal'] = 0
            df_with_signals.loc[(df_with_signals['trend_signal'] == 1) &
                                (df_with_signals['reversal_signal'] == 1), 'combined_signal'] = 1
            df_with_signals.loc[(df_with_signals['trend_signal'] == -1) &
                                (df_with_signals['reversal_signal'] == -1), 'combined_signal'] = -1

            # 保存到数据库的信号集合
            collection_name = f"{symbol.replace('/', '_')}_{tf}_signals"
            components['db_handler'].save_dataframe(df_with_signals.iloc[-1:], collection_name, append=True)

            # 获取最新行的数据
            latest_row = df_with_signals.iloc[-1]
            latest_close = latest_row['close']
            latest_time = df_with_signals.index[-1]

            # 记录最新信号
            logger.info(f"{tf}周期 @ {latest_time} - 价格: {latest_close:.2f}, "
                        f"趋势信号: {latest_row['trend_signal']}, "
                        f"反转信号: {latest_row['reversal_signal']}, "
                        f"组合信号: {latest_row['combined_signal']}")

            # 根据最新信号生成交易建议
            if latest_row['combined_signal'] == 1:
                logger.info(f"【交易提示】{tf}周期建议: 买入 {symbol}")
            elif latest_row['combined_signal'] == -1:
                logger.info(f"【交易提示】{tf}周期建议: 卖出 {symbol}")

    # 注册回调函数
    components['realtime_collector'].register_callback(on_data_update)

    # 启动实时数据采集
    components['realtime_collector'].start()

    return components['realtime_collector']


def main():
    """
    主函数 - 运行完整的交易系统
    """
    logger.info("启动数字货币交易系统")

    # 选择交易对
    symbol = DATA_CONFIG['default_symbol']

    # 初始化系统组件
    components = initialize_system(symbol)

    # 处理历史数据并生成交易信号
    signal_data = process_historical_data(components, symbol)

    # 回测不同的策略信号
    # 以1小时和4小时时间周期为例
    for timeframe in ['1h', '4h']:
        if timeframe in signal_data:
            # 回测趋势信号
            trend_results, trend_metrics = backtest_strategy(
                components, signal_data, timeframe=timeframe, signal_column='trend_signal')

            # 回测反转信号
            reversal_results, reversal_metrics = backtest_strategy(
                components, signal_data, timeframe=timeframe, signal_column='reversal_signal')

            # 回测组合信号
            combined_results, combined_metrics = backtest_strategy(
                components, signal_data, timeframe=timeframe, signal_column='combined_signal')

            # 可视化表现最好的策略
            # 比较三种策略的总收益率
            strategies = {
                "趋势策略": trend_metrics.get('总收益率', 0) if trend_metrics else 0,
                "反转策略": reversal_metrics.get('总收益率', 0) if reversal_metrics else 0,
                "组合策略": combined_metrics.get('总收益率', 0) if combined_metrics else 0
            }

            # 找出表现最好的策略
            best_strategy = max(strategies, key=strategies.get)
            logger.info(f"{timeframe}周期表现最佳的是{best_strategy}，收益率: {strategies[best_strategy]:.2f}%")

            # 展示最佳策略的详细回测结果
            if best_strategy == "趋势策略" and trend_results is not None:
                logger.info("生成趋势策略的回测可视化报告...")
                components['strategy_visualizer'].create_full_report(trend_results, trend_metrics)
            elif best_strategy == "反转策略" and reversal_results is not None:
                logger.info("生成反转策略的回测可视化报告...")
                components['strategy_visualizer'].create_full_report(reversal_results, reversal_metrics)
            elif best_strategy == "组合策略" and combined_results is not None:
                logger.info("生成组合策略的回测可视化报告...")
                components['strategy_visualizer'].create_full_report(combined_results, combined_metrics)

    # 设置实时数据处理和策略信号生成
    realtime_collector = setup_realtime_strategy(components, symbol)

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
