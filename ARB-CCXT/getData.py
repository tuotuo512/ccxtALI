# 交易所和K线数据

import os
import pandas as pd
import time
import ccxt


def initialize_exchange():
    # 创建并配置交易所实例
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'timeout': 20000,  # 设置超时时间为60秒
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'},
        'proxies': {
            'http': 'http://127.0.0.1:18081',
            'https': 'http://127.0.0.1:18081',
        }
    })
    return exchange


def reconnect_exchange(exchange):
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            exchange.load_markets()
            print("连接交易所成功")
            return True
        except ccxt.RequestTimeout as e:
            print("请求超时，正在重试...")
            retry_count += 1
            time.sleep(10)  # 等待一段时间后重试，这里设置为10秒
        except Exception as e:
            print("重新连接交易所失败:", str(e))
            retry_count += 1
            time.sleep(120)  # 对于非超时错误，等待时间设置得更长一些
    print("无法重新连接交易所，达到最大重试次数")
    return False


def fetch_and_process_market_data(exchange, historical_df=None):
    if historical_df is None or historical_df.empty:
        data = exchange.fetch_ohlcv('JUP/USDT:USDT', '1m', limit=1000)
        historical_df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    else:
        # 获取最新的一根K线
        latest_data = exchange.fetch_ohlcv('JUP/USDT:USDT', '1m', limit=1)
        latest_df = pd.DataFrame(latest_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 在添加之前移除任何重复的时间戳
        historical_df = historical_df[historical_df['timestamp'] != latest_df['timestamp'].iloc[0]]
        historical_df = pd.concat([historical_df, latest_df])

        # 保持DataFrame的大小为1000
        if len(historical_df) > 1000:
            historical_df = historical_df.iloc[-1000:]

    # 将timestamp列转换为日期时间格式 下一行是换成世界时间
    # 转换timestamp列为日期时间格式
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'], unit='ms')
    historical_df.set_index('timestamp', inplace=True)
    # print(historical_df)

    historical_df.index = historical_df.index.floor('1Min')
    # 数据重采样
    df_1m = historical_df.resample('1Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_3m = historical_df.resample('3Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_5m = historical_df.resample('5Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_15m = historical_df.resample('15Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_30m = historical_df.resample('30Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    return df_1m, df_3m, df_5m, df_15m, df_30m


# # 主函数
# def main():
#     exchange = initialize_exchange()
#     if reconnect_exchange(exchange):
#         df_1m, df_3m, df_5m, df_15m, df_30m = fetch_and_process_market_data(exchange)
#
#         # 打印1分钟K线的行数
#         print(f"15分钟K线的行数: {len(df_15m)}")
#         print(df_15m)
#
#         # 打印最新一分钟的收盘价
#         if not df_15m.empty:
#             latest_close_price = df_15m['close'].iloc[-1]
#             print(f"最新一分钟的收盘价: {latest_close_price}")
#         else:
#             print("没有获取到最新的1分钟K线数据")
#
#
# # 运行主函数
# if __name__ == '__main__':
#     main()
