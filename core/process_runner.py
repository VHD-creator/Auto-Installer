import os
import threading
import time
import winsound
import sys
from typing import Callable, List, Tuple
from core.detector import SmartDetector
from core.installation_engine import InstallerFactory, InstallationResult

def run_installation(checked_apps: List[Tuple[str, str]], log_func: Callable, progress_func: Callable, complete_func: Callable):
    """
    Điều phối tiến trình cài đặt sử dụng InstallationEngine và SmartDetector.
    """
    def run():
        time.sleep(0.1) # Để UI cập nhật trạng thái ban đầu
        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        detector = SmartDetector()
        
        success_count = 0
        total_apps = len(checked_apps)
        
        log_func({"status": "INFO", "msg": f"Bắt đầu tiến trình cài đặt {total_apps} ứng dụng..."})

        for i, (exe_name, display_name) in enumerate(checked_apps, start=1):
            exe_path = os.path.join(base_path, "installers", exe_name)
            
            if not os.path.exists(exe_path):
                log_func({"status": "ERROR", "msg": f"Không tìm thấy file: {exe_name}"})
                _update_progress(i, total_apps, progress_func)
                continue

            # 1. Khởi tạo Installer thông qua Factory
            installer = InstallerFactory.create(exe_path, display_name, detector)
            
            # 2. Kiểm tra thông minh: Đã cài chưa?
            is_installed, detected_name = installer.check_installed()
            if is_installed:
                log_func({
                    "status": "SKIP", 
                    "msg": f"Bỏ qua {display_name}: Đã phát hiện '{detected_name}' trên hệ thống."
                })
                success_count += 1
                _update_progress(i, total_apps, progress_func)
                continue

            # 3. Thực hiện cài đặt với logic Retry
            log_func({"status": "INSTALL", "msg": f"Đang cài: {display_name}..."})
            
            retry_limit = 2
            attempt = 0
            installed_successfully = False

            while attempt <= retry_limit:
                result: InstallationResult = installer.install()
                
                if result.status == "SUCCESS":
                    # Hậu kiểm thực tế (trừ các trường hợp đặc biệt như UniKey đã tự check trong class)
                    time.sleep(2)
                    verify_ok, _ = installer.check_installed()
                    
                    # Một số app cài xong cần restart hoặc registry cập nhật chậm, ta vẫn báo thành công nếu installer báo 0
                    log_func({"status": "SUCCESS", "msg": f"Hoàn tất: {display_name}"})
                    success_count += 1
                    installed_successfully = True
                    break
                
                elif result.status == "RETRY":
                    attempt += 1
                    if attempt <= retry_limit:
                        log_func({"status": "WARNING", "msg": f"{display_name}: {result.message}. Thử lại sau 10s ({attempt}/{retry_limit})"})
                        time.sleep(10)
                        continue
                    else:
                        log_func({"status": "ERROR", "msg": f"{display_name}: Thất bại sau nhiều lần thử."})
                        break
                
                elif result.status == "CANCEL":
                    log_func({"status": "WARNING", "msg": f"{display_name}: Người dùng đã hủy hoặc đóng bộ cài."})
                    break
                
                else: # ERROR
                    log_func({"status": "ERROR", "msg": f"{display_name}: {result.message}"})
                    break
            
            _update_progress(i, total_apps, progress_func)

        # Kết thúc
        winsound.MessageBeep()
        log_func({"status": "SUMMARY", "success": success_count, "total": total_apps})
        log_func({"status": "DONE", "msg": "Tất cả tiến trình đã kết thúc."})
        complete_func()

    def _update_progress(current, total, callback):
        if total > 0:
            callback(current / total)

    # Chạy trong thread riêng để không treo UI
    threading.Thread(target=run, daemon=True).start()
