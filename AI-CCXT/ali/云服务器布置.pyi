
#  okx
#  API d4f72342-a1e3-4b4d-bb6d-a0f764eaac4e
#  密钥 43914C14D233A853A098762FC945F71E

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
#    cd ccxtALI/AI-CCXT/ali         cd ccxtALI/AI-CCXT/ali/sell


#  更新某个文件 先删除
#    rm getData.py
#    先删除   因为 wget 通常用于下载文件或网页，而不是克隆 Git 仓库。
#    wget https://raw.githubusercontent.com/tuotuo512/ccxtALI/master/AI-CCXT/ali/sell/run_sell.py
#    wget https://raw.githubusercontent.com/tuotuo512/ccxtALI/master/AI-CCXT/ali/sell/SuperRsiTrend_sell.py

#  运行
#    python3 run.py

# 回家看
#  1、在服务器上启动一个新的 screen 会话：     screen -S mysession
#  2、 在 screen 会话中运行您的脚本：  python3 run.py
#  3、 回家后，重新连接到会话：     screen -r mysession

#  查看运行中的 run.py 进程
#  ps aux | grep run.py
#  kill 000000

#  查看IP  curl ifconfig.me

#  更新服务器仓库  git pull origin master

#  打开编辑：
#  nano run_sell.py
#  nano SuperRsiTrend_sell.py