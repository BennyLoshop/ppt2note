import tkinter as tk
from tkinter import font
import subprocess
import os
import psutil
import threading
import time
import p2n_api

def get_device_code():
    """调用 p2n_api.getDevice() 获取设备信息"""
    try:
        info = p2n_api.getDevice()
        return info.get("device_code", "未知")
    except Exception as e:
        print("获取设备信息失败:", e)
        return "未知"

def is_process_running(exe_name):
    """检测指定进程是否在运行"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def run_process_if_not_running(exe_path):
    """如果指定 exe 没有运行，则启动"""
    exe_name = os.path.basename(exe_path)
    if not is_process_running(exe_name):
        try:
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        except Exception as e:
            print(f"启动 {exe_name} 失败:", e)

def monitor_p2nd():
    """后台线程监控 p2nd.exe"""
    exe_path = os.path.join(os.getcwd(), "p2nd.exe")
    while True:
        run_process_if_not_running(exe_path)
        time.sleep(5)  # 每 5 秒检查一次

# ---------- Tkinter 界面 ----------
root = tk.Tk()
root.title("P2N 设备状态")
root.geometry("600x300")
root.resizable(False, False)

device_code = get_device_code()

# 大字体显示 device_code
f = font.Font(root, family='Helvetica', size=48, weight='bold')
lbl_device = tk.Label(root, text=device_code, font=f, fg="blue")
lbl_device.pack(pady=40)

# 提示绑定用户
lbl_hint = tk.Label(root, text="绑定用户: https://p2n.loshop.com.cn/", font=('Arial', 16))
lbl_hint.pack()

# ---------- 启动后台线程 ----------
t = threading.Thread(target=monitor_p2nd, daemon=True)
t.start()

root.mainloop()
