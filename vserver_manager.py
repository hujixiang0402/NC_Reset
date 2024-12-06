from netcup_webservice import NetcupWebservice
import sys
import requests
import time
import socket


def load_config():
    """从 config.sh 文件加载 Netcup 和 Qbittorrent 凭据"""
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


# 从 config.sh 文件加载配置
config = load_config()
LOGIN_NAME = config.get("LOGIN_NAME")
PASSWORD = config.get("PASSWORD")
QB_USERNAME = config.get("QB_USERNAME")
QB_PASSWORD = config.get("QB_PASSWORD")
QB_PORT = config.get("QB_PORT")

# 检查配置是否完整
if not LOGIN_NAME or not PASSWORD:
    print("请确保 config.sh 文件中包含有效的 LOGIN_NAME 和 PASSWORD。")
    sys.exit(1)

if not QB_USERNAME or not QB_PASSWORD or not QB_PORT:
    print("请确保 config.sh 文件中包含有效的 QB_USERNAME、QB_PASSWORD 和 QB_PORT。")
    sys.exit(1)

# 初始化客户端
client = NetcupWebservice(loginname=LOGIN_NAME, password=PASSWORD)


def get_ipv4():
    """获取服务器的本地 IPv4 地址"""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"无法获取本地 IPv4 地址: {e}")
        return None


def qb_request(api, method="GET", data=None):
    """发送请求到 Qbittorrent 的 Web API"""
    try:
        qb_ip = get_ipv4()
        if not qb_ip:
            print("无法获取本地 IPv4 地址。")
            return None

        base_url = f"http://{qb_ip}:{QB_PORT}/api/v2"
        url = f"{base_url}{api}"

        # 登录
        if api == "/auth/login":
            payload = {"username": QB_USERNAME, "password": QB_PASSWORD}
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("登录 Qbittorrent 成功！")
                return response.cookies
            else:
                print(f"登录失败，错误代码: {response.status_code}")
                return None

        # 其他请求
        cookies = qb_request("/auth/login")
        if cookies:
            if method == "GET":
                response = requests.get(url, cookies=cookies)
            else:
                response = requests.post(url, cookies=cookies, data=data)

            if response.status_code == 200:
                return response.json() if method == "GET" else response
            else:
                print(f"请求失败，错误代码: {response.status_code}")
        return None

    except Exception as e:
        print(f"与 Qbittorrent 通信时发生错误: {e}")
        return None


def pause_all_torrents():
    """暂停所有种子"""
    print("暂停 Qbittorrent 中的所有种子...")
    qb_request("/torrents/pauseAll", method="POST")


def resume_all_torrents():
    """恢复所有种子"""
    print("恢复 Qbittorrent 中的所有种子...")
    qb_request("/torrents/resumeAll", method="POST")


def nc_hard_reboot_with_qb(server_name):
    """硬重启服务器并处理 Qbittorrent 的种子"""
    try:
        # 暂停种子
        pause_all_torrents()

        # 等待 1 分钟
        print("等待 1 分钟后重启服务器...")
        time.sleep(60)

        # 硬重启服务器
        print(f"开始重启服务器 '{server_name}'...")
        reset_server(server_name)

        # 等待服务器重启完成
        print("等待服务器完成重启...")
        time.sleep(60)  # 此处为模拟等待，实际场景可考虑检查服务器状态

        # 额外等待 1 分钟
        print("服务器已重启，等待 1 分钟后恢复种子...")
        time.sleep(60)

        # 恢复种子
        resume_all_torrents()
        print("已恢复所有种子！")

    except Exception as e:
        print(f"硬重启操作失败: {e}")


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
    print("10. 退出")
    print("11. NC 一键硬重启")


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


def main():
    # 初始化服务器名称和昵称的映射
    server_mapping = fetch_server_mapping()

    while True:
        print_menu()
        choice = input("请选择操作：")

        if choice == "1":
            print("服务器:")
            for nickname, server_name in server_mapping.items():
                print(f"- {nickname}")

        elif choice == "11":
            nickname = input("请输入服务器昵称：")
            server_name = get_server_by_nickname(nickname, server_mapping)
            if server_name:
                nc_hard_reboot_with_qb(server_name)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "10":
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")


if __name__ == "__main__":
    main()
