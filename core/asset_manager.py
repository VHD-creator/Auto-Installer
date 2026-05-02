import os
import customtkinter as ctk
from PIL import Image

class AssetManager:
    # Lấy đường dẫn gốc của project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(BASE_DIR, "gui", "assets")
    
    _cache = {}

    @classmethod
    def get_app_icon(cls, icon_filename, size=(34, 34)):
        """Lấy icon ứng dụng từ gui/assets/apps/ dựa trên tên file trong config"""
        if not icon_filename:
            return None
            
        icon_path = os.path.join(cls.ASSETS_DIR, "apps", icon_filename)
        
        # Nếu file không có đuôi hoặc không tồn tại, thử tìm với các đuôi phổ biến
        if not os.path.exists(icon_path):
            name_without_ext = os.path.splitext(icon_filename)[0]
            for ext in [".png", ".jpg", ".jpeg", ".ico"]:
                temp_path = os.path.join(cls.ASSETS_DIR, "apps", f"{name_without_ext}{ext}")
                if os.path.exists(temp_path):
                    icon_path = temp_path
                    break

        if os.path.exists(icon_path):
            cache_key = f"app_{icon_path}_{size}"
            if cache_key not in cls._cache:
                try:
                    pil_img = Image.open(icon_path)
                    cls._cache[cache_key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                except Exception:
                    return None
            return cls._cache[cache_key]
        return None

    @classmethod
    def get_system_icon(cls, icon_name, size=(24, 24)):
        """Lấy icon hệ thống từ gui/assets/icons/"""
        for ext in [".png", ".jpg", ".jpeg"]:
            icon_path = os.path.join(cls.ASSETS_DIR, "icons", f"{icon_name}{ext}")
            if os.path.exists(icon_path):
                cache_key = f"sys_{icon_name}_{size}"
                if cache_key not in cls._cache:
                    try:
                        pil_img = Image.open(icon_path)
                        cls._cache[cache_key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                    except Exception:
                        return None
                return cls._cache[cache_key]
        return None
