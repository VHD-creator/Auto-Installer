# Auto Install Tool

Công cụ hỗ trợ cài đặt hàng loạt ứng dụng tự động trên Windows, được xây dựng bằng Python và CustomTkinter.

## ✨ Tính năng
- Giao diện hiện đại, hỗ trợ Dark/Light mode.
- Cài đặt nhiều ứng dụng cùng lúc ở chế độ im lặng (Silent Install).
- Dễ dàng tùy chỉnh danh sách ứng dụng qua file `config.json`.
- Yêu cầu quyền Admin tự động khi khởi chạy.

## 🛠 Yêu cầu hệ thống
- Python 3.10 trở lên.
- Hệ điều hành Windows.

## 🚀 Hướng dẫn cài đặt cho lập trình viên

1. **Clone repository:**
   ```bash
   git clone https://github.com/VHD-creator/Auto-Installer.git
   cd Auto-Installer
   ```

2. **Cài đặt thư viện cần thiết:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Chạy ứng dụng:**
   ```powershell
   python main.py
   ```

## 📦 Cách Build ra file .exe

Nếu bạn muốn đóng gói ứng dụng thành một file thực thi duy nhất (`.exe`), hãy sử dụng PyInstaller với file cấu hình `.spec` đã có sẵn:

```powershell
pyinstaller AutoInstallTool.spec
```

Sau khi chạy lệnh trên, file `.exe` hoàn chỉnh sẽ nằm trong thư mục `dist/`.

## ⚙️ Tùy chỉnh danh sách App
Bạn có thể chỉnh sửa file `config.json` để thêm hoặc bớt các ứng dụng cần cài đặt. Đảm bảo các file cài đặt tương ứng được đặt trong thư mục `installers/`.

---
*Phát triển bởi Phạm Sự*
