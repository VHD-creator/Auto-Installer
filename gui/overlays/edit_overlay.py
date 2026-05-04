import os
import shutil
import json
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
from gui.styles import Styles
from core.asset_manager import AssetManager

class EditOverlay(ctk.CTkFrame):
    def __init__(self, parent, idx=None, old_name="", old_exe="", on_success_callback=None, log_func=None):
        super().__init__(parent, fg_color=("gray20", "gray10"))
        
        self.idx = idx
        self.old_name = old_name
        self.old_exe = old_exe
        self.on_success_callback = on_success_callback
        self.log_func = log_func if log_func else print
        self.icon_deleted = False
        self.copy_whole_folder = False
        
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Center Frame
        center_frame = ctk.CTkFrame(
            self, 
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"], 
            corner_radius=12, 
            border_width=2, 
            border_color=Styles.COLOR_PRIMARY
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.55)

        title_text = "Thêm mới ứng dụng" if idx is None else "Chỉnh sửa ứng dụng"
        lbl = ctk.CTkLabel(center_frame, text=title_text, font=Styles.FONT_TITLE_SMALL)
        lbl.pack(pady=(15, 5))

        # Icon & Name Layout
        icon_row = ctk.CTkFrame(center_frame, fg_color="transparent")
        icon_row.pack(fill="x", padx=30, pady=(10, 5))
        
        # Load current data if editing
        current_icon_img = None
        old_desc = ""
        if idx is not None:
            base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            config_path = os.path.join(base_path, "config.json")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    app_data = config_data["apps"][idx]
                    icon_name = app_data.get("icon", "")
                    old_desc = app_data.get("description", "")
                    current_icon_img = AssetManager.get_app_icon(icon_name, size=(48, 48))
            except: pass

        self.icon_preview = ctk.CTkLabel(
            icon_row, 
            text="" if current_icon_img else "📦", 
            image=current_icon_img,
            font=(Styles.FONT_FAMILY_MAIN, 32), 
            width=64, 
            height=64, 
            corner_radius=12, 
            fg_color=("gray90", "gray20")
        )
        self.icon_preview.pack(side="left", padx=(0, 15))
        
        info_frame = ctk.CTkFrame(icon_row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        self.entry_rename = ctk.CTkEntry(info_frame, font=Styles.FONT_INFO, height=35, placeholder_text="Tên ứng dụng")
        if idx is not None:
            self.entry_rename.insert(0, old_name)
        self.entry_rename.pack(fill="x", pady=(0, 5))
        
        self.selected_icon_path = [None]
        
        btn_icon_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_icon_row.pack(anchor="w", pady=(2, 0))

        self.btn_pick_icon = ctk.CTkButton(
            btn_icon_row, 
            text="Chọn Icon (PNG/ICO)", 
            height=24, 
            font=Styles.FONT_DESC,
            command=self.pick_icon,
            fg_color=("gray80", "gray30"),
            text_color=Styles.TEXT_PRIMARY
        )
        self.btn_pick_icon.pack(side="left", padx=(0, 5))

        self.btn_remove_icon = ctk.CTkButton(
            btn_icon_row, 
            text="Xóa Icon", 
            height=24, 
            width=80,
            font=Styles.FONT_DESC,
            command=self.remove_icon,
            fg_color=Styles.COLOR_ERROR,
            hover_color=Styles.COLOR_ERROR_HOVER,
            text_color="white"
        )
        self.btn_remove_icon.pack(side="left")

        self.entry_desc = ctk.CTkEntry(center_frame, font=Styles.FONT_DESC, height=35, placeholder_text="Mô tả ngắn gọn về ứng dụng...")
        if idx is not None:
            self.entry_desc.insert(0, old_desc)
        self.entry_desc.pack(fill="x", padx=30, pady=(5, 0))
        
        self.lbl_note = ctk.CTkLabel(
            center_frame, 
            text="* Lưu ý: vui lòng chạy quyền admin Unikey trước khi thao tác", 
            font=(Styles.FONT_FAMILY_MAIN, 11, "italic"),
            text_color=Styles.COLOR_ERROR,
            anchor="w"
        )
        self.lbl_note.pack(fill="x", padx=35, pady=(2, 10))
        
        self.entry_rename.focus()
        if idx is not None:
            self.entry_rename.select_range(0, "end")

        file_layout = ctk.CTkFrame(center_frame, fg_color="transparent")
        file_layout.pack(fill="x", padx=30, pady=10)

        exe_text = f"File: {old_exe}" if old_exe else "File: Chưa chọn file"
        self.exe_label = ctk.CTkLabel(
            file_layout, 
            text=exe_text, 
            font=Styles.FONT_DESC,
            anchor="w"
        )
        self.exe_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.selected_file_path = [None]

        btn_change_file = ctk.CTkButton(
            file_layout, 
            text="Thay đổi" if idx is not None else "Chọn file", 
            width=100, 
            height=35,
            command=self.pick_file,
            fg_color=Styles.COLOR_PRIMARY,
            hover_color=("#2980b9", "#1f618d")
        )
        btn_change_file.pack(side="right")

        btn_action_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        btn_action_frame.pack(fill="x", padx=30, pady=(20, 10))

        self.btn_confirm = ctk.CTkButton(
            btn_action_frame, 
            text="Xác nhận", 
            fg_color=Styles.COLOR_SUCCESS, 
            hover_color=Styles.COLOR_SUCCESS_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.on_confirm
        )
        self.btn_confirm.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.btn_cancel = ctk.CTkButton(
            btn_action_frame, 
            text="Quay lại", 
            fg_color=Styles.COLOR_ERROR, 
            hover_color=Styles.COLOR_ERROR_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.destroy
        )
        self.btn_cancel.pack(side="right", padx=(10, 0), expand=True, fill="x")

    def pick_file(self):
        f_path = filedialog.askopenfilename(
            title="Chọn file cài đặt",
            filetypes=[("Install Files", "*.exe *.msi *.iso *.cmd *.bat"), ("All Files", "*.*")]
        )
        if f_path:
            self.selected_file_path[0] = f_path
            self.exe_label.configure(text=f"File mới: {os.path.basename(f_path)}")
            
            file_dir = os.path.dirname(f_path)
            try:
                other_files = [f for f in os.listdir(file_dir) if f != os.path.basename(f_path) and os.path.isfile(os.path.join(file_dir, f))]
                if other_files:
                    ans = messagebox.askyesno("Copy toàn bộ thư mục?", "Thư mục chứa file này còn có các file khác (có thể là file phụ trợ).\nBạn có muốn copy TOÀN BỘ thư mục này vào phần mềm không?")
                    self.copy_whole_folder = ans
                else:
                    self.copy_whole_folder = False
            except Exception:
                self.copy_whole_folder = False

    def pick_icon(self):
        f_path = filedialog.askopenfilename(
            title="Chọn Icon cho ứng dụng",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.ico"), ("All Files", "*.*")]
        )
        if f_path:
            self.selected_icon_path[0] = f_path
            self.icon_deleted = False
            try:
                pil_img = Image.open(f_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
                self.icon_preview.configure(image=ctk_img, text="")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể nạp icon: {e}")

    def remove_icon(self):
        self.selected_icon_path[0] = None
        self.icon_deleted = True
        self.icon_preview.configure(image="", text="📦")

    def on_confirm(self):
        new_name = self.entry_rename.get().strip()
        new_desc = self.entry_desc.get().strip()
        if not new_name:
            messagebox.showwarning("Cảnh báo", "Tên không được để trống!")
            return

        if self.idx is None and not self.selected_file_path[0]:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file cài đặt!")
            return

        self.btn_confirm.configure(state="disabled", text="Đang xử lý...")
        self.btn_cancel.configure(state="disabled")

        def save_process():
            base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            config_path = os.path.join(base_path, "config.json")
            installers_dir = os.path.join(base_path, "installers")
            os.makedirs(installers_dir, exist_ok=True)

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if self.idx is not None:
                    data["apps"][self.idx]["name"] = new_name
                    data["apps"][self.idx]["description"] = new_desc

                    if self.selected_file_path[0]:
                        file_path = self.selected_file_path[0]
                        filename = os.path.basename(file_path)

                        if getattr(self, "copy_whole_folder", False):
                            safe_folder_name = "".join([c for c in new_name if c.isalnum() or c in (" ", "-", "_")]).strip()
                            if not safe_folder_name: safe_folder_name = f"app_{self.idx}"
                            dest_dir = os.path.join(installers_dir, safe_folder_name)
                            if os.path.exists(dest_dir):
                                shutil.rmtree(dest_dir, ignore_errors=True)
                            shutil.copytree(os.path.dirname(file_path), dest_dir)
                            data["apps"][self.idx]["exe"] = f"{safe_folder_name}/{filename}"
                        else:
                            dest_path = os.path.join(installers_dir, filename)
                            old_file_name = data["apps"][self.idx].get("exe")
                            if old_file_name and old_file_name != filename:
                                old_file_full = os.path.join(installers_dir, old_file_name)
                                if os.path.exists(old_file_full) and os.path.isfile(old_file_full):
                                    try: os.remove(old_file_full)
                                    except: pass
                            if not os.path.exists(dest_path):
                                shutil.copy2(file_path, dest_path)
                            data["apps"][self.idx]["exe"] = filename
                    
                    # Handle Icon Update
                    if self.icon_deleted:
                        old_icon_name = data["apps"][self.idx].get("icon")
                        if old_icon_name:
                            # Xóa icon cũ nếu không có app nào khác dùng
                            other_icons = [app.get("icon") for i, app in enumerate(data["apps"]) if i != self.idx]
                            if old_icon_name not in other_icons:
                                old_icon_full = os.path.join(AssetManager.ASSETS_DIR, "apps", old_icon_name)
                                if os.path.exists(old_icon_full):
                                    try: os.remove(old_icon_full)
                                    except: pass
                            if "icon" in data["apps"][self.idx]:
                                del data["apps"][self.idx]["icon"]
                    
                    elif self.selected_icon_path[0]:
                        old_icon_name = data["apps"][self.idx].get("icon")
                        
                        icon_src = self.selected_icon_path[0]
                        icon_ext = os.path.splitext(icon_src)[1]
                        safe_name = "".join([c for c in new_name if c.isalnum()]).lower()
                        icon_filename = f"{safe_name}{icon_ext}"
                        
                        # Xóa icon cũ nếu khác icon mới và không có app nào khác đang dùng
                        if old_icon_name and old_icon_name != icon_filename:
                            other_icons = [app.get("icon") for i, app in enumerate(data["apps"]) if i != self.idx]
                            if old_icon_name not in other_icons:
                                old_icon_full = os.path.join(AssetManager.ASSETS_DIR, "apps", old_icon_name)
                                if os.path.exists(old_icon_full):
                                    try: os.remove(old_icon_full)
                                    except: pass

                        assets_apps_dir = os.path.join(AssetManager.ASSETS_DIR, "apps")
                        os.makedirs(assets_apps_dir, exist_ok=True)
                        icon_dest = os.path.join(assets_apps_dir, icon_filename)
                        shutil.copy2(icon_src, icon_dest)
                        data["apps"][self.idx]["icon"] = icon_filename

                    self.log_func(f"[INFO] Đã cập nhật ứng dụng: {new_name}")
                else:
                    file_path = self.selected_file_path[0]
                    filename = os.path.basename(file_path)
                    
                    if getattr(self, "copy_whole_folder", False):
                        safe_folder_name = "".join([c for c in new_name if c.isalnum() or c in (" ", "-", "_")]).strip()
                        if not safe_folder_name: safe_folder_name = "new_app"
                        dest_dir = os.path.join(installers_dir, safe_folder_name)
                        if os.path.exists(dest_dir):
                            shutil.rmtree(dest_dir, ignore_errors=True)
                        shutil.copytree(os.path.dirname(file_path), dest_dir)
                        saved_exe = f"{safe_folder_name}/{filename}"
                    else:
                        dest_path = os.path.join(installers_dir, filename)
                        if not os.path.exists(dest_path):
                            shutil.copy2(file_path, dest_path)
                        saved_exe = filename

                    new_app = {
                        "name": new_name,
                        "description": new_desc,
                        "exe": saved_exe,
                        "type": "Install"
                    }
                    
                    # Handle New Icon
                    if self.selected_icon_path[0]:
                        icon_src = self.selected_icon_path[0]
                        icon_ext = os.path.splitext(icon_src)[1]
                        safe_name = "".join([c for c in new_name if c.isalnum()]).lower()
                        icon_filename = f"{safe_name}{icon_ext}"
                        
                        assets_apps_dir = os.path.join(AssetManager.ASSETS_DIR, "apps")
                        os.makedirs(assets_apps_dir, exist_ok=True)
                        icon_dest = os.path.join(assets_apps_dir, icon_filename)
                        shutil.copy2(icon_src, icon_dest)
                        new_app["icon"] = icon_filename
                    
                    data["apps"].append(new_app)
                    self.log_func(f"[INFO] Đã thêm ứng dụng mới: {new_name}")

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                # Xóa cache icon để giao diện cập nhật ngay lập tức
                AssetManager.clear_cache()

                def on_success():
                    if self.on_success_callback:
                        self.on_success_callback()
                    self.destroy()

                self.after(0, on_success)
            except Exception as e:
                self.log_func(f"[ERROR] Không thể lưu thay đổi: {e}")
                
                def on_error():
                    messagebox.showerror("Lỗi", f"Lỗi lưu cấu hình: {e}")
                    self.btn_confirm.configure(state="normal", text="Xác nhận")
                    self.btn_cancel.configure(state="normal")
                
                self.after(0, on_error)

        threading.Thread(target=save_process, daemon=True).start()
