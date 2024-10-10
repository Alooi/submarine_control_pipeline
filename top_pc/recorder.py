import csv
from datetime import datetime
import os
import cv2

class DataLogger:
    def __init__(self):
        self.file_path = None
        self.video_file_path = None
        self.file = None
        self.video_file = None
        self.writer = None
        self.video_feed = None

    def _initialize_csv(self):
        self.file = open(self.file_path, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Timestamp', 'Data'])

    def _initialize_video(self):
        self.video_file = cv2.VideoWriter(self.video_file_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))

    def start_recording(self, video_opencv):
        self.video_feed = video_opencv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # check if the folder exists
        try:
            os.makedirs("records")
        except FileExistsError:
            pass
        self.file_path = f"records/recording_{timestamp}.csv"
        self.video_file_path = f"records/recording_{timestamp}.mp4"
        # print the full path from current directory
        print("recording started on: ", os.path.join(os.getcwd(), self.file_path))
        self._initialize_csv()
        self.video_feed.start_recording(self.video_file)

    def stop_recording(self):
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None
        self.video_feed.stop_recording()

    def log_data(self, data):
        if self.writer:
            timestamp = datetime.now().isoformat()
            self.writer.writerow([timestamp, data])
        else:
            raise RuntimeError("Recording has not been started. Call start_recording() first.")
        if self.video_feed:
            self.video_feed.get_frame(self.video_file)
