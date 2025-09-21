import wmi
import os
import hashlib
import json

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

def get_open_ppt_files_from_cmdline():
    c = wmi.WMI()
    ppt_files = []

    for p in c.Win32_Process():
        if p.Name.lower() in ["powerpnt.exe", "wpp.exe"]:  # PowerPoint / WPS
            if p.CommandLine:
                parts = p.CommandLine.replace('"', '').split()
                for part in parts:
                    if part.lower().endswith((".ppt", ".pptx")) and os.path.exists(part):
                        ppt_files.append(part)
    return ppt_files

def calc_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 你的上传函数，这里用示例替代
def uploadPpt(file_path):
    print(f"上传: {file_path}")
    # 在这里调用你的上传逻辑
    # 返回值可以忽略或者返回上传结果

if __name__ == "__main__":
    ppt_files = get_open_ppt_files_from_cmdline()
    if not ppt_files:
        print("没有检测到打开的PPT文件")
    else:
        for file_path in ppt_files:
            file_md5 = calc_md5(file_path)
            if file_md5 in processed_md5:
                print(f"已处理过，跳过: {file_path}")
            else:
                uploadPpt(file_path)
                processed_md5.add(file_md5)
        save_md5()
        print("处理完成")
