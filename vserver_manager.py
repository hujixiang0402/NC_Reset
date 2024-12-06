from netcup_webservice import NetcupWebservice
import sys

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

if not LOGIN_NAME or not PASSWORD:
    print("请确保 config.sh 文件中包含有效的 LOGIN_NAME 和 PASSWORD。")
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
    print("10. 退出")

def get_vserver_nickname(vserver_name):
    """获取虚拟服务器的昵称"""
    try:
        info = client.get_vserver_information(vserver_name)
        # 检查返回的对象是否有 nickname 属性
        if hasattr(info, "nickname"):
            return info.nickname  # 通过属性访问昵称
        else:
            return vserver_name  # 如果没有昵称属性，返回原始名称
    except Exception as e:
        print(f"获取昵称时出错: {e}")
        return vserver_name

def get_servers():
    """获取所有服务器并显示昵称"""
    try:
        servers = client.get_vservers()
        print("\n服务器:")
        for server in servers:
            nickname = get_vserver_nickname(server)
            print(f"- {nickname}")
    except Exception as e:
        print(f"错误: {e}")

def get_server_state(server_name):
    """获取服务器状态"""
    try:
        nickname = get_vserver_nickname(server_name)
        state = client.get_vserver_state(server_name)
        print(f"服务器 '{nickname}' 的状态: {state}")
    except Exception as e:
        print(f"错误: {e}")

def start_server(server_name):
    """启动服务器"""
    try:
        nickname = get_vserver_nickname(server_name)
        client.start_vserver(server_name)
        print(f"服务器 '{nickname}' 启动成功！")
    except Exception as e:
        print(f"错误: {e}")

def stop_server(server_name):
    """停止服务器"""
    try:
        nickname = get_vserver_nickname(server_name)
        client.stop_vserver(server_name)
        print(f"服务器 '{nickname}' 停止成功！")
    except Exception as e:
        print(f"错误: {e}")

def reset_server(server_name):
    """硬重置服务器"""
    try:
        nickname = get_vserver_nickname(server_name)
        client.reset_vserver(server_name)
        print(f"服务器 '{nickname}' 已硬重置！")
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
        nickname = get_vserver_nickname(server_name)
        traffic = client.get_vserver_traffic_of_day(server_name)
        print(f"服务器 '{nickname}' 当日流量: {traffic}")
    except Exception as e:
        print(f"错误: {e}")

def get_server_information(server_name):
    """获取服务器详细信息"""
    try:
        nickname = get_vserver_nickname(server_name)
        info = client.get_vserver_information(server_name)
        print(f"服务器 '{nickname}' 详细信息:")
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
    while True:
        print_menu()
        choice = input("请选择操作：")
        
        if choice == "1":
            get_servers()
        
        elif choice == "2":
            server_name = input("请输入服务器名称：")
            get_server_state(server_name)
        
        elif choice == "3":
            server_name = input("请输入服务器名称：")
            start_server(server_name)
        
        elif choice == "4":
            server_name = input("请输入服务器名称：")
            stop_server(server_name)
        
        elif choice == "5":
            server_name = input("请输入服务器名称：")
            reset_server(server_name)
        
        elif choice == "6":
            server_name = input("请输入服务器名称：")
            get_server_traffic(server_name)
        
        elif choice == "7":
            server_name = input("请输入服务器名称：")
            new_nickname = input("请输入新的昵称：")
            change_server_nickname(server_name, new_nickname)
        
        elif choice == "8":
            new_password = input("请输入新的密码：")
            change_user_password(new_password)
        
        elif choice == "9":
            server_name = input("请输入服务器名称：")
            get_server_information(server_name)
        
        elif choice == "10":
            print("退出程序...")
            sys.exit(0)
        
        else:
            print("无效选择，请重新选择。")

if __name__ == "__main__":
    main()
