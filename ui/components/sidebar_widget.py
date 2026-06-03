"""Sidebar widget with logo, navigation menu, and footer."""
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, QSize
from ui.components.collapsible_menu import CollapsibleMenu
from controllers.sidebar_controller import SidebarController


class SidebarWidget(QWidget):
    """Sidebar component with navigation menu."""

    menuClicked = Signal(str)
    
    # Logo size
    LOGO_SIZE = 40

    def __init__(self):
        """Initialize the sidebar widget."""
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("sidebar")
        
        # Track all navigable buttons for active state
        self._all_buttons: list[QPushButton] = []
        self._active_button: QPushButton | None = None
        
        # Create main layout
        container = QVBoxLayout()
        container.addLayout(self._setup_header(), 1)
        container.addLayout(self._setup_menu(), 9)
        container.addLayout(self._setup_footer(), 1)
        self.setLayout(container)

    def _setup_header(self) -> QHBoxLayout:
        """Create the header section with logo and title."""
        header_container = QHBoxLayout()
        
        # Load and display logo
        base_dir = Path(__file__).resolve().parent.parent.parent
        icon_path = base_dir / "assets" / "logo.svg"
        app_logo = QIcon(str(icon_path))
        
        logo_label = QLabel()
        logo_label.setPixmap(app_logo.pixmap(self.LOGO_SIZE, self.LOGO_SIZE))
        logo_label.setObjectName("header-logo")
        
        # Title
        title = QLabel("Auto Install Tool V3")
        title.setObjectName("header-title")
        title.setWordWrap(True)
        
        header_container.addWidget(logo_label)
        header_container.addWidget(title)
        header_container.addStretch()
        
        return header_container

    def _set_button_icon(self, button: QPushButton, icon_name: str):
        """Helper to set icon for a button."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        icon_path = str(base_dir / "assets" / icon_name)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(26, 26))
        button.setCursor(Qt.PointingHandCursor)

    def _setup_menu(self) -> QVBoxLayout:
        """Create the navigation menu."""
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        management_menu = CollapsibleMenu("Management")
        self.app_btn = management_menu.add_item("Applications")
        self._set_button_icon(self.app_btn, "apps-management.svg")

        self.category_btn = management_menu.add_item("Categories")
        self._set_button_icon(self.category_btn, "category.svg")
        
        # Create menu buttons
        self.homeButton = QPushButton("Home")
        self._set_button_icon(self.homeButton, "home_icon.svg")
        
        self.manageAppsButton = QPushButton("Manage Apps")
        self.manageAppsButton.setCursor(Qt.PointingHandCursor)
        
        self.settingsButton = QPushButton("Settings")
        self._set_button_icon(self.settingsButton, "settings.svg")
        
        # Register all navigable buttons
        self._all_buttons.extend([
            self.homeButton, self.settingsButton,
            self.app_btn, self.category_btn
        ])
        
        # Add buttons to layout
        menu_layout.addWidget(self.homeButton)
        menu_layout.addWidget(management_menu)
        menu_layout.addWidget(self.settingsButton)
        menu_layout.addStretch()
        
        # Connect signals
        self.controller = SidebarController(self)
        
        # Set Home as active by default
        self._set_active_button(self.homeButton)
        
        return menu_layout

    def _setup_footer(self) -> QVBoxLayout:
        """Create the footer section."""
        footer_container = QVBoxLayout()
        footer_container.addWidget(QLabel("Copyright by Danny"))
        return footer_container



    def _on_menu_click(self, button: QPushButton, page_id: str):
        """Handle menu button click: set active state and emit signal."""
        self._set_active_button(button)
        self.menuClicked.emit(page_id)

    def _set_active_button(self, button: QPushButton):
        """Set the active button and update styles."""
        # Clear previous active
        if self._active_button:
            self._active_button.setProperty("active", False)
            self._active_button.style().polish(self._active_button)
        
        # Set new active
        button.setProperty("active", True)
        button.style().polish(button)
        self._active_button = button
