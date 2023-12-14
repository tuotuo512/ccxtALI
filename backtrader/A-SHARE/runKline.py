import baostock as bs
import pandas as pd
import mplfinance as mpf

# 第一部分：建立股票池
stock_pool = ["sh.600519", "sz.000001"]  # 示例股票代码，注意baostock使用的是这种格式


def add_stock(code):
    if code not in stock_pool:
        stock_pool.append(code)


# 第二部分：使用Baostock获取K线数据
def get_kline_data(code):
    bs.login()  # 登录baostock
    rs = bs.query_history_k_data_plus(
        code,
        "date,time,open,high,low,close,volume",
        start_date='2023-01-01', end_date='2023-12-10',
        frequency="5", adjustflag="3"  # 设置为5分钟频率
    )
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    bs.logout()
    result = pd.DataFrame(data_list, columns=rs.fields)
    if result.empty:
        print("No data returned from get_kline_data")
        return None
    return result


# 第三部分：数据清理

# 第三部分：数据清理
def clean_data(df):
    if df is None or df.empty:
        print("DataFrame is empty or None in clean_data")
        return df
    # 转换时间格式
    df['time'] = df['time'].str.slice(0, 2) + ':' + df['time'].str.slice(2, 4) + ':' + df['time'].str.slice(4, 6)
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])  # 合并日期和时间列
    df.set_index('datetime', inplace=True)
    df.drop(['date', 'time'], axis=1, inplace=True)
    df.fillna(method='ffill', inplace=True)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    return df


# 第四部分：修改成符合backtrader格式

def prepare_for_backtrader(df):
    df_reset = df.reset_index()
    df_reset.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_reset['datetime'] = df_reset['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')  # 格式化日期时间
    return df_reset[['datetime', 'open', 'high', 'low', 'close', 'volume']]


# 第5部分：保存的K线数据
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)


# 示例使用
df = get_kline_data(stock_pool[0])  # 获取K线数据
df_clean = clean_data(df)  # 数据清理
df_backtrader = prepare_for_backtrader(df_clean)  # 准备Backtrader格式的数据
save_to_csv(df_backtrader, 'backtrader_data.csv')  # 保存为CSV


# 第五部分：绘制K线图
def plot_kline(df, start_date=None, end_date=None):
    if df is None or df.empty:
        print("DataFrame is empty or None in plot_kline")
        return

    # 如果提供了日期范围，只绘制该范围内的数据
    if start_date is not None and end_date is not None:
        df = df[start_date:end_date]

    mpf.plot(df, type='candle', mav=(3, 6, 9), volume=True)


# 示例使用
add_stock("sh.600519")  # 添加新股票
df = get_kline_data(stock_pool[0])  # 获取5分钟K线数据
df_clean = clean_data(df)  # 数据清理

# 指定绘图的时间范围
plot_kline(df_clean, '2023-12-01', '2023-12-10')
