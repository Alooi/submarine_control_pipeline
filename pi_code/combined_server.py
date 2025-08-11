import threading
import socket
import os
import cv2
from flask import Flask, Response
import logging
import time
import signal
import sys

# --- Handshaker logic ---
def handshaker(stop_event):
    # setup the ip dhcp
    os.system("sudo dhclient eth0")
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

    while not stop_event.is_set():
        try:
            sock.settimeout(1.0)
            packet, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue
        except Exception as e:
            if stop_event.is_set():
                break
            print(f"Handshaker error: {e}")
            continue
        packet = packet.decode("utf-8")
        print(f"Received packet: {packet} from {addr}")

        if packet == "Who are you?":
            response = "I am RPi"
            sock.sendto(response.encode("utf-8"), addr)
            print(f"Sent response: {response}")

# --- Video feeder logic ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

cameras = {}
latest_frames = {}
frame_locks = {}
available_cameras = []

def setup_camera(camera_index):
    camera = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        return None
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 15)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    for i in range(5):
        ret, frame = camera.read()
        if ret:
            break
        time.sleep(0.5)
    else:
        camera.release()
        return None
    return camera

def capture_frames(camera_index, stop_event):
    camera = cameras[camera_index]
    jpeg_encode_params = [cv2.IMWRITE_JPEG_QUALITY, 70]
    time.sleep(1)
    consecutive_failures = 0
    max_failures = 10
    while not stop_event.is_set():
        success, frame = camera.read()
        if not success:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                camera.release()
                time.sleep(2)
                new_camera = setup_camera(camera_index)
                if new_camera:
                    cameras[camera_index] = new_camera
                    camera = new_camera
                    consecutive_failures = 0
                else:
                    time.sleep(5)
                    continue
            else:
                time.sleep(0.1)
                continue
        else:
            consecutive_failures = 0
        ret, buffer = cv2.imencode(".jpg", frame, jpeg_encode_params)
        if ret:
            with frame_locks[camera_index]:
                latest_frames[camera_index] = buffer.tobytes()
        time.sleep(0.01)

def generate_frames(camera_index):
    while True:
        with frame_locks[camera_index]:
            if camera_index in latest_frames:
                frame_bytes = latest_frames[camera_index]
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
        time.sleep(1/30)

@app.route("/video_feed_1")
def video_feed_1():
    if len(available_cameras) < 1:
        return "No cameras available", 404
    return Response(
        generate_frames(available_cameras[0]), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/video_feed_2")
def video_feed_2():
    if len(available_cameras) < 2:
        return "Camera 2 not available", 404
    return Response(
        generate_frames(available_cameras[1]), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/status")
def status():
    status_info = {
        "available_cameras": available_cameras,
        "camera_status": {}
    }
    for cam_idx in available_cameras:
        has_frame = cam_idx in latest_frames and latest_frames[cam_idx] is not None
        status_info["camera_status"][cam_idx] = {
            "has_recent_frame": has_frame,
            "camera_active": cam_idx in cameras
        }
    return status_info

def video_feeder(stop_event):
    # Find available cameras indices
    for i in range(10):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            available_cameras.append(i)
        camera.release()
    if not available_cameras:
        print("No cameras found!")
        return
    for camera_index in available_cameras:
        camera = setup_camera(camera_index)
        if camera is None:
            continue
        cameras[camera_index] = camera
        latest_frames[camera_index] = None
        frame_locks[camera_index] = threading.Lock()
        capture_thread = threading.Thread(target=capture_frames, args=(camera_index, stop_event), daemon=True)
        capture_thread.start()
    time.sleep(5)
    # Flask's run() is blocking, so we check stop_event in a thread
    def flask_runner():
        app.run(host="0.0.0.0", port=5000, threaded=True)
    flask_thread = threading.Thread(target=flask_runner, daemon=True)
    flask_thread.start()
    while not stop_event.is_set():
        time.sleep(0.5)

if __name__ == "__main__":
    stop_event = threading.Event()

    def signal_handler(sig, frame):
        print("Shutting down gracefully...")
        stop_event.set()
        time.sleep(1)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    t1 = threading.Thread(target=handshaker, args=(stop_event,), daemon=True)
    t2 = threading.Thread(target=video_feeder, args=(stop_event,), daemon=True)
    t1.start()
    t2.start()
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
