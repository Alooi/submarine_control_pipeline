from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math
import sys


class MessagesLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll_angle = 0
        self.line_gap = 10

    def set_roll_angle(self, angle):
        self.roll_angle = angle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Displaying a dummy text in the middle of the rectangle syaing video feed
        text_rect = self.rect()
        # gray background
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRect(text_rect)
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, "Messages Log here")
