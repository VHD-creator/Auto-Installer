"""Base class for all pages in the application."""
from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    """Base class for all pages with common attributes."""

    page_id: str = ""
    title: str = ""

    def __init__(self):
        """Initialize the base page."""
        super().__init__()