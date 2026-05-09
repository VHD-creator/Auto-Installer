import customtkinter as ctk

from gui.styles import Styles
from core.asset_manager import AssetManager

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_tab_change):
        super().__init__(master, width=280, corner_radius=0, fg_color=("#f6f8fa", "#0d1117"))
        self.pack_propagate(False)
        self.on_tab_change = on_tab_change
        self._locked = False       # Trạng thái khoá điều hướng tab
        self._current_tab = None   # Tab đang được chọn

        # Load icons (Phóng to hơn chữ một chút)
        icon_logo = AssetManager.get_system_icon("title-logo", size=(42, 42))
        icon_install = AssetManager.get_system_icon("menu-install", size=(26, 26))
        icon_edit = AssetManager.get_system_icon("menu-edit", size=(26, 26))
        icon_info = AssetManager.get_system_icon("information", size=(26, 26))
        # 👇 Đổi tên file "version-check" thành tên PNG bạn đã đặt trong gui/assets/icons/
        icon_version = AssetManager.get_system_icon("version-check", size=(16, 16))

        # Header với Logo và Text (2 dòng như trong ảnh)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(padx=20, pady=(30, 20), fill="x")
        
        logo_label = ctk.CTkLabel(header_frame, image=icon_logo, text="")
        logo_label.pack(side="left", padx=(0, 12))
        
        title_text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_text_frame.pack(side="left")
        
        ctk.CTkLabel(title_text_frame, text="AUTO INSTALL TOOL", font=Styles.FONT_TITLE_MEDIUM, anchor="w").pack(fill="x")
        ctk.CTkLabel(title_text_frame, text="by Phạm Sự", font=Styles.FONT_DESC, text_color=Styles.TEXT_SECONDARY, anchor="w").pack(fill="x")

        # Footer (Như trong ảnh)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", padx=25, pady=25, fill="x")
        
        ctk.CTkLabel(footer_frame, image=icon_version, text="  Version 2.6.0", compound="left", font=Styles.FONT_DESC, text_color=Styles.TEXT_SECONDARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(footer_frame, text="© 2026 Phạm Sự", font=Styles.FONT_DESC, text_color=Styles.TEXT_SECONDARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(footer_frame, text="All rights reserved", font=Styles.FONT_DESC, text_color=Styles.TEXT_SECONDARY, anchor="w").pack(fill="x")

        self.btn_install_tab = ctk.CTkButton(
            self, 
            text="      Cài đặt App", 
            image=icon_install,
            compound="left",
            anchor="w",
            command=lambda: self._on_button_click("install"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_install_tab.pack(padx=15, pady=8, fill="x")

        self.btn_edit_tab = ctk.CTkButton(
            self, 
            text="      Chỉnh sửa", 
            image=icon_edit,
            compound="left",
            anchor="w",
            command=lambda: self._on_button_click("edit"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_edit_tab.pack(padx=15, pady=8, fill="x")

        self.btn_info_tab = ctk.CTkButton(
            self, 
            text="      Giới thiệu", 
            image=icon_info,
            compound="left",
            anchor="w",
            command=lambda: self._on_button_click("info"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_info_tab.pack(padx=15, pady=8, fill="x")

    def _on_button_click(self, tab_name):
        if self._locked:
            return
        self.select_tab(tab_name)
        self.on_tab_change(tab_name)

    def select_tab(self, tab_name):
        self._current_tab = tab_name  # Lưu tab đang active để khôi phục sau khi unlock
        self.btn_install_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.btn_edit_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.btn_info_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        if tab_name == "install":
            self.btn_install_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        elif tab_name == "edit":
            self.btn_edit_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        elif tab_name == "info":
            self.btn_info_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))

    def set_edit_tab_enabled(self, enabled):
        """Bật hoặc tắt nút chuyển sang tab Chỉnh sửa."""
        state = "normal" if enabled else "disabled"
        self.btn_edit_tab.configure(state=state)
        if not enabled:
            # Làm mờ nút nếu bị tắt
            self.btn_edit_tab.configure(text_color=("gray60", "gray50"))
        else:
            # Khôi phục màu nếu tab không phải là tab hiện tại
            if self._current_tab != "edit":
                self.btn_edit_tab.configure(text_color=("gray10", "gray90"))
            else:
                self.btn_edit_tab.configure(text_color=("white", "white"))

    def lock(self):
        """Khoá điều hướng tab khi overlay đang hiển thị.
        Tab đang active giữ màu sáng, các tab còn lại mờ nhẹ.
        """
        self._locked = True
        
        # Map tab name -> button
        tab_btn_map = {
            "install": self.btn_install_tab,
            "edit":    self.btn_edit_tab,
            "info":    self.btn_info_tab,
        }
        active_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        
        for tab_name, btn in tab_btn_map.items():
            if tab_name == self._current_tab:
                # Tab active: vẫn sáng, chỉ disable để không click được
                btn.configure(
                    state="disabled",
                    fg_color=active_color,
                    text_color=("white", "white"),
                    hover_color=active_color,
                )
            else:
                # Tab không active: mờ nhẹ (text mờ, nền trong suốt)
                btn.configure(
                    state="disabled",
                    fg_color="transparent",
                    text_color=("gray60", "gray50"),
                    hover_color="transparent",
                )

    def unlock(self):
        """Mở khoá điều hướng tab sau khi overlay đóng."""
        self._locked = False
        for btn in (self.btn_install_tab, self.btn_edit_tab, self.btn_info_tab):
            btn.configure(
                state="normal",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
            )
        # Khôi phục highlight cho tab đang active
        if self._current_tab:
            self.select_tab(self._current_tab)
