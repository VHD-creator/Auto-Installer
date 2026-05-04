import customtkinter as ctk
import os
import sys
from gui.sidebar import Sidebar
from gui.header import Header
from gui.tabs.install_tab import InstallTab
from gui.tabs.edit_tab import EditTab
from gui.tabs.info_tab import InfoTab

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Auto install app by Phạm Sự")
        self.geometry("1100x750+0+0")
        self.resizable(False, False)
        self.configure(fg_color=("#ffffff", "#0d1117"))

        # 0. Set Window Icon
        self._set_window_icon()


        # 1. Sidebar
        self.sidebar = Sidebar(self, on_tab_change=self.switch_tab)
        self.sidebar.pack(side="left", fill="both")

        # 2. Container bên phải
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.pack(side="right", fill="both", expand=True)

        # 3. Header
        self.header = Header(right_container)
        self.header.pack(side="top", fill="x")

        # 4. Content Area
        self.content_area = ctk.CTkFrame(right_container, fg_color="transparent")
        self.content_area.pack(side="top", fill="both", expand=True)

        # 5. Khởi tạo các Tab
        self.install_tab = InstallTab(self.content_area)
        self.edit_tab = EditTab(self.content_area, on_data_changed_callback=self.install_tab.load_app_list)
        self.info_tab = InfoTab(self.content_area)

        # Mặc định mở Install Tab
        self.switch_tab("install")

    def switch_tab(self, tab_name):
        self.sidebar.select_tab(tab_name)
        self.install_tab.pack_forget()
        self.edit_tab.pack_forget()
        self.info_tab.pack_forget()

        if tab_name == "install":
            self.header.set_title("CHỌN ỨNG DỤNG CẦN CÀI ĐẶT")
            self.install_tab.pack(fill="both", expand=True)
            self.install_tab.load_app_list()
        elif tab_name == "edit":
            self.header.set_title("QUẢN LÝ & CHỈNH SỬA ỨNG DỤNG")
            self.edit_tab.pack(fill="both", expand=True)
            self.edit_tab.load_edit_app_list()
        elif tab_name == "info":
            self.header.set_title("VỀ ỨNG DỤNG")
            self.info_tab.pack(fill="both", expand=True)

    def _set_window_icon(self):
        def apply_icon():
            try:
                # Xác định đường dẫn icon dựa trên việc có đang chạy file .exe hay không
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                icon_path = os.path.join(base_path, "gui", "assets", "icons", "title-logo.png")
                
                if os.path.exists(icon_path):
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    # Chuyển đổi sang PhotoImage để tkinter có thể hiểu được
                    self.icon_photo = ImageTk.PhotoImage(img)
                    self.iconphoto(False, self.icon_photo)
            except Exception as e:
                print(f"Không thể thiết lập icon cửa sổ: {e}")

        # Chạy sau 200ms để đảm bảo CustomTkinter đã khởi tạo xong cửa sổ
        self.after(200, apply_icon)


