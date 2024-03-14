import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error



# 假设df是一个Pandas DataFrame，包含IDT1、IDT2、IDT3和目标列'target'
# 加载数据
df = pd.read_csv('your_data.csv')

# 划分特征和目标变量
X = df[['IDT1', 'IDT2', 'IDT3']]
y = df['target']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型训练
model = LinearRegression()
model.fit(X_train, y_train)

# 模型评估
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'Mean Squared Error: {mse}')

# 可以根据模型性能进一步调整模型参数，选择不同的模型进行测试
