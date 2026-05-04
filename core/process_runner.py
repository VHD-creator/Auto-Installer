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
            log_func({"status": "INSTALL", "msg": f"Đang cài: {name} ..."})
            exe_path = os.path.join(base_path, "installers", exe)

            if not os.path.exists(exe_path):
                log_func({"status": "ERROR", "msg": f"Không tìm thấy file: {exe}"})
                continue

            try:
                exe_lower = exe.lower()
                name_lower = name.lower()
                
                result = None

                if "unikey" in exe_lower:
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    dest_path = os.path.join(desktop, exe)
                    if not os.path.exists(dest_path):
                        shutil.copy2(exe_path, desktop)
                        log_func({"status": "SUCCESS", "msg": "UniKey đã được sao chép ra Desktop."})
                        success += 1
                    else:
                        log_func({"status": "INFO", "msg": "UniKey đã tồn tại trên Desktop, bỏ qua."})
                    continue # Bỏ qua các bước dưới vì UniKey là dạng copy

                elif "foxit" in exe_lower:
                    log_func({"status": "INFO", "msg": "Đang cài Foxit PDF Reader ở chế độ im lặng..."})
                    result = subprocess.run([exe_path, "/quiet"], check=False)
                elif "office 2019" in name_lower:
                    if os.path.exists(exe_path):
                        log_func({"status": "INFO", "msg": "Đang cài đặt Office 2019..."})
                        result = subprocess.run([exe_path], check=False)
                    else:
                        log_func({"status": "ERROR", "msg": "Không tìm thấy file cài Office 2019."})
                elif "office 365" in name_lower:
                    config_xml = os.path.join(base_path, "installers", "configuration-Office365-x64.xml")
                    if os.path.exists(exe_path) and os.path.exists(config_xml):
                        log_func({"status": "INFO", "msg": "Đang cài đặt Office 365 tự động bằng ODT..."})
                        result = subprocess.run([exe_path, "/configure", config_xml], check=False)
                    else:
                        log_func({"status": "ERROR", "msg": "Thiếu setup.exe hoặc file .xml của Office 365."})
                elif "winrar" in exe_lower:
                    log_func({"status": "INFO", "msg": "Đang cài đặt WinRAR ở chế độ im lặng..."})
                    result = subprocess.run([exe_path, "/S"], check=False)
                elif exe_lower.endswith('.cmd') or exe_lower.endswith('.bat'):
                    log_func({"status": "INFO", "msg": f"Đang chạy script {name}..."})
                    result = subprocess.run(f'start /wait "" "{exe_path}"', shell=True, cwd=os.path.dirname(exe_path))
                elif exe_lower.endswith('.iso'):
                    log_func({"status": "INFO", "msg": f"Đang mount file ISO và cài đặt {name}..."})
                    ps_mount = f'$Image = Mount-DiskImage -ImagePath "{exe_path}" -PassThru; ($Image | Get-Volume).DriveLetter'
                    mount_proc = subprocess.run(["powershell", "-Command", ps_mount], capture_output=True, text=True, shell=True)
                    drive_letter = mount_proc.stdout.strip()
                    
                    if drive_letter:
                        drive_path = f"{drive_letter}:\\"
                        target_exe = None
                        for exe_name in ["setup.exe", "install.exe", "autorun.exe"]:
                            if os.path.exists(os.path.join(drive_path, exe_name)):
                                target_exe = os.path.join(drive_path, exe_name)
                                break
                        
                        if not target_exe:
                            for file in os.listdir(drive_path):
                                if file.lower().endswith('.exe'):
                                    target_exe = os.path.join(drive_path, file)
                                    break
                        
                        if target_exe:
                            log_func({"status": "INFO", "msg": f"Đang chạy {os.path.basename(target_exe)} (Vui lòng tự đóng đĩa ảo ISO sau khi cài xong)..."})
                            result = subprocess.run([target_exe], check=False)
                        else:
                            log_func({"status": "ERROR", "msg": f"Không tìm thấy file .exe trong ISO {name}."})
                            result = subprocess.CompletedProcess(args=[], returncode=1)
                        
                        # Không tự động unmount ISO theo yêu cầu của user
                    else:
                        log_func({"status": "ERROR", "msg": f"Không thể mount file ISO {name}."})
                        result = subprocess.CompletedProcess(args=[], returncode=1)
                else:
                    log_func({"status": "INFO", "msg": f"Đang cài đặt {name}..."})
                    try:
                        result = subprocess.run(
                            [
                                exe_path,
                                "/silent", "/verysilent", "/S", "/quiet", "/qn", "/s", "/NORESTART", "/SUPPRESSMSGBOXES",
                                "-s", "/passive", "--silent", "--quiet", "-silent", "-quiet", "--unattended",
                                "/extract", "--mode=silent"
                            ],
                            check=False,
                            cwd=os.path.dirname(exe_path)
                        )
                    except:
                        result = subprocess.run([exe_path], check=False, cwd=os.path.dirname(exe_path))

                # Kiểm tra kết quả sau khi cài đặt
                if result:
                    if result.returncode == 0:
                        log_func({"status": "SUCCESS", "msg": f"Xử lý xong: {name}"})
                        success += 1
                    elif result.returncode in [1602, 1223, 1]: # Các mã phổ biến khi người dùng bấm Hủy
                        log_func({"status": "ABORTED", "msg": f"Người dùng đã ngắt cài đặt: {name}"})
                    else:
                        log_func({"status": "ERROR", "msg": f"Cài đặt {name} thất bại (Mã lỗi: {result.returncode})"})

            except Exception as e:
                log_func({"status": "ERROR", "msg": f"Lỗi khi cài {name}: {e}"})

            progress_func(i / total)

        winsound.MessageBeep()
        log_func({"status": "SUMMARY", "success": success, "total": total})
        log_func({"status": "DONE", "msg": "Trình cài đặt đã đóng..."})
        complete_func()

    threading.Thread(target=run, daemon=True).start()
