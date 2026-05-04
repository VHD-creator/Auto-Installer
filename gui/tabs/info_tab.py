import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Auto Install Tool là công cụ hỗ trợ cài đặt ứng dụng hàng loạt một cách nhanh chóng và tự động.
Phiên bản 2.0 (CustomTkinter Edition) mang đến trải nghiệm hiện đại với khả năng cài đặt im lặng,
giúp người dùng không cần thao tác thủ công như nhấn "Next" nhiều lần.

Ứng dụng cho phép tùy chỉnh linh hoạt thông qua file cấu hình config.json,
phù hợp cho cả người dùng cá nhân lẫn kỹ thuật viên.

• Tác giả: Phạm Sự
Cảm ơn bạn sử dụng sản phẩm!
"""
        info_desc = ctk.CTkLabel(info_card, text=about_text, font=Styles.FONT_INFO, justify="left")
        info_desc.pack(padx=30, pady=10, anchor="w")
