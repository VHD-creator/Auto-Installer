import os
import sys
import json
import customtkinter as ctk
from tkinter import messagebox
from core.config_manager import load_config
from gui.overlays.edit_overlay import EditOverlay
from gui.styles import Styles

class EditTab(ctk.CTkFrame):
    def __init__(self, master, on_data_changed_callback=None):
        super().__init__(master, fg_color="transparent")
        
        self.on_data_changed_callback = on_data_changed_callback
        self.edit_vars = []

        edit_top_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(10, 5))

        edit_header_row = ctk.CTkFrame(edit_top_frame, fg_color="transparent")
        edit_header_row.pack(fill="x", padx=10, pady=(5, 5))

        edit_title_label = ctk.CTkLabel(edit_header_row, text="Quản lý & Chỉnh sửa ứng dụng", font=Styles.FONT_TITLE_SMALL)
        edit_title_label.pack(side="left")

        self.edit_selection_label = ctk.CTkLabel(edit_header_row, text="Đã chọn: 0", font=Styles.FONT_LABEL_BOLD, text_color=Styles.COLOR_PRIMARY)
        self.edit_selection_label.pack(side="right")

        self.edit_scroll_frame = ctk.CTkScrollableFrame(edit_top_frame)
        self.edit_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        edit_bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(5, 10))

        btn_edit_frame = ctk.CTkFrame(edit_bottom_frame, fg_color="transparent")
        btn_edit_frame.pack(fill="x", padx=5, pady=5)

        self.btn_add_app = ctk.CTkButton(
            btn_edit_frame,
            text="➕ Thêm mới",
            fg_color=Styles.COLOR_SUCCESS,
            hover_color=Styles.COLOR_SUCCESS_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.open_add_overlay
        )
        self.btn_add_app.pack(side="left", padx=(5, 10))

        self.btn_del_app = ctk.CTkButton(
            btn_edit_frame,
            text="🗑️ Xóa",
            fg_color=Styles.COLOR_ERROR,
            hover_color=Styles.COLOR_ERROR_HOVER,
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            command=self.delete_apps_from_edit
        )
        self.btn_del_app.pack(side="left", padx=10)

        self.load_edit_app_list()

    def update_selection_count(self, *args):
        checked_count = sum(1 for var, _ in self.edit_vars if var.get())
        self.edit_selection_label.configure(text=f"Đã chọn: {checked_count}")

    def load_edit_app_list(self):
        for widget in self.edit_scroll_frame.winfo_children():
            widget.destroy()
            
        self.edit_vars = []
        current_apps = load_config()

        for i, app in enumerate(current_apps):
            name = app.get("name", "Unknown")
            exe = app.get("exe", "")
            var = ctk.BooleanVar(value=False)

            row_frame = ctk.CTkFrame(self.edit_scroll_frame, height=60)
            row_frame.pack_propagate(False)
            row_frame.pack(fill="x", padx=15, pady=8)

            original_bg = row_frame.cget("fg_color")

            cb = ctk.CTkCheckBox(row_frame, text="", variable=var, width=24)
            cb.pack(side="left", padx=15)

            name_lbl = ctk.CTkLabel(
                row_frame, 
                text=name, 
                font=Styles.FONT_LABEL_BOLD,
                anchor="w"
            )
            name_lbl.pack(side="left", fill="x", expand=True, padx=10)

            # Toggle checkbox when clicking row or name label
            row_frame.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))
            name_lbl.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))

            is_hovering = [False]

            def update_row_color(rf, v, nl, is_hover=False):
                if is_hover:
                    rf.configure(cursor="hand2")
                    nl.configure(cursor="hand2")
                else:
                    rf.configure(cursor="")
                    nl.configure(cursor="")

                if v.get():
                    nl.configure(text_color="white")
                    if is_hover:
                        rf.configure(fg_color=("#2980b9", "#1f618d"))
                    else:
                        rf.configure(fg_color=("#3498db", "#2980b9"))
                else:
                    nl.configure(text_color=("black", "white"))
                    if is_hover:
                        rf.configure(fg_color=("gray85", "gray25"))
                    else:
                        rf.configure(fg_color=original_bg)

            def handle_enter(e, r=row_frame, v=var, n=name_lbl):
                is_hovering[0] = True
                update_row_color(r, v, n, True)
                
            def handle_leave(e, r=row_frame, v=var, n=name_lbl):
                is_hovering[0] = False
                update_row_color(r, v, n, False)

            row_frame.bind("<Enter>", handle_enter)
            row_frame.bind("<Leave>", handle_leave)
            name_lbl.bind("<Enter>", handle_enter)
            name_lbl.bind("<Leave>", handle_leave)
            cb.bind("<Enter>", handle_enter)
            cb.bind("<Leave>", handle_leave)

            var.trace_add("write", lambda *args, r=row_frame, v=var, n=name_lbl: (update_row_color(r, v, n, is_hovering[0]), self.update_selection_count()))

            btn_edit_item = ctk.CTkButton(
                row_frame,
                text="Chỉnh sửa",
                width=100,
                height=35,
                fg_color=Styles.COLOR_SUCCESS,
                hover_color=Styles.COLOR_SUCCESS_HOVER,
                command=lambda idx=i, n=name, e=exe: self.open_edit_overlay(idx, n, e)
            )
            btn_edit_item.pack(side="right", padx=10)

            self.edit_vars.append((var, app))
            
        self.update_selection_count()

    def open_add_overlay(self):
        EditOverlay(
            self.master.master, # Get access to main right container area or top root
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

    def delete_apps_from_edit(self):
        checked_to_del = [app.get("name") for var, app in self.edit_vars if var.get()]
        if not checked_to_del:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ít nhất một ứng dụng để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(checked_to_del)} ứng dụng khỏi danh sách?")
        if not confirm:
            return

        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_path = os.path.join(base_path, "config.json")
        installers_dir = os.path.join(base_path, "installers")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data.get("apps", []):
                if item.get("name") in checked_to_del:
                    exe_name = item.get("exe")
                    if exe_name:
                        file_to_del = os.path.join(installers_dir, exe_name)
                        if os.path.exists(file_to_del):
                            try:
                                os.remove(file_to_del)
                            except:
                                pass

            data["apps"] = [item for item in data.get("apps", []) if item.get("name") not in checked_to_del]

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thực hiện xóa: {e}")

    def refresh_all(self):
        self.load_edit_app_list()
        if self.on_data_changed_callback:
            self.on_data_changed_callback()
