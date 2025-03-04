"""
趋势信号生成模块

基于技术和基本面因子生成趋势信号
"""
import numpy as np


class TrendSignalGenerator:
    """
    趋势信号生成器

    基于各种技术指标和市场条件生成趋势交易信号
    """

    def __init__(self, lookback_period=20):
        """
        初始化趋势信号生成器

        Args:
            lookback_period: 回溯周期，用于计算趋势强度
        """
        self.lookback_period = lookback_period

    def generate_signals(self, df):
        """
        生成趋势交易信号

        Args:
            df: 包含技术因子的DataFrame

        Returns:
            包含交易信号的DataFrame
        """
        # 复制原始数据
        result_df = df.copy()

        # 添加基础趋势信号
        result_df = self._add_ma_crossover_signals(result_df)
        result_df = self._add_macd_signals(result_df)
        result_df = self._add_breakout_signals(result_df)

        # 生成综合趋势信号
        result_df = self._generate_composite_signal(result_df)

        return result_df

    def _add_ma_crossover_signals(self, df):
        """添加均线交叉信号"""
        # 快速均线上穿慢速均线 = 看涨信号
        df['ma_crossover_bullish'] = ((df['ma5'] > df['ma20']) &
                                      (df['ma5'].shift(1) <= df['ma20'].shift(1))).astype(int)

        # 快速均线下穿慢速均线 = 看跌信号
        df['ma_crossover_bearish'] = ((df['ma5'] < df['ma20']) &
                                      (df['ma5'].shift(1) >= df['ma20'].shift(1))).astype(int)

        return df

    def _add_macd_signals(self, df):
        """添加MACD信号"""
        # MACD柱状线由负变正 = 看涨信号
        df['macd_bullish'] = ((df['macd_hist'] > 0) &
                              (df['macd_hist'].shift(1) <= 0)).astype(int)

        # MACD柱状线由正变负 = 看跌信号
        df['macd_bearish'] = ((df['macd_hist'] < 0) &
                              (df['macd_hist'].shift(1) >= 0)).astype(int)

        return df

    def _add_breakout_signals(self, df):
        """添加突破信号"""
        # 计算N日高点和低点
        df['highest_high'] = df['high'].rolling(window=self.lookback_period).max()
        df['lowest_low'] = df['low'].rolling(window=self.lookback_period).min()

        # 向上突破 = 看涨信号
        df['breakout_bullish'] = ((df['close'] > df['highest_high'].shift(1)) &
                                  (df['close'].shift(1) <= df['highest_high'].shift(2))).astype(int)

        # 向下突破 = 看跌信号
        df['breakout_bearish'] = ((df['close'] < df['lowest_low'].shift(1)) &
                                  (df['close'].shift(1) >= df['lowest_low'].shift(2))).astype(int)

        return df

    def _generate_composite_signal(self, df):
        """生成综合趋势信号"""
        # 复制 DataFrame 以避免修改原始数据
        result_df = df.copy()

        # 计算看涨信号总数
        bullish_signals = result_df['ma_crossover_bullish'] + result_df['macd_bullish'] + result_df['breakout_bullish']

        # 计算看跌信号总数
        bearish_signals = result_df['ma_crossover_bearish'] + result_df['macd_bearish'] + result_df['breakout_bearish']

        # 综合信号: 1=看涨, -1=看跌, 0=中性
        result_df['trend_signal'] = 0
        result_df.loc[bullish_signals > bearish_signals, 'trend_signal'] = 1
        result_df.loc[bearish_signals > bullish_signals, 'trend_signal'] = -1

        # 信号强度: 基于信号数量的差异(范围从-3到3)
        result_df['signal_strength'] = bullish_signals - bearish_signals

        # 添加趋势方向持续期
        result_df['trend_duration'] = 0

        # 计算当前趋势持续的K线数量
        current_trend = 0
        duration = 0

        # 创建一个趋势持续时间数组
        trend_durations = np.zeros(len(result_df))

        for i in range(len(result_df)):
            if i == 0:
                current_trend = result_df['trend_signal'].iloc[i]
                duration = 1
            elif result_df['trend_signal'].iloc[i] == current_trend:
                duration += 1
            else:
                current_trend = result_df['trend_signal'].iloc[i]
                duration = 1

            # 存储到数组中
            trend_durations[i] = duration

        # 一次性更新趋势持续时间列
        result_df['trend_duration'] = trend_durations

        return result_df
