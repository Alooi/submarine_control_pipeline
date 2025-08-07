from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget
import math

class ObstacleWidget(QWidget):
    def __init__(self, parent=None, max_distance=20, test_mode=False):
        super().__init__(parent)
        self.distance_to_obstacle = 10
        self.max_distance = max_distance
        self._test_mode = test_mode
        if self._test_mode:
            self._test_timer = QTimer(self)
            self._test_timer.timeout.connect(self._update_test)
            self._test_timer.start(50)
            self._test_phase = 0

    def _update_test(self):
        # Smoothly animate distance_to_obstacle between 0 and max_distance
        self._test_phase += 0.05
        d = self.max_distance / 2 + (self.max_distance / 2) * math.sin(self._test_phase)
        self.set_distance(d)

    def set_distance(self, distance):
        self.distance_to_obstacle = distance
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Regions
        margin = 30
        bar_height = h // 2

        # Draw background (road/space)
        painter.fillRect(margin, bar_height - 10, w - 2 * margin, 20, QColor(200, 200, 200))

        # Draw obstacle (red rectangle)
        obstacle_x = margin + (w - 2 * margin) * (self.distance_to_obstacle / self.max_distance)
        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.drawRect(obstacle_x - 10, bar_height - 15, 20, 30)

        # Draw vehicle (black pill) at left
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRoundedRect(margin - 15, bar_height - 15, 30, 30, 10, 10)

        # Draw distance label
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(0, 0, w, margin, Qt.AlignCenter, f"Obstacle: {self.distance_to_obstacle:.1f} m")
