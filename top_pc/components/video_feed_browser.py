from PySide6.QtWidgets import QWidget, QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout

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
        if self.browser.load(url):
            self.status = True
        