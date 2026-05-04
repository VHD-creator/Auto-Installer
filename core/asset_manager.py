import os
import sys
import customtkinter as ctk
from PIL import Image

class AssetManager:
    # 1. Đường dẫn bên ngoài (Để lưu icon apps do người dùng thêm)
    EXTERNAL_BASE = os.path.dirname(os.path.realpath(sys.argv[0]))
    ASSETS_DIR = os.path.join(EXTERNAL_BASE, "gui", "assets")
    
    # 2. Đường dẫn nội bộ (Để lấy icon hệ thống đi kèm app)
    if getattr(sys, 'frozen', False):
        INTERNAL_BASE = sys._MEIPASS
    else:
        INTERNAL_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    SYS_ICONS_DIR = os.path.join(INTERNAL_BASE, "gui", "assets", "icons")

    _cache = {}

    @classmethod
    def clear_cache(cls):
        """Xóa toàn bộ cache để ép app load lại ảnh mới từ đĩa"""
        cls._cache = {}

    @classmethod
    def get_app_icon(cls, icon_filename, size=(34, 34)):
        """Lấy icon ứng dụng từ thư mục ngoại vi (gui/assets/apps/)"""
        if not icon_filename:
            return cls.get_system_icon("default-app-icon", size)
            
        icon_path = os.path.join(cls.ASSETS_DIR, "apps", icon_filename)
        
        # Nếu không thấy ở ngoài, thử tìm trong gói đi kèm (nếu có)
        if not os.path.exists(icon_path):
            icon_path = os.path.join(cls.INTERNAL_BASE, "gui", "assets", "apps", icon_filename)

        if not os.path.exists(icon_path):
            return cls.get_system_icon("default-app-icon", size)

        cache_key = f"app_{icon_path}_{size}"
        if cache_key not in cls._cache:
            try:
                # Sử dụng 'with' và copy() để không giữ lock file, giúp ghi đè file sau này dễ dàng
                with Image.open(icon_path) as img:
                    pil_img = img.copy()
                cls._cache[cache_key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            except Exception:
                return cls.get_system_icon("default-app-icon", size)
        
        return cls._cache[cache_key]

    @classmethod
    def get_system_icon(cls, icon_name, size=(24, 24)):
        """Lấy icon hệ thống từ thư mục nội bộ (gui/assets/icons/)"""
        for ext in [".png", ".jpg", ".jpeg", ".ico"]:
            icon_path = os.path.join(cls.SYS_ICONS_DIR, f"{icon_name}{ext}")
            if os.path.exists(icon_path):
                cache_key = f"sys_{icon_name}_{size}"
                if cache_key not in cls._cache:
                    try:
                        with Image.open(icon_path) as img:
                            pil_img = img.copy()
                        cls._cache[cache_key] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                    except Exception:
                        return None
                return cls._cache[cache_key]
        return None

