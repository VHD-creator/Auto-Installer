import os
import sys
import customtkinter as ctk
from tkinter import messagebox
import tkinter.font as tkfont
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
        self.is_installing = False  # Cờ kiểm tra đang cài đặt hay không
        
        # Top Frame
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(5, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(top_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cấu hình sẵn trọng số cho 3 cột để tránh lỗi tính toán kích thước ban đầu
        self.scroll_frame.grid_columnconfigure(0, weight=1, uniform="column")
        self.scroll_frame.grid_columnconfigure(1, weight=1, uniform="column")
        self.scroll_frame.grid_columnconfigure(2, weight=1, uniform="column")

        # Bottom Frame (Cố định chiều cao để không chiếm quá nhiều không gian)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent", height=280)
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(5, 10))
        self.bottom_frame.pack_propagate(False)

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

        # Khung Log dạng Textbox
        self.log_textbox = ctk.CTkTextbox(
            self.bottom_frame, 
            fg_color=("#f5f5f5", "#151515"), 
            corner_radius=8, 
            font=Styles.FONT_LOG,
            wrap="word",
            state="disabled"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cấu hình màu sắc cho Textbox
        self.log_textbox.tag_config("timestamp", foreground=Styles.TEXT_SECONDARY[0])
        self.log_textbox.tag_config("SUCCESS", foreground=Styles.COLOR_SUCCESS)
        self.log_textbox.tag_config("ERROR", foreground=Styles.COLOR_ERROR)
        self.log_textbox.tag_config("INSTALL", foreground=Styles.COLOR_PRIMARY)
        self.log_textbox.tag_config("WARNING", foreground=Styles.COLOR_WARNING)
        self.log_textbox.tag_config("INFO", foreground=Styles.COLOR_PRIMARY)
        self.log_textbox.tag_config("SKIP", foreground="#f39c12")  # Màu cam vàng cho app bỏ qua
        
        # Cấu hình tự động thụt lề và các mốc Tab (tabs) để chia thành 3 cột riêng biệt
        try:
            # Lấy đúng font đã được scale của tkinter Text bên dưới để tính toán chính xác số pixel
            actual_font_str = self.log_textbox._textbox.cget("font")
            actual_font = tkfont.Font(font=actual_font_str)
            
            # Cột 2 (Status) bắt đầu sau Cột 1 (Timestamp ~ 10 ký tự) + 15px khoảng cách
            tab1_px = actual_font.measure("[00:00:00]") + 15
            # Cột 3 (Content) bắt đầu sau Cột 2 (Status dài nhất ~ 7 ký tự) + 20px khoảng cách
            tab2_px = tab1_px + actual_font.measure("SUCCESS") + 20
            
            # Tạo font in đậm an toàn (không bị lỗi tỷ lệ scale của customtkinter)
            bold_font_config = actual_font.actual()
            bold_font_config["weight"] = "bold"
            bold_font = tkfont.Font(**bold_font_config)
            self.log_textbox._textbox.tag_config("bold", font=bold_font)
            
        except Exception:
            tab1_px = 90
            tab2_px = 180
            
        # Gán tab stops cho toàn bộ textbox
        self.log_textbox._textbox.configure(tabs=(tab1_px, "l", tab2_px, "l"))
        # Gán lmargin2 (thụt lề cho các dòng rớt xuống) bằng đúng mốc tab2_px
        self.log_textbox._textbox.tag_config("log_wrap", lmargin2=tab2_px)

        if self.load_app_list():
            self.log({"status": "INFO", "msg": "Đã tải danh sách ứng dụng từ config.json thành công."})

    def log(self, msg):
        self.after(0, lambda: self._log(msg))

    def _log(self, data):
        timestamp = time.strftime("[%H:%M:%S]")
        status = "INFO"
        content = ""
        tag = "INFO"

        # Nếu dữ liệu là Dictionary (Xử lý trực tiếp)
        if isinstance(data, dict):
            status = data.get("status", "INFO")
            content = data.get("msg", "")
            
            if status == "SUCCESS" or status == "SUMMARY":
                tag = "SUCCESS"
                if status == "SUMMARY":
                    content = f"Hoàn thành: {data.get('success', 0)}/{data.get('total', 0)} thành công"
            elif status == "ERROR":
                tag = "ERROR"
            elif status == "INSTALL":
                tag = "INSTALL"
            elif status == "WARNING":
                tag = "WARNING"
            elif status == "SKIP":
                tag = "SKIP"
            elif status in ["DONE", "ABORTED", "CANCEL"]:
                tag = "WARNING"
            elif status == "INFO":
                tag = "INFO"
                
        # Nếu dữ liệu là String
        else:
            content = data
            status = ""

        self.log_textbox.configure(state="normal")
        
        # Chèn Timestamp (Tab sang Cột 2)
        self.log_textbox.insert("end", f"{timestamp}\t", "timestamp")
        
        # Chèn Status (Tab sang Cột 3)
        if status:
            self.log_textbox.insert("end", f"{status}\t", (tag, "bold"))
        else:
            self.log_textbox.insert("end", "\t\t")
            
        # Chèn Content với tag log_wrap để các dòng phụ tự thụt lề
        self.log_textbox.insert("end", f"{content}\n", "log_wrap")
        
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("0.0", "end")
        self.log_textbox.configure(state="disabled")

    def load_app_list(self):
        # Ép ứng dụng cập nhật kích thước thực tế của khung hình trước khi tính toán grid
        self.update_idletasks()
        
        # Xóa các card cũ trong scroll_frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Thêm một chút delay nhỏ để CustomTkinter có thời gian dọn dẹp widget cũ
        self.after(10)
            
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
            # Cập nhật lại giao diện để scrollbar xuất hiện đúng
            self.after(100, self.update_idletasks)
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

    def set_interaction_state(self, state):
        """Khóa hoặc mở khóa tương tác của toàn bộ giao diện cài đặt."""
        new_tk_state = "normal" if state else "disabled"
        
        # 1. Khóa/Mở khóa các Card ứng dụng
        for item in self.vars:
            item["card"].set_enabled(state)
            
        # 2. Khóa/Mở khóa các nút chức năng
        self.btn_select_all.configure(state=new_tk_state)
        self.btn_install.configure(state=new_tk_state)

        # 3. Thông báo cho MainApp để khóa Sidebar (tab Chỉnh sửa)
        if hasattr(self.master.master.master, "set_navigation_locked"):
            self.master.master.master.set_navigation_locked(not state)

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
        self.is_installing = True
        self.set_interaction_state(False)
        
        def on_progress(val):
            self.after(0, lambda: self.progress.set(val))
            
        def on_complete():
            def _finish():
                self.is_installing = False
                self.set_interaction_state(True)
                self.deselect_all()
            self.after(0, _finish)

        run_installation(checked, self.log, on_progress, on_complete)
