"""Main page for selecting applications to install."""
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QTextEdit
)
from PySide6.QtCore import Qt

from ui.pages.base_page import BasePage


class MainPage(BasePage):
    """Main page for displaying and selecting applications."""

    page_id = "main"
    title = "Chọn ứng dụng cần cài"

    def __init__(self):
        """Initialize the main page."""
        super().__init__()
        
        container = QVBoxLayout()
        container.addLayout(self._setup_header(), 1)
        content_label = QLabel("Đang tải danh sách ứng dụng...")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(content_label, 4)
        container.addLayout(self._setup_log_screen(), 2)

        self.setLayout(container)

    
    
    def _setup_header(self) -> QHBoxLayout:
        """Create the header with search and category filter."""
        header = QHBoxLayout()
        
        # Search box
        search_box = QLineEdit()
        search_box.setObjectName("search-box")
        search_box.setPlaceholderText("Tìm kiếm...")
        
        # Category selector
        # TODO: Load categories from config.json
        category_select_box = QComboBox()
        category_select_box.setObjectName("category-select")
        category_select_box.addItem("Tất cả ứng dụng")

        # Add widgets with proportions
        header.addWidget(search_box, 5)
        header.addStretch(3)
        header.addWidget(category_select_box, 2)
        
        return header
    
    def _setup_log_screen(self) -> QVBoxLayout:
        """Create the log screen section."""
        log_screen = QVBoxLayout()

        # Log title
        log_title = QLabel("Log")
        log_title.setObjectName("log-title")

        # Log text area (read-only)
        self.log_area = QTextEdit()
        self.log_area.setObjectName("log-area")
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Nhật ký cài đặt sẽ hiển thị ở đây...")

        log_screen.addWidget(log_title)
        log_screen.addWidget(self.log_area)

        return log_screen

    def append_log(self, message: str):
        """Append a message to the log area."""
        self.log_area.append(message)
