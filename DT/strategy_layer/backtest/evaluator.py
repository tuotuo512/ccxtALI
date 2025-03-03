"""
交易策略回测评估模块

用于评估交易策略的历史表现
"""
import pandas as pd
import numpy as np
from datetime import datetime


class StrategyEvaluator:
    """
    策略回测评估器

    用于评估交易策略的历史表现和各项指标
    """

    def __init__(self, initial_capital=10000.0, position_size=0.1, commission=0.001):
        """
        初始化策略评估器

        Args:
            initial_capital: 初始资金
            position_size: 每次交易的仓位比例(0-1)
            commission: 交易手续费率
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.commission = commission

    def backtest_signals(self, df, signal_column, price_column='close'):
        """
        回测交易信号

        Args:
            df: 包含价格和信号的DataFrame
            signal_column: 信号列名
            price_column: 价格列名

        Returns:
            包含回测结果的DataFrame
        """
        # 复制原始数据
        result_df = df.copy()

        # 添加仓位列
        result_df['position'] = 0

        # 根据信号生成仓位
        # signal: 1=看涨(做多), -1=看跌(做空), 0=中性(不操作)
        result_df['position'] = result_df[signal_column]

        # 为了避免未来信息的使用，将position向后移动一个周期
        result_df['position'] = result_df['position'].shift(1)

        # 第一个周期没有仓位
        result_df['position'].iloc[0] = 0

        # 计算每日回报率
        result_df['returns'] = result_df[price_column].pct_change()

        # 计算策略回报率(考虑仓位)
        result_df['strategy_returns'] = result_df['position'] * result_df['returns']

        # 考虑交易成本
        result_df['trade'] = result_df['position'].diff().abs()
        result_df['cost'] = result_df['trade'] * self.commission
        result_df['strategy_returns'] = result_df['strategy_returns'] - result_df['cost']

        # 计算累积回报
        result_df['cumulative_returns'] = (1 + result_df['returns']).cumprod() - 1
        result_df['strategy_cumulative_returns'] = (1 + result_df['strategy_returns']).cumprod() - 1

        # 计算账户价值
        result_df['portfolio_value'] = self.initial_capital * (1 + result_df['strategy_cumulative_returns'])

        return result_df

    def calculate_metrics(self, backtest_df):
        """
        计算策略评估指标

        Args:
            backtest_df: 回测结果DataFrame

        Returns:
            包含策略评估指标的字典
        """
        # 提取策略日收益率
        returns = backtest_df['strategy_returns'].dropna()

        if len(returns) == 0:
            print("警告: 没有足够的数据计算指标")
            return {}

        # 计算总收益率
        total_return = backtest_df['strategy_cumulative_returns'].iloc[-1]

        # 计算年化收益率(假设252个交易日/年)
        days = (backtest_df.index[-1] - backtest_df.index[0]).days
        annual_return = (1 + total_return) ** (252 / max(days, 1)) - 1

        # 计算夏普比率(假设无风险利率为0)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)

        # 计算最大回撤
        cumulative = backtest_df['portfolio_value']
        max_drawdown = 0
        peak = cumulative.iloc[0]

        for value in cumulative:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # 计算胜率
        winning_trades = (returns > 0).sum()
        total_trades = (backtest_df['trade'] > 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # 返回指标字典
        metrics = {
            '初始资金': self.initial_capital,
            '结束资金': backtest_df['portfolio_value'].iloc[-1],
            '总收益率': total_return * 100,
            '年化收益率': annual_return * 100,
            '夏普比率': sharpe_ratio,
            '最大回撤': max_drawdown * 100,
            '交易次数': total_trades,
            '胜率': win_rate * 100
        }

        return metrics