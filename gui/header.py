import customtkinter as ctk

class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=65, corner_radius=0, fg_color=("#ffffff", "#0d1117"))
        self.pack_propagate(False)

        appearance_mode_menu = ctk.CTkOptionMenu(
            self, 
            values=["System", "Dark", "Light"], 
            command=lambda mode: ctk.set_appearance_mode(mode)
        )
        appearance_mode_menu.pack(side="right", padx=20, pady=18)
