"""
技术分析因子模块

包含各种常用技术指标的计算函数
"""
import pandas as pd
import numpy as np
import pandas_ta as ta


class TechnicalFactors:
    """
    技术分析因子计算类

    用于计算各种技术指标，并将其添加到价格数据DataFrame中
    """

    def __init__(self):
        """初始化技术因子计算器"""
        pass

    def add_basic_factors(self, df):
        """
        添加基础技术因子

        Args:
            df: 包含OHLCV数据的DataFrame，必须有['open', 'high', 'low', 'close', 'volume']这些列

        Returns:
            添加了技术因子的DataFrame
        """
        # 复制原始数据，避免修改原始数据
        result_df = df.copy()

        # 检查数据格式
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in result_df.columns for col in required_columns):
            raise ValueError(f"输入数据缺少必要列: {required_columns}")

        # 添加基础价格因子
        result_df = self._add_price_factors(result_df)

        # 添加趋势因子
        result_df = self._add_trend_factors(result_df)

        # 添加震荡指标
        result_df = self._add_oscillator_factors(result_df)

        # 添加成交量因子
        result_df = self._add_volume_factors(result_df)

        return result_df

    def _add_price_factors(self, df):
        """添加价格相关因子"""
        # 获取价格数据
        close = df['close']
        high = df['high']
        low = df['low']

        # 计算价格变动百分比
        df['returns'] = close.pct_change() * 100

        # 计算价格波动率 (20日)
        df['volatility_20'] = df['returns'].rolling(window=20).std()

        # 计算区间最高价和最低价
        df['highest_20'] = high.rolling(window=20).max()
        df['lowest_20'] = low.rolling(window=20).min()

        # 计算当前价格在过去20个周期区间的位置(0-100)
        df['price_position'] = (close - df['lowest_20']) / (df['highest_20'] - df['lowest_20']) * 100

        return df

    def _add_trend_factors(self, df):
        """添加趋势相关因子"""
        close = df['close']

        # 计算移动平均线
        df['ma5'] = ta.sma(close, length=5)
        df['ma10'] = ta.sma(close, length=10)
        df['ma20'] = ta.sma(close, length=20)
        df['ma60'] = ta.sma(close, length=60)

        # 添加MACD指标
        macd = ta.macd(close, fast=12, slow=26, signal=9)
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']

        # 计算均线差值百分比
        df['ma5_10_diff'] = (df['ma5'] / df['ma10'] - 1) * 100
        df['ma10_20_diff'] = (df['ma10'] / df['ma20'] - 1) * 100
        df['ma20_60_diff'] = (df['ma20'] / df['ma60'] - 1) * 100

        return df

    def _add_oscillator_factors(self, df):
        """添加震荡指标因子"""
        close = df['close']
        high = df['high']
        low = df['low']

        # 计算RSI指标
        df['rsi_14'] = ta.rsi(close, length=14)

        # 添加随机指标KD
        stoch = ta.stoch(high, low, close, k=9, d=3, smooth_k=3)
        df['k_9_3'] = stoch['STOCHk_9_3_3']
        df['d_9_3'] = stoch['STOCHd_9_3_3']

        return df

    def _add_volume_factors(self, df):
        """添加成交量相关因子"""
        volume = df['volume']
        close = df['close']

        # 计算成交量移动平均
        df['volume_ma5'] = ta.sma(volume, length=5)
        df['volume_ma20'] = ta.sma(volume, length=20)

        # 成交量比率
        df['volume_ratio'] = volume / df['volume_ma20']

        # 计算OBV (On-Balance Volume)
        df['obv'] = ta.obv(close, volume)

        return df

    def add_custom_factors(self, df):
        """
        添加自定义技术因子

        这里可以添加你自己设计的因子和特征

        Args:
            df: 包含价格数据和基本因子的DataFrame

        Returns:
            添加了自定义因子的DataFrame
        """
        # 复制原始数据
        result_df = df.copy()

        # 示例：添加一个价格动量指标 (当前价格与N日前价格的比值)
        result_df['momentum_5'] = result_df['close'] / result_df['close'].shift(5) - 1
        result_df['momentum_10'] = result_df['close'] / result_df['close'].shift(10) - 1
        result_df['momentum_20'] = result_df['close'] / result_df['close'].shift(20) - 1

        # 示例：添加一个自定义的均线交叉信号
        # 黄金交叉：短期均线上穿长期均线
        result_df['golden_cross'] = ((result_df['ma5'] > result_df['ma20']) &
                                     (result_df['ma5'].shift(1) <= result_df['ma20'].shift(1))).astype(int)

        # 死亡交叉：短期均线下穿长期均线
        result_df['death_cross'] = ((result_df['ma5'] < result_df['ma20']) &
                                    (result_df['ma5'].shift(1) >= result_df['ma20'].shift(1))).astype(int)

        # 示例：添加一个结合RSI和成交量的自定义指标
        result_df['rsi_volume_factor'] = result_df['rsi_14'] * result_df['volume_ratio']

        # 添加布林带指标
        bbands = ta.bbands(close=result_df['close'], length=20, std=2)
        result_df['bb_upper'] = bbands['BBU_20_2.0']
        result_df['bb_middle'] = bbands['BBM_20_2.0']
        result_df['bb_lower'] = bbands['BBL_20_2.0']

        # 添加相对于布林带位置的指标 (0-100)
        result_df['bb_position'] = (result_df['close'] - result_df['bb_lower']) / (
                    result_df['bb_upper'] - result_df['bb_lower']) * 100

        # 添加CMF (Chaikin Money Flow)
        result_df['cmf'] = ta.cmf(high=result_df['high'], low=result_df['low'],
                                  close=result_df['close'], volume=result_df['volume'], length=20)

        # 添加DMI (Directional Movement Index)
        dmi = ta.adx(high=result_df['high'], low=result_df['low'], close=result_df['close'], length=14)
        result_df['adx'] = dmi['ADX_14']
        result_df['di_plus'] = dmi['DMP_14']
        result_df['di_minus'] = dmi['DMN_14']

        return result_df