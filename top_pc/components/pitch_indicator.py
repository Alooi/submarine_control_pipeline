from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math
import sys

class PitchIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pitch_angle = 0
        self.line_gap = 10

    def set_pitch_angle(self, angle):
        self.pitch_angle = angle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Drawing circle
        radius = min(self.width(), self.height()) // 2 - 10
        center = QPointF((self.width() / 2), (self.height() / 2))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center, radius, radius)

        # Drawing pitch indicator line, which moves vertically as it stays horizontal
        painter.setPen(QPen(Qt.red, 3))
        pitch_radians = math.radians(self.pitch_angle)
        end_y = center.y() - radius * math.sin(pitch_radians)
        end_x = center.x() + radius * math.cos(pitch_radians)
        start_y = center.y() - radius * math.sin(pitch_radians)
        painter.drawLine(QPointF(center.x(), start_y), QPointF(end_x, end_y))
        
        # draw the opposite line
        end_y = center.y() - radius * math.sin(pitch_radians)
        end_x = center.x() - radius * math.cos(pitch_radians)
        start_y = center.y() - radius * math.sin(pitch_radians)
        painter.drawLine(QPointF(center.x(), start_y), QPointF(end_x, end_y))
        
        # draw a black line horizontally to represent the horizon
        painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(center.x() - radius, center.y(), center.x() + radius, center.y())

        # Displaying pitch angle text above the circle
        text_rect = self.rect()
        text_rect.moveTop(text_rect.top() - 20)  # Adjust the offset as needed
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)  # Increase the font size by 2 points
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.pitch_angle:.1f}°")
