# 全局配置

# 交易所配置
EXCHANGE_CONFIG = {
    'name': 'binance',
    'api_key': '',  # 填入API密钥
    'api_secret': '',  # 填入API密钥
    'test_mode': True  # 测试模式
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
