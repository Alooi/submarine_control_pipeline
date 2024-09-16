import socket
import time
import threading
import sys
from controller import Controller

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# import MainWindow
from main_window import MainWindow
import configparser

class BigBoyControl:
    def __init__(self):
        # Broadcast address and port
        self.BROADCAST_IP = "192.168.1.255"  # Broadcast address for your network
        self.PORT = 5005
        self.MESSAGE = b"Who are you?"
        self.use_controller = False
        self.window = None

        self.camera_ports = [5000, 5001]

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.devices = {}  # Dictionary to store IP and device names

    def parse_sensor_data(self, data):
        # Split the data into lines
        lines = data.split('\n')[1:]  # Skip the first line

        # Initialize an empty dictionary
        sensor_data = {}

        # Loop through each line and split by colon
        for line in lines:
            if line:  # Check if the line is not empty
                key, value = line.split(': ')
                # Convert value to float or int if possible
                if value.isdigit():
                    sensor_data[key] = int(value)
                else:
                    try:
                        sensor_data[key] = float(value)
                    except ValueError:
                        sensor_data[key] = value  # Keep as string if conversion fails

        return sensor_data

    def get_devices(self, device_name="", addr=None):
        if device_name:
            print(f"Device found: {device_name} at {addr[0]}")
            self.devices[addr[0]] = device_name
            return self.devices
        else:
            # otherwise send broadcast message
            self.sock.sendto(self.MESSAGE, (self.BROADCAST_IP, self.PORT))

            print("Waiting for responses from devices...")
        return self.devices
    def listen_to_data(self):
        # Listen for data from devices
        while True:
            data = None
            data, addr = self.sock.recvfrom(1024)
            # send to functions
            # if data starts with "I am", then it is a device name
            if data.decode().startswith("I am"):
                device_name = data.decode().split("I am ")[1]
                self.get_devices(device_name, addr)
            elif data.decode().startswith("data"):
                # print(data.decode())
                # send to update the network status
                self.window.network_status.set_device_status(self.devices[addr[0]], addr[0], True)
                # send data to update gauge
                self.update_gauges(data.decode())
            else:
                # reset the status of every device
                for device in self.devices:
                    self.window.network_status.set_device_status(self.devices[device], device, False)

    def input_stream(self):
        controller = Controller()
        t = threading.Thread(target=controller.get_controller_values)
        t.start()
        while True:
            if controller.button[9]:
                self.use_controller = not self.use_controller
                print(f"Controller is {'on' if self.use_controller else 'off'}")
            if self.use_controller:
                # convert controller values to bytes
                controller_values = ("controller: " + str(controller.axis)).encode()
                # send values to teensy
                self.sock.sendto(controller_values, (self.devices['Teensy'], self.PORT))
    
    def refresh_stuff(self):
        self.get_devices()
        # if key "RPi" is in devices, then initiate video feed
        if 'RPi' in self.devices: 
            self.window.initiate_video_feed(self.devices['RPi'], self.camera_ports)
        
    def run(self):
        # run the GUI
        app = QApplication(sys.argv)
        self.window = MainWindow()
        self.window.show()
        self.devices = self.get_devices()
        # manually initialize the video feed
        self.window.initiate_video_feed("localhost", self.camera_ports)
        self.window.network_status.refresh_button.clicked.connect(lambda: self.refresh_stuff())
        # run the listen_to_data function in a separate thread
        data_listener = threading.Thread(target=self.listen_to_data)
        data_listener.start()
        # run the input_stream function in a separate thread
        input_stream = threading.Thread(target=self.input_stream)
        input_stream.start()
        sys.exit(app.exec())
        

    # create a function to update the gauges

    def update_gauges(self, data):
        # parse the sensor data
        data = self.parse_sensor_data(data)
        # set the pitch angle
        self.window.pitch_indicator.set_pitch_angle(data['Pitch'])

        # set the roll angle
        self.window.roll_indicator.set_roll_angle(data['Roll'])

        # set the yaw angle
        self.window.yaw_indicator.set_yaw_angle(data['Yaw'])

        # set the depth value
        self.window.depth_widget.set_depth(data['Depth'])

        # set the depthStatus value
        self.window.depth_connection.set_status(status=data['depthStatus'])

        # set the imuStatus value
        self.window.imu_connection.set_status(status=data["imuStatus"])
        # self.window.camera_connection.set_status(status=self.window.video_feed.status)

if __name__ == "__main__":
    # Load configuration from setup.config
    config = configparser.ConfigParser()
    config.read('/home/ali/codebases/big_boy_control/setup.config')

    # Update the instance variables
    main_frame = BigBoyControl()
    main_frame.camera_ports = [config.getint('VideoFeed', 'CAMERA_PORT1', fallback=5000), config.getint('VideoFeed', 'CAMERA_PORT2', fallback=5001)]
    main_frame.run()