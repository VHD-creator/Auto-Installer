import os
import sys
import json
import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog
from core.config_manager import load_config
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

        self.load_edit_app_list()

    def load_edit_app_list(self):
        for widget in self.edit_scroll_frame.winfo_children():
            widget.destroy()
            
        self.edit_vars = []
        current_apps = load_config()

        # Định nghĩa bảng màu đồng bộ với AppCard
        color_row_bg = ("#ffffff", "#161b22")
        color_row_border = ("#d0d7de", "#30363d")
        color_row_hover = ("#f6f8fa", "#1f242c")

        for i, app in enumerate(current_apps):
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

            # 1. App Icon with Hover Overlay (Click để đổi ảnh ngay lập tức)
            icon_name = app.get("icon", "")
            app_icon = AssetManager.get_app_icon(icon_name, size=(44, 44))
            overlay_img = AssetManager.get_system_icon("edit-overlay", size=(44, 44))

            icon_container = ctk.CTkFrame(row_frame, width=54, height=54, corner_radius=10, fg_color=("#f0f0f0", "#1a1a1a"))
            icon_container.pack(side="left", padx=12, pady=8)
            icon_container.pack_propagate(False)

            icon_lbl = ctk.CTkLabel(icon_container, text="" if app_icon else "📦", image=app_icon)
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

            overlay_lbl = ctk.CTkLabel(icon_container, text="", image=overlay_img, cursor="hand2")
            overlay_lbl.bind("<Button-1>", lambda e, idx=i: self.pick_and_replace_icon(idx))
            
            def on_enter(e):
                overlay_lbl.place(relx=0.5, rely=0.5, anchor="center")
                
            def on_leave(e):
                # Kiểm tra xem chuột có thực sự rời khỏi container không
                x, y = icon_container.winfo_pointerxy()
                target = icon_container.winfo_containing(x, y)
                
                # Nếu target vẫn là container hoặc con của nó thì không ẩn
                if target == icon_container or (target and target.master == icon_container):
                    return
                overlay_lbl.place_forget()
            
            icon_container.bind("<Enter>", on_enter)
            icon_container.bind("<Leave>", on_leave)
            overlay_lbl.bind("<Leave>", on_leave) # Overlay cũng cần bind leave để tránh mất event

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
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa ứng dụng này?"):
            try:
                base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
                config_path = os.path.join(base_path, "config.json")
                
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                config_data["apps"].pop(app_idx)
                
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

    def pick_and_replace_icon(self, app_idx):
        file_path = filedialog.askopenfilename(
            title="Chọn Icon mới cho ứng dụng",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.ico")]
        )
        if not file_path:
            return

        try:
            base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            assets_apps_dir = os.path.join(base_path, "gui", "assets", "apps")
            os.makedirs(assets_apps_dir, exist_ok=True)

            ext = os.path.splitext(file_path)[1]
            new_icon_name = f"app_icon_{app_idx}_{int(os.path.getmtime(file_path))}{ext}" # Thêm timestamp để tránh cache
            dest_path = os.path.join(assets_apps_dir, new_icon_name)

            shutil.copy2(file_path, dest_path)

            config_path = os.path.join(base_path, "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config_data["apps"][app_idx]["icon"] = new_icon_name

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Thành công", f"Đã cập nhật icon mới!")
            self.load_edit_app_list()
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật icon: {e}")
