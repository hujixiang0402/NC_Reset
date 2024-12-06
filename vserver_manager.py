from netcup_webservice import NetcupWebservice
import sys
import time
import requests


def load_config():
    """从 config.sh 文件加载配置"""
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


# 从 config.sh 文件加载凭据
config = load_config()
LOGIN_NAME = config.get("LOGIN_NAME")
PASSWORD = config.get("PASSWORD")
QB_PORT = config.get("QB_PORT")
QB_USERNAME = config.get("QB_USERNAME")
QB_PASSWORD = config.get("QB_PASSWORD")

# 检查是否成功加载凭据
if not LOGIN_NAME or not PASSWORD:
    print("请确保 config.sh 文件中包含有效的 LOGIN_NAME 和 PASSWORD。")
    sys.exit(1)

# 初始化 Netcup 客户端
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
                nickname = getattr(info, 'vServerNickname', server)
                ipv4 = getattr(info, 'ipv4', None)
                mapping[nickname] = {"name": server, "ipv4": ipv4}
            except Exception:
                mapping[server] = {"name": server, "ipv4": None}
    except Exception as e:
        print(f"获取服务器信息时出错: {e}")
    return mapping


def get_server_by_nickname(nickname, mapping):
    """根据昵称获取服务器信息"""
    return mapping.get(nickname, None)


def get_servers(mapping):
    """获取所有服务器并显示昵称"""
    print("\n服务器:")
    for nickname, details in mapping.items():
        print(f"- {nickname} (IP: {details['ipv4']})")


def get_server_state(server_name):
    """获取服务器状态"""
    try:
        state = client.get_vserver_state(server_name)
        print(f"服务器 '{server_name}' 的状态: {state}")
    except Exception as e:
        print(f"错误: {e}")


def start_server(server_name):
    """启动服务器"""
    try:
        client.start_vserver(server_name)
        print(f"服务器 '{server_name}' 启动成功！")
    except Exception as e:
        print(f"错误: {e}")


def stop_server(server_name):
    """停止服务器"""
    try:
        client.stop_vserver(server_name)
        print(f"服务器 '{server_name}' 停止成功！")
    except Exception as e:
        print(f"错误: {e}")


def reset_server(server_name):
    """硬重置服务器"""
    try:
        client.reset_vserver(server_name)
        print(f"服务器 '{server_name}' 已硬重置！")
    except Exception as e:
        print(f"错误: {e}")


def change_user_password(new_password):
    """更改用户密码"""
    try:
        client.change_user_password(new_password)
        print("用户密码已更改！")
    except Exception as e:
        print(f"错误: {e}")


def get_server_traffic(server_name):
    """获取服务器流量统计"""
    try:
        traffic = client.get_vserver_traffic_of_day(server_name)
        print(f"服务器 '{server_name}' 当日流量: {traffic}")
    except Exception as e:
        print(f"错误: {e}")


def get_server_information(server_name):
    """获取服务器详细信息"""
    try:
        info = client.get_vserver_information(server_name)
        print(f"服务器 '{server_name}' 详细信息:")
        print(info)
    except Exception as e:
        print(f"错误: {e}")


def change_server_nickname(server_name, new_nickname):
    """修改服务器昵称"""
    try:
        client.set_vserver_nickname(server_name, new_nickname)
        print(f"服务器 '{server_name}' 昵称已更改为 '{new_nickname}'！")
    except Exception as e:
        print(f"错误: {e}")


def qb_login(ip, port, username, password):
    """登录 QBittorrent Web API"""
    try:
        session = requests.Session()
        url = f"http://{ip}:{port}/api/v2/auth/login"
        response = session.post(url, data={"username": username, "password": password})
        if response.text == "Ok.":
            print(f"成功登录 QBittorrent ({ip}:{port})")
            return session
        else:
            print("登录 QBittorrent 失败，请检查用户名和密码。")
            return None
    except Exception as e:
        print(f"连接 QBittorrent 失败: {e}")
        return None


def qb_pause_all(session, ip, port):
    """暂停所有种子"""
    try:
        url = f"http://{ip}:{port}/api/v2/torrents/pause"
        response = session.post(url)
        if response.status_code == 200:
            print("所有种子已暂停。")
        else:
            print("暂停种子失败，请检查 QBittorrent 状态。")
    except Exception as e:
        print(f"暂停种子时发生错误: {e}")


def qb_resume_all(session, ip, port):
    """恢复所有种子"""
    try:
        url = f"http://{ip}:{port}/api/v2/torrents/resume"
        response = session.post(url)
        if response.status_code == 200:
            print("所有种子已恢复。")
        else:
            print("恢复种子失败，请检查 QBittorrent 状态。")
    except Exception as e:
        print(f"恢复种子时发生错误: {e}")


def reset_server_with_qb(server_name, server_ip, qb_config):
    """通过 QBittorrent 暂停种子后重启服务器并恢复种子"""
    qb_port = qb_config["QB_PORT"]
    qb_username = qb_config["QB_USERNAME"]
    qb_password = qb_config["QB_PASSWORD"]

    # 登录 QBittorrent
    qb_session = qb_login(server_ip, qb_port, qb_username, qb_password)
    if not qb_session:
        print("无法连接到 QBittorrent，终止操作。")
        return

    # 暂停所有种子
    qb_pause_all(qb_session, server_ip, qb_port)

    # 等待 1 分钟
    print("等待 1 分钟...")
    time.sleep(60)

    # 重启服务器
    try:
        client.reset_vserver(server_name)
        print(f"服务器 '{server_name}' 已硬重启。")
    except Exception as e:
        print(f"重启服务器时发生错误: {e}")
        return

    # 等待服务器重启完成
    print("等待服务器重启完成...")
    time.sleep(60)

    # 恢复所有种子
    qb_resume_all(qb_session, server_ip, qb_port)


def main():
    """主程序"""
    server_mapping = fetch_server_mapping()

    while True:
        print_menu()
        choice = input("请选择操作：")

        if choice == "1":
            get_servers(server_mapping)

        elif choice == "2":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                get_server_state(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "3":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                start_server(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "4":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                stop_server(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "5":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                reset_server(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "6":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                get_server_traffic(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "7":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                new_nickname = input("请输入新的昵称：")
                change_server_nickname(server["name"], new_nickname)
                server_mapping = fetch_server_mapping()  # 更新映射
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "8":
            new_password = input("请输入新的密码：")
            change_user_password(new_password)

        elif choice == "9":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                get_server_information(server["name"])
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "10":
            nickname = input("请输入服务器昵称：")
            server = get_server_by_nickname(nickname, server_mapping)
            if server:
                reset_server_with_qb(server["name"], server["ipv4"], config)
            else:
                print(f"服务器 '{nickname}' 未找到。")

        elif choice == "11":
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")

if __name__ == "__main__":
    main()
