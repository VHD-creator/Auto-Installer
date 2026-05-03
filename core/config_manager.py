import json
import os
import sys

CONFIG_FILE = "config.json"

def load_config():
    base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    config_path = os.path.join(base_path, CONFIG_FILE)
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"apps": []}, f, ensure_ascii=False, indent=4)
        return []
        
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("apps", [])

def save_config(apps_list):
    base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    config_path = os.path.join(base_path, CONFIG_FILE)
    temp_path = config_path + ".tmp"
    
    try:
        # 1. Ghi vào file tạm
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump({"apps": apps_list}, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno()) # Ép dữ liệu ghi xuống đĩa cứng
            
        # 2. Thay thế file cũ bằng file tạm (Atomic Operation)
        os.replace(temp_path, config_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Lỗi bảo vệ file config.json: {e}")
