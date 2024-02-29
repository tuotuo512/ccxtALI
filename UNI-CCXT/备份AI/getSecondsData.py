import websocket
import json
import datetime
import pandas as pd

# 初始化一个空的 DataFrame，用于存储 K 线数据
columns = ['timestamp', 'open', 'high', 'low', 'close']
kline_data = pd.DataFrame(columns=columns)

# 当前 K 线的开始时间
start_time = None

# 处理收到的消息
def on_message(ws, message):
    print("Received Message:", message)  # 打印接收到的消息
    global kline_data, start_time
    current_time = datetime.datetime.utcnow()  # 使用协调世界时


    # 解析消息
    data = json.loads(message)
    price = float(data['p'])

    # 判断是否新的 10 秒周期
    if start_time is None or (current_time - start_time).seconds >= 10:
        # 保存前一个周期的 K 线数据
        if not kline_data.empty:
            print("10 second Kline:", kline_data.iloc[-1])

        # 重置 K 线数据
        kline_data = pd.DataFrame(columns=columns)
        kline_data.loc[0] = [current_time, price, price, price, price]
        start_time = current_time
    else:
        # 更新 K 线数据
        kline_data.at[0, 'high'] = max(kline_data.at[0, 'high'], price)
        kline_data.at[0, 'low'] = min(kline_data.at[0, 'low'], price)
        kline_data.at[0, 'close'] = price

# 创建 WebSocket 连接
def on_open(ws):
    print("WebSocket Client Connected")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": ["ethusdt@trade"],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))

# 主函数
if __name__ == "__main__":
    socket = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
    ws.run_forever()
