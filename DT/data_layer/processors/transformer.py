"""
数据转换模块

负责对清洗后的数据进行转换，计算技术指标和特征
"""

import pandas as pd
import numpy as np
import talib
import logging

# 设置日志
logger = logging.getLogger(__name__)


class DataTransformer:
    """
    数据转换器

    计算各种技术指标和特征，用于后续分析和模型训练
    """

    def __init__(self):
        """
        初始化数据转换器
        """
        pass

    def add_basic_indicators(self, df):
        """
        添加基础技术指标

        Args:
            df: 清洗后的OHLCV数据

        Returns:
            pd.DataFrame: 添加指标后的DataFrame
        """
        if df.empty:
            logger.warning("输入数据为空，无法计算指标")
            return df

        result = df.copy()

        try:
            # 1. 移动平均线
            result['MA5'] = talib.SMA(result['close'].values, timeperiod=5)
            result['MA10'] = talib.SMA(result['close'].values, timeperiod=10)
            result['MA20'] = talib.SMA(result['close'].values, timeperiod=20)
            result['MA60'] = talib.SMA(result['close'].values, timeperiod=60)

            # 2. 指数移动平均线
            result['EMA12'] = talib.EMA(result['close'].values, timeperiod=12)
            result['EMA26'] = talib.EMA(result['close'].values, timeperiod=26)

            # 3. MACD
            macd, macd_signal, macd_hist = talib.MACD(
                result['close'].values,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            result['MACD'] = macd
            result['MACD_SIGNAL'] = macd_signal
            result['MACD_HIST'] = macd_hist

            # 4. RSI
            result['RSI6'] = talib.RSI(result['close'].values, timeperiod=6)
            result['RSI12'] = talib.RSI(result['close'].values, timeperiod=12)
            result['RSI24'] = talib.RSI(result['close'].values, timeperiod=24)

            # 5. 布林带
            upper, middle, lower = talib.BBANDS(
                result['close'].values,
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            result['BB_UPPER'] = upper
            result['BB_MIDDLE'] = middle
            result['BB_LOWER'] = lower

            # 6. ATR - 平均真实波幅
            result['ATR'] = talib.ATR(
                result['high'].values,
                result['low'].values,
                result['close'].values,
                timeperiod=14
            )

            # 7. OBV - 能量潮指标
            result['OBV'] = talib.OBV(result['close'].values, result['volume'].values)

            logger.info("已添加基础技术指标")

        except Exception as e:
            logger.error(f"计算技术指标失败: {str(e)}")

        return result

    def add_trend_indicators(self, df):
        """
        添加趋势相关指标

        Args:
            df: 包含基础指标的DataFrame

        Returns:
            pd.DataFrame: 添加趋势指标后的DataFrame
        """
        if df.empty:
            return df

        result = df.copy()

        try:
            # 1. ADX - 平均趋向指数
            result['ADX'] = talib.ADX(
                result['high'].values,
                result['low'].values,
                result['close'].values,
                timeperiod=14
            )

            # 2. DI+ 和 DI-
            result['PLUS_DI'] = talib.PLUS_DI(
                result['high'].values,
                result['low'].values,
                result['close'].values,
                timeperiod=14
            )

            result['MINUS_DI'] = talib.MINUS_DI(
                result['high'].values,
                result['low'].values,
                result['close'].values,
                timeperiod=14
            )

            # 3. 抛物线转向指标 (SAR)
            result['SAR'] = talib.SAR(
                result['high'].values,
                result['low'].values,
                acceleration=0.02,
                maximum=0.2
            )

            # 4. CCI - 顺势指标
            result['CCI'] = talib.CCI(
                result['high'].values,
                result['low'].values,
                result['close'].values,
                timeperiod=14
            )

            # 5. 价格位置（相对于移动平均线）
            if 'MA20' in result.columns:
                result['PRICE_REL_MA20'] = result['close'] / result['MA20'] - 1

            if 'MA60' in result.columns:
                result['PRICE_REL_MA60'] = result['close'] / result['MA60'] - 1

            logger.info("已添加趋势指标")

        except Exception as e:
            logger.error(f"计算趋势指标失败: {str(e)}")

        return result

    def add_volatility_indicators(self, df):
        """
        添加波动率相关指标

        Args:
            df: 包含基础指标的DataFrame

        Returns:
            pd.DataFrame: 添加波动率指标后的DataFrame
        """
        if df.empty:
            return df

        result = df.copy()

        try:
            # 1. 计算历史波动率 (过去N根K线的收盘价标准差)
            for period in [5, 10, 20]:
                result[f'VOLATILITY_{period}'] = result['close'].rolling(window=period).std() / result['close']

            # 2. 真实波幅 (TR)
            result['TR'] = talib.TRANGE(
                result['high'].values,
                result['low'].values,
                result['close'].values
            )

            # 3. 布林带宽度
            if all(x in result.columns for x in ['BB_UPPER', 'BB_LOWER', 'BB_MIDDLE']):
                result['BB_WIDTH'] = (result['BB_UPPER'] - result['BB_LOWER']) / result['BB_MIDDLE']

            logger.info("已添加波动率指标")

        except Exception as e:
            logger.error(f"计算波动率指标失败: {str(e)}")

        return result

    def add_custom_indicators(self, df):
        """
        添加自定义指标，特别适合数字货币交易

        Args:
            df: DataFrame对象

        Returns:
            pd.DataFrame: 添加自定义指标后的DataFrame
        """
        if df.empty:
            return df

        result = df.copy()

        try:
            # 1. 计算涨跌幅
            result['RETURN'] = result['close'].pct_change()

            # 2. 计算累积收益
            result['CUM_RETURN'] = (1 + result['RETURN']).cumprod() - 1

            # 3. 计算高低点指标 (当前价格距离过去N周期高点的百分比)
            for period in [20, 50]:
                result[f'HIGH_DIST_{period}'] = result['close'] / result['high'].rolling(period).max() - 1
                result[f'LOW_DIST_{period}'] = result['close'] / result['low'].rolling(period).min() - 1

            # 4. 成交量变化率
            result['VOLUME_CHANGE'] = result['volume'].pct_change()

            # 5. 成交量相对均值
            result['VOLUME_REL_MA20'] = result['volume'] / result['volume'].rolling(20).mean()

            # 6. 价格波动范围比率
            result['RANGE_RATIO'] = (result['high'] - result['low']) / (result['open'] + result['close']) * 2

            logger.info("已添加自定义指标")

        except Exception as e:
            logger.error(f"计算自定义指标失败: {str(e)}")

        return result

    def transform_data(self, df, add_all_indicators=True):
        """
        对数据进行完整转换，添加所有或选定的指标

        Args:
            df: 原始OHLCV数据
            add_all_indicators: 是否添加所有指标

        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        if df.empty:
            return df

        # 先添加基础指标
        result = self.add_basic_indicators(df)

        if add_all_indicators:
            # 添加其他类型的指标
            result = self.add_trend_indicators(result)
            result = self.add_volatility_indicators(result)
            result = self.add_custom_indicators(result)

        # 删除NaN值
        result = result.dropna()

        return result

    def transform_all_timeframes(self, data_dict, add_all_indicators=True):
        """
        转换所有时间周期的数据

        Args:
            data_dict: 包含多个时间周期数据的字典
            add_all_indicators: 是否添加所有指标

        Returns:
            dict: 转换后的数据字典
        """
        result = {}
        for timeframe, df in data_dict.items():
            logger.info(f"转换{timeframe}周期数据")
            result[timeframe] = self.transform_data(df, add_all_indicators)

        return result


# 使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 导入示例数据
    from data_layer.collectors.historical import HistoricalDataCollector

    # 获取历史数据
    collector = HistoricalDataCollector()
    data = collector.fetch_ohlcv(timeframe='1h', limit=200)

    # 创建转换器
    transformer = DataTransformer()

    # 添加所有指标
    transformed_data = transformer.transform_data(data)

    # 打印转换后的数据信息
    print(f"原始数据列: {data.columns.tolist()}")
    print(f"转换后数据列: {transformed_data.columns.tolist()}")
    print(f"转换后数据行数: {len(transformed_data)}")
    print("\n前5行数据:")
    print(transformed_data.head())