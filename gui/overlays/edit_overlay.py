import os
import shutil
import json
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog
from gui.styles import Styles

class EditOverlay(ctk.CTkFrame):
    def __init__(self, parent, idx=None, old_name="", old_exe="", on_success_callback=None, log_func=None):
        super().__init__(parent, fg_color=("gray20", "gray10"))
        
        self.idx = idx
        self.old_name = old_name
        self.old_exe = old_exe
        self.on_success_callback = on_success_callback
        self.log_func = log_func if log_func else print
        
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Center Frame
        center_frame = ctk.CTkFrame(
            self, 
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"], 
            corner_radius=12, 
            border_width=2, 
            border_color=Styles.COLOR_PRIMARY
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.45)

        title_text = "Thêm mới ứng dụng" if idx is None else "Chỉnh sửa ứng dụng"
        lbl = ctk.CTkLabel(center_frame, text=title_text, font=Styles.FONT_TITLE_SMALL)
        lbl.pack(pady=(15, 5))

        self.entry_rename = ctk.CTkEntry(center_frame, font=Styles.FONT_INFO, height=40, placeholder_text="Tên ứng dụng")
        if idx is not None:
            self.entry_rename.insert(0, old_name)
        self.entry_rename.pack(fill="x", padx=30, pady=10)
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

        btn_confirm = ctk.CTkButton(
            btn_action_frame, 
            text="Xác nhận", 
            fg_color=Styles.COLOR_SUCCESS, 
            hover_color=Styles.COLOR_SUCCESS_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.on_confirm
        )
        btn_confirm.pack(side="left", padx=(0, 10), expand=True, fill="x")

        btn_cancel = ctk.CTkButton(
            btn_action_frame, 
            text="Quay lại", 
            fg_color=Styles.COLOR_ERROR, 
            hover_color=Styles.COLOR_ERROR_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(10, 0), expand=True, fill="x")

    def pick_file(self):
        f_path = filedialog.askopenfilename(
            title="Chọn file cài đặt",
            filetypes=[("Executable Files", "*.exe *.msi"), ("All Files", "*.*")]
        )
        if f_path:
            self.selected_file_path[0] = f_path
            self.exe_label.configure(text=f"File mới: {os.path.basename(f_path)}")

    def on_confirm(self):
        new_name = self.entry_rename.get().strip()
        if not new_name:
            messagebox.showwarning("Cảnh báo", "Tên không được để trống!")
            return

        if self.idx is None and not self.selected_file_path[0]:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file cài đặt!")
            return

        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_path = os.path.join(base_path, "config.json")
        installers_dir = os.path.join(base_path, "installers")
        os.makedirs(installers_dir, exist_ok=True)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if self.idx is not None:
                data["apps"][self.idx]["name"] = new_name

                if self.selected_file_path[0]:
                    file_path = self.selected_file_path[0]
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(installers_dir, filename)

                    old_file_name = data["apps"][self.idx].get("exe")
                    if old_file_name and old_file_name != filename:
                        old_file_full = os.path.join(installers_dir, old_file_name)
                        if os.path.exists(old_file_full):
                            try:
                                os.remove(old_file_full)
                            except:
                                pass

                    if not os.path.exists(dest_path):
                        shutil.copy2(file_path, dest_path)

                    data["apps"][self.idx]["exe"] = filename

                self.log_func(f"[INFO] Đã cập nhật ứng dụng: {new_name}")
            else:
                file_path = self.selected_file_path[0]
                filename = os.path.basename(file_path)
                dest_path = os.path.join(installers_dir, filename)

                if not os.path.exists(dest_path):
                    shutil.copy2(file_path, dest_path)

                new_app = {
                    "name": new_name,
                    "exe": filename,
                    "type": "Install"
                }
                data["apps"].append(new_app)
                self.log_func(f"[INFO] Đã thêm ứng dụng mới: {new_name}")

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            if self.on_success_callback:
                self.on_success_callback()
                
            self.destroy()
        except Exception as e:
            self.log_func(f"[ERROR] Không thể lưu thay đổi: {e}")
            messagebox.showerror("Lỗi", f"Lỗi lưu cấu hình: {e}")
