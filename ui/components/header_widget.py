"""Header widget with title, search, and category filter."""
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt


class HeaderWidget(QWidget):
    """Header component with title, search box, and category selector."""

    def __init__(self):
        """Initialize the header widget."""
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("header")
        
        # Set up layout
        container = QVBoxLayout()
        container.addLayout(self._setup_top_section())
        self.setLayout(container)

    def _setup_top_section(self) -> QHBoxLayout:
        """Create the top section with title."""
        top_section = QHBoxLayout()
        
        self.title = QLabel("TODO: Lấy title từ metadata")
        self.title.setObjectName("page-title")
        top_section.addWidget(self.title)
        
        return top_section
    
    def update_page_info(
            self,
            title
    ):
        self.title.setText(title)