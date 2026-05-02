import os
import shutil
import subprocess
import threading
import time
import winsound
import sys

def run_installation(checked_apps, log_func, progress_func, complete_func):
    def run():
        time.sleep(0.1)
        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        success = 0
        total = len(checked_apps)

        for i, (exe, name) in enumerate(checked_apps, start=1):
            log_func(f"[INSTALL] Đang cài: {name} ...")
            exe_path = os.path.join(base_path, "installers", exe)

            if not os.path.exists(exe_path):
                log_func(f"[ERROR] Không tìm thấy file: {exe}")
                continue

            try:
                exe_lower = exe.lower()
                name_lower = name.lower()

                if "unikey" in exe_lower:
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    dest_path = os.path.join(desktop, exe)
                    if not os.path.exists(dest_path):
                        shutil.copy2(exe_path, desktop)
                        log_func("[SUCCESS] UniKey đã được sao chép ra Desktop.")
                        success += 1
                    else:
                        log_func("[INFO] UniKey đã tồn tại trên Desktop, bỏ qua.")

                elif "foxit" in exe_lower:
                    log_func("[INFO] Đang cài Foxit PDF Reader ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/quiet"], check=False)
                    if result.returncode == 0:
                        log_func(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                elif "office 2019" in name_lower:
                    setup_exe = exe_path
                    if os.path.exists(setup_exe):
                        log_func("[INFO] Đang cài đặt Office 2019...")
                        result = subprocess.run([setup_exe], check=False)
                        if result.returncode == 0:
                            log_func(f"[SUCCESS] Xử lý xong: {name}")
                            success += 1
                        else:
                            log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")
                    else:
                        log_func("[ERROR] Không tìm thấy Office2019ProPlus.exe.")

                elif "office 365" in name_lower:
                    setup_exe = exe_path
                    config_xml = os.path.join(base_path, "installers", "configuration-Office365-x64.xml")
                    if os.path.exists(setup_exe) and os.path.exists(config_xml):
                        log_func("[INFO] Đang cài đặt Office 365 tự động bằng ODT...")
                        result = subprocess.run([setup_exe, "/configure", config_xml], check=False)
                        if result.returncode == 0:
                            log_func(f"[SUCCESS] Xử lý xong: {name}")
                            success += 1
                        else:
                            log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")
                    else:
                        log_func("[ERROR] Không tìm thấy setup.exe hoặc configuration.xml của ODT.")

                elif "winrar" in exe_lower:
                    log_func("[INFO] Đang cài đặt WinRAR ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/S"], check=False)
                    if result.returncode == 0:
                        log_func(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                elif "zalo" in exe_lower:
                    log_func("[INFO] Đang cài đặt Zalo ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/quiet", "/S"], check=False)
                    if result.returncode == 0:
                        log_func(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                else:
                    log_func(f"[INFO] Đang cài đặt {name} ở chế độ im lặng...")
                    try:
                        result = subprocess.run([exe_path, "/silent", "/verysilent"], check=False)
                    except:
                        result = subprocess.run([exe_path], check=False)

                    if result.returncode == 0:
                        log_func(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log_func(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

            except Exception as e:
                log_func(f"[ERROR] Lỗi khi cài {name}: {e}")

            progress_func(i / total)

        winsound.MessageBeep()
        log_func(f"SUMMARY:{success}/{total}")
        log_func("Trình cài đặt đã đóng...")
        complete_func()

    threading.Thread(target=run, daemon=True).start()
