import os
import sys
import json
import shutil
import winsound
import customtkinter as ctk
from tkinter import messagebox, filedialog
from core.config_manager import load_config, save_config
from gui.overlays.edit_overlay import EditOverlay
from gui.styles import Styles
from core.asset_manager import AssetManager

class EditTab(ctk.CTkFrame):
    def __init__(self, master, on_data_changed_callback=None):
        super().__init__(master, fg_color="transparent")
        
        self.on_data_changed_callback = on_data_changed_callback
        self.edit_vars = []

        edit_top_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(5, 5))

        self.edit_scroll_frame = ctk.CTkScrollableFrame(edit_top_frame, fg_color="transparent")
        self.edit_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        edit_bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(5, 10))

        btn_edit_frame = ctk.CTkFrame(edit_bottom_frame, fg_color="transparent")
        btn_edit_frame.pack(fill="x", padx=5, pady=5)

        # Toolbar: Chỉ giữ nút Thêm mới vì giờ đã chuyển sang xóa từng dòng
        self.btn_add_app = ctk.CTkButton(
            btn_edit_frame,
            text="➕ Thêm mới ứng dụng",
            fg_color=Styles.COLOR_SUCCESS,
            hover_color=Styles.COLOR_SUCCESS_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.open_add_overlay
        )
        self.btn_add_app.pack(side="left", padx=5)

        self.dragged_widget = None
        self.dragged_index = -1
        self.drag_start_y = 0
        self.row_widgets = []
        self.current_apps = []

        self.load_edit_app_list()

    def load_edit_app_list(self):
        for widget in self.edit_scroll_frame.winfo_children():
            widget.destroy()
            
        self.edit_vars = []
        self.row_widgets = []
        self.current_apps = load_config()

        # Định nghĩa bảng màu đồng bộ với AppCard
        color_row_bg = ("#ffffff", "#161b22")
        color_row_border = ("#d0d7de", "#30363d")
        color_row_hover = ("#f6f8fa", "#1f242c")

        for i, app in enumerate(self.current_apps):
            name = app.get("name", "Unknown")
            exe = app.get("exe", "")

            # Row Frame với bảng màu đồng bộ
            row_frame = ctk.CTkFrame(
                self.edit_scroll_frame, 
                height=70, 
                corner_radius=10,
                border_width=1,
                border_color=color_row_border,
                fg_color=color_row_bg
            )
            row_frame.pack_propagate(False)
            row_frame.pack(fill="x", padx=10, pady=5)

            original_bg = row_frame.cget("fg_color")

            # Drag Handle
            drag_handle = ctk.CTkLabel(row_frame, text="☰", font=(Styles.FONT_FAMILY_MAIN, 20), text_color="gray50", cursor="fleur", width=30)
            drag_handle.pack(side="left", padx=(10, 0))
            
            drag_handle.bind("<ButtonPress-1>", lambda e, idx=i, w=row_frame: self.on_drag_start(e, idx, w))
            drag_handle.bind("<B1-Motion>", self.on_drag_motion)
            drag_handle.bind("<ButtonRelease-1>", self.on_drag_release)

            # 1. App Icon
            icon_name = app.get("icon", "")
            app_icon = AssetManager.get_app_icon(icon_name, size=(44, 44))

            icon_container = ctk.CTkFrame(row_frame, width=54, height=54, corner_radius=10, fg_color=("#f0f0f0", "#1a1a1a"))
            icon_container.pack(side="left", padx=12, pady=8)
            icon_container.pack_propagate(False)

            icon_lbl = ctk.CTkLabel(icon_container, text="" if app_icon else "📦", image=app_icon)
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")


            # 2. App Name
            name_lbl = ctk.CTkLabel(
                row_frame, 
                text=name, 
                font=Styles.FONT_LABEL_BOLD,
                anchor="w"
            )
            name_lbl.pack(side="left", fill="x", expand=True, padx=15)

            # 3. Action Buttons (Xóa và Chỉnh sửa)
            btn_delete_item = ctk.CTkButton(
                row_frame,
                text="Xóa",
                width=70,
                height=35,
                fg_color="transparent",
                border_width=1,
                border_color=Styles.COLOR_ERROR,
                text_color=Styles.COLOR_ERROR,
                hover_color=("#fee2e2", "#450a0a"),
                command=lambda idx=i: self.delete_single_app(idx)
            )
            btn_delete_item.pack(side="right", padx=(0, 15))

            btn_edit_item = ctk.CTkButton(
                row_frame,
                text="Chỉnh sửa",
                width=110,
                height=35,
                fg_color=Styles.COLOR_SUCCESS,
                hover_color=Styles.COLOR_SUCCESS_HOVER,
                command=lambda idx=i, n=name, e=exe: self.open_edit_overlay(idx, n, e)
            )
            btn_edit_item.pack(side="right", padx=10)

            # Row hover effect
            def handle_enter(e, r=row_frame):
                r.configure(fg_color=color_row_hover)
                
            def handle_leave(e, r=row_frame):
                r.configure(fg_color=color_row_bg)

            row_frame.bind("<Enter>", handle_enter)
            row_frame.bind("<Leave>", handle_leave)

            self.row_widgets.append(row_frame)

    def on_drag_start(self, event, idx, widget):
        self.dragged_index = idx
        self.dragged_widget = widget
        self.drag_start_y = event.y_root
        widget.configure(border_color=Styles.COLOR_PRIMARY, border_width=2)
        
    def on_drag_motion(self, event):
        if not self.dragged_widget: return
        
        current_y = event.y_root
        target_index = -1
        
        for i, w in enumerate(self.row_widgets):
            w_y = w.winfo_rooty()
            w_h = w.winfo_height()
            if w_y <= current_y <= w_y + w_h:
                target_index = i
                break
                
        if target_index != -1 and target_index != self.dragged_index:
            self.row_widgets[self.dragged_index], self.row_widgets[target_index] = self.row_widgets[target_index], self.row_widgets[self.dragged_index]
            self.current_apps[self.dragged_index], self.current_apps[target_index] = self.current_apps[target_index], self.current_apps[self.dragged_index]
            
            for w in self.row_widgets:
                w.pack_forget()
            for w in self.row_widgets:
                w.pack(fill="x", padx=10, pady=5)
                
            self.dragged_index = target_index

    def on_drag_release(self, event):
        if not self.dragged_widget: return
        
        color_row_border = ("#d0d7de", "#30363d")
        self.dragged_widget.configure(border_color=color_row_border, border_width=1)
        self.dragged_widget = None
        
        save_config(self.current_apps)
        
        self.load_edit_app_list()
        
        if self.on_data_changed_callback:
            self.on_data_changed_callback()

    def open_add_overlay(self):
        EditOverlay(
            self.master.master, 
            idx=None, 
            old_name="", 
            old_exe="", 
            on_success_callback=self.refresh_all,
            log_func=None
        )

    def open_edit_overlay(self, idx, name, exe):
        EditOverlay(
            self.master.master, 
            idx=idx, 
            old_name=name, 
            old_exe=exe, 
            on_success_callback=self.refresh_all,
            log_func=None
        )

    def delete_single_app(self, app_idx):
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa ứng dụng này?"):
            try:
                base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
                config_path = os.path.join(base_path, "config.json")
                
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                # 1. Lấy thông tin app trước khi xóa
                app_to_delete = config_data["apps"][app_idx]
                icon_name = app_to_delete.get("icon")
                exe_name = app_to_delete.get("exe")
                
                # 2. Xóa khỏi config
                config_data["apps"].pop(app_idx)
                
                # 3. Xóa file icon nếu không còn app nào dùng chung
                if icon_name:
                    other_icons = [app.get("icon") for app in config_data["apps"]]
                    if icon_name not in other_icons:
                        icon_path = os.path.join(base_path, "gui", "assets", "apps", icon_name)
                        if os.path.exists(icon_path):
                            try: os.remove(icon_path)
                            except: pass
                            
                # 4. Xóa file bộ cài trong installers nếu không còn app nào dùng chung
                if exe_name:
                    other_exes = [app.get("exe") for app in config_data["apps"]]
                    if exe_name not in other_exes:
                        if "/" in exe_name or "\\" in exe_name:
                            exe_dir = os.path.dirname(exe_name).replace("\\", "/")
                            is_dir_used = any(
                                (app.get("exe") or "").replace("\\", "/").startswith(exe_dir + "/")
                                for app in config_data["apps"]
                            )
                            if not is_dir_used:
                                full_dir_path = os.path.join(base_path, "installers", exe_dir)
                                if os.path.exists(full_dir_path) and os.path.isdir(full_dir_path):
                                    try: shutil.rmtree(full_dir_path)
                                    except: pass
                        else:
                            exe_path = os.path.join(base_path, "installers", exe_name)
                            if os.path.exists(exe_path):
                                try: os.remove(exe_path)
                                except: pass
                
                # 5. Lưu lại config
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)
                
                self.load_edit_app_list()
                if self.on_data_changed_callback:
                    self.on_data_changed_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa ứng dụng: {e}")


    def refresh_all(self):
        self.load_edit_app_list()
        if self.on_data_changed_callback:
            self.on_data_changed_callback()


