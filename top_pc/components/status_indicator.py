from PySide6.QtWidgets import QWidget, QApplication, QPushButton
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, Signal, QObject
import sys
from .Indicator_Viz import LEDIndicator


class NetworkStatus(QWidget):
    # Define signals for thread-safe communication
    device_status_changed = Signal(str, str, bool)  # name, device, status
    other_status_changed = Signal(str, bool)  # device, status
    record_status_changed = Signal(bool)  # status

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
        self._connect_signals()

    def _connect_signals(self):
        """Connect signals to slots for thread-safe operation"""
        self.device_status_changed.connect(self._update_device_status)
        self.other_status_changed.connect(self._update_other_status)
        self.record_status_changed.connect(self._update_record_status)

    def _setup_ui(self):
        self.refresh_button.move(0, 0)
        self.record_button.move(90, 0)
        # Position record indicator below buttons, not overlapping
        self.record_indicator.move(10, self.refresh_button.height() + 5)
        self.record_indicator.setFixedSize(180, 20)
        self.record_indicator.setParent(self)  # Ensure proper parenting
        self.record_indicator.show()  # Ensure it's visible

    def set_devices(self, devices):
        self.devices = devices
        # Remove old indicators
        for indicator in self.device_indicators.values():
            indicator.setParent(None)
            indicator.deleteLater()
        self.device_indicators = {}
        # Create new indicators
        for i, device in enumerate(self.devices):
            indicator = LEDIndicator(device, self)
            indicator.setParent(self)  # Explicitly set parent
            # Position below record indicator
            y_pos = self.refresh_button.height() + 25 + (20 * i)
            indicator.move(10, y_pos)
            indicator.setFixedSize(180, 20)
            indicator.set_status(self.devices[device])
            indicator.show()  # Make sure it's visible
            self.device_indicators[device] = indicator
        self.update()

    def set_device_status(self, name, device, status):
        """Thread-safe method to update device status"""
        self.device_status_changed.emit(name, device, status)

    def _update_device_status(self, name, device, status):
        """Internal method that runs in main thread"""
        if name not in self.device_indicators:  # Check indicators, not devices
            self.devices[name] = status
            indicator = LEDIndicator(name, self)
            # Calculate proper position
            total_existing = len(self.device_indicators)
            y_pos = self.refresh_button.height() + 25 + (20 * total_existing)
            indicator.move(10, y_pos)
            indicator.setFixedSize(180, 20)
            indicator.set_status(status)
            indicator.show()  # Make sure it's visible
            self.device_indicators[name] = indicator
        else:
            self.devices[name] = status
            if name in self.device_indicators:
                self.device_indicators[name].set_status(status)
        self._reposition_all_indicators()
        self.update()

    def set_record_status(self, status):
        """Thread-safe method to update record status"""
        self.record_status_changed.emit(status)

    def _update_record_status(self, status):
        """Internal method that runs in main thread"""
        self.record_status = status
        self.record_indicator.set_status(status)
        self.update()

    def set_other_status(self, device, status):
        """Thread-safe method to update other device status"""
        self.other_status_changed.emit(device, status)

    def _update_other_status(self, device, status):
        """Internal method that runs in main thread"""
        self.other_devices[device] = status
        if device not in self.other_indicators:
            indicator = LEDIndicator(device, self)
            # Position below all device indicators
            y_pos = self.refresh_button.height() + 25 + (20 * len(self.device_indicators)) + (20 * len(self.other_indicators))
            indicator.move(10, y_pos)
            indicator.setFixedSize(180, 20)
            indicator.set_status(status)
            indicator.show()  # Make sure it's visible
            self.other_indicators[device] = indicator
        else:
            self.other_indicators[device].set_status(status)
        # Reposition all indicators to maintain proper layout
        self._reposition_all_indicators()
        self.update()

    def _reposition_all_indicators(self):
        """Helper method to reposition all indicators in proper order"""
        # Reposition record indicator
        self.record_indicator.move(10, self.refresh_button.height() + 5)
        
        # Reposition device indicators
        for i, device in enumerate(self.device_indicators):
            y_pos = self.refresh_button.height() + 25 + (20 * i)
            self.device_indicators[device].move(10, y_pos)
        
        # Reposition other indicators
        for i, device in enumerate(self.other_indicators):
            y_pos = self.refresh_button.height() + 25 + (20 * len(self.device_indicators)) + (20 * i)
            self.other_indicators[device].move(10, y_pos)

    def resizeEvent(self, event):
        self._reposition_all_indicators()
        super().resizeEvent(event)

    def paintEvent(self, event):
        # Only draw grid lines for visual separation
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        button_height = self.refresh_button.height()
        # Include record indicator and all other indicators in line count
        total_lines = 1 + len(self.device_indicators) + len(self.other_indicators)  # +1 for record indicator
        for line in range(total_lines):
            y_pos = button_height + 5 + (20 * line)
            painter.drawLine(0, y_pos, self.width(), y_pos)

