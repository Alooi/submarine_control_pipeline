from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

class LEDIndicator(QWidget):
    def __init__(self, label="", parent=None):
        super().__init__(parent)
        self.color = QColor(255, 0, 0)
        self.label = label

        # set size to 20x20
        self.setFixedSize(180, 20)
        
    def set_status(self, status=0):
        if status:
            self.color = QColor(0, 255, 0)
        else:
            self.color = QColor(255, 0, 0)
        self.update()

    def set_status_label(self, label):
        self.label = label
        self.update()

    def paintEvent(self, event):
        # draw small circle
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.color)
        painter.drawEllipse(0, 0, 20, 20)

        # draw text after 20 pixels
        painter.drawText(20, 0, self.width(), self.height(), Qt.AlignCenter, self.label)

        # draw border
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(0, 0, 20, 20)
