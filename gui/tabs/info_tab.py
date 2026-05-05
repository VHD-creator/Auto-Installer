import customtkinter as ctk
from gui.styles import Styles

class InfoTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        info_card = ctk.CTkFrame(self)
        info_card.pack(fill="both", padx=40, pady=20, expand=True)

        about_text = """
Auto Install Tool là công cụ hỗ trợ cài đặt ứng dụng hàng loạt một cách nhanh chóng và tự động.
Phiên bản 2.1.0 (CustomTkinter Edition) mang đến trải nghiệm hiện đại với khả năng cài đặt im lặng,
giúp người dùng không cần thao tác thủ công như nhấn "Next" nhiều lần. 

Một số file đuôi iso, bat hoặc cmd sẽ không cài im lặng mà sẽ hiện GUI lên cho người dùng thao tác dễ dàng.

Ứng dụng cho phép tùy chỉnh linh hoạt thông qua file cấu hình config.json,
phù hợp cho cả người dùng cá nhân lẫn kỹ thuật viên.

🌟 CÁC TÍNH NĂNG MỚI NỔI BẬT:
• Hỗ trợ đa dạng file cài đặt: Bổ sung khả năng chạy file .bat, .cmd và tự động mount ổ đĩa ảo cho file .iso.
• Tùy chỉnh ứng dụng: Thêm trường Mô tả chi tiết cho ứng dụng, đồng thời hỗ trợ thay đổi hoặc xóa Icon (ảnh đại diện).
• Sắp xếp ứng dụng: Tùy ý sắp xếp thứ tự cài đặt của các ứng dụng. 
• Quản lý dữ liệu thông minh: Xử lý và dọn dẹp sạch sẽ thư mục ứng dụng khi người dùng quyết định xóa phần mềm.
• Tối ưu hóa trải nghiệm: Các tác vụ nặng (như sao chép thư mục lớn) được chạy ngầm giúp giao diện mượt mà, không bị treo.
• Cảnh báo người dùng chạy quyền Admin cho Unikey để đảm bảo gõ tiếng Việt không bị lỗi.
• Cải thiện giao diện đẹp mắt dễ dùng hơn

• Tác giả: Phạm Sự
Cảm ơn bạn đã tin tưởng và sử dụng sản phẩm!
"""
        info_desc = ctk.CTkTextbox(info_card, font=Styles.FONT_INFO, wrap="word", fg_color="transparent", text_color=Styles.TEXT_PRIMARY)
        info_desc.insert("0.0", about_text.strip())
        info_desc.configure(state="disabled")
        info_desc.pack(fill="both", expand=True, padx=20, pady=20)
