from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math
import sys

class YawIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.yaw_angle = 0
        self.line_gap = 10

    def set_yaw_angle(self, angle):
        self.yaw_angle = angle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Drawing circle
        radius = min(self.width(), self.height()) // 2 - 10
        center = QPointF((self.width() / 2), (self.height() / 2))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center, radius, radius)

        # Drawing arrow head
        painter.setPen(QPen(Qt.red, 3))
        painter.setBrush(QColor(Qt.red))
        painter.save()
        painter.translate(center)
        painter.rotate(-self.yaw_angle)
        painter.translate(-center)
        painter.drawPolygon(
            [
                QPointF(center.x(), center.y() - 50),
                QPointF(center.x() - 10, center.y()),
                QPointF(center.x() + 10, center.y()),
            ]
        )
        painter.restore()


        # Displaying yaw angle text above the circle
        text_rect = self.rect()
        text_rect.moveTop(text_rect.top() - 20)  # Adjust the offset as needed
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)  # Increase the font size by 2 points
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.yaw_angle:.1f}°")
