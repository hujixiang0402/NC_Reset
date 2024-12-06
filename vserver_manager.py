import time
import requests
from netcup_webservice import NetcupWebservice
import sys

# 加载 config.sh 配置文件
def load_config():
    """从 config.sh 文件加载 Netcup 凭据"""
    config = {}
    try:
        with open("config.sh", "r") as f:
            for line in f.readlines():
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip().strip('"')
        return config
    except Exception as e:
        print(f"无法加载配置文件: {e}")
        sys.exit(1)

# 加载 config.txt 配置文件中的 qBittorrent 配置信息
def load_qbittorrent_config():
    """从 config.txt 文件加载 qBittorrent 配置信息"""
    config = {}
    try:
        with open("/root/NC_Reset/config.txt", "r") as f:
            for line in f.readlines():
                if "USERNAME" in line:
                    config["USERNAME"] = line.split("=")[1].strip()
                elif "PASSWORD" in line:
                    config["PASSWORD"] = line.split("=")[1].strip()
                elif "PORT" in line:
                    config["PORT"] = line.split("=")[1].strip()
                elif "|" in line:  # 机器名称|IP地址
                    machine, ip = line.split("|")
                    config[machine.strip()] = ip.strip()
        return config
    except Exception as e:
        print(f"无法加载 qBittorrent 配置文件: {e}")
        sys.exit(1)

# 从 config.sh 文件加载 Netcup 登录凭据
config = load_config()
LOGIN_NAME = config.get("LOGIN_NAME")
PASSWORD = config.get("PASSWORD")

# 加载 qBittorrent 配置信息
qb_config = load_qbittorrent_config()
USERNAME = qb_config["USERNAME"]
PASSWORD = qb_config["PASSWORD"]
PORT = qb_config["PORT"]

# 初始化 Netcup 客户端
client = NetcupWebservice(loginname=LOGIN_NAME, password=PASSWORD)

# 暂停所有 qBittorrent 种子
def pause_qbittorrent():
    """暂停所有 qBittorrent 种子"""
    url = f'http://{qb_config["ngb-1"]}:{PORT}/api/v2/torrents/pause'
    auth = (USERNAME, PASSWORD)
    try:
        response = requests.post(url, auth=auth)
        if response.status_code == 200:
            print("所有种子已暂停。")
        else:
            print("无法暂停种子。")
    except Exception as e:
        print(f"暂停种子时发生错误: {e}")

# 恢复所有 qBittorrent 种子
def resume_qbittorrent():
    """恢复所有 qBittorrent 种子"""
    url = f'http://{qb_config["ngb-1"]}:{PORT}/api/v2/torrents/resume'
    auth = (USERNAME, PASSWORD)
    try:
        response = requests.post(url, auth=auth)
        if response.status_code == 200:
            print("所有种子已恢复。")
        else:
            print("无法恢复种子。")
    except Exception as e:
        print(f"恢复种子时发生错误: {e}")

# 硬重置服务器
def reset_server(server_name):
    """硬重置服务器"""
    try:
        client.reset_vserver(server_name)
        print(f"服务器 '{server_name}' 已硬重置！")
    except Exception as e:
        print(f"错误: {e}")

# 获取服务器映射
def fetch_server_mapping():
    """获取服务器名称和昵称的映射"""
    mapping = {}
    try:
        servers = client.get_vservers()
        for server in servers:
            try:
                info = client.get_vserver_information(server)
                nickname = getattr(info, 'vServerNickname', server)  # 获取昵称
                mapping[nickname] = server  # 建立昵称到名称的映射
            except Exception:
                mapping[server] = server  # 如果获取失败，用名称作为映射
    except Exception as e:
        print(f"获取服务器信息时出错: {e}")
    return mapping

# 根据昵称获取服务器名称
def get_server_by_nickname(nickname, mapping):
    """根据昵称获取服务器名称"""
    return mapping.get(nickname, None)

# 打印菜单
def print_menu():
    """打印功能菜单"""
    print("\n--- Netcup 服务器 管理器 ---")
    print("1. 查看所有服务器")
    print("2. 获取服务器状态")
    print("3. 启动服务器")
    print("4. 停止服务器")
    print("5. 重启服务器")
    print("6. 获取服务器流量")
    print("7. 修改服务器昵称")
    print("8. 更改用户密码")
    print("9. 查看服务器信息")
    print("10. NC 一键硬重启")
    print("11. 退出")

# 主函数
def main():
    # 初始化服务器名称和昵称的映射
    server_mapping = fetch_server_mapping()

    while True:
        print_menu()
        choice = input("请选择操作：")

        if choice == "1":
            get_servers(server_mapping)

        elif choice == "2":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                get_server_state(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "3":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                start_server(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "4":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                stop_server(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "5":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                reset_server(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "6":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                get_server_traffic(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "7":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                new_nickname = input("请输入新的昵称：")
                change_server_nickname(server_name, new_nickname)
                server_mapping = fetch_server_mapping()  # 更新映射
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "8":
            new_password = input("请输入新的密码：")
            change_user_password(new_password)

        elif choice == "9":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                get_server_information(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "10":  # 功能序号10，NC 一键硬重启
            print("开始执行一键硬重启...")
            # 暂停所有 qBittorrent 种子
            pause_qbittorrent()
            time.sleep(60)  # 等待 1 分钟
            # 重启服务器
            nickname = input("请输入要重启的服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                reset_server(server_name)
                time.sleep(60)  # 等待服务器重启完成
                # 恢复所有 qBittorrent 种子
                resume_qbittorrent()
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "11":  # 退出程序
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")

if __name__ == "__main__":
    main()
