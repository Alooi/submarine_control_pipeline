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
        self.other_devices = {}
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
        
    def set_other_status(self, device, status):
        self.other_devices[device] = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 1))
        
        # Draw the grid lines starting after the refresh button
        button_height = self.refresh_button.height()
        total_lines = len(self.devices) + len(self.other_devices)
        for line in range(total_lines):
            painter.drawLine(0, button_height + 20 * line, self.width(), button_height + 20 * line)
        
        # Draw the status indicators for devices
        for i, device in enumerate(self.devices):
            y_position = button_height + 20 * i + 10  # Center vertically in the line
            if self.devices[device]:
                color = QColor(0, 255, 0)
            else:
                color = QColor(255, 0, 0)

            painter.setBrush(color)
            painter.drawEllipse(10, y_position - 10, 20, 20)  # Center vertically in the line

            painter.drawText(40, y_position + 5, device)  # Align text to the left middle

            painter.setPen(QPen(Qt.black, 1))
            painter.drawEllipse(10, y_position - 10, 20, 20)

        # Draw the status indicators for other devices
        for i, device in enumerate(self.other_devices):
            y_position = button_height + 20 * (len(self.devices) + i) + 10  # Center vertically in the line
            if self.other_devices[device]:
                color = QColor(0, 255, 0)
            else:
                color = QColor(255, 0, 0)

            painter.setBrush(color)
            painter.drawEllipse(10, y_position - 10, 20, 20)  # Center vertically in the line
            
            painter.drawText(40, y_position + 5, device)  # Align text to the left middle
            
        self.refresh_button.move(0, 0)
        
        self.record_button.move(90, 0)
        
        # record status indicator
        y_position = self.refresh_button.height() + 20 * (len(self.devices) + len(self.other_devices)) + 10
        if self.record_status:
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)
        painter.setBrush(color)
        painter.drawEllipse(10, y_position - 10, 20, 20)  # Center vertically in the line
        painter.drawText(40, y_position + 5, "Recording")  # Align text to the left middle
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(10, y_position - 10, 20, 20)

        