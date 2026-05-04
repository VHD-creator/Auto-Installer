import customtkinter as ctk
from gui.styles import Styles

class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=65, corner_radius=0, fg_color=("#ffffff", "#0d1117"))
        self.pack_propagate(False)

        # Title Label (Căn trái)
        self.title_label = ctk.CTkLabel(
            self, 
            text="", 
            font=Styles.FONT_TITLE_SMALL,
            text_color=Styles.TEXT_PRIMARY
        )
        self.title_label.pack(side="left", padx=25, pady=18)

        # Appearance Mode Menu (Căn phải - Tùy chỉnh màu sắc đẹp hơn)
        appearance_mode_menu = ctk.CTkOptionMenu(
            self, 
            values=["System", "Dark", "Light"], 
            command=lambda mode: ctk.set_appearance_mode(mode),
            width=120,
            height=32,
            font=Styles.FONT_DESC,
            fg_color=("#f3f4f6", "#1f2937"), # Nền nút
            button_color=("#e5e7eb", "#374151"), # Nền phần mũi tên
            button_hover_color=Styles.COLOR_PRIMARY,
            dropdown_fg_color=("#ffffff", "#111827"), # Nền danh sách đổ xuống
            dropdown_hover_color=Styles.COLOR_PRIMARY,
            dropdown_text_color=Styles.TEXT_PRIMARY,
            text_color=Styles.TEXT_PRIMARY,
            corner_radius=8
        )
        appearance_mode_menu.pack(side="right", padx=20, pady=18)


    def set_title(self, text):
        self.title_label.configure(text=text)
