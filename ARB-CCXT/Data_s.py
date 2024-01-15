import websocket
import json
import pandas as pd
import datetime

try:
    import thread
except ImportError:
    import _thread as thread
import time

# 全局变量，用于存储当前10秒窗口的数据
current_10s_window = {"open": None, "high": float('-inf'), "low": float('inf'), "close": None, "volume": 0,
                      "start_time": None}
last_window_time = None


def on_message(ws, message):
    global current_10s_window, last_window_time
    message_data = json.loads(message)
    kline = message_data['k']

    # 转换时间戳为 datetime 对象
    kline_start_time = datetime.datetime.utcfromtimestamp(kline['t'] / 1000.0)

    # 检查是否新的10秒窗口
    if current_10s_window["start_time"] is None or (
            kline_start_time - current_10s_window["start_time"]).total_seconds() >= 10:
        if current_10s_window["start_time"] is not None:
            process_10s_window()  # 处理上一个10秒窗口的数据

        # 重置为新的10秒窗口
        current_10s_window = {"open": float(kline['o']), "high": float(kline['h']), "low": float(kline['l']),
                              "close": float(kline['c']), "volume": float(kline['v']), "start_time": kline_start_time}
    else:
        # 更新当前窗口的数据
        current_10s_window["high"] = max(current_10s_window["high"], float(kline['h']))
        current_10s_window["low"] = min(current_10s_window["low"], float(kline['l']))
        current_10s_window["close"] = float(kline['c'])
        current_10s_window["volume"] += float(kline['v'])


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        ws.send(json.dumps({'method': 'SUBSCRIBE', 'params': ['btcusdt@kline_1m'], 'id': 1}))
        # 保持连接
        while True:
            time.sleep(1)
        ws.close()

    thread.start_new_thread(run, ())


def process_10s_window():
    global current_10s_window
    # 这里处理10秒窗口的数据
    # 您可以将数据添加到 DataFrame 或执行其他逻辑
    print("Processed 10s window:", current_10s_window)


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@kline_1m",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
