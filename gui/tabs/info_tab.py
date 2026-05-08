import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Auto Install Tool là giải pháp hàng đầu hỗ trợ cài đặt ứng dụng hàng loạt một cách nhanh chóng, chính xác và hoàn toàn tự động. 
Phiên bản 2.5.0 (Intelligence Edition) là một bước nhảy vọt về công nghệ, mang đến trải nghiệm cài đặt "không chạm" đỉnh cao.

🌟 CÁC TÍNH NĂNG ĐỘT PHÁ TRÊN V2.5.0:

🚀 SIÊU NHẬN DIỆN "SMART-HUNTING":
Tự động dò tìm flag silent (/S, /silent, /qn) ngay trong mã máy của hơn 50 loại engine cài đặt phổ biến nhất thế giới (Inno, NSIS, MSI, InstallShield...).

🧠 HỆ THỐNG "HẬU KIỂM" THÔNG MINH:
Xác thực thực tế qua Registry sau mỗi lần cài đặt. Nếu tiến trình bị hủy ngang, hệ thống sẽ nhận biết và báo chính xác trạng thái ngay lập tức.

🔍 QUÉT SÂU 3 LỚP (SMART SKIP):
Tự động bỏ qua app đã có qua Registry, App Paths và tệp thực thi trên ổ đĩa. Hỗ trợ nhận diện cả các phần mềm Portable (không cần cài đặt).

🛡️ CÔNG NGHỆ BẢO MẬT ĐA TẦNG:
Xử lý an toàn mọi đường dẫn file phức tạp qua mã hóa Base64, đảm bảo tiến trình cài đặt luôn thông suốt và chính xác tuyệt đối.

🎨 GIAO DIỆN HIỆN ĐẠI & MƯỢT MÀ:
Trải nghiệm đỉnh cao với CustomTkinter, hệ thống Log đa sắc thái và quản lý Icon chuyên nghiệp không làm khóa file hệ thống.

Tác giả: Phạm Sự
Cảm ơn bạn đã tin tưởng và sử dụng sản phẩm!
"""
        info_desc = ctk.CTkTextbox(info_card, font=Styles.FONT_INFO, wrap="word", fg_color="transparent", text_color=Styles.TEXT_PRIMARY)
        info_desc.insert("0.0", about_text.strip())
        info_desc.configure(state="disabled")
        info_desc.pack(fill="both", expand=True, padx=20, pady=20)
