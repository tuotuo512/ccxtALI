import pandas as pd
from exchange_settings import initialize_exchange, reconnect_exchange

exchange = initialize_exchange
def calculate_24h_volume(hourly_data):
    # 从小时数据中获取最新的24条记录（24小时）
    last_24h_data = hourly_data[-24:]
    # 计算过去24小时的成交量总和
    vol_24h = sum([x[5] for x in last_24h_data])
    return vol_24h

def calculate_recent_volume(minute_data, minutes):
    # 从分钟数据中获取最新的记录
    recent_data = minute_data[-minutes:]
    # 计算最新几分钟的成交量总和
    recent_volume = sum([x[5] for x in recent_data])
    return recent_volume

# 获取小时数据和分钟数据
hourly_data = exchange.fetch_ohlcv('ETH/USDT:USDT', '1h')
minute_data = exchange.fetch_ohlcv('ETH/USDT:USDT', '1m')

# 计算24小时总成交量
vol_24h = calculate_24h_volume(hourly_data)

# 计算最新5分钟和15分钟的成交量
vol_5m = calculate_recent_volume(minute_data, 5)
vol_15m = calculate_recent_volume(minute_data, 15)

# 计算比值
vol_ratio_5m = vol_5m / (vol_24h * 1440 / 5)
vol_ratio_15m = vol_15m / (vol_24h * 1440 / 15)

print("最新5分钟成交量与24小时平均的比值:", vol_ratio_5m)

