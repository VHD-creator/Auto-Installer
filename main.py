"""Auto Installer V3 - Entry point of the application."""
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


def main():
    """Initialize and run the application."""
    app = QApplication([])
    
    # Load and apply stylesheet
    style_path = Path(__file__).resolve().parent / "assets" / "style.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text())
    
    # Create and configure main window
    window = MainWindow()
    window.setWindowTitle("Auto Installer V3 By Danny")
    window.setWindowIcon(QIcon("./assets/logo.svg"))
    window.show()
    
    app.exec()


if __name__ == "__main__":
    main()