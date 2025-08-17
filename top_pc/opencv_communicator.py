import sys
import subprocess
import time
import argparse
import threading

class opencv_communicator():
    def __init__(self, url):
        self.opencv_process = None
        self.url = url
        self.output_thread = None
        self.running = False
        self.feed_title = url.split("_")[-1]

    def start_opencv(self):
        if self.opencv_process is None:
            try:
                self.opencv_process = subprocess.Popen(
                    [sys.executable, "opencv_video.py", self.url],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if self.opencv_process.poll() is not None:
                    self.running = False
                    raise RuntimeError("Failed to start OpenCV process")
                print("OpenCV process started")
                self.running = True
                self.output_thread = threading.Thread(target=self.read_output)
                self.output_thread.start()
            except Exception as e:
                print(f"Error starting OpenCV process: {e}")
                self.running = False
                self.opencv_process = None

    def read_output(self):
        while self.running:
            output = self.opencv_process.stdout.readline()
            if output:
                print(f"opencv says: {output.strip()}")
            else:
                break

    def start_recording(self, file_name):
        if self.opencv_process is not None:
            print(f"Recording to {file_name}")
            self.opencv_process.stdin.write(f"start_recording {file_name}\n")
            self.opencv_process.stdin.flush()
            time.sleep(0.1)  # Allow time for processing

    def stop_recording(self):
        if self.opencv_process is not None:
            print("Stopping recording")
            self.opencv_process.stdin.write("stop_recording\n")
            self.opencv_process.stdin.flush()
            time.sleep(0.1)  # Allow time for processing

    def stop_opencv(self):
        if self.opencv_process is not None:
            self.running = False
            self.opencv_process.stdin.write("stop\n")
            self.opencv_process.stdin.flush()
            print("Command to stop OpenCV sent")
            self.opencv_process.terminate()
            self.opencv_process = None
            print("OpenCV process terminated")
            
    def start_obstacle_avoidance(self):
        if self.opencv_process is not None:
            print("Starting obstacle avoidance")
            self.opencv_process.stdin.write("start_obstacle_avoidance\n")
            self.opencv_process.stdin.flush()
            time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenCV Communicator")
    parser.add_argument("url", help="URL to start OpenCV with")
    args = parser.parse_args()

    communicator = opencv_communicator(args.url)
    communicator.start_opencv()
    communicator.opencv_process.stdin.write("show_stream\n")
    communicator.opencv_process.stdin.flush()
    print("Command to show stream sent")

    try:
        while True:
            command = input("Enter command (record <filename>, stop_record, stop): ")
            if command.startswith("record "):
                _, file_name = command.split(" ", 1)
                communicator.record(file_name)
            elif command == "stop_record":
                communicator.stop_record()
            elif command == "stop":
                communicator.stop_opencv()
                break
            else:
                print("Unknown command")
    except KeyboardInterrupt:
        communicator.stop_opencv()
        print("Process interrupted and terminated")
