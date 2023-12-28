# 引入交易所设置
from exchange_settings import initialize_exchange, reconnect_exchange

import pandas as pd

import websocket
import json
import threading
import sys  # 导入 sys 模块

# 确保 historical_df 是全局变量
global historical_df

# 步骤 1: 获取历史 K 线数据 (get_data)
def get_data(exchange):
    # 获取最新的1000根1分钟K线数据
    data = exchange.fetch_ohlcv('ARB/USDT:USDT', '1m', limit=100)
    # 转换数据到pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # 将timestamp列转换为日期时间格式
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # 设置timestamp列为索引
    df.set_index('timestamp', inplace=True)
    return df


# 步骤 2： WebSocket 实时数据获取函数；并将这些实时数据添加到 historical_df 中
def websocket_kline(symbol, interval, df):
    ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"

    def on_message(ws, message):
        message_data = json.loads(message)
        kline = message_data['k']
        # 添加新的 K 线数据到 DataFrame
        new_row = {
            'timestamp': pd.to_datetime(kline['t'], unit='ms'),
            'open': kline['o'],
            'high': kline['h'],
            'low': kline['l'],
            'close': kline['c'],
            'volume': kline['v']
        }
        df.loc[new_row['timestamp']] = [new_row['open'], new_row['high'], new_row['low'], new_row['close'],
                                        new_row['volume']]
        print("New data received and added to DataFrame")

    def on_open(ws):
        print("Opened connection to WebSocket")

    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
    ws.run_forever()


# 生成不同时间间隔的聚合数据
def aggregate_data(df):
    df_1m = df.resample('1Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_3m = df.resample('3Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_5m = df.resample('5Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_15m = df.resample('15Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    df_30m = df.resample('30Min').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    return df_1m, df_3m, df_5m, df_15m, df_30m


# 主函数中的调用
# import mplfinance as mpf

# 主函数中的调用
if __name__ == '__main__':
    exchange = initialize_exchange()
    if not reconnect_exchange(exchange):
        print("无法连接到交易所")
        sys.exit()  # 使用 sys.exit() 来退出程序

    historical_df = get_data(exchange)
    df_1m, df_3m, df_5m, df_15m, df_30m = aggregate_data(historical_df)

    # 使用线程运行 WebSocket 客户端
    threading.Thread(target=websocket_kline, args=("ARB/USDT:USDT", "1m", historical_df)).start()

    # # 使用 mplfinance 绘制 K 线图
    # mpf.plot(df_1m, type='candle', style='charles',
    #          title='1 Minute OHLC Candlestick Chart',
    #          ylabel='Price (USDT)')
    #
    # # 其他分析或可视化代码...
