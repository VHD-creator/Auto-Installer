import sys
from core.admin_check import enforce_single_instance, elevate_admin
import customtkinter as ctk

# 1. Yêu cầu quyền Admin trước
elevate_admin()

# 2. Ngăn chặn chạy đa tiến trình
enforce_single_instance()

# 3. Import App và khởi động
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

from gui.main_app import MainApp

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
