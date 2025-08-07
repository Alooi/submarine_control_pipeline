from PySide6.QtWidgets import QWidget, QApplication, QPushButton
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
import sys
from .Indicator_Viz import LEDIndicator


class NetworkStatus(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = {}
        self.device_indicators = {}
        self.other_devices = {}
        self.other_indicators = {}
        self.refresh_button = QPushButton("Refresh", self)
        self.record_button = QPushButton("Record", self)
        self.record_status = False
        self.record_indicator = LEDIndicator("Recording", self)
        self._setup_ui()

    def _setup_ui(self):
        self.refresh_button.move(0, 0)
        self.record_button.move(90, 0)
        self.record_indicator.move(10, 0)
        self.record_indicator.setFixedSize(180, 20)

    def set_devices(self, devices):
        self.devices = devices
        # Remove old indicators
        for indicator in self.device_indicators.values():
            indicator.setParent(None)
        self.device_indicators = {}
        # Create new indicators
        for i, device in enumerate(self.devices):
            indicator = LEDIndicator(device, self)
            indicator.move(10, self.refresh_button.height() + 20 * i)
            indicator.setFixedSize(180, 20)
            indicator.set_status(self.devices[device])
            self.device_indicators[device] = indicator
        self.update()

    def set_device_status(self, name, device, status):
        if name not in self.devices:
            self.devices[name] = status
            indicator = LEDIndicator(name, self)
            indicator.move(10, self.refresh_button.height() + 20 * len(self.device_indicators))
            indicator.setFixedSize(180, 20)
            indicator.set_status(status)
            self.device_indicators[name] = indicator
        else:
            self.devices[name] = status
            self.device_indicators[name].set_status(status)
        self.update()

    def set_record_status(self, status):
        self.record_status = status
        self.record_indicator.set_status(status)
        self.update()

    def set_other_status(self, device, status):
        self.other_devices[device] = status
        if device not in self.other_indicators:
            indicator = LEDIndicator(device, self)
            indicator.move(10, self.refresh_button.height() + 20 * (len(self.device_indicators) + len(self.other_indicators)))
            indicator.setFixedSize(180, 20)
            indicator.set_status(status)
            self.other_indicators[device] = indicator
        else:
            self.other_indicators[device].set_status(status)
        self.update()

    def resizeEvent(self, event):
        # Reposition indicators on resize
        for i, device in enumerate(self.device_indicators):
            self.device_indicators[device].move(10, self.refresh_button.height() + 20 * i)
        for i, device in enumerate(self.other_indicators):
            self.other_indicators[device].move(10, self.refresh_button.height() + 20 * (len(self.device_indicators) + i))
        self.record_indicator.move(10, self.refresh_button.height() + 20 * (len(self.device_indicators) + len(self.other_indicators)))
        super().resizeEvent(event)

    def paintEvent(self, event):
        # Only draw grid lines for visual separation
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        button_height = self.refresh_button.height()
        total_lines = len(self.device_indicators) + len(self.other_indicators) + 1
        for line in range(total_lines):
            painter.drawLine(0, button_height + 20 * line, self.width(), button_height + 20 * line)

