"""
反转信号生成模块

基于技术和基本面因子生成反转交易信号
"""
import pandas as pd
import numpy as np


class ReversalSignalGenerator:
    """
    反转信号生成器

    基于超买超卖指标和价格模式生成反转交易信号
    """

    def __init__(self, rsi_overbought=70, rsi_oversold=30):
        """
        初始化反转信号生成器

        Args:
            rsi_overbought: RSI超买阈值
            rsi_oversold: RSI超卖阈值
        """
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signals(self, df):
        """
        生成反转交易信号

        Args:
            df: 包含技术因子的DataFrame

        Returns:
            包含交易信号的DataFrame
        """
        # 复制原始数据
        result_df = df.copy()

        # 添加RSI反转信号
        result_df = self._add_rsi_reversal_signals(result_df)

        # 添加随机指标KD反转信号
        result_df = self._add_stochastic_reversal_signals(result_df)

        # 添加价格动量反转信号
        result_df = self._add_momentum_reversal_signals(result_df)

        # 生成综合反转信号
        result_df = self._generate_composite_signal(result_df)

        return result_df

    def _add_rsi_reversal_signals(self, df):
        """添加RSI反转信号"""
        # 从超买区域回落 = 看跌反转信号
        df['rsi_bearish_reversal'] = ((df['rsi_14'] < self.rsi_overbought) &
                                      (df['rsi_14'].shift(1) >= self.rsi_overbought)).astype(int)

        # 从超卖区域回升 = 看涨反转信号
        df['rsi_bullish_reversal'] = ((df['rsi_14'] > self.rsi_oversold) &
                                      (df['rsi_14'].shift(1) <= self.rsi_oversold)).astype(int)

        return df

    def _add_stochastic_reversal_signals(self, df):
        """添加随机指标KD反转信号"""
        # KD指标参数
        k_overbought = 80
        k_oversold = 20

        # 从超买区域回落 = 看跌反转信号
        df['stoch_bearish_reversal'] = ((df['k_9_3'] < k_overbought) &
                                        (df['k_9_3'].shift(1) >= k_overbought) &
                                        (df['k_9_3'] < df['d_9_3'])).astype(int)

        # 从超卖区域回升 = 看涨反转信号
        df['stoch_bullish_reversal'] = ((df['k_9_3'] > k_oversold) &
                                        (df['k_9_3'].shift(1) <= k_oversold) &
                                        (df['k_9_3'] > df['d_9_3'])).astype(int)

        return df

    def _add_momentum_reversal_signals(self, df):
        """添加价格动量反转信号"""
        # 计算短期价格动量(5日)
        df['short_momentum'] = df['close'].pct_change(5)

        # 计算中期价格动量(20日)
        df['medium_momentum'] = df['close'].pct_change(20)

        # 短期动量负但中期动量正 = 短期超卖可能反弹
        df['momentum_bullish_reversal'] = ((df['short_momentum'] < 0) &
                                           (df['medium_momentum'] > 0) &
                                           (df['short_momentum'] > df['short_momentum'].shift(1))).astype(int)

        # 短期动量正但中期动量负 = 短期超买可能回调
        df['momentum_bearish_reversal'] = ((df['short_momentum'] > 0) &
                                           (df['medium_momentum'] < 0) &
                                           (df['short_momentum'] < df['short_momentum'].shift(1))).astype(int)

        return df

    def _generate_composite_signal(self, df):
        """生成综合反转信号"""
        # 计算看涨反转信号总数
        bullish_signals = df['rsi_bullish_reversal'] + df['stoch_bullish_reversal'] + df['momentum_bullish_reversal']

        # 计算看跌反转信号总数
        bearish_signals = df['rsi_bearish_reversal'] + df['stoch_bearish_reversal'] + df['momentum_bearish_reversal']

        # 综合信号: 1=看涨反转, -1=看跌反转, 0=无反转信号
        df['reversal_signal'] = 0
        df.loc[bullish_signals >= 2, 'reversal_signal'] = 1  # 至少两个看涨反转信号
        df.loc[bearish_signals >= 2, 'reversal_signal'] = -1  # 至少两个看跌反转信号

        # 信号强度: 基于信号数量(范围从-3到3)
        df['reversal_strength'] = bullish_signals - bearish_signals

        return df