import cv2
import sys
import select
import time

class VideoProcessor:
    def __init__(self, url):
        self.url = url
        self.cap = None
        self.fps = 30
        self.width = None
        self.height = None
        self.out = None
        self.recording = False
        self.show_stream = True
        self.fps_list = []
        self.failing = False
        print("VideoProcessor initialized")
        # self.start_camera()
        
    def avg_fps(self, fps, over=100):
        self.fps_list = self.fps_list[-over:]
        self.fps_list.append(fps)
        return sum(self.fps_list) / len(self.fps_list)

    def start_camera(self):
        print ("Starting camera with url: ", self.url)
        self.cap = cv2.VideoCapture(self.url)  # Use the URL for video capture
        # fps and resolution
        if not self.cap.isOpened():
            print("Error: Could not open the video device")
            # sys.exit(1)
        # self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        # self.fps = 30
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.sleep_time = 1 / self.fps

        while True:
            start = time.time()
            # Check if there's any input from the parent process
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                command = sys.stdin.readline().strip().split()
                if command[0] == "stop":
                    self.stop_camera()
                    break
                elif command[0] == "show_stream":
                    self.show_stream = True
                elif command[0] == "start_recording":
                    print(f"Recording at {self.fps} fps and {self.width}x{self.height} resolution")
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    self.out = cv2.VideoWriter(command[1], fourcc, self.fps, (self.width, self.height))
                    self.recording = True
                elif command[0] == "stop_recording":
                    if self.recording:
                        self.out.release()
                        self.recording = False
                        print("Recording stopped")
                    else:
                        print("No recording in progress")
                else:
                    print("Unknown command:", command)

            # Normal OpenCV operations
            ret, frame = self.cap.read()
            if not ret:
                if not self.failing:
                    print("Failed to grab frame")
                self.failing = True
                pass
            else:
                self.failing = False
                if self.recording:
                    self.save_frame(frame)
                if self.show_stream:
                    # draw fps on the frame
                    cv2.putText(frame, f"FPS: {self.fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Video Feed", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.show_stream = False
                    cv2.destroyAllWindows()

            # # limit the loop speed to the camera's FPS
            # time.sleep(self.sleep_time)
            end = time.time()
            self.fps = self.avg_fps(1 / (end - start))

        self.cap.release()
        cv2.destroyAllWindows()

    def save_frame(self, frame):
        self.out.write(frame)
        
    def stop_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python opencv_video.py <video_url>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    processor = VideoProcessor(video_url)
    processor.start_camera()
