import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Công cụ tự động cài đặt ứng dụng hàng loạt (Auto Install Tool).

• Phiên bản: 2.0 (CustomTkinter Edition)
• Tính năng: Cài đặt im lặng, không cần bấm Next.
• Cấu hình: Dễ dàng tùy chỉnh qua file config.json.
• Tác giả: Phạm Sự

Cảm ơn bạn đã sử dụng sản phẩm!
"""
        info_desc = ctk.CTkLabel(info_card, text=about_text, font=Styles.FONT_INFO, justify="left")
        info_desc.pack(padx=30, pady=10, anchor="w")
