import os
from netcup_webservice import NetcupWebservice
import sys
import subprocess


def load_config_from_file(file_path):
    """从指定路径加载 Netcup 凭据"""
    config = {}
    try:
        with open(file_path, "r") as f:
            for line in f.readlines():
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip().strip('"')
        return config
    except Exception as e:
        print(f"无法加载配置文件: {e}")
        return None


def clone_or_update_repo(repo_url, local_path):
    """克隆或更新 GitHub 仓库"""
    try:
        if os.path.exists(local_path):
            print("检测到本地目录存在，尝试拉取更新...")
            subprocess.run(["git", "-C", local_path, "pull"], check=True)
        else:
            print("本地目录不存在，开始克隆仓库...")
            subprocess.run(["git", "clone", repo_url, local_path], check=True)
        print("仓库同步完成！")
    except subprocess.CalledProcessError as e:
        print(f"仓库同步失败: {e}")


# GitHub 仓库相关信息
REPO_URL = "https://github.com/your_username/NC_Reset.git"
LOCAL_REPO_PATH = "/root/NC_Reset"

# 确保 GitHub 仓库已同步
clone_or_update_repo(REPO_URL, LOCAL_REPO_PATH)

# 优先从配置文件加载凭据
config_file_path = os.path.join(LOCAL_REPO_PATH, "config.sh")
config = load_config_from_file(config_file_path)

if config and "LOGIN_NAME" in config and "PASSWORD" in config:
    LOGIN_NAME = config["LOGIN_NAME"]
    PASSWORD = config["PASSWORD"]
    print(f"从配置文件加载凭据成功！\n登录名: {LOGIN_NAME}")
else:
    print("未找到配置文件或文件无效，请手动输入凭据。")
    LOGIN_NAME = input("登录名: ").strip()
    PASSWORD = input("密码: ").strip()

# 检查是否成功加载凭据
if not LOGIN_NAME or not PASSWORD:
    print("未提供有效的 LOGIN_NAME 和 PASSWORD。退出程序...")
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
    print("6. 获取服务器流量")
    print("7. 修改服务器昵称")
    print("8. 更改用户密码")
    print("9. 查看服务器信息")
    print("10. 退出")


# 以下为其他功能代码，与原功能逻辑相同


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
            print("退出程序...")
            sys.exit(0)

        else:
            print("无效选择，请重新选择。")


if __name__ == "__main__":
    main()
