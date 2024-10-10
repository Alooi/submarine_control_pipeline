import cv2


# opens a video feed from a browser link and records it
class VideoFeedOpencv:
    def __init__(self, urls):
        self.urls = urls
        self.status = False
        self.browsers = []
        self.full_urls = []
        self.video_file = None
        
    def set_urls(self, ip):
        # check if the full urls array is empty
        if len(self.full_urls) > 0:
            return
        for url in self.urls:
            self.full_urls.append(f"http://{ip}:5000/{url}")
             
    # def show_streams(self):
    #     for browser in self.browsers:
    #         if browser.isOpened():
    #             ret, frame = browser.read()
    #             if ret:
    #                 cv2.imshow("Video Stream", frame)
    #             else:
    #                 print("Failed to read frame")
    #         else:
    #             print("Browser not loaded")
    
    def start_recording(self, video_file):
        self.video_file = video_file
        for url in self.full_urls:
            browser = cv2.VideoCapture(url)
            self.browsers.append(browser)
    
    def stop_recording(self):
        self.video_file.release()
    
    def get_frame(self, video_file):
        for browser in self.browsers:
            if browser.isOpened():
                ret, frame = browser.read()
                if ret:
                    video_file.write(frame)
                else:
                    print("Failed to read frame")
            else:
                print("Browser not loaded")

    def close(self):
        for browser in self.browsers:
            browser.release()
        cv2.destroyAllWindows()
