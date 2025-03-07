# 全局配置

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

# 交易配置
TRADING_CONFIG = {
    'symbols': ['BTC/USDT', 'ETH/USDT'],
    'timeframes': ['1h', '4h', '1d'],
    'default_timeframe': '1h',
    'risk_per_trade': 0.02,  # 每笔交易风险2%
    'max_open_trades': 3
}

# 数据库配置
DB_CONFIG = {
    'mongodb': {
        'uri': 'mongodb://localhost:27017/',
        'db_name': 'crypto_trading'
    }
}


