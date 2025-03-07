"""
数据转换模块

负责对清洗后的数据进行转换，计算技术指标和特征
"""

import logging

import pandas as pd
import pandas_ta as ta

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
            result['MA5'] = ta.sma(result['close'], length=5)
            result['MA10'] = ta.sma(result['close'], length=10)
            result['MA20'] = ta.sma(result['close'], length=20)
            result['MA60'] = ta.sma(result['close'], length=60)

            # 2. 指数移动平均线
            result['EMA12'] = ta.ema(result['close'], length=12)
            result['EMA26'] = ta.ema(result['close'], length=26)

            # 3. MACD
            macd = ta.macd(result['close'], fast=12, slow=26, signal=9)
            result['MACD'] = macd['MACD_12_26_9']
            result['MACD_SIGNAL'] = macd['MACDs_12_26_9']
            result['MACD_HIST'] = macd['MACDh_12_26_9']

            # 4. RSI
            result['RSI6'] = ta.rsi(result['close'], length=6)
            result['RSI12'] = ta.rsi(result['close'], length=12)
            result['RSI24'] = ta.rsi(result['close'], length=24)

            # 5. 布林带
            bbands = ta.bbands(result['close'], length=20, std=2)
            result['BB_UPPER'] = bbands['BBU_20_2.0']
            result['BB_MIDDLE'] = bbands['BBM_20_2.0']
            result['BB_LOWER'] = bbands['BBL_20_2.0']

            # 6. ATR - 平均真实波幅
            result['ATR'] = ta.atr(result['high'], result['low'], result['close'], length=14)

            # 7. OBV - 能量潮指标
            result['OBV'] = ta.obv(result['close'], result['volume'])

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
            # 使用pandas_ta计算ADX和方向指标
            dmi = ta.adx(result['high'], result['low'], result['close'], length=14)
            result['ADX'] = dmi['ADX_14']
            result['PLUS_DI'] = dmi['DMP_14']
            result['MINUS_DI'] = dmi['DMN_14']

            # 3. 抛物线转向指标 (SAR)
            result['SAR'] = ta.psar(result['high'], result['low'])['PSARl_0.02_0.2']

            # 4. CCI - 顺势指标
            result['CCI'] = ta.cci(result['high'], result['low'], result['close'], length=14)

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
            result['TR'] = ta.true_range(result['high'], result['low'], result['close'])

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

            # 7. 钱德动量摆动指标 (CMO)
            result['CMO'] = ta.cmo(result['close'], length=14)

            # 8. 资金流量指标 (MFI)
            result['MFI'] = ta.mfi(result['high'], result['low'], result['close'], result['volume'], length=14)

            # 9. 漩涡指标 (Vortex)
            vortex = ta.vortex(result['high'], result['low'], result['close'], length=14)
            result['VORTEX_POS'] = vortex['VTXP_14']
            result['VORTEX_NEG'] = vortex['VTXM_14']

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

    # 创建测试数据
    import pandas as pd
    import numpy as np

    # 创建模拟的OHLCV数据
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=200, freq='1H')
    test_data = pd.DataFrame({
        'open': np.random.normal(100, 5, 200),
        'high': np.random.normal(105, 5, 200),
        'low': np.random.normal(95, 5, 200),
        'close': np.random.normal(100, 5, 200),
        'volume': np.random.normal(1000, 200, 200)
    }, index=dates)

    # 确保high>low，high>open, high>close
    for idx, row in test_data.iterrows():
        max_val = max(row['open'], row['close']) + abs(np.random.normal(2, 1))
        min_val = min(row['open'], row['close']) - abs(np.random.normal(2, 1))
        test_data.loc[idx, 'high'] = max_val
        test_data.loc[idx, 'low'] = min_val
        test_data.loc[idx, 'volume'] = abs(test_data.loc[idx, 'volume'])

    # 创建转换器
    transformer = DataTransformer()

    # 添加所有指标
    transformed_data = transformer.transform_data(test_data)

    # 打印转换后的数据信息
    print(f"原始数据列: {test_data.columns.tolist()}")
    print(f"转换后数据列: {transformed_data.columns.tolist()}")
    print(f"转换后数据行数: {len(transformed_data)}")
    print("\n前5行数据:")
    print(transformed_data.head())