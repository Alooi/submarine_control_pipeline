from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

class DepthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.depth = 0
        self.max_depth = 20

    def set_depth(self, depth):
        self.depth = depth
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background
        painter.fillRect(
            self.rect().adjusted(0, 0, -self.width() / 2, 0), QColor(0, 255, 255)
        )  # Set the background color here

        # Calculate the line position
        line_y = self.height() * (self.depth / self.max_depth)

        # Draw the line
        painter.setPen(QPen(Qt.black, 3))  # Set the line thickness here
        painter.drawLine(0, line_y, self.width() / 2, line_y)  # Modify the width here

        # Draw the depth text
        text_rect = self.rect().adjusted(0, 0, -self.width() / 2, 0)
        font = painter.font()
        font.setPointSize(16)  # Set the text size here
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.depth} m")
