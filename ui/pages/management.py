"""Main page for selecting applications to install."""
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QScrollArea, QWidget, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ui.pages.base_page import BasePage
from controllers.management_controller import ManagementController


class AppCard(QFrame):
    toggled = Signal(object, bool)

    def __init__(self, app_name, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.is_selected = False
        
        self.setObjectName("category-card")
        self.setCursor(Qt.PointingHandCursor)
        
        card_layout = QVBoxLayout(self)
        
        name_label = QLabel(app_name)
        name_label.setObjectName("category-card-name")
        
        card_layout.addWidget(name_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.setProperty("selected", self.is_selected)
            self.style().unpolish(self)
            self.style().polish(self)
            self.toggled.emit(self, self.is_selected)
        super().mousePressEvent(event)


class ManagementPage(BasePage):
    """Main page for displaying and selecting applications."""

    page_id = "manage"
    title = "Quản lí bộ cài đặt app"

    def __init__(self):
        """Initialize the main page."""
        super().__init__()
        
        self.selected_apps = set()

        container = QVBoxLayout()
        container.addLayout(self._setup_header())
        container.addLayout(self._setup_content())

        self.setLayout(container)
        self.load_apps()
        
        self.controller = ManagementController(self)

    def _setup_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        # Search box
        search_box = QLineEdit()
        search_box.setObjectName("search-box")
        search_box.setPlaceholderText("Tìm kiếm ứng dụng...")

        header.addWidget(search_box)
        header.addStretch()

        return header
    
    def _setup_content(self) -> QVBoxLayout:
        container = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("category-scroll-area")

        self.grid_container = QWidget()
        self.grid_container.setObjectName("scroll-content")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.grid_container)

        self.add_btn = QPushButton(" Thêm ứng dụng mới")
        self.add_btn.setIcon(QIcon("assets/plus.svg"))
        self.add_btn.setObjectName("add-category-btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)

        self.delete_btn = QPushButton(" Xóa các ứng dụng đã chọn")
        self.delete_btn.setIcon(QIcon("assets/minus.svg"))
        self.delete_btn.setObjectName("delete-btn")
        self.delete_btn.setCursor(Qt.PointingHandCursor)

        command_section = QHBoxLayout()
        command_section.addWidget(self.add_btn)
        command_section.addWidget(self.delete_btn)

        container.addWidget(self.scroll_area)
        container.addLayout(command_section)

        return container

    def load_apps(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.selected_apps.clear()
        
        items = [
            "App 1",
            "App 2",
            "App 3",
            "App 4",
            "App 5",
        ]
        
        for index, item in enumerate(items):
            card = AppCard(item)
            card.toggled.connect(self.on_app_toggled)
            
            row = index // 2
            col = index % 2
            self.grid_layout.addWidget(card, row, col)

    def on_app_toggled(self, card, is_selected):
        if is_selected:
            self.selected_apps.add(card)
        else:
            self.selected_apps.discard(card)