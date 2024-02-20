import pandas as pd
import time
import ccxt

def initialize_exchange():
    # 创建并配置交易所实例
    exchange = ccxt.okx({
        'apiKey': 'd4f72342-a1e3-4b4d-bb6d-a0f764eaac4e',
        'secret': '43914C14D233A853A098762FC945F71E',
        'password': 'Tt123457.',  # Replace with your API passphrase
        'enableRateLimit': True,  # Enables built-in rate limit support
        'proxies': {
            'http': 'http://127.0.0.1:18081',
            'https': 'http://127.0.0.1:18081',
        }
    })
    # Specify the account type, in this case, futures
    exchange.options['defaultType'] = 'futures'
    print("交易所实例已创建")  # 确认交易所实例被成功创建
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


def fetch_and_process_market_data(exchange, historical_df=None):
    if historical_df is None or historical_df.empty:
        data = exchange.fetch_ohlcv('ETH-USDT', '1m', 1000)
        historical_df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    else:
        latest_data = exchange.fetch_ohlcv('ETH-USDT', '1m', 1)
        latest_df = pd.DataFrame(latest_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # 在添加之前移除任何重复的时间戳
        historical_df = historical_df[historical_df['timestamp'] != latest_df['timestamp'].iloc[0]]
        historical_df = pd.concat([historical_df, latest_df])

        # Keep the DataFrame size to 1000 rows
        if len(historical_df) > 1000:
            historical_df = historical_df.iloc[-1000:]

    # 将timestamp列转换为日期时间格式 下一行是换成世界时间
    # 转换timestamp列为日期时间格式
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'], unit='ms')
    historical_df.set_index('timestamp', inplace=True)
    print(historical_df)
    historical_df.index = historical_df.index.floor('1Min')

    # 数据重采样
    df_1m = historical_df.resample('1Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    print("最新的十根1分钟K线数据:\n", df_1m.tail(10))

    df_3m = historical_df.resample('3Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_5m = historical_df.resample('5Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_15m = historical_df.resample('15Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_30m = historical_df.resample('30Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_60m = historical_df.resample('60Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    return df_1m, df_3m, df_5m, df_15m, df_30m, df_60m

# 主函数
def main():
    exchange = initialize_exchange()
    if reconnect_exchange(exchange):
        df_1m, df_3m, df_5m, df_15m, df_30m, df_60m= fetch_and_process_market_data(exchange)

        # 打印1分钟K线的行数
        print(f"15分钟K线的行数: {len(df_15m)}")
        print(df_15m)

        # 打印最新一分钟的收盘价
        if not df_15m.empty:
            latest_close_price = df_15m['close'].iloc[-1]
            print(f"最新一分钟的收盘价: {latest_close_price}")
        else:
            print("没有获取到最新的1分钟K线数据")


# 运行主函数
if __name__ == '__main__':
    main()
