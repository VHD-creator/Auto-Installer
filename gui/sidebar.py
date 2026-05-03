import customtkinter as ctk

from gui.styles import Styles

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_tab_change):
        super().__init__(master, width=220, corner_radius=0, fg_color=("#f6f8fa", "#0d1117"))
        self.pack_propagate(False)
        self.on_tab_change = on_tab_change

        header_label = ctk.CTkLabel(self, text="AUTO INSTALL TOOL", font=Styles.FONT_TITLE_MEDIUM)
        header_label.pack(padx=20, pady=(25, 20), anchor="w")

        self.btn_install_tab = ctk.CTkButton(
            self, 
            text="📦 Cài đặt App", 
            command=lambda: self._on_button_click("install"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_install_tab.pack(padx=10, pady=8, fill="x")

        self.btn_edit_tab = ctk.CTkButton(
            self, 
            text="✏️ Chỉnh sửa", 
            command=lambda: self._on_button_click("edit"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_edit_tab.pack(padx=10, pady=8, fill="x")

        self.btn_info_tab = ctk.CTkButton(
            self, 
            text="ℹ️ Giới thiệu", 
            command=lambda: self._on_button_click("info"),
            height=45,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=Styles.FONT_BUTTON
        )
        self.btn_info_tab.pack(padx=10, pady=8, fill="x")

    def _on_button_click(self, tab_name):
        self.select_tab(tab_name)
        self.on_tab_change(tab_name)

    def select_tab(self, tab_name):
        self.btn_install_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.btn_edit_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.btn_info_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        if tab_name == "install":
            self.btn_install_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        elif tab_name == "edit":
            self.btn_edit_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        elif tab_name == "info":
            self.btn_info_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
