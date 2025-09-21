import os
import hashlib
import json
import time
import win32com.client
import core
import p2n_api
from concurrent.futures import ThreadPoolExecutor, as_completed

MD5_RECORD_FILE = "ppt_md5_record.json"

# 加载已处理的MD5
if os.path.exists(MD5_RECORD_FILE):
    with open(MD5_RECORD_FILE, "r") as f:
        processed_md5 = set(json.load(f))
else:
    processed_md5 = set()

def save_md5():
    with open(MD5_RECORD_FILE, "w") as f:
        json.dump(list(processed_md5), f, indent=2)

def get_all_open_ppt_files():
    """
    返回当前打开的 PowerPoint 所有文件路径
    """
    try:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        files = [presentation.FullName for presentation in ppt_app.Presentations]
        return files
    except Exception as e:
        print("无法连接到 PowerPoint:", e)
        return []

def calc_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def uploadPpt(file_path):
    """
    用户自定义上传函数
    """
    print(f"上传: {file_path}")
    device = p2n_api.getDevice()
    print(device)
    users = p2n_api.get_user_list(device['device_code'],device['sign'])
    print(users)
    with ThreadPoolExecutor(max_workers=20) as executor:
        # submit 所有任务，但不存回调
        futures = [executor.submit(core.uploadPpt, file_path,(t[0],t[1]),t[2]) for t in users]

        # 等待所有任务完成
        for f in futures:
            f.result()
    

if __name__ == "__main__":
    while True:
        ppt_files = get_all_open_ppt_files()
        if not ppt_files:
            print("没有检测到打开的PPT文件")
        else:
            for file_path in ppt_files:
                if not os.path.exists(file_path):
                    print(f"文件不存在，跳过: {file_path}")
                    continue
                file_md5 = calc_md5(file_path)
                if file_md5 in processed_md5:
                    print(f"已处理过，跳过: {file_path}")
                else:
                    uploadPpt(file_path)
                    processed_md5.add(file_md5)
            save_md5()
            print("处理完成")
        time.sleep(1)
