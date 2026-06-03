"""Collapsible menu widget with animated arrow icon."""
from pathlib import Path

from PySide6.QtCore import QPropertyAnimation, QSize, QEasingCurve, Property, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
)
from PySide6.QtGui import QPixmap, QTransform, QIcon


class ArrowState(QWidget):
    """Invisible widget that holds the rotation angle as a Qt Property for animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, value: float):
        self._angle = value

    angle = Property(float, _get_angle, _set_angle)


class CollapsibleMenu(QWidget):
    """A collapsible menu with animated arrow icon rotation."""

    ICON_SIZE = 20

    def __init__(self, title):
        super().__init__()

        self.expanded = False
        self.title = title

        # Load arrow pixmap
        base_dir = Path(__file__).resolve().parent.parent.parent
        icon_path = str(base_dir / "assets" / "right-arrow.svg")
        self._original_pixmap = QPixmap(icon_path)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Single header button with icon (hover covers both icon & text)
        self.header_btn = QPushButton(title)
        self.header_btn.setObjectName("menuHeader")
        self.header_btn.setIcon(QIcon(self._original_pixmap))
        self.header_btn.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.header_btn.setCursor(Qt.PointingHandCursor)

        self.main_layout.addWidget(self.header_btn)

        # Container Sub Menu
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.content_widget.setMaximumHeight(0)
        self.main_layout.addWidget(self.content_widget)

        # Content expand/collapse animation
        self.content_animation = QPropertyAnimation(
            self.content_widget,
            b"maximumHeight"
        )
        self.content_animation.setDuration(200)
        self.content_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Arrow rotation animation via helper widget
        self._arrow_state = ArrowState(self)
        self._arrow_state.setVisible(False)
        self.arrow_animation = QPropertyAnimation(
            self._arrow_state,
            b"angle"
        )
        self.arrow_animation.setDuration(200)
        self.arrow_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.arrow_animation.valueChanged.connect(self._update_arrow_icon)

        self.header_btn.clicked.connect(self.toggle)

    def _update_arrow_icon(self, _value):
        """Update the header button icon to match the current rotation angle."""
        angle = self._arrow_state._angle
        transform = QTransform().rotate(angle)
        rotated = self._original_pixmap.transformed(transform)
        scaled = rotated.scaled(
            QSize(self.ICON_SIZE, self.ICON_SIZE),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.header_btn.setIcon(QIcon(scaled))

    def add_item(self, text, callback=None):
        """Add a submenu item button."""
        btn = QPushButton(text)
        btn.setObjectName("submenuButton")
        btn.setCursor(Qt.PointingHandCursor)
        if callback:
            btn.clicked.connect(callback)
        self.content_layout.addWidget(btn)
        return btn

    def toggle(self):
        """Toggle the collapsible menu open/closed with animations."""
        height = self.content_layout.sizeHint().height()

        self.content_animation.stop()
        self.arrow_animation.stop()

        if self.expanded:
            # Collapse: rotate 90° → 0°, shrink content
            self.content_animation.setStartValue(height)
            self.content_animation.setEndValue(0)
            self.arrow_animation.setStartValue(90.0)
            self.arrow_animation.setEndValue(0.0)
        else:
            # Expand: rotate 0° → 90°, grow content
            self.content_animation.setStartValue(0)
            self.content_animation.setEndValue(height)
            self.arrow_animation.setStartValue(0.0)
            self.arrow_animation.setEndValue(90.0)

        self.content_animation.start()
        self.arrow_animation.start()

        self.expanded = not self.expanded