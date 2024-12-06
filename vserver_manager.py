import os
import subprocess
import sys
from netcup_webservice import NetcupWebservice


def clone_or_update_repo(repo_url, local_path):
    """
    如果目录存在且有内容，则尝试拉取最新更新。
    否则，克隆仓库到指定目录。
    """
    if os.path.exists(local_path):
        if os.listdir(local_path):  # 目录非空
            print(f"目录 {local_path} 已存在且非空，尝试更新...")
            try:
                subprocess.run(
                    ["git", "-C", local_path, "pull"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(f"更新完成: {local_path}")
            except subprocess.CalledProcessError as e:
                print(f"更新失败: {e.stderr.decode()}")
        else:  # 目录为空
            print(f"目录 {local_path} 为空，开始克隆...")
            subprocess.run(["git", "clone", repo_url, local_path], check=True)
    else:
        print(f"目录 {local_path} 不存在，开始克隆...")
        subprocess.run(["git", "clone", repo_url, local_path], check=True)


def load_credentials_from_file(config_path):
    """
    从 config.sh 文件加载 Netcup 登录凭据。
    """
    if not os.path.exists(config_path):
        print(f"配置文件 {config_path} 不存在，请手动输入登录凭据。")
        return None

    credentials = {}
    try:
        with open(config_path, "r") as f:
            for line in f.readlines():
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    credentials[key.strip()] = value.strip().strip('"')
        login_name = credentials.get("LOGIN_NAME")
        password = credentials.get("PASSWORD")
        if login_name and password:
            print("从配置文件中成功加载登录凭据。")
            return login_name, password
        else:
            print(f"配置文件 {config_path} 格式无效。")
            return None
    except Exception as e:
        print(f"读取配置文件时出错: {e}")
        return None


def prompt_for_credentials():
    """
    提示用户手动输入 Netcup 登录凭据。
    """
    print("请输入 Netcup 登录凭据（用于 API）...")
    login_name = input("登录名: ").strip()
    password = input("密码: ").strip()
    return login_name, password


def initialize_client(config_path):
    """
    初始化 Netcup 客户端：尝试从配置文件加载凭据，否则提示用户输入。
    """
    credentials = load_credentials_from_file(config_path)
    if not credentials:
        credentials = prompt_for_credentials()
    login_name, password = credentials
    return NetcupWebservice(loginname=login_name, password=password)


def display_servers(client):
    """
    显示所有服务器及其昵称。
    """
    try:
        vservers = client.get_vservers()
        print("\n服务器:")
        for server in vservers:
            nickname = server.get("vServerNickname", server["vServerName"])
            print(f"- {nickname}")
    except Exception as e:
        print(f"获取服务器列表时出错: {e}")


def get_server_details(client, nickname):
    """
    根据服务器昵称获取详细信息。
    """
    try:
        vservers = client.get_vservers()
        for server in vservers:
            if server.get("vServerNickname") == nickname or server.get("vServerName") == nickname:
                details = client.get_vserver_information(server["vServerName"])
                print(f"\n服务器 '{nickname}' 详细信息:")
                print(details)
                return
        print(f"未找到昵称或名称为 '{nickname}' 的服务器。")
    except Exception as e:
        print(f"获取服务器信息时出错: {e}")


def main():
    # 配置 GitHub 仓库信息
    REPO_URL = "https://github.com/mihneamanolache/netcup-webservice"
    LOCAL_PATH = "/root/NC_Reset"

    # 克隆或更新仓库
    clone_or_update_repo(REPO_URL, LOCAL_PATH)

    # 初始化客户端
    CONFIG_PATH = os.path.join(LOCAL_PATH, "config.sh")
    client = initialize_client(CONFIG_PATH)

    # 主菜单
    while True:
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
        choice = input("请选择操作：").strip()

        if choice == "1":
            display_servers(client)
        elif choice == "9":
            nickname = input("请输入服务器昵称或名称：").strip()
            get_server_details(client, nickname)
        elif choice == "10":
            print("退出程序。")
            break
        else:
            print("功能未实现或输入无效，请重新选择。")


if __name__ == "__main__":
    main()
