import cv2
import socket
import struct
import pickle

# Set up UDP socket
udp_ip = "127.0.0.1"
udp_port = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Open the two USB cameras
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        break

    # Serialize the frames
    data1 = pickle.dumps(frame1)
    data2 = pickle.dumps(frame2)

    # Send the frames over UDP
    sock.sendto(struct.pack("Q", len(data1)) + data1, (udp_ip, udp_port))
    sock.sendto(struct.pack("Q", len(data2)) + data2, (udp_ip, udp_port))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the cameras and close windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()
sock.close()