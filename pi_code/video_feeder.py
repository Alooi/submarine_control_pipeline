import cv2
from flask import Flask, Response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
logging.info("Flask app is running")


def generate_frames(camera_index):
    camera = cv2.VideoCapture(camera_index)
    logging.info(f"Camera {camera_index} opened: {camera.isOpened()}")
    try:
        while True:
            success, frame = camera.read()
            if not success:
                logging.error(f"Camera {camera_index} is disconnected")
                break
            else:
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
    except Exception as e:
        logging.exception(f"Exception occurred in generate_frames: {e}")
    finally:
        camera.release()
        logging.info(f"Camera {camera_index} released")


@app.route("/video_feed_1")
def video_feed_1():
    logging.info("Starting the video feed 1")
    return Response(
        generate_frames(0), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video_feed_2")
def video_feed_2():
    return Response(
        generate_frames(1), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    logging.info("Starting the Flask app")
    app.run(host="0.0.0.0", port=5000)