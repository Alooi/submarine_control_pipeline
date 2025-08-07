from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget
import random
import math

class DepthWidget(QWidget):
    def __init__(self, parent=None, test_mode=False):
        super().__init__(parent)
        self.distance_to_surface = 0
        self.distance_to_seabed = 20
        self._test_mode = test_mode
        if self._test_mode:
            self._test_timer = QTimer(self)
            self._test_timer.timeout.connect(self._update_test)
            self._test_timer.start(50)
            self._test_phase = 0

    def _update_test(self):
        # Smoothly animate between 0 and 10, with offset
        self._test_phase += 0.05
        d1 = 5 + 5 * math.sin(self._test_phase)
        d2 = 5 + 5 * math.sin(self._test_phase + math.pi / 2)  # 90 degree offset
        self.set_distances(d1, d2)

    def set_distances(self, distance_to_surface, distance_to_seabed):
        self.distance_to_surface = distance_to_surface
        self.distance_to_seabed = distance_to_seabed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Widget geometry
        w = self.width() / 2
        h = self.height()

        # Heights for each region (proportional to distances)
        total_water = self.distance_to_surface + self.distance_to_seabed
        # Center the sub in the middle of the water region
        pill_width = 40
        pill_height = 20
        water_region_height = h - 60  # leave 30px for surface and seabed labels
        sub_y = 30 + water_region_height / 2

        # Calculate proportional heights
        if total_water > 0:
            surface_height = water_region_height * (self.distance_to_surface / total_water)
            seabed_height = water_region_height * (self.distance_to_seabed / total_water)
        else:
            surface_height = seabed_height = water_region_height / 2

        # Top of water region
        water_top = 30
        surface_y = sub_y - surface_height
        seabed_y = sub_y + seabed_height

        # Draw above surface (white)
        painter.fillRect(0, 0, w, surface_y, QColor(255, 255, 255))

        # Draw water (blue)
        painter.fillRect(0, surface_y, w, seabed_y - surface_y, QColor(0, 120, 255))

        # Draw seabed (brown)
        painter.fillRect(0, seabed_y, w, h - seabed_y, QColor(139, 69, 19))

        # Draw water surface line
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawLine(0, surface_y, w, surface_y)

        # Draw seabed line
        painter.setPen(QPen(QColor(139, 69, 19), 2))
        painter.drawLine(0, seabed_y, w, seabed_y)

        # Draw the submarine (black pill) stationary in the middle
        pill_x = (w / 2) - (pill_width / 2)
        pill_y = sub_y - pill_height / 2
        painter.setBrush(QColor(0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pill_x, pill_y, pill_width, pill_height, 10, 10)

        # Draw the submarine label inside the pill
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(pill_x, pill_y, pill_width, pill_height, Qt.AlignCenter, "SUB")

        # Draw distance labels
        painter.setPen(Qt.black)
        font.setPointSize(17)
        painter.setFont(font)
        painter.drawText(0, 0, w, 30, Qt.AlignCenter, f"Surface: {self.distance_to_surface:.1f} m")
        painter.drawText(0, h - 30, w, 30, Qt.AlignCenter, f"Seabed: {self.distance_to_seabed:.1f} m")
