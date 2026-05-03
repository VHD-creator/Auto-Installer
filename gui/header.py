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

        # Appearance Mode Menu (Căn phải)
        appearance_mode_menu = ctk.CTkOptionMenu(
            self, 
            values=["System", "Dark", "Light"], 
            command=lambda mode: ctk.set_appearance_mode(mode)
        )
        appearance_mode_menu.pack(side="right", padx=20, pady=18)

    def set_title(self, text):
        self.title_label.configure(text=text)
