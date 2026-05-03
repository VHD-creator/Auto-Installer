import customtkinter as ctk
from core.asset_manager import AssetManager
from gui.styles import Styles
import os

class AppCard(ctk.CTkFrame):
    def __init__(self, master, name, description="Mô tả ứng dụng...", app_icon=None, command=None, **kwargs):
        # Định nghĩa bảng màu (Light, Dark)
        self.color_bg = ("#ffffff", "#161b22")
        self.color_border = ("#d0d7de", "#30363d")
        self.color_hover = ("#f6f8fa", "#1f242c")
        self.color_selected_bg = ("#ddf4ff", "#1c2b3a")
        self.color_selected_border = (Styles.COLOR_PRIMARY, "#0078d4")
        
        self.text_primary = Styles.TEXT_PRIMARY
        self.text_secondary = Styles.TEXT_SECONDARY
        
        super().__init__(master, corner_radius=12, border_width=1, border_color=self.color_border, fg_color=self.color_bg, **kwargs)
        
        self.command = command
        self.selected = False
        
        # Load Indicator Assets từ AssetManager
        self.img_checked = AssetManager.get_system_icon("check-circle", size=(24, 24))
        self.img_unchecked = AssetManager.get_system_icon("unchecked", size=(24, 24))
        
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Icon area (Left)
        self.icon_frame = ctk.CTkFrame(self, width=54, height=54, corner_radius=12, fg_color=("#f6f8fa", "#21262d"))
        self.icon_frame.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        self.icon_frame.grid_propagate(False)
        
        if app_icon:
            self.icon_label = ctk.CTkLabel(self.icon_frame, image=app_icon, text="")
        else:
            self.icon_label = ctk.CTkLabel(self.icon_frame, text="📦", font=(Styles.FONT_FAMILY_MAIN, 24))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 2. Text area (Middle)
        self.name_label = ctk.CTkLabel(self, text=name, font=Styles.FONT_LABEL_BOLD, text_color=self.text_primary, anchor="w")
        self.name_label.grid(row=0, column=1, sticky="sw", padx=(0, 10), pady=(15, 0))
        
        self.full_description = description
        self.scrolling = False
        self.marquee_offset = 0
        self.marquee_speed = 150 # milliseconds
        
        self.desc_label = ctk.CTkLabel(self, text=description, font=Styles.FONT_DESC, text_color=self.text_secondary, anchor="w")
        self.desc_label.grid(row=1, column=1, sticky="nw", padx=(0, 10), pady=(2, 15))
        
        # 3. Selection Indicator (Right)
        self.indicator = ctk.CTkLabel(self, text="", image=self.img_unchecked)
        if not self.img_unchecked:
             self.indicator.configure(text="○", font=(Styles.FONT_FAMILY_MAIN, 20), text_color=("#afb8c1", "#484f58"))
        self.indicator.grid(row=0, column=2, rowspan=2, padx=20)
        
        # Bind click events
        for widget in [self, self.name_label, self.desc_label, self.icon_frame, self.icon_label, self.indicator]:
            widget.bind("<Button-1>", self._on_click)
            
        # Hover effects
        for widget in [self, self.name_label, self.desc_label, self.icon_frame, self.icon_label, self.indicator]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, event=None):
        self.toggle_selection()
        if self.command:
            self.command()

    def _on_enter(self, event=None):
        if not self.selected:
            self.configure(border_color=("#afb8c1", "#484f58"), fg_color=self.color_hover)
        
        if self.scrolling:
            return
            
        # Bắt đầu hiệu ứng chữ chạy nếu text dài (ví dụ > 25 ký tự)
        if len(self.full_description) > 25:
            self.scrolling = True
            self._animate_marquee()

    def _on_leave(self, event=None):
        # Kiểm tra xem chuột có thực sự rời khỏi toàn bộ AppCard không
        x, y = self.winfo_pointerxy()
        target = self.winfo_containing(x, y)
        
        # Nếu vẫn đang ở trong AppCard hoặc các widget con thì không dừng
        is_inside = False
        if target == self:
            is_inside = True
        else:
            curr = target
            while curr:
                if curr == self:
                    is_inside = True
                    break
                curr = curr.master if hasattr(curr, 'master') else None
        
        if is_inside:
            return

        if not self.selected:
            self.configure(border_color=self.color_border, fg_color=self.color_bg)
            
        # Dừng hiệu ứng và reset text
        self.scrolling = False
        self.marquee_offset = 0
        self.desc_label.configure(text=self.full_description)

    def _animate_marquee(self):
        if not self.scrolling:
            return
            
        padded_text = self.full_description + "       "
        # Chạy từ phải sang trái (chuẩn marquee) giúp dễ đọc hơn để xem phần bị ẩn bên phải
        self.marquee_offset = (self.marquee_offset + 1) % len(padded_text)
        new_text = padded_text[self.marquee_offset:] + padded_text[:self.marquee_offset]
        
        self.desc_label.configure(text=new_text)
        self.after(self.marquee_speed, self._animate_marquee)

    def toggle_selection(self, state=None):
        if state is not None:
            self.selected = state
        else:
            self.selected = not self.selected
            
        if self.selected:
            self.configure(border_color=self.color_selected_border, fg_color=self.color_selected_bg)
            if self.img_checked:
                self.indicator.configure(image=self.img_checked)
            else:
                self.indicator.configure(text="●", text_color=self.color_selected_border)
        else:
            self.configure(border_color=self.color_border, fg_color=self.color_bg)
            if self.img_unchecked:
                self.indicator.configure(image=self.img_unchecked)
            else:
                self.indicator.configure(text="○", text_color=("#afb8c1", "#484f58"))
            
    def is_selected(self):
        return self.selected
