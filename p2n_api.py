import requests
import os
import json

BASE_URL = "https://p2n.loshop.com.cn"  # 你的部署地址

DEVICE_JSON = "device.json"

# ---------- 获取新设备 ----------
def getDevice():
    """
    从本地 device.json 读取设备码，如果不存在或为空则向服务器请求新设备
    返回: {"device_code": ..., "sign": ...}
    """
    # 先检查本地文件
    if os.path.exists(DEVICE_JSON):
        try:
            with open(DEVICE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "device_code" in data and "sign" in data:
                    return data
        except Exception:
            pass  # 读取失败则重新获取

    # 向服务器请求新设备
    resp = requests.get(f"{BASE_URL}/newDevice", timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # 保存到本地 JSON
    with open(DEVICE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data

def get_user_list(device_code, sign):
    """
    获取指定设备绑定的用户列表
    返回: [(username, password, user_id), ...]
    """
    params = {"device_code": device_code, "sign": sign}
    resp = requests.get(f"{BASE_URL}/getUserInfo", params=params, timeout=10)
    resp.raise_for_status()
    users = resp.json().get("users", [])
    return [(u["username"], u["password"], u["user_id"]) for u in users]

# ---------- 清空本地设备（可选） ----------
def clearDevice():
    if os.path.exists(DEVICE_JSON):
        os.remove(DEVICE_JSON)

# ---------- 绑定用户 ----------
def bind_user(username, password, device_code):
    data = {"username": username, "password": password, "device_code": device_code}
    resp = requests.post(f"{BASE_URL}/", json=data, timeout=10)
    if resp.status_code != 200:
        raise Exception(resp.text)
    return resp.text

# ---------- 查询用户绑定设备 ----------
def query_user_devices(username):
    params = {"username": username}
    resp = requests.get(f"{BASE_URL}/getUserInfoByUsername", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("devices", [])

# ---------- 删除设备绑定 ----------
def delete_device_binding(username, device_code, password):
    data = {"username": username, "device_code": device_code, "password": password}
    resp = requests.post(f"{BASE_URL}/deleteDeviceBinding", json=data, timeout=10)
    if resp.status_code != 200:
        raise Exception(resp.text)
    return resp.text

# ---------- 示例 ----------
if __name__ == "__main__":
    # 获取新设备
    device = new_device()
    print("新设备:", device)

    # 绑定用户
    try:
        res = bind_user("testuser", "123456", device["device_code"])
        print("绑定结果:", res)
    except Exception as e:
        print("绑定失败:", e)

    # 查询绑定设备
    devices = query_user_devices("testuser")
    print("绑定设备列表:", devices)

    # 删除设备绑定（需要输入正确密码）
    if devices:
        try:
            res = delete_device_binding("testuser", devices[0]["device_code"], "123456")
            print("删除结果:", res)
        except Exception as e:
            print("删除失败:", e)
