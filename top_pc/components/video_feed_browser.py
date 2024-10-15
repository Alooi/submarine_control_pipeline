from PySide6.QtWidgets import QWidget, QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout
import cv2

class VideoFeedBrowser(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        # Create a QWebEngineView instance
        self.browser = QWebEngineView()
        self.browser.setUrl(url)
        self.status = False

        # Set the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)

        # check the availability of the camera feed
        self.browser.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, success):
        if success:
            self.status = True
            print("Browser loaded")
        else:
            self.status = False
            print("Failed to load browser")
            
    # def get_frame(self, video_file):
    #     # use the cv2 library to record the browser window
    #     # if self.status:
    #     #     frame = cv2.imread(self.browser.grab().toImage())
    #     #     # convert the frame to the correct format
    #     #     frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    #     #     video_file.write(frame)
    #     pass