import threading
import cv2
from flask import Flask, Response
import logging
import socket
import os

# ---------------------- Video Feeder Section ---------------------- #


class SystemManager:
    def __init__(self):
        # Shared variables
        self.pc_connection = False
        self.pcIP = None
        self.pcPort = None
        self.cameras = []
        self.recording = False
        self.file_name = None
        self.out_files = []
        self.num_streams = 0

        # Initialize Flask app for video feeds
        self.app = Flask(__name__)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logging.info("SystemManager initialized")

        # Define Flask routes
        self.app.add_url_rule("/video_feed_1", view_func=self.video_feed_1)
        self.app.add_url_rule("/video_feed_2", view_func=self.video_feed_2)

    # Video feeder methods
    def generate_frames(self, camera_index, count):
        camera = cv2.VideoCapture(camera_index)
        self.num_streams += 1
        logging.info(f"Camera {camera_index} opened: {camera.isOpened()}")
        try:
            while True:
                success, frame = camera.read()
                if not success:
                    logging.error(f"Camera {camera_index} is disconnected")
                    break
                else:
                    if self.recording and len(self.out_files) > 1:
                        self.out_files[count].write(frame)

                    ret, buffer = cv2.imencode(".jpg", frame)
                    frame = buffer.tobytes()
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                    )
        except Exception as e:
            logging.exception(f"Exception occurred in generate_frames: {e}")
        finally:
            camera.release()
            logging.info(f"Camera {camera_index} released")

    def video_feed_1(self):
        logging.info("Starting the video feed 1")
        return Response(
            self.generate_frames(self.cameras[0], 0),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    def video_feed_2(self):
        return Response(
            self.generate_frames(self.cameras[1], 1),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    def start_video_feeder(self):
        # Find available cameras indices
        logging.info("Finding available cameras")
        for i in range(10):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                logging.info(f"Camera {i} is available")
                self.cameras.append(i)
            camera.release()

        logging.info("Starting the Flask app for video feed")
        self.app.run(host="0.0.0.0", port=5000)

    def start_recording(self, file_name):
        self.recording = True
        # create recording folder if it doesn't exist
        if not os.path.exists("records"):
            os.makedirs("records")
            logging.info("Created records folder")
        logging.info(f"Recording to {file_name}")
        # create a video writer object
        logging.info(f"number of cameras: {len(self.cameras)}")
        for i in range(len(self.cameras)):
            out_file = cv2.VideoWriter(
                file_name + f"_{i}.mp4",
                cv2.VideoWriter_fourcc(*"mp4v"),
                30,
                (1920, 1080),
            )
            logging.info(f"created {file_name}_{i}.mp4")
            self.out_files.append(out_file)

        logging.info(f"Recording started")

    def stop_recording(self):
        self.recording = False
        for out_file in self.out_files:
            out_file.release()
        logging.info("Recording stopped")

    # Handshaker method
    def start_handshaker(self):
        # Set up the UDP listener
        os.system("sudo dhclient eth0")
        UDP_IP = "0.0.0.0"  # Listen on all interfaces
        UDP_PORT = 5005  # Set your port

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        logging.info(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

        while True:
            # Listen for incoming packets
            packet, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
            packet = packet.decode("utf-8")  # Decode the bytes to a string
            # logging.info(f"Received packet: {packet} from {addr}")

            if packet == "Who are you?":
                # Store the PC IP and port
                self.pcIP = addr[0]
                self.pcPort = addr[1]
                self.pc_connection = True

                # Send the response back to the sender
                response = "I am RPi"
                sock.sendto(response.encode("utf-8"), addr)
                # logging.info(f"Sent response: {response}")
            # elif packet.startswith("start_recording"):
            #     logging.info("start_recording command received")
            #     parts = packet.split()
            #     if len(parts) == 2:
            #         self.file_name = parts[1]
            #         self.start_recording(self.file_name)
            #     else:
            #         logging.info("Invalid start_recording command format")
            # elif packet == "stop_recording":
            #     logging.info("stop_recording command received")
            #     self.stop_recording()

    # Start both threads
    def start_system(self):
        # Create threads for video feeder and handshaker
        video_thread = threading.Thread(target=self.start_video_feeder)
        handshaker_thread = threading.Thread(target=self.start_handshaker)

        # Start both threads
        video_thread.start()
        handshaker_thread.start()

        # Join threads to the main thread to keep them running
        video_thread.join()
        handshaker_thread.join()


if __name__ == "__main__":
    system_manager = SystemManager()
    system_manager.start_system()
