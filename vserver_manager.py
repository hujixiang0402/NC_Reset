from netcup_webservice import NetcupWebservice
import sys
import datetime


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


# 从 config.sh 文件加载凭据
config = load_config()
LOGIN_NAME = config.get("LOGIN_NAME")
PASSWORD = config.get("PASSWORD")

# 检查是否成功加载凭据
if not LOGIN_NAME or not PASSWORD:
    print("请确保 config.sh 文件中包含有效的 LOGIN_NAME 和 PASSWORD。")
    sys.exit(1)

# 初始化客户端
client = NetcupWebservice(loginname=LOGIN_NAME, password=PASSWORD)


def print_menu():
    """打印功能菜单"""
    print("\n--- Netcup 服务器 管理器 ---")
    print("1. 查看所有服务器")
    print("2. 获取服务器状态")
    print("3. 启动服务器")
    print("4. 停止服务器")
    print("5. 重启服务器")
    print("6. 获取服务器月流量")  # 修改为月流量
    print("7. 修改服务器昵称")
    print("8. 更改用户密码")
    print("9. 查看服务器信息")
    print("10. 退出")


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


def get_servers(mapping):
    """获取所有服务器并显示昵称"""
    print("\n服务器:")
    for nickname, server_name in mapping.items():
        print(f"- {nickname}")


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
    """获取服务器本月流量统计"""
    try:
        # 获取当前时间并提取年份和月份
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        # 获取流量统计令牌
        token = client.get_vserver_stat_token(server_name, year, month)
        if not token:
            print(f"无法获取服务器 '{server_name}' 的流量令牌。")
            return
        
        # 使用令牌获取流量
        traffic = client.get_vserver_stat(token)
        
        print(f"服务器 '{server_name}' {year}年{month}月的流量:")
        print(traffic)  # 假设流量数据已经是我们需要的格式，可以根据实际情况调整输出格式
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
                get_server_traffic(server_name)  # 获取本月流量
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
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")


if __name__ == "__main__":
    main()
