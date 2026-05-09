import os
import subprocess
import shutil
import time
from abc import ABC, abstractmethod
from core.detector import SmartDetector
from core.installer_analyzer import analyze_installer, detect_silent_flags

class InstallationResult:
    def __init__(self, status: str, message: str, return_code: int = 0):
        self.status = status
        self.message = message
        self.return_code = return_code

class BaseInstaller(ABC):
    def __init__(self, exe_path: str, display_name: str, detector: SmartDetector):
        self.exe_path = exe_path
        self.display_name = display_name
        self.detector = detector
        self.metadata = analyze_installer(exe_path)
        self.silent_flags = detect_silent_flags(exe_path) or []

    def check_installed(self) -> tuple[bool, str]:
        """Kiểm tra xem app đã cài chưa."""
        return self.detector.is_installed(
            self.display_name, 
            self.metadata.get("ProductName") or self.metadata.get("FileDescription"),
            self.metadata.get("ProductCode"),
            self.metadata.get("CompanyName")
        )

    @abstractmethod
    def install(self) -> InstallationResult:
        pass

class EXEInstaller(BaseInstaller):
    def install(self) -> InstallationResult:
        try:
            cmd = [self.exe_path] + self.silent_flags
            # Đặc biệt cho một số app như Zalo, Foxit, WinRAR đã được detect_silent_flags xử lý
            result = subprocess.run(cmd, check=False, cwd=os.path.dirname(self.exe_path), timeout=1200)
            return self._handle_result(result.returncode)
        except subprocess.TimeoutExpired:
            return InstallationResult("ERROR", "Quá thời gian cài đặt (20 phút)")
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi hệ thống: {str(e)}")

    def _handle_result(self, code: int) -> InstallationResult:
        success_codes = [0, 3010, 1641]
        cancel_codes = [1, 1602, 1223, 3221225786, -1073741510, -1073741819, -1]
        
        if code in success_codes:
            msg = "Cài đặt thành công"
            if code in [3010, 1641]: msg += " (Yêu cầu khởi động lại)"
            return InstallationResult("SUCCESS", msg, code)
        elif code in cancel_codes:
            return InstallationResult("CANCEL", "Người dùng đã hủy cài đặt", code)
        elif code == 1618:
            return InstallationResult("RETRY", "Hệ thống bận (Installer khác đang chạy)", code)
        else:
            return InstallationResult("ERROR", f"Lỗi cài đặt (Mã {code})", code)

class MSIInstaller(BaseInstaller):
    def install(self) -> InstallationResult:
        try:
            # MSI luôn dùng msiexec
            flags = self.silent_flags if self.silent_flags else ["/qn", "/norestart"]
            cmd = ["msiexec.exe", "/i", self.exe_path] + flags
            result = subprocess.run(cmd, check=False, timeout=1200)
            return self._handle_result(result.returncode)
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi MSI: {str(e)}")

    def _handle_result(self, code: int) -> InstallationResult:
        # MSI có bộ mã lỗi tương tự EXE nhưng chuẩn hóa hơn
        if code in [0, 3010, 1641]:
            return InstallationResult("SUCCESS", "MSI cài đặt thành công", code)
        elif code == 1602:
            return InstallationResult("CANCEL", "Người dùng hủy MSI", code)
        elif code == 1618:
            return InstallationResult("RETRY", "Windows Installer đang bận", code)
        else:
            return InstallationResult("ERROR", f"Lỗi MSI (Mã {code})", code)

class ScriptInstaller(BaseInstaller):
    def install(self) -> InstallationResult:
        try:
            # Chạy .bat hoặc .cmd
            cmd = f'start /wait "" "{self.exe_path}"'
            result = subprocess.run(cmd, shell=True, check=False, cwd=os.path.dirname(self.exe_path))
            return InstallationResult("SUCCESS", "Script đã thực thi xong")
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi script: {str(e)}")

class ISOInstaller(BaseInstaller):
    def install(self) -> InstallationResult:
        try:
            safe_path = self.exe_path.replace("'", "''")
            ps_mount = f"$Image = Mount-DiskImage -ImagePath '{safe_path}' -PassThru; ($Image | Get-Volume).DriveLetter"
            mount_proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_mount], capture_output=True, text=True)
            drive_letter = mount_proc.stdout.strip().splitlines()[-1] if mount_proc.stdout.strip() else ""
            
            if not drive_letter:
                return InstallationResult("ERROR", "Không thể mount file ISO/IMG")

            drive_path = f"{drive_letter}:\\"
            target = None
            for cand in ["setup.exe", "install.exe", "autorun.exe"]:
                if os.path.exists(os.path.join(drive_path, cand)):
                    target = os.path.join(drive_path, cand)
                    break
            
            if not target:
                for f in os.listdir(drive_path):
                    if f.lower().endswith(('.exe', '.msi')):
                        target = os.path.join(drive_path, f)
                        break
            
            if target:
                if target.lower().endswith('.msi'):
                    res = subprocess.run(["msiexec.exe", "/i", target], check=False)
                else:
                    res = subprocess.run([target], check=False)
                return InstallationResult("SUCCESS", f"Đã chạy cài đặt từ {drive_letter}:")
            return InstallationResult("ERROR", "Không tìm thấy bộ cài trong ISO")
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi ISO: {str(e)}")

class UniKeyInstaller(BaseInstaller):
    """Xử lý riêng cho UniKey (copy ra Desktop)"""
    def check_installed(self) -> tuple[bool, str]:
        # UniKey thường không "cài đặt" vào registry, chỉ copy file
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(os.path.join(desktop, os.path.basename(self.exe_path))):
            return True, "Đã có trên Desktop"
        return False, ""

    def install(self) -> InstallationResult:
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shutil.copy2(self.exe_path, desktop)
            return InstallationResult("SUCCESS", "Đã copy UniKey ra Desktop")
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi copy UniKey: {str(e)}")

class OfficeInstaller(BaseInstaller):
    """Xử lý Office Deployment Tool (ODT) và các ứng dụng Office đơn lẻ."""
    def install(self) -> InstallationResult:
        try:
            dir_name = os.path.dirname(self.exe_path)
            config_xml = None
            
            # 1. Xác định file XML cấu hình
            if self.exe_path.lower().endswith('.xml'):
                config_xml = self.exe_path
                setup_exe = os.path.join(dir_name, "setup.exe")
            else:
                setup_exe = self.exe_path
                # Tìm file .xml bất kỳ trong cùng thư mục
                xml_files = [f for f in os.listdir(dir_name) if f.lower().endswith(".xml")]
                if xml_files:
                    config_xml = os.path.join(dir_name, xml_files[0])

            # 2. Kiểm tra tính hợp lệ của chế độ im lặng (Silent)
            is_silent_ready = False
            if config_xml and os.path.exists(config_xml):
                try:
                    with open(config_xml, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'Level="None"' in content:
                            is_silent_ready = True
                except: pass

            # 3. Thực thi
            if os.path.exists(setup_exe):
                if is_silent_ready:
                    # Chế độ im lặng tuyệt đối
                    res = subprocess.run([setup_exe, "/configure", config_xml], check=False, cwd=dir_name)
                    return InstallationResult("SUCCESS", "Office: Cài đặt im lặng hoàn tất")
                else:
                    # Chế độ GUI (Thủ công) - Không dùng /configure hoặc dùng nhưng không có Level="None"
                    # Nếu có XML nhưng không có Level="None", vẫn chạy /configure để áp dụng cấu hình nhưng sẽ hiện GUI
                    if config_xml:
                        res = subprocess.run([setup_exe, "/configure", config_xml], check=False, cwd=dir_name)
                    else:
                        res = subprocess.run([setup_exe], check=False, cwd=dir_name)
                    return InstallationResult("SUCCESS", "Office: Cài đặt thủ công (GUI) hoàn tất")
            
            return InstallationResult("ERROR", "Không tìm thấy setup.exe để cài đặt Office")
        except Exception as e:
            return InstallationResult("ERROR", f"Lỗi Office: {str(e)}")

class InstallerFactory:
    @staticmethod
    def create(exe_path: str, display_name: str, detector: SmartDetector) -> BaseInstaller:
        ext = os.path.splitext(exe_path)[1].lower()
        name_lower = display_name.lower()
        exe_lower = os.path.basename(exe_path).lower()

        # 1. Các file đĩa ảo luôn đi qua ISOInstaller để Mount
        if ext in [".iso", ".img"]:
            return ISOInstaller(exe_path, display_name, detector)

        # 2. Xử lý đặc biệt cho UniKey
        if "unikey" in name_lower or "unikey" in exe_lower:
            return UniKeyInstaller(exe_path, display_name, detector)
        
        # 3. Xử lý Office (Setup.exe + XML)
        office_keywords = [
            "office", "word", "excel", "powerpoint", "outlook", "onenote", 
            "access", "publisher", "visio", "project", "teams", "onedrive", 
            "sharepoint", "skype for business", "copilot", "clipchamp", 
            "loop", "sway", "forms", "odt", "proplus"
        ]
        if any(kw in name_lower or kw in exe_lower for kw in office_keywords) or ext == ".xml":
            return OfficeInstaller(exe_path, display_name, detector)

        # 4. Các định dạng cơ bản khác
        if ext == ".msi":
            return MSIInstaller(exe_path, display_name, detector)
        elif ext in [".bat", ".cmd"]:
            return ScriptInstaller(exe_path, display_name, detector)
        else:
            return EXEInstaller(exe_path, display_name, detector)
