"""Manager for handling page navigation in a stacked widget."""
from PySide6.QtCore import Signal, QObject

from ui.pages.main_page import MainPage
from ui.pages.management import ManagementPage
from ui.pages.settings import SettingsPage
from ui.pages.categories_management import CategoriesManager


class PageManager(QObject):
    """Manages page registration and navigation in the stacked widget."""
    pageChanged = Signal(object)

    def __init__(self, stack, parent=None):
        """Initialize the page manager."""
        super().__init__(parent)

        self.stack = stack
        self.pages = {}
        self.register_pages()

    def register_pages(self):
        """Register all available pages."""
        page_list = [
            MainPage,
            ManagementPage,
            SettingsPage,
            CategoriesManager,
        ]

        for PageClass in page_list:
            page = PageClass()
            self.pages[page.page_id] = page
            self.stack.addWidget(page)

    def navigate(self, page_id):
        """Navigate to the specified page."""
        page = self.pages.get(page_id)

        if page:
            self.stack.setCurrentWidget(page)
            self.pageChanged.emit(page)