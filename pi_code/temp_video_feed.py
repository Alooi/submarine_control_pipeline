import cv2
from flask import Flask, Response

app = Flask(__name__)


def generate_frames():
    # Capture video from the default webcam
    camera = cv2.VideoCapture(0)
    while True:
        # Read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Yield the frame as a byte stream for Flask
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    # Route to stream video frames
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
