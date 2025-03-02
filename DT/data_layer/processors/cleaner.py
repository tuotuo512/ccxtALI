"""
数据清洗模块

负责清理市场数据中的缺失值、异常值和重复项
"""

import pandas as pd
import numpy as np
import logging

# 设置日志
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    数据清洗器

    处理缺失值、异常值、重复数据等问题
    """

    def __init__(self):
        """
        初始化数据清洗器
        """
        pass

    def clean_ohlcv_data(self, df):
        """
        清理OHLCV数据

        Args:
            df: 包含OHLCV数据的DataFrame

        Returns:
            pd.DataFrame: 清理后的DataFrame
        """
        if df.empty:
            logger.warning("输入数据为空，无需清理")
            return df

        # 复制数据，避免修改原始数据
        cleaned_df = df.copy()

        # 1. 处理重复索引
        if cleaned_df.index.duplicated().any():
            logger.info(f"发现重复索引，保留最后出现的记录")
            cleaned_df = cleaned_df[~cleaned_df.index.duplicated(keep='last')]

        # 2. 处理缺失值
        if cleaned_df.isnull().values.any():
            missing_count = cleaned_df.isnull().sum().sum()
            logger.info(f"发现{missing_count}个缺失值")

            # 使用前向填充处理缺失值
            cleaned_df = cleaned_df.fillna(method='ffill')

            # 如果仍有缺失值(比如起始数据)，使用后向填充
            if cleaned_df.isnull().values.any():
                cleaned_df = cleaned_df.fillna(method='bfill')

        # 3. 处理异常值 (例如：价格和成交量为0或负数)
        # 处理价格为0或负数
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if (cleaned_df[col] <= 0).any():
                count = (cleaned_df[col] <= 0).sum()
                logger.warning(f"发现{count}条{col}列的价格为0或负数")

                # 将异常值替换为前一个有效值
                mask = cleaned_df[col] <= 0
                cleaned_df.loc[mask, col] = np.nan
                cleaned_df[col] = cleaned_df[col].fillna(method='ffill').fillna(method='bfill')

        # 处理成交量为负数
        if (cleaned_df['volume'] < 0).any():
            count = (cleaned_df['volume'] < 0).sum()
            logger.warning(f"发现{count}条成交量为负数")
            cleaned_df.loc[cleaned_df['volume'] < 0, 'volume'] = 0

        # 4. 检查并修复OHLC关系 (high应该>=open,close,low；low应该<=open,close)
        # 修复high值
        high_issue = (cleaned_df['high'] < cleaned_df[['open', 'close']].max(axis=1))
        if high_issue.any():
            count = high_issue.sum()
            logger.warning(f"发现{count}条high值小于open或close")
            cleaned_df.loc[high_issue, 'high'] = cleaned_df.loc[high_issue, ['open', 'close']].max(axis=1)

        # 修复low值
        low_issue = (cleaned_df['low'] > cleaned_df[['open', 'close']].min(axis=1))
        if low_issue.any():
            count = low_issue.sum()
            logger.warning(f"发现{count}条low值大于open或close")
            cleaned_df.loc[low_issue, 'low'] = cleaned_df.loc[low_issue, ['open', 'close']].min(axis=1)

        # 5. 确保数据按时间排序
        if not cleaned_df.index.is_monotonic_increasing:
            logger.info("数据未按时间排序，进行排序")
            cleaned_df = cleaned_df.sort_index()

        return cleaned_df

    def clean_all_timeframes(self, data_dict):
        """
        清理所有时间周期的数据

        Args:
            data_dict: 包含多个时间周期数据的字典

        Returns:
            dict: 清理后的数据字典
        """
        result = {}
        for timeframe, df in data_dict.items():
            logger.info(f"清理{timeframe}周期数据")
            result[timeframe] = self.clean_ohlcv_data(df)

        return result


# 使用示例
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 创建测试数据
    dates = pd.date_range('2023-01-01', periods=10, freq='1Min')
    data = {
        'open': [100, 101, 102, 103, 0, 105, 106, 107, 108, 109],
        'high': [102, 103, 104, 105, 106, 107, 108, 107, 110, 111],
        'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'volume': [1000, 1100, 1200, 1300, -1, 1500, 1600, 1700, 1800, 1900]
    }
    df = pd.DataFrame(data, index=dates)

    # 创建数据清洗器
    cleaner = DataCleaner()

    # 清理数据
    cleaned_df = cleaner.clean_ohlcv_data(df)

    # 打印结果
    print("原始数据:")
    print(df)
    print("\n清理后数据:")
    print(cleaned_df)