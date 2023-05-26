import _pickle as cPickle
import gzip
import pandas as pd

def load(path):
    with gzip.open(path, 'rb', compresslevel=1) as file_object:
        raw_data = file_object.read()
    return cPickle.loads(raw_data)

data = load("ETHUSDT_20230410_1m_futures.pkl")

# 重命名列，并只保留需要的列
data = data.rename(columns={'candle_begin_time': 'datetime'})
data = data[['datetime', 'high', 'low', 'open', 'close', 'volume']]

##数据数量统计
##print(data.shape)

##数据表头格式
print(data.columns)

##数据最后5行
print(data.tail(5))


#数据起始时间
data = data[data['datetime'] > '2023-03-01']


# 改成CSV格式
data.to_csv("ETH-2023-3-1M-clean.csv", index=False)
