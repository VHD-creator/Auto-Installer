import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Auto Install Tool là giải pháp hàng đầu hỗ trợ cài đặt ứng dụng hàng loạt một cách nhanh chóng, chính xác và hoàn toàn tự động. 
Phiên bản 2.4.0 (CustomTkinter Edition) là một bước nhảy vọt về công nghệ, mang đến trải nghiệm cài đặt "một chạm" đỉnh cao cho cả người dùng cá nhân và kỹ thuật viên chuyên nghiệp.

🌟 CÁC TÍNH NĂNG MỚI NỔI BẬT TRÊN V2.4:

🚀 HỆ THỐNG NHẬN DIỆN "ULTRA-SMART":
Tự động trích xuất Metadata và ProductCode từ lõi file .exe, .msi để đưa ra tham số cài đặt Silent (im lặng) với độ chính xác tuyệt đối.

🔍 CÔNG NGHỆ "DEEP SCAN":
Khả năng nhận diện sâu các bộ cài nén SFX (7-Zip, WinRAR), WiX Burn và các loại Wrapper phức tạp chứa MSI bên trong driver.

🧠 QUẢN LÝ CÀI ĐẶT THÔNG MINH (SMART SKIP):
Tự động bỏ qua các ứng dụng đã có trên máy bằng thuật toán đối soát Registry và Fuzzy Matching tiên tiến, ngăn chặn tình trạng cài đè lãng phí thời gian.

📂 MỞ RỘNG HỖ TRỢ ĐA ĐỊNH DẠNG:
Hỗ trợ thực thi script .bat, .cmd và tự động mount đĩa ảo cho file .iso, .img chỉ với một cú click chuột.

🎨 TỐI ƯU HÓA TRẢI NGHIỆM (UX/UI):
Giao diện hiện đại, hệ thống Log tiếng Việt thời gian thực hiển thị minh bạch mọi tiến trình và tham số cài đặt.

⚡ HIỆU NĂNG VÀ BẢO MẬT:
Xử lý đa luồng (Multithreading) giúp ứng dụng luôn mượt mà. Cơ chế ngăn chặn đa tiến trình và kiểm tra quyền Admin đảm bảo môi trường cài đặt an toàn nhất.

🧹 QUẢN LÝ DỮ LIỆU SẠCH:
Tự động dọn dẹp rác dữ liệu và tối ưu hóa file cấu hình khi thay đổi danh sách ứng dụng.

Tác giả: Phạm Sự
Cảm ơn bạn đã tin tưởng và sử dụng sản phẩm!
"""
        info_desc = ctk.CTkTextbox(info_card, font=Styles.FONT_INFO, wrap="word", fg_color="transparent", text_color=Styles.TEXT_PRIMARY)
        info_desc.insert("0.0", about_text.strip())
        info_desc.configure(state="disabled")
        info_desc.pack(fill="both", expand=True, padx=20, pady=20)
