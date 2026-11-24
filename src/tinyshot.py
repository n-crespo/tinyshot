import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget


class SnippingTool(QWidget):
    def __init__(self):
        super().__init__()
        # Freeze the screen: capture it once before the overlay appears, then
        # draw that image as the overlay's background and crop from it.
        self.frozen = QGuiApplication.primaryScreen().grabWindow(0)
        self.dpr = self.frozen.devicePixelRatio()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.BypassWindowManagerHint
            | Qt.WindowType.Tool
        )
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        self.selected_rect = QRect()
        self.trigger_button = None

        # Show last: the first paint can happen synchronously and needs the
        # state above.
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.trigger_button = event.button()
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == self.trigger_button and self.is_selecting:
            self.is_selecting = False
            self.selected_rect = QRect(self.start_point, event.pos()).normalized()

            if self.selected_rect.width() > 5 and self.selected_rect.height() > 5:
                pixmap = self.grab_selection()
                QGuiApplication.clipboard().setPixmap(pixmap)

                if self.trigger_button == Qt.MouseButton.RightButton:
                    downloads_dir = Path.home() / "Downloads"
                    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    pixmap.save(
                        str(downloads_dir / f"Screenshot-{date_str}.png"), "PNG"
                    )

                QApplication.quit()
            else:
                self.trigger_button = None
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.frozen)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.is_selecting:
            rect = QRect(self.start_point, self.end_point).normalized()

            # Redraw the selected area untinted from the frozen image.
            painter.drawPixmap(rect, self.frozen, self.to_device(rect))

            painter.setPen(QPen(QColor(128, 128, 128), 2))
            painter.drawRect(rect)

    def to_device(self, rect: QRect) -> QRect:
        """Map a logical widget rect to physical pixels in the frozen image."""
        return QRect(
            round(rect.x() * self.dpr),
            round(rect.y() * self.dpr),
            round(rect.width() * self.dpr),
            round(rect.height() * self.dpr),
        )

    def grab_selection(self) -> QPixmap:
        pixmap = self.frozen.copy(self.to_device(self.selected_rect))
        pixmap.setDevicePixelRatio(1.0)
        return pixmap


if __name__ == "__main__":
    app = QApplication(sys.argv)
    snipper = SnippingTool()
    snipper.show()
    sys.exit(app.exec())
