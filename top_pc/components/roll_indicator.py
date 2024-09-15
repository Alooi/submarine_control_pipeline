from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math
import sys

class RollIndicator(QWidget):
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

        # Drawing circle
        radius = min(self.width(), self.height()) // 2 - 10
        center = QPointF((self.width() / 2), (self.height() / 2))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center, radius, radius)

        # Drawing roll indicator line
        painter.setPen(QPen(Qt.red, 3))
        roll_radians = math.radians(self.roll_angle)
        end_x = center.x() + radius * math.cos(roll_radians)
        end_y = center.y() - radius * math.sin(roll_radians)
        painter.drawLine(center, QPointF(end_x, end_y))
        
        # Drawing arrow head
        painter.setPen(QPen(Qt.red, 3))
        painter.setBrush(QColor(Qt.red))
        painter.save()
        painter.translate(center)
        painter.rotate(-self.roll_angle)
        painter.translate(-center)
        painter.drawPolygon(
            [
                QPointF(center.x(), center.y() - 10),
                QPointF(center.x() - 10, center.y()),
                QPointF(center.x() + 10, center.y()),
            ]
        )
        painter.restore()

        # draw the opposite line
        end_x = center.x() - radius * math.cos(roll_radians)
        end_y = center.y() + radius * math.sin(roll_radians)
        painter.drawLine(center, QPointF(end_x, end_y))

        # Displaying roll angle text above the circle
        text_rect = self.rect()
        text_rect.moveTop(text_rect.top() - 20)  # Adjust the offset as needed
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)  # Increase the font size by 2 points
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.roll_angle:.1f}°")
