import cv2
import sys
import select
import time
import threading
from obstacle_detector import ObstacleDetector  # Assuming you have an obstacle detection module
import matplotlib.pyplot as plt

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
        self.last_frame = None  # Store the last frame for button callback
        print("VideoProcessor initialized")
        # self.start_camera()
        self.detect = False
        self.detector = None
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.visualize = True  # Set to True if you want to visualize the obstacles
        # threading-related
        self.obstacle_thread = None
        self.obstacle_thread_running = False
        self.obstacle_lock = threading.Lock()
        self.obstacle_frame = None
        self.obstacle_vis_image = None
        self.obstacle_vis_window_open = False  # Track if vis window is open

    def avg_fps(self, fps, over=100):
        self.fps_list = self.fps_list[-over:]
        self.fps_list.append(fps)
        return sum(self.fps_list) / len(self.fps_list)

    def obstacle_avoidance_worker(self):
        while self.obstacle_thread_running:
            with self.obstacle_lock:
                frame = self.obstacle_frame
            if frame is not None and self.detector is not None:
                try:
                    obstacle_map = self.detector.process_frame(frame)
                    if self.visualize:
                        vis_image = self.detector.visualize_obstacles(frame, obstacle_map, self.fig, self.ax)
                        with self.obstacle_lock:
                            self.obstacle_vis_image = vis_image
                except Exception as e:
                    print("Exception in obstacle avoidance thread:", e)
            time.sleep(0.01)  # avoid busy loop

    def start_camera(self):
        print ("Starting camera with url: ", self.url)
        self.cap = cv2.VideoCapture(self.url)  # Use the URL for video capture
        # fps and resolution
        if not self.cap.isOpened():
            print("Error: Could not open the video device")
            sys.exit(1)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
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
                elif command[0] == "start_obstacle_avoidance":
                    print("opencv_video: Starting obstacle avoidance")
                    self.detect = True
                    try:
                        self.detector = ObstacleDetector()
                        print("ObstacleDetector initialized")
                    except Exception as e:
                        import traceback
                        print("Failed to initialize ObstacleDetector:")
                        traceback.print_exc()
                        self.detect = False
                        continue
                    if not hasattr(self, 'fig') or not hasattr(self, 'ax'):
                        self.fig = plt.figure(figsize=(10, 8))
                        self.ax = self.fig.add_subplot(111, projection='3d')
                    # Start obstacle avoidance thread
                    if self.obstacle_thread is None or not self.obstacle_thread.is_alive():
                        self.obstacle_thread_running = True
                        self.obstacle_thread = threading.Thread(target=self.obstacle_avoidance_worker, daemon=True)
                        self.obstacle_thread.start()
                    self.obstacle_vis_window_open = True
                elif command[0] == "stop_obstacle_avoidance":
                    print("opencv_video: Stopping obstacle avoidance")
                    self.detect = False
                    self.obstacle_thread_running = False
                    if self.obstacle_thread is not None:
                        self.obstacle_thread.join(timeout=1)
                        self.obstacle_thread = None
                    # Close the visualization window if open
                    if self.obstacle_vis_window_open:
                        cv2.destroyWindow('Live 3D Visualization')
                        self.obstacle_vis_window_open = False
                    if hasattr(self, 'fig') and hasattr(self, 'ax'):
                        plt.close(self.fig)
                        self.fig = None
                        self.ax = None
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
                self.last_frame = frame  # Store the latest frame
                if self.detect:
                    with self.obstacle_lock:
                        self.obstacle_frame = frame.copy()
                    with self.obstacle_lock:
                        vis_image = self.obstacle_vis_image
                    if self.visualize and vis_image is not None and self.detect:
                        cv2.imshow('Live 3D Visualization', vis_image)
                        self.obstacle_vis_window_open = True
                        # Check for 'q' key to exit the loop
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    elif not self.detect and self.obstacle_vis_window_open:
                        cv2.destroyWindow('Live 3D Visualization')
                        self.obstacle_vis_window_open = False
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
        # Stop thread if running
        self.obstacle_thread_running = False
        if self.obstacle_thread is not None:
            self.obstacle_thread.join(timeout=1)
            self.obstacle_thread = None
        # Ensure visualization window is closed
        if self.obstacle_vis_window_open:
            cv2.destroyWindow('Live 3D Visualization')
            self.obstacle_vis_window_open = False

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
