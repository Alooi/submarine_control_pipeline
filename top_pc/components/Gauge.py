from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget

class CircularGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(200, 200)
        self.value = 0

    def setValue(self, value):
        self.value = value
        self.update()
    
    def get_value(self):
        return self.value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the gauge properties
        gaugeRect = QRectF(10, 10, 180, 180)
        startAngle = 270 * 16  # 135 degrees
        spanAngle = (self.value / 100) * -360 * 16  # -360 degrees

        # Draw the background circle
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(gaugeRect)

        # Draw the progress arc
        painter.setPen(QPen(QColor(0, 120, 255), 10))
        painter.drawArc(gaugeRect, startAngle, spanAngle)

        # Draw the text value
        painter.setPen(QPen(Qt.black))
        painter.setFont(self.font())
        painter.drawText(gaugeRect, Qt.AlignCenter, f"{self.value}%")
