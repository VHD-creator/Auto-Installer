import os
import winreg
import re
import unicodedata
from typing import Tuple, Optional, List

class SmartDetector:
    """
    Hệ thống cảm biến thông minh để phát hiện phần mềm đã cài đặt trên Windows.
    Sử dụng đa tầng: Registry (Uninstall) -> App Paths -> MuiCache -> Disk Scan.
    """
    
    _UNINSTALL_KEYS = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]

    @staticmethod
    def normalize(text: str) -> str:
        """Chuẩn hóa chuỗi tiếng Việt và loại bỏ ký tự đặc biệt."""
        if not text: return ""
        text = unicodedata.normalize('NFKD', str(text))
        text = "".join([c for c in text if not unicodedata.combining(c)])
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return " ".join(text.split())

    def is_installed(self, display_name: str, metadata_name: str = "", msi_product_code: str = "", company_name: str = "") -> Tuple[bool, str]:
        """
        Kiểm tra ứng dụng đã cài đặt với độ chính xác cao.
        Returns: (is_installed, detected_name)
        """
        dn_norm = self.normalize(display_name)
        mn_norm = self.normalize(metadata_name)
        cn_norm = self.normalize(company_name)

        # 1. Xử lý đặc biệt cho Microsoft Office
        office_res = self._check_office(dn_norm, mn_norm)
        if office_res: return office_res

        # 2. Kiểm tra MSI Product Code (Chính xác tuyệt đối)
        if msi_product_code:
            msi_res = self._check_msi_code(msi_product_code)
            if msi_res: return msi_res

        # 3. Quét Registry Uninstall với Fuzzy Matching
        registry_res = self._scan_uninstall_registry(dn_norm, mn_norm, cn_norm)
        if registry_res: return registry_res

        # 4. Kiểm tra App Paths
        app_path_res = self._check_app_paths(dn_norm, mn_norm)
        if app_path_res: return app_path_res

        # 5. Kiểm tra MuiCache (Dấu vết thực thi)
        mui_res = self._check_muicache(dn_norm, mn_norm)
        if mui_res: return mui_res

        # 6. Quét thư mục cài đặt (Disk Scan)
        disk_res = self._scan_program_folders(dn_norm, mn_norm)
        if disk_res: return disk_res

        return False, ""

    def _check_office(self, dn_norm: str, mn_norm: str) -> Optional[Tuple[bool, str]]:
        is_office_suite = ("office" in dn_norm or "office" in mn_norm or re.search(r'\bo\d{3,4}\b', dn_norm)) \
                          and not ("visio" in dn_norm or "project" in dn_norm)
        
        is_standalone_office = "visio" in dn_norm or "project" in dn_norm or \
                               "visio" in mn_norm or "project" in mn_norm

        if is_office_suite:
            for key_path in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe",
                             r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe"]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        return True, "Microsoft Office"
                except OSError: pass

        if is_standalone_office:
            target = "visio.exe" if "visio" in dn_norm or "visio" in mn_norm else "winproj.exe"
            for key_path in [f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{target}",
                             f"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{target}"]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        return True, f"Microsoft {target.split('.')[0].capitalize()}"
                except OSError: pass
        return None

    def _check_msi_code(self, code: str) -> Optional[Tuple[bool, str]]:
        clean_code = code.strip("{}").lower()
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for key_path in self._UNINSTALL_KEYS:
                try:
                    with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                        count = winreg.QueryInfoKey(key)[0]
                        for i in range(count):
                            sub_name = winreg.EnumKey(key, i)
                            if sub_name.strip("{}").lower() == clean_code:
                                try:
                                    with winreg.OpenKey(hive, f"{key_path}\\{sub_name}") as sub:
                                        dn, _ = winreg.QueryValueEx(sub, "DisplayName")
                                        return True, dn
                                except: return True, code
                except OSError: pass
        return None

    def _scan_uninstall_registry(self, dn_norm: str, mn_norm: str, cn_norm: str) -> Optional[Tuple[bool, str]]:
        search_patterns = [p for p in [dn_norm, mn_norm] if p]
        core_keywords = []
        for p in search_patterns:
            kws = [kw for kw in p.split() if len(kw) > 1 and kw not in ['setup', 'install', 'version', 'standalone']]
            if kws: core_keywords.append(kws)

        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
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
                                            
                                            reg_dn_norm = self.normalize(reg_dn)
                                            reg_pub_norm = self.normalize(reg_pub)
                                            
                                            # Match exact or partial
                                            for p in search_patterns:
                                                if p == reg_dn_norm or p in reg_dn_norm or reg_dn_norm in p:
                                                    return True, reg_dn
                                            
                                            # Keyword matching with publisher boost
                                            pub_matched = cn_norm and cn_norm in reg_pub_norm
                                            for kws in core_keywords:
                                                matches = sum(1 for kw in kws if kw in reg_dn_norm)
                                                threshold = 0.5 if pub_matched else 0.75
                                                if matches >= len(kws) * threshold and matches > 0:
                                                    return True, reg_dn
                                        except: pass
                                except: pass
                    except OSError: pass
        return None

    def _check_app_paths(self, dn_norm: str, mn_norm: str) -> Optional[Tuple[bool, str]]:
        potential_exes = set()
        for n in [dn_norm, mn_norm]:
            if not n: continue
            potential_exes.add(f"{n.replace(' ', '')}.exe")
            potential_exes.add(f"{n.split()[0]}.exe")
            
        for exe in potential_exes:
            key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{exe}"
            for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                for access in [winreg.KEY_READ | winreg.KEY_WOW64_64KEY, winreg.KEY_READ | winreg.KEY_WOW64_32KEY]:
                    try:
                        with winreg.OpenKey(hive, key_path, 0, access):
                            return True, f"App Path: {exe}"
                    except OSError: pass
        return None

    def _check_muicache(self, dn_norm: str, mn_norm: str) -> Optional[Tuple[bool, str]]:
        mui_key = r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, mui_key) as key:
                count = winreg.QueryInfoKey(key)[1]
                for i in range(count):
                    try:
                        _, val_data, _ = winreg.EnumValue(key, i)
                        val_norm = self.normalize(str(val_data))
                        for p in [dn_norm, mn_norm]:
                            if p and len(p) > 4 and p in val_norm:
                                return True, f"MuiCache: {val_data}"
                    except: pass
        except: pass
        return None

    def _scan_program_folders(self, dn_norm: str, mn_norm: str) -> Optional[Tuple[bool, str]]:
        search_names = [n for n in [dn_norm, mn_norm] if n and len(n) > 3]
        prog_dirs = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("LocalAppData", ""), "Programs")
        ]
        
        for base in prog_dirs:
            if not base or not os.path.exists(base): continue
            try:
                for item in os.listdir(base):
                    item_norm = self.normalize(item)
                    if any(s in item_norm for s in search_names):
                        full_path = os.path.join(base, item)
                        if os.path.isdir(full_path):
                            # Verify if it contains exes
                            exes = [f for f in os.listdir(full_path) if f.lower().endswith('.exe')]
                            if exes: return True, f"Folder: {item}"
            except: pass
        return None
