import pandas as pd
import os

# 设置文件夹路径
folder_path = r'C:\Users\Administrator\Desktop\量化学习backtrader\数据-bn'

# 获取文件夹中所有CSV文件的列表
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 使用 pd.concat() 合并 DataFrame
dfs = []  # 用于存储各个 DataFrame 的列表
for file in file_list:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)

    # 重命名列以确保一致性
    # 这里假设列名是数字且每个文件的列顺序是一致的
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                  'close_time', 'quote_asset_volume', 'number_of_trades',
                  'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']

    # 选择需要的列
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

    # 将时间戳转换为可读的日期格式，假设时间戳是毫秒单位
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 将 'timestamp' 列重命名为 'datetime'
    df.rename(columns={'timestamp': 'datetime'}, inplace=True)

    dfs.append(df)

# 检查是否至少有一个 DataFrame 被添加到列表
if dfs:
    # 合并所有 DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # 获取当前工作目录的路径
    current_directory = os.getcwd()

    # 设置输出文件的名称
    output_filename = 'ETHUSDT-1M-2022-2023.csv'

    # 将当前目录的路径与文件名结合起来，创建输出文件的完整路径
    output_file = os.path.join(current_directory, output_filename)

    # 其他的代码...

    # 导出为CSV
    combined_df.to_csv(output_file, index=False)

    print("数据已成功导出到:", output_file)
else:
    print("没有数据可以合并。请检查文件是否包含所需的列。")
