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

from parse_data import SensorDataParser
parser = SensorDataParser()

from recorder import DataLogger
from opencv_communicator import opencv_communicator

class BigBoyControl:
    def __init__(self):
        # Broadcast address and port
        self.BROADCAST_IP = "192.168.1.255"  # Broadcast address for your network
        self.PORT = 5005
        self.MESSAGE = b"Who are you?"
        self.use_controller = False
        self.window = None

        self.record_flag = False
        self.recorder = DataLogger()
        self.video_feed = []
        self.teensy_address = None
        self.new_devices = {}
        self.pi_exist = False

        self.camera_urls = [5000, 5001]

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
            # print(f"Device found: {device_name} at {addr[0]}")
            self.devices[addr[0]] = device_name
            # set the device status to true
            self.window.network_status.set_device_status(device_name, addr[0], True)
            if device_name == "Teensy":
                self.teensy_address = addr[0]
            return self.devices
        else:
            # otherwise send broadcast message
            self.sock.sendto(self.MESSAGE, (self.BROADCAST_IP, self.PORT))

            # print("Waiting for responses from devices...")
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
                data = parser(data.decode())
                # send to update the network status
                # self.window.network_status.set_device_status(self.devices[addr[0]], addr[0], True)
                # if record flag is true, then log the data
                if self.record_flag:
                    self.recorder.log_data(data)
                    # self.video_feed.get_frame(self.recorder.video_file)
                # send data to update gauge
                self.update_gauges(data)
            elif data.decode().startswith("message"):
                # send message to the message log
                pass

    def input_stream(self):
        controller = Controller()
        controller_status = controller.active
        prev_controller_values = None
        while True:
            controller.get_controller_values()
            if controller.active:
                if not controller_status:
                    controller_status = True
                    self.window.network_status.set_other_status("controller", True)
                # convert controller values to bytes
                controller_values = ("controller: " + str(controller.axis)).encode()
                # if current controller values does not equal previous controller values
                if controller_values != prev_controller_values:
                    prev_controller_values = controller_values
                    # send values to teensy
                    self.sock.sendto(controller_values, (self.teensy_address, self.PORT))
            else:
                if controller_status:
                    controller_status = False
                    self.window.network_status.set_other_status("controller", False)

    def refresh_stuff(self):
        # set all devices status to False
        for device in self.devices:
            self.window.network_status.set_device_status(self.devices[device], device, False)
        # get the devices again
        self.get_devices()
        # if key "RPi" is in devices, then initiate video feed
        self.check_pi()

    def check_pi(self):
        # check if the pi is connected
        for device in self.devices:
            if self.devices[device] == "RPi" and not self.pi_exist:
                # self.window.initiate_video_feed(device, self.camera_urls)
                # self.video_feed.set_urls(device)
                # self.window.camera_connection.set_status(True)
                self.window.network_status.set_other_status("Camera Feed", True)  # Use set_other_status for camera
                for url in self.camera_urls:
                    full_url = f"http://{device}:5000/{url}"
                    self.video_feed.append(opencv_communicator(full_url))
                self.pi_exist = True
                for feed in self.video_feed:
                    feed.start_opencv()
                return True
        return False

    def keep_alive(self):  # (temporary solution)
        self.refresh_stuff()

    def record_data_switch(self):
        self.record_flag = not self.record_flag
        self.window.network_status.set_record_status(self.record_flag)
        if self.record_flag:
            self.recorder.start_recording(self.video_feed)
        else:
            self.recorder.stop_recording()

    def run(self):
        # run the GUI
        app = QApplication(sys.argv)
        self.window = MainWindow()
        self.window.show()
        self.devices = self.get_devices()
        # manually initialize the video feed
        self.window.network_status.refresh_button.clicked.connect(lambda: self.refresh_stuff())
        self.window.network_status.record_button.clicked.connect(lambda: self.record_data_switch())
        # run the listen_to_data function in a separate thread
        data_listener = threading.Thread(target=self.listen_to_data)
        data_listener.start()
        # run the input_stream function in a separate thread
        input_stream = threading.Thread(target=self.input_stream)
        input_stream.start()
        # keep the GUI alive (temporary solution)
        self.timer = QTimer()
        self.timer.timeout.connect(self.keep_alive)
        self.timer.start(2000)
        sys.exit(app.exec())

    # create a function to update the gauges

    def update_gauges(self, data):
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
        # If you want to update camera status from data, use:
        # self.window.network_status.set_other_status("Camera Feed", data.get("cameraStatus", False))

if __name__ == "__main__":
    # Load configuration from setup.config
    config = configparser.ConfigParser()
    config.read('/home/ali/codebases/big_boy_control/setup.config')

    # Update the instance variables
    main_frame = BigBoyControl()
    main_frame.camera_urls = ["video_feed_1", "video_feed_2"]
    main_frame.run()
