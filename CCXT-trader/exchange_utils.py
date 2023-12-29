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
        except Exception as e:
            print("重新连接交易所失败:", str(e))
            retry_count += 1
            time.sleep(120)
    print("无法重新连接交易所，达到最大重试次数")
    return False


def fetch_and_process_market_data(exchange):
    data = exchange.fetch_ohlcv('ETH/USDT:USDT', '1m', limit=500)


    # 暂停一段时间，比如1分钟
    time.sleep(10)

    # 转换数据到pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # 将timestamp列转换为日期时间格式 下一行是换成世界时间
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df['timestamp'] = df['timestamp'].dt.tz_localize('Asia/Shanghai').dt.tz_convert('UTC')

    # 设置timestamp列为索引
    df.set_index('timestamp', inplace=True)

    df.index = df.index.floor('1min')
    df_5m = df.resample('1min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 将df_5m保存到CSV文件中,查看缺失和对错
    # df_5m.to_csv('df_5m.csv')

    # 生成15分钟数据
    df_15m = df.resample('3Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成30分钟数据
    df_30m = df.resample('5Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成60分钟数据
    df_1h = df.resample('15Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # 生成240分钟数据
    df_4h = df.resample('30Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    return df_15m, df_30m, df_1h, df_4h

# # 主函数  （测试）
# def main():
#     exchange = initialize_exchange()
#     if reconnect_exchange(exchange):
#         df_15m, df_30m, df_1h, df_4h = fetch_and_process_market_data(exchange)
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
