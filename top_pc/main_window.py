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
from components.Obstacle_Viz import ObstacleWidget  # Import ObstacleWidget

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


from PySide6.QtWidgets import QSplitter, QFrame  # Add QFrame import


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
        self.down_echo_connection = LEDIndicator(label="Down-Echo Sensor")
        self.front_echo_connection = LEDIndicator(label="Front-Echo Sensor")
        self.imu_connection = LEDIndicator(label="IMU Sensor")

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

        # Create left-side indicator layout (network status only)
        left_indicator_layout = QVBoxLayout()
        left_indicator_frame = QFrame()
        left_indicator_frame.setLayout(left_indicator_layout)
        left_indicator_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")

        self.network_status = NetworkStatus()
        left_indicator_layout.addWidget(self.network_status)

        # Wrap gauges in a QFrame
        gauges_frame = QFrame()
        gauges_frame.setLayout(gauges_layout)
        gauges_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")

        # # Wrap video feed in a QFrame
        # video_frame = QFrame()
        # video_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")

        # Add widgets to the middle splitter
        middle_splitter.addWidget(left_indicator_frame)
        middle_splitter.addWidget(gauges_frame)
        # middle_splitter.addWidget(video_frame)

        # Set splitter sizes: 1/5 for indicators, 4/5 for gauges/depth
        middle_splitter.setSizes([int(self.width() * 1/5), int(self.width() * 4/5)])

        self.roll_indicator = RollIndicator()
        self.pitch_indicator = PitchIndicator()
        self.yaw_indicator = YawIndicator()
        self.depth_widget = DepthWidget()

        # Wrap depth in a QFrame
        depth_frame = QFrame()
        depth_frame.setLayout(depth_layout)
        depth_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")

        depth_layout.addWidget(self.depth_connection)
        depth_layout.addWidget(self.down_echo_connection)
        depth_layout.addWidget(self.depth_widget)

        # Obstacle avoidance layout
        obstacle_layout = QVBoxLayout()
        obstacle_frame = QFrame()
        obstacle_frame.setLayout(obstacle_layout)
        obstacle_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")
        obstacle_layout.addWidget(self.front_echo_connection)

        # Add horizontal obstacle indicator
        self.obstacle_widget = ObstacleWidget()
        obstacle_layout.addWidget(self.obstacle_widget)

        # Add both frames to gauges_layout
        gauges_layout.addWidget(depth_frame)
        gauges_layout.addWidget(obstacle_frame)

        circular_gauges.addWidget(self.imu_connection)
        circular_gauges.addWidget(self.roll_indicator)
        circular_gauges.addWidget(self.pitch_indicator)
        circular_gauges.addWidget(self.yaw_indicator)
        gauges_layout.addLayout(circular_gauges)

        main_splitter.addWidget(
            middle_splitter
        )  # Add the middle splitter to the main one

        # Bottom part (messages only)
        messages_layout = QVBoxLayout()
        messages_frame = QFrame()
        messages_frame.setLayout(messages_layout)
        messages_frame.setStyleSheet("QFrame { border: 2px solid #444; border-radius: 8px; }")

        self.messages_log = MessagesLog()
        messages_layout.addWidget(self.messages_log)

        bottom_splitter.addWidget(messages_frame)

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
