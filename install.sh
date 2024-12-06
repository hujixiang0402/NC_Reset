#!/bin/bash

# 更新系统并安装必要的工具
echo "更新系统并安装必要的工具..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git wget

# 克隆 GitHub 仓库
echo "克隆 GitHub 仓库..."
git clone https://github.com/hujixiang0402/reset_vserver.git
cd reset_vserver

# 创建虚拟环境并激活
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

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

# 设置 Python 脚本权限
chmod +x vserver_manager.py

# 运行脚本
echo "运行 vServer 管理器..."
python vserver_manager.py

# 退出虚拟环境
deactivate
