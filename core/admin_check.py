import ctypes
import sys

# Quyền Admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Kiểm tra Single Instance
MUTEX_NAME = "Global\\AutoInstallTool_Mutex_PhamSu"

def check_single_instance():
    global mutex_handle
    kernel32 = ctypes.windll.kernel32
    mutex_handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
    
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(mutex_handle)
        return False
    return True

def enforce_single_instance():
    if not check_single_instance():
        from tkinter import messagebox
        messagebox.showwarning("Thông báo", "Ứng dụng đang chạy!\nVui lòng tắt ứng dụng trước khi khởi chạy lại.")
        sys.exit()
