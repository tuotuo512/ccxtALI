#下载 git
#sudo apt-get update
#sudo apt-get install git

#git仓库
#   git clone https://github.com/tuotuo512/ccxtALI.git


#Ubuntu/Debian 系统 Python 3.10 。
#使用 Deadsnakes PPA 安装（推荐）  首先，安装必要的软件来添加新的 PPA：
#   sudo apt-get update
#   sudo apt-get install -y software-properties-common

# 添加 Deadsnakes PPA：
#   sudo add-apt-repository ppa:deadsnakes/ppa

#  更新包列表并安装 Python 3.10：
#   sudo apt-get update
#  sudo apt-get install -y python3.10


# 打开文件夹路径
#    cd ccxtALI/AI-CCXT/ali

#  更新某个文件 先删除
#    rm getData.py


#    wget https://github.com/tuotuo512/ccxtALI.git
#    python3 run_ali.py

#   查看IP  curl ifconfig.me

#  更新服务器仓库  git pull origin master


# 策略组合：=================
# X*震荡  + Y*趋势

# 参数比例 ：时间、 震荡参数、 看涨参数  、预期价格比率、日K站稳？


# 仓位策略===================
# 目前单一


# 策略逻辑=====================
# 指标-----------------
# 1.成交量放大，抓大跌 反转
# 2.super 抓趋势
# 3.RSI背离 底部进场，回归离场背离减仓

# 支撑 123
# 阻力 123
# 进场
# 离场


# 1-抄底策略-----------------------
# 策略1 ：如果抄底，偏离+超卖+秒级反转
# 策略2 ： 支撑跌破，触发止损，成交量暴涨

# 2-震荡策略-----------------------
# 策略1 ：偏离 +反转
