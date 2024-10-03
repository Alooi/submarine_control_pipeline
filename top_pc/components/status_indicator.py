from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math
import sys
from PySide6.QtWidgets import QPushButton


class NetworkStatus(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = {}
        self.refresh_button = QPushButton("Refresh", self)
        self.record_button = QPushButton("Record", self)
        self.record_status = False
        
    def set_devices(self, devices):
        self.devices = devices
        for device in self.devices:
            self.devices[device] = False
        self.update()

    def set_device_status(self, name, device, status):
        # if the device does not exists, add it
        if name not in self.devices:
            self.devices[name] = status
        else:
            self.devices[name] = status
        self.update()
        
    def set_record_status(self, status):
        self.record_status = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 1))

        # Draw the status indicators
        for i, device in enumerate(self.devices):
            if self.devices[device]:
                color = QColor(0, 255, 0)
            else:
                color = QColor(255, 0, 0)

            painter.setBrush(color)
            painter.drawEllipse(20 * i, self.height() / 2 - 10, 20, 20)  # Center vertically

            painter.drawText(20 * i + 25, self.height() / 2 + 5, device)  # Align text to the left middle

            painter.setPen(QPen(Qt.black, 1))
            painter.drawEllipse(20 * i, self.height() / 2 - 10, 20, 20)
            
        self.refresh_button.move(0, 0)
        self.record_button.move(0, 20)
        
        # record status indicator
        if self.record_status:
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)
        painter.setBrush(color)
        painter.drawEllipse(0, 40, 20, 20)
        painter.drawText(25, 55, "Recording")
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(0, 40, 20, 20)

        