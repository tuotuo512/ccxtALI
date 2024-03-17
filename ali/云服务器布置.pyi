
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
#    cd ccxtALI/ali/buy        cd ccxtALI/ali/sell


#  更新某个文件 先删除
#    rm -rf ccxtALI    删除文件夹
#    rm getData.py    删除文件  rm SuperRsiTrend.py
#    先删除   因为 wget 通常用于下载文件或网页，而不是克隆 Git 仓库。
#    wget https://raw.githubusercontent.com/tuotuo512/ccxtALI/master/ali/buy/run.py
#    wget https://raw.githubusercontent.com/tuotuo512/ccxtALI/master/ali/buy/SuperRsiTrend.py
#    wget https://raw.githubusercontent.com/tuotuo512/ccxtALI/master/ali/buy/getData.py

#  运行
#    python3 run.py

# 新会话！回家看！
#  1、在服务器上启动一个新的 screen 会话：     screen -S 123
#  2、 在 screen 会话中运行您的脚本：  python3 run.py    python3 run_sell.py
#  3、所有会话列表   screen -ls

#  恢复会话：要恢复名为 123 的会话，可以使用以下命令：
#  4、 回家后，重新连接到会话：     screen -r 123

#  后台或者、断开会话：
#  如果您想离开会话而保持它在后台运行，可以按下 Ctrl + A，然后按下 D。这会将您的 screen 会话放到后台。

#  查看运行中的 run.py 进程
#  ps aux | grep run_sell.py
#  kill 000000

#  查看IP  curl ifconfig.me

#  更新服务器仓库  git pull origin master

#  打开编辑：
#  nano run_sell.py     nano getData.py
#  nano SuperRsiTrend_sell.py