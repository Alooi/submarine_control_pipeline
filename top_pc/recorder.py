import csv
from datetime import datetime
import os

class DataLogger:
    def __init__(self):
        self.file_path = None
        self.file = None
        self.writer = None

    def _initialize_csv(self):
        self.file = open(self.file_path, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Timestamp', 'Data'])

    def start_recording(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # check if the folder exists
        try:
            os.makedirs("records")
        except FileExistsError:
            pass
        self.file_path = f"records/recording_{timestamp}.csv"
        # print the full path from current directory
        print("recording started on: ", os.path.join(os.getcwd(), self.file_path))
        self._initialize_csv()

    def stop_recording(self):
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None

    def log_data(self, data):
        if self.writer:
            timestamp = datetime.now().isoformat()
            self.writer.writerow([timestamp, data])
        else:
            raise RuntimeError("Recording has not been started. Call start_recording() first.")