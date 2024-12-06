#!/bin/bash

# 更新系统并安装必要的工具
echo "更新系统并安装必要的工具..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git wget

# 克隆 GitHub 仓库并确保获取最新更新
echo "确保获取最新的 GitHub 仓库更新..."
if [ -d "NC_Reset" ]; then
    echo "NC_Reset 目录已存在，覆盖 vserver_manager.py 和 install.sh 文件..."
    cd NC_Reset
    git pull origin main  # 拉取最新的更新
    rm -f vserver_manager.py install.sh  # 删除旧的文件
else
    git clone https://github.com/hujixiang0402/NC_Reset.git
    cd NC_Reset
fi

# 下载更新的 vserver_manager.py 和 install.sh 文件
echo "下载更新的 vserver_manager.py 和 install.sh 文件..."
wget https://raw.githubusercontent.com/hujixiang0402/NC_Reset/main/vserver_manager.py
wget https://raw.githubusercontent.com/hujixiang0402/NC_Reset/main/install.sh

# 创建虚拟环境并激活
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 手动安装 Python 依赖
echo "安装 Python 依赖..."
pip install netcup-webservice

# 检查是否存在 config.sh 文件，如果存在则从中读取登录信息
if [ -f "config.sh" ]; then
    echo "从 config.sh 文件读取登录凭据..."
    source config.sh
else
    # 提示用户输入 Netcup 登录凭据并保存为配置文件
    echo "请输入 Netcup 登录凭据（用于 API）..."
    read -p "登录名: " login_name
    read -sp "密码: " password
    echo ""
    echo "登录凭据保存中..."
    echo "LOGIN_NAME=\"$login_name\"" > config.sh
    echo "PASSWORD=\"$password\"" >> config.sh
    # 设置配置文件权限
    chmod +x config.sh
fi

# 设置 Python 脚本权限
chmod +x vserver_manager.py

# 运行脚本
echo "运行 vServer 管理器..."
python vserver_manager.py

# 退出虚拟环境
deactivate
