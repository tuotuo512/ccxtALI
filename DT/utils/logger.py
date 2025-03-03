# 日志工具
import logging
import os
from datetime import datetime

def setup_logger(name, log_level=logging.INFO):
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}_{name}.log")
    file_handler = logging.FileHandler(log_file)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    
    # 设置格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger