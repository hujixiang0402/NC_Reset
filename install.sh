import sys
import time
import requests
from netcup_webservice import NetcupWebservice

# 从 config.txt 文件读取配置
def load_config():
    """从 config.txt 文件加载配置信息"""
    config = {}
    try:
        with open("/root/NC_Reset/config.txt", "r") as f:
            for line in f.readlines():
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip().strip('"')
                elif "|" in line:
                    server_name, ip_address = line.strip().split("|", 1)
                    config[server_name.strip()] = ip_address.strip()
        return config
    except Exception as e:
        print(f"无法加载配置文件: {e}")
        sys.exit(1)

# 从 config.txt 文件加载配置信息
config = load_config()

# 获取 qBittorrent 配置信息
qb_username = config.get("USERNAME")
qb_password = config.get("PASSWORD")
qb_port = config.get("PORT")

# 获取服务器 IP 地址
server_ips = {k: v for k, v in config.items() if k.startswith('ngb-')}

# 检查是否加载了 qBittorrent 配置信息
if not qb_username or not qb_password or not qb_port:
    print("请确保 config.txt 文件中包含有效的 qBittorrent 配置信息。")
    sys.exit(1)

# 检查是否加载了服务器 IP 地址
if not server_ips:
    print("请确保 config.txt 文件中包含有效的服务器 IP 地址。")
    sys.exit(1)

# 初始化 Netcup 客户端（需要读取 API 凭据）
LOGIN_NAME = config.get("LOGIN_NAME")
PASSWORD = config.get("PASSWORD")
if not LOGIN_NAME or not PASSWORD:
    print("请确保 config.txt 文件中包含有效的 Netcup 登录凭据。")
    sys.exit(1)

client = NetcupWebservice(loginname=LOGIN_NAME, password=PASSWORD)

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

def get_server_by_nickname(nickname, mapping):
    """根据昵称获取服务器名称"""
    return mapping.get(nickname, None)

def pause_qbittorrent():
    """暂停 qBittorrent 中的所有种子"""
    url = f"http://{qb_username}:{qb_password}@localhost:{qb_port}/api/v2/torrents/pause"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("所有种子已暂停。")
        else:
            print(f"暂停种子失败: {response.status_code}")
    except Exception as e:
        print(f"无法暂停 qBittorrent 种子: {e}")

def resume_qbittorrent():
    """恢复 qBittorrent 中的所有种子"""
    url = f"http://{qb_username}:{qb_password}@localhost:{qb_port}/api/v2/torrents/resume"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("所有种子已恢复。")
        else:
            print(f"恢复种子失败: {response.status_code}")
    except Exception as e:
        print(f"无法恢复 qBittorrent 种子: {e}")

def reset_server(server_name):
    """硬重置服务器"""
    try:
        client.reset_vserver(server_name)
        print(f"服务器 '{server_name}' 已硬重置！")
    except Exception as e:
        print(f"错误: {e}")

def nc_hard_reboot(server_name):
    """执行 NC 一键硬重启操作"""
    print(f"准备暂停 qBittorrent 中的所有种子...")
    pause_qbittorrent()
    print("等待 1 分钟以确保 qBittorrent 中的所有种子暂停...")
    time.sleep(60)  # 等待一分钟
    print(f"准备重启服务器 '{server_name}'...")
    reset_server(server_name)
    print("等待 1 分钟以确保服务器重启完成...")
    time.sleep(60)  # 等待一分钟
    print("恢复 qBittorrent 中的所有种子...")
    resume_qbittorrent()

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

        elif choice == "10":
            server_name = input("请输入要重启的服务器昵称：")
            server_name = get_server_by_nickname(server_name, server_mapping)
            if server_name:
                nc_hard_reboot(server_name)
            else:
                print(f"服务器 '{server_name}' 未找到。")

        elif choice == "11":
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")


if __name__ == "__main__":
    main()
