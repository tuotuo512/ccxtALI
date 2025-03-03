"""
数据层配置文件

包含数据采集、处理和存储相关的所有配置信息
"""

# 交易所配置
EXCHANGE_CONFIG = {
    'binance': {
        'apiKey': 'T780wE4qqCkGnEpoIGHA3fQJ8xqdYwPAm3fpCqqHTiCp8Hjm62RpYnTQ0FzBRa6y',
        'secret': 'lUUaFJLLA4X5vesJa1gtEpE1beeaU7CMTBgOdKq6Aawljwal7CgGFvjieRw5oN1l',
        'timeout': 20000,
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'},
    },
    'use_proxy': True,  # 是否使用代理
    'proxy_settings': {
        'http': 'http://127.0.0.1:18081',
        'https': 'http://127.0.0.1:18081',
    }
}

# 数据采集配置
DATA_CONFIG = {
    'default_symbol': 'BTC/USDT:USDT',  # 默认交易对
    'available_symbols': ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'AAVE/USDT:USDT', 'UNI/USDT:USDT'],
    'timeframes': ['1m', '3m', '5m', '15m', '30m'],  # 支持的时间周期
    'default_limit': 1000,  # 每次请求的K线数量
    'max_retries': 5,  # 最大重试次数
    'retry_delay': 10,  # 重试延迟(秒)
}

# 数据库配置
DATABASE_CONFIG = {
    'mysql': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'crypto_trading'
    },
    'mongodb': {
        'host': 'localhost',
        'port': 27017,
        'database': 'crypto_trading'
    },
    # 本地文件存储配置
    'local_storage': {
        'data_dir': 'data/market_data',  # 市场数据保存目录
    }
}