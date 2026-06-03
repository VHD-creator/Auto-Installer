from ui.pages.base_page import BasePage
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, 
    QPushButton, QScrollArea, QWidget, QGridLayout, QFrame
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from services.data_manager import DataManager
from controllers.categories_controller import CategoriesController

class CategoryCard(QFrame):
    clicked = Signal(object)

    def __init__(self, cat_data, parent=None):
        super().__init__(parent)
        self.cat_data = cat_data
        self.setObjectName("category-card")
        self.setCursor(Qt.PointingHandCursor)
        
        card_layout = QVBoxLayout(self)
        
        name_label = QLabel(cat_data.get("name", ""))
        name_label.setObjectName("category-card-name")
        
        id_label = QLabel(f"ID: {cat_data.get('id', '')}")
        id_label.setObjectName("category-card-id")
        
        card_layout.addWidget(name_label)
        card_layout.addWidget(id_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)

class CategoriesManager(BasePage):
    page_id = "categories"
    title = "Quản lí danh mục ứng dụng"

    def __init__(self):
        super().__init__()

        self.data_manager = DataManager()
        self.selected_card = None

        container = QVBoxLayout()
        container.addLayout(self._setup_header())
        container.addLayout(self._setup_content())

        self.setLayout(container)
        self.load_categories()
        
        self.controller = CategoriesController(self)
        

    def _setup_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        search_box = QLineEdit()
        search_box.setObjectName("search-box")
        search_box.setPlaceholderText("Tìm kiếm danh mục...")
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

        command_section = QHBoxLayout()

        self.add_btn = QPushButton(" Thêm danh mục")
        self.add_btn.setIcon(QIcon("assets/plus.svg"))
        self.add_btn.setObjectName("add-category-btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)

        self.edit_btn = QPushButton(" Sửa danh mục")
        self.edit_btn.setObjectName("add-category-btn")
        self.edit_btn.setCursor(Qt.PointingHandCursor)

        self.delete_btn = QPushButton(" Xóa danh mục")
        self.delete_btn.setIcon(QIcon("assets/minus.svg"))
        self.delete_btn.setObjectName("delete-btn")
        self.delete_btn.setCursor(Qt.PointingHandCursor)

        command_section.addWidget(self.add_btn)
        command_section.addWidget(self.edit_btn)
        command_section.addWidget(self.delete_btn)

        container.addWidget(self.scroll_area)
        container.addLayout(command_section)

        return container
    
    def load_categories(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.selected_card = None
        categories = self.data_manager.load_categories()

        for index, cat in enumerate(categories):
            card = CategoryCard(cat)
            card.clicked.connect(self.on_card_clicked)
            
            row = index // 2
            col = index % 2
            self.grid_layout.addWidget(card, row, col)

    def on_card_clicked(self, card):
        if self.selected_card:
            self.selected_card.setProperty("selected", False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)

        self.selected_card = card
        self.selected_card.setProperty("selected", True)
        self.selected_card.style().unpolish(self.selected_card)
        self.selected_card.style().polish(self.selected_card)
