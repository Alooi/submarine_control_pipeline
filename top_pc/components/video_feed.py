import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPainter


class VideoFeed(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url  # URL of the video feed (e.g., http://localhost:5000)
        self.capture = cv2.VideoCapture(self.url)

        self.current_frame = None  # Store the current frame

    def update_frame(self):
        # Read the frame from the video feed
        success, frame = self.capture.read()
        if success:
            # Convert BGR to RGB since OpenCV uses BGR and Qt expects RGB
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.update()  # Trigger a repaint event

    def paintEvent(self, event):
        if self.current_frame is not None:
            # Convert the frame to QImage for display
            height, width, channel = self.current_frame.shape
            bytes_per_line = 3 * width
            qimg = QImage(
                self.current_frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            )

            # Create a QPainter to paint the image on the widget
            painter = QPainter(self)
            painter.drawImage(0, 0, qimg)
