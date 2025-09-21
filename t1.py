import json
import os
import requests
from pathlib import Path

# ========== 配置 ==========
json_file = "resources.json"           # 输入 JSON 文件
download_root = Path("D:/d")           # 下载保存的根目录（建议放磁盘根目录缩短路径）

# ========== 工具函数 ==========
def to_long_path(path: Path) -> str:
    """
    Windows 下加上 \\?\ 前缀支持长路径
    其他平台直接返回字符串
    """
    p = str(path.resolve())
    if os.name == "nt":  # Windows
        return r"\\?\{}".format(p)
    return p

# ========== 下载函数 ==========
def download_file(url, save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        with open(to_long_path(save_path), "wb") as f:   # 使用长路径写文件
            f.write(resp.content)
        print(f"✅ 下载成功: {save_path}")
    except Exception as e:
        print(f"❌ 下载失败: {save_path} | 错误: {e}")

# ========== 主逻辑 ==========
def main():
    # 读取 JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    resource_list = data.get("resourceList", [])

    # 遍历下载
    for res in resource_list:
        file_id_path = res["id"]   # 原始路径（带目录层级）
        url = res["ossImageUrl"]

        # 拼接本地路径
        local_path = download_root / file_id_path.lstrip("/")  # 去掉开头的 /

        # 下载文件
        download_file(url, local_path)

    print("全部下载完成 ✅")

if __name__ == "__main__":
    main()
