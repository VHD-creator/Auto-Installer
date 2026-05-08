import os
import shutil
import subprocess
import threading
import time
import winsound
import sys
import winreg
import re
import unicodedata
from core.installer_analyzer import detect_silent_flags, analyze_installer

# Danh sách các registry key chứa thông tin phần mềm đã cài đặt
_UNINSTALL_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]

def normalize_vni(text):
    """Loại bỏ dấu tiếng Việt và chuẩn hóa chuỗi để so sánh."""
    if not text: return ""
    # 1. Chuyển sang NFKD để tách các ký tự dấu ra khỏi chữ cái gốc
    text = unicodedata.normalize('NFKD', str(text))
    # 2. Loại bỏ các ký tự dấu (combining characters)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 3. Chuyển về chữ thường, thay thế các ký tự đặc biệt bằng khoảng trắng
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # 4. Gom nhiều khoảng trắng thành 1 và trim
    return " ".join(text.split())

def is_app_installed(display_name, metadata_name="", msi_product_code="", company_name=""):
    """
    Kiểm tra ứng dụng đã cài đặt với độ thông minh cao.
    Ưu tiên: ProductCode (MSI) > Metadata (CompanyName + ProductName) > Fuzzy DisplayName.
    """
    # Chuẩn hóa các tên đầu vào
    dn_lower = normalize_vni(display_name)
    mn_lower = normalize_vni(metadata_name)
    cn_lower = normalize_vni(company_name)

    # 1. Kiểm tra trường hợp đặc biệt: Microsoft Office
    is_office_suite = ("office" in dn_lower or "office" in mn_lower or re.search(r'\bo\d{3,4}\b', dn_lower)) \
                      and not ("visio" in dn_lower or "project" in dn_lower)
    
    is_standalone_office = "visio" in dn_lower or "project" in dn_lower or \
                           "visio" in mn_lower or "project" in mn_lower

    if is_office_suite:
        # Kiểm tra Word/Excel có sẵn không (Đại diện cho bộ Office chính)
        for key_path in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe",
                         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    return True, "Microsoft Office (Đã cài đặt)"
            except OSError: pass

    if is_standalone_office:
        # Kiểm tra riêng cho Visio hoặc Project (Tránh skip nhầm khi máy đã có Word/Excel)
        target_exe = "visio.exe" if "visio" in dn_lower or "visio" in mn_lower else "winproj.exe"
        for key_path in [f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{target_exe}",
                         f"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{target_exe}"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    return True, f"Microsoft {target_exe.replace('.exe', '').capitalize()} (Đã cài đặt)"
            except OSError: pass

    # 2. Nếu là MSI, ưu tiên kiểm tra qua ProductCode (Chính xác 100%)
    if msi_product_code:
        msi_code_clean = msi_product_code.strip().lower()
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for key_path in _UNINSTALL_KEYS:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        count = winreg.QueryInfoKey(key)[0]
                        for i in range(count):
                            sub_name = winreg.EnumKey(key, i)
                            # Đảm bảo so sánh chính xác ProductCode (bỏ qua dấu ngoặc nhọn nếu có)
                            sub_name_clean = sub_name.strip("{}").lower()
                            msi_code_clean_final = msi_code_clean.strip("{}").lower()
                            
                            if sub_name_clean == msi_code_clean_final:
                                with winreg.OpenKey(hive, f"{key_path}\\{sub_name}") as sub:
                                    try:
                                        d_name, _ = winreg.QueryValueEx(sub, "DisplayName")
                                        return True, d_name
                                    except:
                                        return True, msi_product_code
                except OSError: pass

    # 3. Quét Registry chi tiết (Fuzzy Matching cho mọi loại app)
    search_names = []
    if metadata_name: search_names.append(metadata_name.strip().lower())
    if display_name: search_names.append(display_name.strip().lower())
    
    comp_norm = cn_lower # Publisher từ file
    
    core_keywords = []
    for s in search_names:
        s_norm = normalize_vni(s)
        kws = [kw for kw in s_norm.split() if len(kw) > 1 and kw not in ['setup', 'install', 'version', 'standalone', 'online']]
        if kws: core_keywords.append(kws)

    # 3. Quét Registry chi tiết (Fuzzy Matching cho mọi loại app)
    # Pre-normalize search patterns for performance
    s_patterns = []
    for s in search_names:
        s_n = normalize_vni(s)
        s_patterns.append((s_n, s_n.replace(" ", "")))
    
    comp_n = normalize_vni(company_name)

    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        # Kiểm tra cả view 64-bit và 32-bit của Registry
        for access in [winreg.KEY_READ | winreg.KEY_WOW64_64KEY, winreg.KEY_READ | winreg.KEY_WOW64_32KEY]:
            for key_path in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"]:
                try:
                    with winreg.OpenKey(hive, key_path, 0, access) as key:
                        count = winreg.QueryInfoKey(key)[0]
                        for i in range(count):
                            try:
                                sub_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(hive, f"{key_path}\\{sub_name}", 0, access) as sub:
                                    try:
                                        reg_dn, _ = winreg.QueryValueEx(sub, "DisplayName")
                                        reg_pub = ""
                                        try: reg_pub, _ = winreg.QueryValueEx(sub, "Publisher")
                                        except: pass
                                        
                                        dn_r_n = normalize_vni(reg_dn)
                                        dn_r_c = dn_r_n.replace(" ", "")
                                        pub_r_n = normalize_vni(reg_pub)
                                        pub_matched = (comp_n and comp_n in pub_r_n)

                                        for s_n, s_c in s_patterns:
                                            if s_n == dn_r_n or s_n in dn_r_n or dn_r_n in s_n:
                                                return True, reg_dn
                                            
                                            for kws in core_keywords:
                                                matches = sum(1 for kw in kws if kw in dn_r_n)
                                                threshold = 0.5 if pub_matched else 0.7
                                                if matches >= len(kws) * threshold and matches > 0:
                                                    return True, reg_dn
                                            
                                            if (s_c in dn_r_c or dn_r_c in s_c) and len(s_c) > 3:
                                                return True, reg_dn
                                    except: pass
                            except: pass
                except OSError: pass

    # 4. Kiểm tra MuiCache (Dành cho bản Portable/Standalone)
    mui_key = r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, mui_key) as key:
            count = winreg.QueryInfoKey(key)[1] # Đếm số lượng value
            for i in range(count):
                val_name, val_data, _ = winreg.EnumValue(key, i)
                val_n = normalize_vni(val_data)
                for s_n, _ in s_patterns:
                    if s_n in val_n and len(s_n) > 4:
                        return True, f"MuiCache: {val_data}"
    except: pass

    # 5. Kiểm tra App Paths
    if not msi_product_code:
        for app_exe in [f"{mn_lower}.exe", f"{dn_lower}.exe", f"{dn_lower.replace(' ', '')}.exe"]:
            for key_path in [f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{app_exe}"]:
                for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    for access in [winreg.KEY_READ | winreg.KEY_WOW64_64KEY, winreg.KEY_READ | winreg.KEY_WOW64_32KEY]:
                        try:
                            with winreg.OpenKey(hive, key_path, 0, access) as key:
                                return True, f"App Path: {app_exe}"
                        except OSError: pass

    # 6. Kiểm tra thư mục cài đặt mặc định
    prog_files = [os.environ.get("ProgramFiles", "C:\\Program Files"),
                  os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                  os.path.join(os.environ.get("LocalAppData", ""), "Programs")]
    
    for base_dir in prog_files:
        if not base_dir or not os.path.exists(base_dir): continue
        try:
            for item in os.listdir(base_dir):
                item_n = normalize_vni(item)
                # Nếu tên thư mục khớp với tên app
                if any(s_n in item_n for s_n, _ in s_patterns if len(s_n) > 3):
                    item_path = os.path.join(base_dir, item)
                    if os.path.isdir(item_path):
                        # Kiểm tra xem có file .exe nào có tên liên quan đến app không
                        for f in os.listdir(item_path):
                            if f.endswith('.exe'):
                                f_n = normalize_vni(f)
                                if any(s_n in f_n for s_n, _ in s_patterns):
                                    return True, f"Folder: {item}"
        except: pass

    return False, ""

def get_silent_args(filepath):
    """
    Sử dụng installer_analyzer để nhận diện tham số cài đặt im lặng.
    """
    return detect_silent_flags(filepath)

def run_installation(checked_apps, log_func, progress_func, complete_func):
    def run():
        time.sleep(0.1)
        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        success = 0
        total = len(checked_apps)

        for i, (exe, name) in enumerate(checked_apps, start=1):
            exe_path = os.path.join(base_path, "installers", exe)
            exe_lower = exe.lower()

            if not os.path.exists(exe_path):
                log_func({"status": "ERROR", "msg": f"Không tìm thấy file: {exe}"})
                continue

            # Phân tích file để lấy metadata chính xác (CompanyName, ProductName, ProductCode)
            info = analyze_installer(exe_path)
            metadata_name = info.get("ProductName") or info.get("FileDescription")
            msi_code = info.get("ProductCode")
            company_name = info.get("CompanyName")

            # Kiểm tra app đã được cài đặt chưa (bỏ qua UniKey vì chỉ copy file)
            if "unikey" not in exe_lower and "unikey" not in name.lower():
                # Ưu tiên dùng thông tin trích xuất trực tiếp từ file bộ cài
                installed, installed_name = is_app_installed(name, metadata_name, msi_code, company_name)
                if installed:
                    log_func({"status": "SKIP", "msg": f"Đã cài sẵn: {name} (Bỏ qua)"})
                    success += 1
                    continue

            log_func({"status": "INSTALL", "msg": f"Đang cài: {name}..."})

            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    exe_lower = exe.lower()
                    name_lower = name.lower()
                    
                    result = None

                    if "unikey" in exe_lower:
                        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                        dest_path = os.path.join(desktop, exe)
                        if not os.path.exists(dest_path):
                            shutil.copy2(exe_path, desktop)
                            log_func({"status": "SUCCESS", "msg": "UniKey: Đã chép ra Desktop."})
                            success += 1
                        else:
                            log_func({"status": "INFO", "msg": "UniKey: Đã tồn tại."})
                            success += 1
                        break # Thoát khỏi vòng lặp retry

                    elif "foxit" in exe_lower:
                        log_func({"status": "INFO", "msg": f"Đang cài: Foxit PDF [/quiet]"})
                        result = subprocess.run([exe_path, "/quiet"], check=False)
                    elif "office 2019" in name_lower:
                        if os.path.exists(exe_path):
                            log_func({"status": "INFO", "msg": "Office 2019: Đang khởi tạo..."})
                            result = subprocess.run([exe_path], check=False)
                        else:
                            log_func({"status": "ERROR", "msg": "Office 2019: Thiếu file cài."})
                            break
                    elif "office 365" in name_lower:
                        # Tìm file XML trong cùng thư mục với setup.exe
                        dir_name = os.path.dirname(exe_path)
                        config_xml = os.path.join(dir_name, "configuration-Office365-x64.xml")
                        # Nếu không thấy tên mặc định, tìm file .xml bất kỳ trong thư mục đó
                        if not os.path.exists(config_xml):
                            xml_files = [f for f in os.listdir(dir_name) if f.lower().endswith(".xml")]
                            if xml_files:
                                config_xml = os.path.join(dir_name, xml_files[0])
                        
                        if os.path.exists(exe_path) and os.path.exists(config_xml):
                            log_func({"status": "INFO", "msg": "Office 365: Đang chạy ODT..."})
                            result = subprocess.run([exe_path, "/configure", config_xml], check=False, cwd=dir_name)
                        else:
                            log_func({"status": "ERROR", "msg": "Office 365: Thiếu file .xml."})
                            break
                    elif "winrar" in exe_lower:
                        log_func({"status": "INFO", "msg": f"Đang cài: WinRAR [/S]"})
                        result = subprocess.run([exe_path, "/S"], check=False)
                    elif exe_lower.endswith('.cmd') or exe_lower.endswith('.bat'):
                        log_func({"status": "INFO", "msg": f"Đang chạy script {name}..."})
                        result = subprocess.run(f'start /wait "" "{exe_path}"', shell=True, cwd=os.path.dirname(exe_path))
                    elif exe_lower.endswith('.xml'):
                        # Xử lý file cấu hình XML (thường dùng cho Office Deployment Tool)
                        setup_exe = os.path.join(os.path.dirname(exe_path), "setup.exe")
                        if os.path.exists(setup_exe):
                            log_func({"status": "INFO", "msg": "Office ODT: Đang chạy..."})
                            result = subprocess.run([setup_exe, "/configure", exe_path], check=False, cwd=os.path.dirname(exe_path))
                        else:
                            log_func({"status": "ERROR", "msg": "XML: Thiếu setup.exe."})
                            break
                    elif exe_lower.endswith('.iso') or exe_lower.endswith('.img'):
                        file_ext = "ISO" if exe_lower.endswith('.iso') else "IMG"
                        log_func({"status": "INFO", "msg": f"{file_ext}: Đang Mount..."})
                        # Escape path for PowerShell
                        safe_exe_path = exe_path.replace("'", "''")
                        ps_mount = f"$Image = Mount-DiskImage -ImagePath '{safe_exe_path}' -PassThru; ($Image | Get-Volume).DriveLetter"
                        mount_proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_mount], capture_output=True, text=True)
                        drive_letter_raw = mount_proc.stdout.strip()
                        # PowerShell đôi khi trả về nhiều dòng kèm warning → chỉ lấy dòng cuối
                        drive_letter_lines = [l.strip() for l in drive_letter_raw.splitlines() if l.strip()]
                        drive_letter = drive_letter_lines[-1] if drive_letter_lines else ""
                        
                        if drive_letter:
                            drive_path = f"{drive_letter}:\\"
                            target_exe = None
                            for candidate_name in ["setup.exe", "install.exe", "autorun.exe"]:
                                if os.path.exists(os.path.join(drive_path, candidate_name)):
                                    target_exe = os.path.join(drive_path, candidate_name)
                                    break
                            
                            if not target_exe:
                                for file in os.listdir(drive_path):
                                    if file.lower().endswith('.exe') or file.lower().endswith('.msi'):
                                        target_exe = os.path.join(drive_path, file)
                                        break
                            
                            if target_exe:
                                log_func({"status": "INFO", "msg": f"ISO: Đang chạy {os.path.basename(target_exe)}"})
                                if target_exe.lower().endswith('.msi'):
                                    cmd_iso = ["msiexec.exe", "/i", target_exe]
                                else:
                                    cmd_iso = [target_exe]
                                # cwd=None → dùng thư mục mặc định, tránh lỗi khi cwd là ổ đĩa ảo
                                result = subprocess.run(cmd_iso, check=False, cwd=None)
                            else:
                                log_func({"status": "ERROR", "msg": f"Không thấy file .exe trong {file_ext} {name}"})
                                break
                            
                            # Không tự động unmount ISO/IMG theo yêu cầu của user
                        else:
                            log_func({"status": "ERROR", "msg": f"Lỗi mount file {file_ext} {name}"})
                            break
                    elif "zalo" in exe_lower or "zalo" in name_lower:
                        log_func({"status": "INFO", "msg": f"Đang cài: Zalo [/S]"})
                        result = subprocess.run([exe_path, "/S"], check=False, cwd=os.path.dirname(exe_path))
                    elif "capcut" in exe_lower or "capcut" in name_lower:
                        # CapCut dùng web bootstrapper — chạy /S sẽ thoát ngay với code 0 mà không cài gì
                        # Phải chạy GUI bình thường để bootstrapper hoạt động đúng
                        log_func({"status": "INFO", "msg": "CapCut: Cần thao tác thủ công."})
                        result = subprocess.run([exe_path], check=False, cwd=os.path.dirname(exe_path))
                    else:
                        # Tự động đọc file để nhận diện kiểu cài đặt
                        silent_args = get_silent_args(exe_path)
                        
                        if silent_args:
                            log_func({"status": "INFO", "msg": f"Lệnh: {' '.join(silent_args)} (Auto)"})
                            if exe_lower.endswith('.msi'):
                                cmd = ["msiexec.exe", "/i", exe_path] + silent_args
                            else:
                                cmd = [exe_path] + silent_args
                        else:
                            log_func({"status": "INFO", "msg": "Chế độ: Thủ công"})
                            if exe_lower.endswith('.msi'):
                                cmd = ["msiexec.exe", "/i", exe_path]
                            else:
                                cmd = [exe_path]

                        try:
                            # Thêm timeout 20 phút (1200s) để tránh treo vĩnh viễn nếu installer lỗi
                            result = subprocess.run(cmd, check=False, cwd=os.path.dirname(exe_path), timeout=1200)
                        except subprocess.TimeoutExpired:
                            log_func({"status": "ERROR", "msg": f"Cài đặt {name} bị quá hạn (Timeout 20m)"})
                            break

                    # Kiểm tra kết quả sau khi cài đặt
                    if result:
                        ret_code = result.returncode
                        # Các mã lỗi/mã thoát khi người dùng chủ động tắt hoặc hệ thống ngắt tiến trình
                        cancel_codes = [1, 1602, 1223, 3221225786, -1073741510, -1073741819, -1]
                        
                        if ret_code in [0, 3010, 1641]:
                            # Hậu kiểm thông minh: Xác minh thực tế trong Registry/Disk sau khi bộ cài báo thành công
                            if "unikey" not in exe_lower and "unikey" not in name_lower:
                                time.sleep(3) # Tăng lên 3s để chắc chắn Registry đã được ghi xong
                                is_installed, _ = is_app_installed(name, metadata_name, msi_code, company_name)
                                if not is_installed:
                                    # Kiểm tra thêm một lần nữa qua App Path hoặc Folder trước khi kết luận hủy
                                    log_func({"status": "CANCEL", "msg": f"{name}: Đã bị hủy bởi người dùng"})
                                    break
                                    
                            msg = f"Xong: {name}"
                            if ret_code in [3010, 1641]:
                                msg += " (Cần khởi động lại)"
                            log_func({"status": "SUCCESS", "msg": msg})
                            success += 1
                            break
                        elif ret_code in cancel_codes:
                            log_func({"status": "CANCEL", "msg": f"{name}: Đã bị hủy bởi người dùng"})
                            break
                        elif ret_code == 1618: # ERROR_INSTALL_ALREADY_RUNNING
                            retry_count += 1
                            if retry_count < max_retries:
                                log_func({"status": "WARNING", "msg": f"Hệ thống bận (Mã 1618), chờ 10s... ({retry_count}/{max_retries})"})
                                time.sleep(10)
                                continue
                            else:
                                log_func({"status": "ERROR", "msg": f"Bỏ qua {name} do hệ thống bận quá lâu."})
                                break
                        else:
                            log_func({"status": "ERROR", "msg": f"Lỗi: {name} (Mã {ret_code})"})
                            break
                    else:
                        break

                except Exception as e:
                    log_func({"status": "ERROR", "msg": f"Lỗi khi cài {name}: {e}"})
                    break

            if total > 0:
                progress_func(i / total)

        winsound.MessageBeep()
        log_func({"status": "SUMMARY", "success": success, "total": total})
        log_func({"status": "DONE", "msg": "Tất cả tiến trình đã xong."})
        complete_func()

    threading.Thread(target=run, daemon=True).start()
