"""
策略回测可视化模块

用于生成交易策略回测的可视化图表
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from IPython.display import display


class StrategyVisualizer:
    """
    策略回测可视化工具

    用于生成交易策略回测的可视化图表
    """

    def __init__(self, figsize=(14, 8)):
        """
        初始化可视化器

        Args:
            figsize: 图表大小
        """
        self.figsize = figsize

    def plot_returns(self, backtest_df):
        """
        绘制回报率曲线

        Args:
            backtest_df: 包含回测结果的DataFrame
        """
        plt.figure(figsize=self.figsize)

        # 绘制策略累积回报率
        plt.plot(backtest_df.index, backtest_df['strategy_cumulative_returns'] * 100,
                 label='策略回报', color='blue', linewidth=2)

        # 绘制买入持有累积回报率
        plt.plot(backtest_df.index, backtest_df['cumulative_returns'] * 100,
                 label='买入持有回报', color='gray', linestyle='--')

        # 设置图表
        plt.title('策略累积回报率对比')
        plt.xlabel('日期')
        plt.ylabel('累积回报率 (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 设置日期格式
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_portfolio_value(self, backtest_df):
        """
        绘制投资组合价值曲线

        Args:
            backtest_df: 包含回测结果的DataFrame
        """
        plt.figure(figsize=self.figsize)

        # 绘制投资组合价值
        plt.plot(backtest_df.index, backtest_df['portfolio_value'],
                 label='投资组合价值', color='green', linewidth=2)

        # 绘制初始资金水平线
        initial_capital = backtest_df['portfolio_value'].iloc[0]
        plt.axhline(y=initial_capital, color='red', linestyle='--',
                    label=f'初始资金: {initial_capital:.2f}')

        # 设置图表
        plt.title('投资组合价值变化')
        plt.xlabel('日期')
        plt.ylabel('价值')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 添加千位分隔符到y轴
        plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))

        # 设置日期格式
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_drawdown(self, backtest_df):
        """
        绘制回撤曲线

        Args:
            backtest_df: 包含回测结果的DataFrame
        """
        # 计算回撤
        portfolio_value = backtest_df['portfolio_value']
        rolling_max = portfolio_value.cummax()
        drawdown = (rolling_max - portfolio_value) / rolling_max * 100

        # 添加回撤列到DataFrame
        backtest_df['drawdown'] = drawdown

        plt.figure(figsize=self.figsize)

        # 绘制回撤曲线
        plt.fill_between(backtest_df.index, 0, drawdown, color='red', alpha=0.3)
        plt.plot(backtest_df.index, drawdown, color='red', label='回撤 (%)')

        # 设置图表
        plt.title('策略回撤')
        plt.xlabel('日期')
        plt.ylabel('回撤 (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 设置y轴方向
        plt.gca().invert_yaxis()

        # 设置日期格式
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_trades(self, backtest_df, price_column='close', signal_column='position'):
        """
        绘制交易信号和价格图

        Args:
            backtest_df: 包含回测结果的DataFrame
            price_column: 价格列名
            signal_column: 信号列名
        """
        plt.figure(figsize=self.figsize)

        # 绘制价格曲线
        plt.plot(backtest_df.index, backtest_df[price_column], color='blue', linewidth=1.5)

        # 找出买入点和卖出点
        buy_signals = backtest_df[(backtest_df[signal_column].shift(1) <= 0) &
                                  (backtest_df[signal_column] > 0)]
        sell_signals = backtest_df[(backtest_df[signal_column].shift(1) >= 0) &
                                   (backtest_df[signal_column] < 0)]

        # 绘制买入点和卖出点
        plt.scatter(buy_signals.index, buy_signals[price_column],
                    marker='^', color='green', s=100, label='买入信号')
        plt.scatter(sell_signals.index, sell_signals[price_column],
                    marker='v', color='red', s=100, label='卖出信号')

        # 设置图表
        plt.title('价格走势和交易信号')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 设置日期格式
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def display_metrics_table(self, metrics):
        """
        显示策略评估指标表格

        Args:
            metrics: 包含策略评估指标的字典
        """
        # 创建指标表格
        metrics_df = pd.DataFrame(list(metrics.items()), columns=['指标', '数值'])

        # 格式化数值
        for i, value in enumerate(metrics_df['数值']):
            if isinstance(value, float):
                if metrics_df['指标'][i] in ['初始资金', '结束资金']:
                    metrics_df.loc[i, '数值'] = f"{value:,.2f}"
                else:
                    metrics_df.loc[i, '数值'] = f"{value:.2f}"

        # 显示表格
        print("\n策略评估指标:")
        display(metrics_df)

    def create_full_report(self, backtest_df, metrics):
        """
        创建完整的策略回测报告

        Args:
            backtest_df: 包含回测结果的DataFrame
            metrics: 包含策略评估指标的字典
        """
        # 显示指标表格
        self.display_metrics_table(metrics)

        # 绘制各类图表
        self.plot_returns(backtest_df)
        self.plot_portfolio_value(backtest_df)
        self.plot_drawdown(backtest_df)
        self.plot_trades(backtest_df)