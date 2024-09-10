import socket
import time
import threading

# Broadcast address and port
BROADCAST_IP = "192.168.1.255"  # Broadcast address for your network
PORT = 5005
MESSAGE = b"Who are you?"

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
devices = {}  # Dictionary to store IP and device names

def get_devices(device_name="", addr=None):
    if device_name:
        print(f"Device found: {device_name} at {addr[0]}")
        devices[addr[0]] = device_name
        return devices
    else:
        # otherwise send broadcast message
        sock.sendto(MESSAGE, (BROADCAST_IP, PORT))

        print("Waiting for responses from devices...")
    return devices

def listen_to_data():
    # Listen for data from devices
    while True:
        data, addr = sock.recvfrom(1024)
        # send to functions
        # if data starts with "I am", then it is a device name
        if data.decode().startswith("I am"):
            print("Sending device name to get_devices")
            device_name = data.decode().split("I am ")[1]
            get_devices(device_name, addr)
        elif data.decode().startswith("data"):
            print("Data received")
            print(data.decode())
            # do something with the data

if __name__ == "__main__":
    devices = get_devices()
    # run the listen_to_data function in a separate thread
    t = threading.Thread(target=listen_to_data)
    t.start()
    # Keep the main thread running
    while True:
        time.sleep(1)
        print("main thread running...")


sock.close()
