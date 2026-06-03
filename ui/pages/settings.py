from ui.pages.base_page import BasePage

from PySide6.QtWidgets import QLabel, QVBoxLayout

class SettingsPage(BasePage):
    page_id = "settings"
    title = "Cài đặt"

    def __init__(self):
        super().__init__()

        container = QVBoxLayout()
        container.addWidget(QLabel("Settings page"))

        self.setLayout(container)