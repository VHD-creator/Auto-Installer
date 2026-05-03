import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from core.config_manager import load_config
from core.process_runner import run_installation
from core.asset_manager import AssetManager
from gui.components.app_card import AppCard
from gui.styles import Styles
import time

class InstallTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.vars = []
        
        # Top Frame
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(5, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(top_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cấu hình sẵn trọng số cho 3 cột để tránh lỗi tính toán kích thước ban đầu
        self.scroll_frame.grid_columnconfigure(0, weight=1, uniform="column")
        self.scroll_frame.grid_columnconfigure(1, weight=1, uniform="column")
        self.scroll_frame.grid_columnconfigure(2, weight=1, uniform="column")

        # Bottom Frame
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=(5, 10))

        btn_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)

        self.btn_select_all = ctk.CTkButton(
            btn_frame, 
            text="Chọn tất cả", 
            command=self.select_all,
            height=40,
            font=Styles.FONT_BUTTON_SMALL
        )
        self.btn_select_all.pack(side="left", padx=(5, 10))
        self.selection_status_label = None # Sẽ hiển thị trong nút Cài đặt

        self.btn_install = ctk.CTkButton(
            btn_frame, 
            text="Cài đặt (0)", 
            command=self.install_apps, 
            height=40,
            font=Styles.FONT_BUTTON_SMALL,
            fg_color=Styles.COLOR_SUCCESS,
            hover_color=Styles.COLOR_SUCCESS_HOVER
        )
        self.btn_install.pack(side="right", padx=5)

        # Thanh Progress bar
        self.progress = ctk.CTkProgressBar(self.bottom_frame, orientation="horizontal", height=15)
        self.progress.pack(fill="x", padx=10, pady=10)
        self.progress.set(0)

        # Khung Log dạng bảng (Không Header)
        self.log_container = ctk.CTkFrame(self.bottom_frame, fg_color=("#f5f5f5", "#151515"), corner_radius=8)
        self.log_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_scroll_frame = ctk.CTkScrollableFrame(self.log_container, fg_color="transparent", corner_radius=0)
        self.log_scroll_frame.pack(fill="both", expand=True)
        
        # Cấu hình grid cho log_scroll_frame
        self.log_scroll_frame.grid_columnconfigure(0, minsize=100) # Cố định 100px cho Timestamp
        self.log_scroll_frame.grid_columnconfigure(1, minsize=100) # Cố định 100px cho Status
        self.log_scroll_frame.grid_columnconfigure(2, weight=1)    # Nội dung co giãn
        
        self.log_row_count = 0

        if self.load_app_list():
            self.log({"status": "INFO", "msg": "Đã tải danh sách ứng dụng từ config.json thành công."})

    def log(self, msg):
        self.after(0, lambda: self._log(msg))

    def _log(self, data):
        timestamp = time.strftime("[%H:%M:%S]")
        status = "INFO"
        status_color = Styles.TEXT_SECONDARY # Mặc định cho INFO
        content = ""

        # Nếu dữ liệu là Dictionary (Xử lý trực tiếp)
        if isinstance(data, dict):
            status = data.get("status", "INFO")
            content = data.get("msg", "")
            
            if status == "SUCCESS" or status == "SUMMARY":
                status_color = Styles.COLOR_SUCCESS
                if status == "SUMMARY":
                    content = f"Hoàn thành: {data.get('success', 0)}/{data.get('total', 0)} ứng dụng"
            elif status == "ERROR":
                status_color = Styles.COLOR_ERROR
            elif status == "INSTALL":
                status_color = Styles.COLOR_PRIMARY
            elif status == "DONE" or status == "ABORTED":
                status_color = Styles.COLOR_WARNING
            elif status == "INFO":
                status_color = Styles.COLOR_PRIMARY # Cho INFO nổi bật hơn một chút
                
        # Nếu dữ liệu là String (Các log đơn giản không màu)
        else:
            content = data
            
        # Tạo row frame (Cố định layout)
        row_frame = ctk.CTkFrame(self.log_scroll_frame, fg_color="transparent", corner_radius=0, height=28)
        row_frame.grid(row=self.log_row_count, column=0, columnspan=3, sticky="ew")
        row_frame.grid_columnconfigure(0, minsize=100)
        row_frame.grid_columnconfigure(1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.pack_propagate(False)

        # Cột 1: Timestamp (Căn trái)
        ctk.CTkLabel(row_frame, text=timestamp, font=Styles.FONT_LOG, text_color=Styles.TEXT_SECONDARY).grid(row=0, column=0, padx=(5, 15), sticky="w")
        
        # Cột 2: Status (Căn trái + In đậm)
        ctk.CTkLabel(row_frame, text=status, font=Styles.FONT_LOG_BOLD, text_color=status_color).grid(row=0, column=1, padx=0, sticky="w")
        
        # Cột 3: Content (Căn trái)
        ctk.CTkLabel(row_frame, text=content, font=Styles.FONT_LOG, anchor="w").grid(row=0, column=2, padx=5, sticky="w")

        self.log_row_count += 1
        
        # Auto scroll xuống cuối
        self.after(10, lambda: self.log_scroll_frame._parent_canvas.yview_moveto(1.0))

    def clear_log(self):
        for widget in self.log_scroll_frame.winfo_children():
            widget.destroy()
        self.log_row_count = 0

    def load_app_list(self):
        # Ép ứng dụng cập nhật kích thước thực tế của khung hình trước khi tính toán grid
        self.update()
        
        # Xóa các card cũ trong scroll_frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        try:
            apps = load_config()
            self.vars = []
            columns = 3
            
            # Sử dụng uniform="column" để ép các cột luôn có chiều rộng bằng chẵn nhau
            self.scroll_frame.grid_columnconfigure(0, weight=1, uniform="column")
            self.scroll_frame.grid_columnconfigure(1, weight=1, uniform="column")
            self.scroll_frame.grid_columnconfigure(2, weight=1, uniform="column")

            for i, app in enumerate(apps):
                name = app.get("name", "Unknown")
                exe = app.get("exe", "")
                icon_name = app.get("icon", "") 
                description = app.get("description", f"Ứng dụng {name}")
                
                # Load icon thông qua AssetManager sử dụng tên file trong config
                app_icon = AssetManager.get_app_icon(icon_name)
                
                # Tạo card trực tiếp trong scroll_frame
                card = AppCard(
                    self.scroll_frame, 
                    name=name, 
                    description=description, 
                    app_icon=app_icon,
                    command=self.update_select_all_btn
                )
                
                r = i // columns
                c = i % columns
                card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
                
                self.vars.append({"exe": exe, "name": name, "card": card})
                
            self.update_select_all_btn()
            return True
        except Exception as e:
            self.log({"status": "ERROR", "msg": f"Lỗi nạp cấu hình: {e}"})
            return False

    def toggle_chip(self, var, btn):
        new_state = not var.get()
        var.set(new_state)
        if new_state:
            btn.configure(fg_color="#2ecc71", hover_color="#27ae60")
        else:
            btn.configure(fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"))
        self.update_select_all_btn()

    def update_select_all_btn(self):
        checked_count = sum(1 for item in self.vars if item["card"].is_selected())
        self.btn_install.configure(text=f"Cài đặt ({checked_count})")

        all_selected = all(item["card"].is_selected() for item in self.vars) if self.vars else False
        if all_selected:
            self.btn_select_all.configure(
                text="Bỏ chọn tất cả", 
                command=self.deselect_all, 
                fg_color=Styles.COLOR_ERROR, 
                hover_color=Styles.COLOR_ERROR_HOVER
            )
        else:
            self.btn_select_all.configure(
                text="Chọn tất cả", 
                command=self.select_all, 
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            )

    def select_all(self):
        for item in self.vars:
            item["card"].toggle_selection(True)
        self.update_select_all_btn()

    def deselect_all(self):
        for item in self.vars:
            item["card"].toggle_selection(False)
        self.update_select_all_btn()

    def install_apps(self):
        self.btn_install.configure(state="disabled")
        checked = [(item["exe"], item["name"]) for item in self.vars if item["card"].is_selected()]
        if not checked:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ít nhất một ứng dụng để cài!")
            self.btn_install.configure(state="normal")
            return

        self.progress.set(0)
        self.clear_log()
        
        def on_progress(val):
            self.after(0, lambda: self.progress.set(val))
            
        def on_complete():
            self.after(0, lambda: self.btn_install.configure(state="normal"))

        run_installation(checked, self.log, on_progress, on_complete)
