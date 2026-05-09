import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Auto Install Tool là giải pháp hàng đầu hỗ trợ cài đặt ứng dụng hàng loạt một cách nhanh chóng, chính xác và hoàn toàn tự động. 
Phiên bản 2.6.0 (Evolution Edition) là một cuộc cách mạng về kiến trúc, mang đến sự ổn định tuyệt đối và khả năng tùy biến vô hạn.

🌟 NHỮNG CẢI TIẾN ĐỘT PHÁ TRÊN PHIÊN BẢN MỚI:

• KIẾN TRÚC OOP & FACTORY PATTERN:
Toàn bộ lõi được tái cấu trúc theo mô hình hướng đối tượng (OOP), giúp xử lý các kịch bản cài đặt phức tạp một cách mượt mà và chính xác hơn bao giờ hết.

• HỖ TRỢ ĐA DẠNG ĐỊNH DẠNG (ALL-IN-ONE):
Không chỉ dừng lại ở EXE/MSI, hệ thống hiện đã hỗ trợ đầy đủ các gói ISO/IMG, bộ cài Office (ODT) và các script tự động (PowerShell, Batch).

• QUY TRÌNH MOUNT & WAIT THÔNG MINH:
Tự động nạp (mount) ổ đĩa ảo cho các bộ cài offline, thông minh nhận diện và chờ đợi quá trình cài đặt thủ công (như Office) trước khi tự động dọn dẹp hệ thống.

• HỆ THỐNG SMART-SKIP 2.0:
Nâng cấp khả năng nhận diện phần mềm đã cài đặt qua 3 tầng bảo mật: Registry sâu, App Paths và Chữ ký tệp trên đĩa, loại bỏ hoàn toàn việc cài đè trùng lặp.

• THI THI ĐA LUỒNG & BẢO MẬT:
Tích hợp mã hóa Base64 cho câu lệnh và hệ thống xử lý tiến trình chạy ẩn (Silent) thế hệ mới, đảm bảo 100% không gây lỗi đường dẫn hay xung đột hệ thống.

• TRẢI NGHIỆM NGƯỜI DÙNG TỐI ƯU:
Giao diện hiển thị Log thời gian thực, quản lý Icon thông minh và cơ chế "Hậu kiểm" (Global Verification) để đảm bảo mọi ứng dụng đều được cài đặt thành công.

Tác giả: Phạm Sự
Cảm ơn bạn đã tin tưởng và sử dụng sản phẩm!
"""
        info_desc = ctk.CTkTextbox(info_card, font=Styles.FONT_INFO, wrap="word", fg_color="transparent", text_color=Styles.TEXT_PRIMARY)
        info_desc.insert("0.0", about_text.strip())
        info_desc.configure(state="disabled")
        info_desc.pack(fill="both", expand=True, padx=20, pady=20)
