import os
import subprocess
import pefile
import json
import re

def get_pe_info(filepath):
    """
    Trích xuất CompanyName và FileDescription từ file PE (.exe) sử dụng pefile.
    """
    pe = None
    try:
        pe = pefile.PE(filepath, fast_load=True)
        info = {}
        
        if hasattr(pe, 'VS_VERSIONINFO') and hasattr(pe, 'FileInfo'):
            for file_info in pe.FileInfo:
                for entry in file_info:
                    if hasattr(entry, 'StringTable'):
                        for st in entry.StringTable:
                            for key, value in st.entries.items():
                                k = key.decode('utf-8', errors='ignore')
                                v = value.decode('utf-8', errors='ignore')
                                info[k] = v
        
        return {
            "CompanyName": info.get("CompanyName", ""),
            "FileDescription": info.get("FileDescription", ""),
            "ProductName": info.get("ProductName", ""),
            "ProductVersion": info.get("ProductVersion", "")
        }
    except Exception as e:
        return {"CompanyName": "", "FileDescription": "", "ProductName": ""}
    finally:
        if pe: pe.close()

def get_msi_product_code(filepath):
    """Lấy ProductCode duy nhất của file MSI."""
    abs_path = os.path.abspath(filepath)
    ps_script = f"""
    try {{
        $path = @'
{abs_path}
'@
        $installer = New-Object -ComObject WindowsInstaller.Installer
        $database = $installer.OpenDatabase($path, 0)
        $view = $database.OpenView("SELECT Value FROM Property WHERE Property='ProductCode'")
        $view.Execute()
        $record = $view.Fetch()
        $code = if ($record) {{ $record.StringData(1) }} else {{ "" }}
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($view) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($database) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($installer) | Out-Null
        Write-Output $code
    }} catch {{ Write-Output "" }}
    """
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, check=False)
        lines = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
        return lines[0] if lines else ""
    except:
        return ""

def get_msi_info(filepath):
    """
    Trích xuất Manufacturer và Title từ file .msi sử dụng PowerShell (An toàn với Base64).
    """
    import base64
    abs_path = os.path.abspath(filepath)
    path_b64 = base64.b64encode(abs_path.encode('utf-16le')).decode('utf-8')
    
    ps_script = f"""
    try {{
        $path = [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('{path_b64}'))
        $installer = New-Object -ComObject WindowsInstaller.Installer
        $database = $installer.OpenDatabase($path, 0)
        
        function Get-MSIProp($name) {{
            $view = $database.OpenView("SELECT Value FROM Property WHERE Property='$name'")
            $view.Execute()
            $record = $view.Fetch()
            if ($record) {{ return $record.StringData(1) }}
            return ""
        }}
        
        $manufacturer = Get-MSIProp "Manufacturer"
        $product = Get-MSIProp "ProductName"
        $version = Get-MSIProp "ProductVersion"
        
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($database) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($installer) | Out-Null
        
        $obj = @{{ CompanyName = $manufacturer; ProductName = $product; FileDescription = $product; ProductVersion = $version }}
        $obj | ConvertTo-Json -Compress
    }} catch {{
        @{{ CompanyName = ""; ProductName = ""; FileDescription = ""; ProductVersion = "" }} | ConvertTo-Json -Compress
    }}
    """
    
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, check=False)
        if proc.stdout:
            output = proc.stdout.strip()
            if '{' in output:
                json_part = output[output.find('{'):output.rfind('}')+1]
                data = json.loads(json_part)
                return {k: str(v).strip() if v else "" for k, v in data.items()}
    except:
        pass
    
    return {"CompanyName": "", "FileDescription": "", "ProductName": ""}

def deep_binary_scan(filepath):
    """
    Quét sâu vào nội dung binary (lên đến 10MB và cả phần cuối file) để tìm dấu vết các engine cài đặt.
    Hệ thống tra xâu thông minh để xác định flag silent chính xác nhất.
    """
    try:
        file_size = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            # 1. Đọc 8MB đầu tiên - Nơi chứa hầu hết các header và signature engine
            head_size = min(file_size, 8388608) 
            head_chunk = f.read(head_size)
            
            # 2. Đọc 1MB cuối cùng - Một số engine như NSIS hoặc SFX để signature ở cuối
            tail_chunk = b""
            if file_size > head_size:
                f.seek(-min(file_size - head_size, 1048576), 2)
                tail_chunk = f.read()
            
            full_scan = head_chunk + tail_chunk

            # --- DANH SÁCH SIGNATURE VÀ FLAG TƯƠNG ỨNG (Sắp xếp theo độ ưu tiên: Cụ thể -> Chung) ---
            signatures = [
                # 1. Ứng dụng cụ thể (Độ ưu tiên cao nhất)
                (b'Zoom Video Communications', ["/silent"]),
                (b'ZoomInstaller', ["/silent"]),
                (b'Zalo', ["/S"]),
                (b'mini_installer', ["--silent", "--install"]), # Chrome/Coccoc
                (b'Google Update', ["/silent"]),
                (b'OfficeDeploymentTool', ["/configure"]),
                (b'Microsoft Visual Studio', ["/q", "/norestart"]),
                (b'VCREDIST', ["/quiet", "/norestart"]),
                (b'Hotfix', ["/quiet", "/norestart"]),
                
                # 2. Engine cài đặt chuyên dụng (Phổ biến nhất)
                (b'Inno Setup Setup Data', ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]),
                (b'InnoSetup', ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]),
                (b'NullsoftInst', ["/S"]),
                
                # 3. Các Engine thương mại & Phổ biến khác
                (b'AI_SETUP_DATA', ["/ai", "/qn"]),
                (b'Caphyon', ["/ai", "/qn"]),
                (b'Advanced Installer', ["/ai", "/qn"]),
                (b'ISSetupStream', ["/s", "/v\"/qn\""]),
                (b'InstallShield', ["/s", "/v\"/qn\""]),
                (b'_isuser.dll', ["/s", "/v\"/qn\""]),
                (b'InstallShield Setup', ["/s", "/v\"/qn\""]),
                (b'WixBurn', ["/install", "/quiet", "/norestart"]),
                (b'BitRock', ["--mode", "unattended"]),
                (b'installbuilder', ["--mode", "unattended"]),
                (b'Qt Installer Framework', ["--silent"]),
                (b'InstallAnywhere', ["-i", "silent"]),
                (b'Setup Factory', ["/S"]),
                (b'Actual Installer', ["/S"]),
                (b'Smart Install Maker', ["/S"]),
                (b'Tarma', ["/s"]),
                (b'Ghost Installer', ["/s"]),
                (b'DeployMaster', ["/s"]),
                (b'CreateInstall', ["-silent"]),
                (b'Wise Installation System', ["/s"]),
                (b'InstallWise', ["/s"]),
                (b'WISE', ["/s"]),
                (b'VISE', ["/s"]),
                (b'PackageForWeb', ["/s"]),
                (b'CreateInstall', ["-silent"]),
                (b'SetupFactory', ["/S"]),
                (b'Greatis Software', ["/s"]),
                (b'Indigo Rose', ["/S"]), # Nhà sản xuất Setup Factory
                (b'Scripting Support', ["/s"]), # Thường là Wise
                
                # 4. Các hệ thống khác & App đặc biệt
                (b'Squirrel', ["--silent"]),
                (b'Microsoft Update', ["/quiet", "/norestart"]),
                (b'Foxit Software', ["/quiet"]),
                (b'TeamViewer', ["/S"]),
                (b'AnyDesk', ["--silent"]),
                (b'VLC media player', ["/S"]),
                (b'Winamp', ["/S"]),
                (b'CCleaner', ["/S"]),
                (b'WinRAR', ["/S"]),
                (b'7-Zip', ["/S"]),
                
                # 5. Container SFX (Độ ưu tiên thấp nhất)
                (b'7zSFX', ["-y"]),
                (b';!@Install@!UTF-8!', ["-y"]),
                (b'RarSFX', ["/s"]),
                (b'Rar!', ["/s"]),
                (b'WinZip Self-Extractor', ["/s"]),
                (b'Enigma Virtual Box', []),
                (b'BoxedApp', []),
                (b'Cameyo', []),
                (b'ThinApp', []),
                (b'Enigma', []),
                (b'VBox', []), # Thường là Enigma Virtual Box
                (b'MoleBox', []),
            ]

            for sig, flags in signatures:
                if sig in full_scan:
                    return flags

            # --- STRING HUNTING (Săn tìm xâu - Lựa chọn cuối cùng) ---
            # Nếu không khớp signature nào, tìm trực tiếp các flag phổ biến trong binary
            # Ưu tiên các flag dài và đặc trưng trước
            if b'/VERYSILENT' in full_scan:
                return ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"]
            if b'--unattended' in full_scan:
                return ["--mode", "unattended"]
            if b'--silent' in full_scan:
                return ["--silent"]
            if b'/S' in full_scan and (b'/S ' in full_scan or b'/S\0' in full_scan or b'/S/' in full_scan or b'/S\"' in full_scan):
                return ["/S"]
            if b'/silent' in full_scan.lower():
                return ["/silent"]
            if b'/quiet' in full_scan.lower():
                return ["/quiet", "/norestart"]
            if b'/qn' in full_scan and b'msiexec' in full_scan.lower():
                return ["/qn", "/norestart"]
            if b'/passive' in full_scan.lower():
                return ["/passive", "/norestart"]
            
            # Kiểm tra các chuỗi đặc trưng cho bộ cài bọc MSI
            if b'msiexec' in full_scan.lower() and (b'/i' in full_scan or b'/x' in full_scan):
                if b'/s' in full_scan.lower(): return ["/s", "/v\"/qn\""]
                return ["/qn"]

    except Exception as e:
        print(f"Deep scan error: {e}")
    return None

def detect_silent_flags(filepath):
    """
    Dựa vào CompanyName và FileDescription để xác định flag silent tương ứng.
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    # 1. Ưu tiên quét Deep Binary trước vì độ chính xác cực cao (không phụ thuộc metadata)
    deep_flags = deep_binary_scan(filepath)
    if deep_flags:
        return deep_flags

    # 2. Dự phòng: Kiểm tra metadata PE (CompanyName, FileDescription)
    info = {}
    if ext == '.exe':
        info = get_pe_info(filepath)
    elif ext == '.msi':
        info = get_msi_info(filepath)
        return ["/qn", "/norestart"] # MSI mặc định dùng flag này
    
    company = info.get("CompanyName", "").strip().lower()
    desc = info.get("FileDescription", "").strip().lower()
    product = info.get("ProductName", "").strip().lower()
    
    # 1. Nullsoft (NSIS)
    if "nullsoft" in company or "nsis" in desc or "nullsoft" in desc or "nsis" in product:
        return ["/S"]
    
    # 2. Inno Setup
    if "inno setup" in company or "inno setup" in desc or "inno setup" in product:
        return ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
    
    # 3. InstallShield (Thường là Wrapper cho MSI)
    if "flexera" in company or "installshield" in desc or "installshield" in product:
        # /v"/qn" để truyền lệnh xuống MSI bên trong
        return ["/s", "/v\"/qn\""]
    
    # 4. Advanced Installer
    if "caphyon" in company or "advanced installer" in desc or "advanced installer" in product:
        return ["/ai", "/qn"]
    
    # 5. WiX Toolset (Burn)
    if "wix" in company or "wix" in desc or "wix" in product:
        return ["/install", "/quiet", "/norestart"]

    # 6. Squirrel (Electron - Discord, Slack, etc.)
    if "squirrel" in company or "squirrel" in desc:
        return ["--silent"]

    # 7. Google (Chrome, etc.)
    if "google" in company or "chrome" in product:
        return ["--silent", "--install"]

    # 8. Microsoft (Office, etc.)
    if "microsoft" in company:
        if "bootstrapper" in desc or "setup" in desc:
            return ["/quiet", "/norestart"]
        if "office" in desc or "office" in product:
            return ["/configure"] # Dành cho ODT
            
    # 9. Zoom
    if "zoom video" in company or "zoom communications" in company or "zoom" in product or "zoom" in desc:
        return ["/silent"]

    # 10. WinRAR
    if "win.rar" in company or "winrar" in product:
        return ["/S"]

    # 11. Cốc Cốc (Dùng chuẩn Chromium)
    if "coc coc" in company or "itim" in company or "coccoc" in product or "cốc cốc" in product:
        return ["--silent", "--install"]

    # 12. Zalo
    if "zalo" in company or "zalo" in product or "zalo" in desc:
        return ["/S"]

    # 13. Adobe
    if "adobe" in company or "adobe" in product:
        if ext == ".exe": return ["/sAll", "/rs", "/msi", "/qn", "/norestart"]
        return ["/qn"]

    # 14. Fallback nâng cao: Nếu không có metadata, kiểm tra sâu tên file & chuỗi
    fname = os.path.basename(filepath).lower()
    
    # Chromium-based (Chrome, Coc Coc, Edge, Brave, etc.)
    if any(x in fname for x in ["coccoc", "coc_coc", "chrome", "brave", "edge", "vivaldi", "opera", "browser"]):
        return ["--silent", "--install"]
        
    # Standard /S Apps
    if any(x in fname for x in ["zalo", "vlc", "teamviewer", "skype", "winrar", "7zip", "ccleaner", "disk-drill", "iobit", "glary"]):
        return ["/S"]
        
    # Inno/NSIS patterns (Dựa trên tên file thường gặp)
    if any(x in fname for x in ["evkey", "telegram", "unikey", "notepads", "k-lite", "potplayer", "gimp"]):
        return ["/VERYSILENT", "/SP-", "/SUPPRESSMSGBOXES", "/NORESTART"]
        
    # Quiet/NoRestart patterns (Microsoft, Drivers, Runtimes)
    if any(x in fname for x in ["vc_redist", "vcredist", "dotnet", "framework", "directx", "driver", "intel", "nvidia", "amd"]):
        return ["/quiet", "/norestart"]
        
    # Silent patterns (Ứng dụng hiện đại)
    if any(x in fname for x in ["anydesk", "zoom", "foxit", "nitro", "sublime", "vscode", "discord", "slack", "spotify"]):
        return ["/silent"]

    # 15. Universal Installer Guessing (Lựa chọn rủi ro cuối cùng)
    # Nếu file có tên chứa 'setup' hoặc 'install' và là .exe
    if ext == '.exe' and any(x in fname for x in ["setup", "install", "update"]):
        # Thử /S vì đây là flag phổ biến nhất của các bộ cài cổ điển
        return ["/S"]

    return []

def get_script_info(filepath):
    """Quét nội dung script .bat, .cmd để tìm tên app hoặc từ khóa."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            
            # 1. Tìm các từ khóa sản phẩm cụ thể
            keywords = {
                "office 365": "Microsoft Office 365",
                "office 2019": "Microsoft Office 2019",
                "office 2021": "Microsoft Office 2021",
                "autocad": "AutoCAD",
                "photoshop": "Adobe Photoshop",
                "unikey": "UniKey",
                "zalo": "Zalo",
                "telegram": "Telegram",
                "discord": "Discord",
                "activate": "Activation Script"
            }
            
            for kw, full_name in keywords.items():
                if kw in content:
                    return full_name
            
            # 2. Tìm lệnh gọi file setup/install
            match = re.search(r'(?:start|call|run|msiexec)\s+.*"?(.*?)\.(?:exe|msi)"?', content)
            if match:
                name = match.group(1).split('\\')[-1].split('/')[-1] # Lấy tên file cuối cùng
                return name.replace('_', ' ').replace('-', ' ').title()
    except:
        pass
    return ""

def get_xml_info(filepath):
    """Trích xuất thông tin từ file cấu hình XML (vd: Office 365)."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Tìm Product ID trong Office XML
            match = re.search(r'Product ID="(.*?)"', content)
            if match:
                pid = match.group(1)
                if "O365" in pid: return "Microsoft Office 365"
                if "ProPlus" in pid: return "Microsoft Office ProPlus"
                return pid
    except:
        pass
    return ""

def get_iso_info(filepath):
    """Lấy thông tin từ file ISO/IMG (Volume Label)."""
    abs_path = os.path.abspath(filepath).replace("'", "''")
    ps_script = f"""
    try {{
        $image = Get-DiskImage -ImagePath '{abs_path}'
        $image | Get-Volume | Select-Object -ExpandProperty FileSystemLabel
    }} catch {{ "" }}
    """
    try:
        proc = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, check=False)
        label = proc.stdout.strip()
        return label if label else ""
    except:
        pass
    return ""

def analyze_installer(filepath):
    """Hàm hợp nhất để phân tích mọi loại file cài đặt."""
    if not os.path.exists(filepath):
        return {"ProductName": "", "CompanyName": "", "ProductCode": "", "Type": "UNKNOWN"}

    ext = os.path.splitext(filepath)[1].lower()
    info = {
        "ProductName": "",
        "CompanyName": "",
        "ProductCode": "",
        "FileDescription": "",
        "Type": ext.upper()[1:] if ext else "UNKNOWN"
    }
    
    if ext == '.exe':
        pe = get_pe_info(filepath)
        info.update(pe)
    elif ext == '.msi':
        msi = get_msi_info(filepath)
        info.update(msi)
        info["ProductCode"] = get_msi_product_code(filepath)
    elif ext in ['.bat', '.cmd']:
        info["ProductName"] = get_script_info(filepath)
    elif ext == '.xml':
        info["ProductName"] = get_xml_info(filepath)
    elif ext in ['.iso', '.img']:
        info["ProductName"] = get_iso_info(filepath)
        
    return info

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        file = sys.argv[1]
        print(f"Analyzing: {file}")
        if file.endswith(".exe"):
            print("PE Info:", get_pe_info(file))
        elif file.endswith(".msi"):
            print("MSI Info:", get_msi_info(file))
        print("Detected Flags:", detect_silent_flags(file))
