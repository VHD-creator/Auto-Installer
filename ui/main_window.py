"""Main window of the Auto Installer application."""
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QStackedWidget,
)

from ui.components.header_widget import HeaderWidget
from ui.components.sidebar_widget import SidebarWidget
from controllers.page_manager import PageManager


class MainWindow(QMainWindow):
    """Main application window with sidebar, header, content area, and footer."""

    # Window dimensions
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    SIDEBAR_WIDTH = 250
    HEADER_HEIGHT = 70
    FOOTER_HEIGHT = 50

    def __init__(self):
        """Initialize the main window and set up UI components."""
        super().__init__()
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Initialize components
        self._setup_components()
        
        # Configure layout
        self._setup_layout()
        
        # Connect signals
        self._connect_signals()

    def _setup_components(self):
        """Create and initialize all UI components."""
        self.sidebar = SidebarWidget()
        self.header = HeaderWidget()
        self.stack = QStackedWidget()
        self.page_manager = PageManager(self.stack)

    def _setup_layout(self):
        """Configure the layout structure of the main window."""
        # Set component sizes
        self.sidebar.setFixedWidth(self.SIDEBAR_WIDTH)
        self.header.setFixedHeight(self.HEADER_HEIGHT)

        # Create content layout (vertical: header, content, footer)
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.header)
        content_layout.addWidget(self.stack)

        # Create main layout (horizontal: sidebar, content)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(content_layout)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _update_header(self, page):
        self.header.update_page_info(
            page.title
        )

    def _connect_signals(self):
        """Connect signals between components."""
        self.sidebar.menuClicked.connect(self.page_manager.navigate)
        self.page_manager.pageChanged.connect(self._update_header)
        self.page_manager.navigate("main")

