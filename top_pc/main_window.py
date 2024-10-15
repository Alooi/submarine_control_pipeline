import sys
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QOpenGLFunctions, QPixmap
from components.Gauge import CircularGauge
from components.Depth_Viz import DepthWidget
from components.roll_indicator import RollIndicator
from components.pitch_indicator import PitchIndicator
from components.yaw_indicator import YawIndicator
from components.video_feed import VideoFeed
from components.status_indicator import NetworkStatus
from components.messages_indicator import MessagesLog
from components.Indicator_Viz import LEDIndicator
from components.video_feed_browser import VideoFeedBrowser

# import size policy
from PySide6.QtWidgets import QSizePolicy

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,  # Import QHBoxLayout
    QWidget,
    QProgressBar,
    QSizePolicy,
    QLabel,
    QLayout,
    QSplitter,
)


from PySide6.QtWidgets import QSplitter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Big Black Sub")
        self.dummy_angle = 1
        self.dummy_angle2 = 1
        self.urls = []
        self.ip = "localhost"
        self.video_feeds = []

        # set the minimum size of the window
        self.setMinimumSize(1024, 720)

        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create splitters for resizable sections
        main_splitter = QSplitter(Qt.Vertical)  # Main splitter (vertical)
        middle_splitter = QSplitter(Qt.Horizontal)  # Middle splitter (horizontal)
        bottom_splitter = QSplitter(Qt.Horizontal)  # Bottom splitter (horizontal)

        self.depth_connection = LEDIndicator(label="Depth Sensor")
        self.imu_connection = LEDIndicator(label="IMU Sensor")
        self.camera_connection = LEDIndicator(label="Camera Feed")

        layout.addWidget(main_splitter)

        # Top part (logo section)
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        logo1 = QLabel()
        logo1.setPixmap(
            QPixmap("assets/kaust_logo.png").scaled(200, 50, Qt.KeepAspectRatio)
        )
        logo2 = QLabel()
        logo2.setPixmap(
            QPixmap("assets/neom_logo.png").scaled(200, 50, Qt.KeepAspectRatio)
        )
        top_layout.addWidget(logo1)
        top_layout.addWidget(logo2)

        # main_splitter.addWidget(top_widget)

        # Middle part (gauges and video feed)
        depth_layout = QVBoxLayout()
        circular_gauges = QVBoxLayout()
        gauges_layout = QHBoxLayout()
        self.video_layout = QVBoxLayout()

        gauges_widget = QWidget()
        video_widget = QWidget()

        gauges_widget.setLayout(gauges_layout)
        self.video_layout.addWidget(self.camera_connection)
        video_widget.setLayout(self.video_layout)

        # Add widgets to the middle splitter
        middle_splitter.addWidget(gauges_widget)
        middle_splitter.addWidget(video_widget)

        self.roll_indicator = RollIndicator()
        self.pitch_indicator = PitchIndicator()
        self.yaw_indicator = YawIndicator()
        self.depth_widget = DepthWidget()

        depth_layout.addWidget(self.depth_connection)
        depth_layout.addWidget(self.depth_widget)
        gauges_layout.addLayout(depth_layout)
        circular_gauges.addWidget(self.imu_connection)
        circular_gauges.addWidget(self.roll_indicator)
        circular_gauges.addWidget(self.pitch_indicator)
        circular_gauges.addWidget(self.yaw_indicator)
        gauges_layout.addLayout(circular_gauges)

        main_splitter.addWidget(
            middle_splitter
        )  # Add the middle splitter to the main one

        # Bottom part (status and messages)
        status_layout = QVBoxLayout()
        messages_layout = QVBoxLayout()

        status_widget = QWidget()
        messages_widget = QWidget()

        status_widget.setLayout(status_layout)
        messages_widget.setLayout(messages_layout)

        self.network_status = NetworkStatus()
        self.messages_log = MessagesLog()

        status_layout.addWidget(self.network_status)
        messages_layout.addWidget(self.messages_log)

        bottom_splitter.addWidget(status_widget)
        bottom_splitter.addWidget(messages_widget)

        main_splitter.addWidget(
            bottom_splitter
        )  # Add the bottom splitter to the main one

        # Set the central widget
        self.setCentralWidget(central_widget)

    # def initiate_video_feed(self, ip, urls):
    #     for url in urls:
    #         if url in self.urls:
    #             continue
    #         self.urls.append(url)
    #         url = "http://" + ip + ":" + "5000" + "/" + url
    #         print(url)
    #         video_feed = VideoFeedBrowser(url)
    #         self.video_feeds.append(video_feed)
    #         self.video_layout.addWidget(video_feed)
