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
        self.BROADCAST_IP = "192.168.2.255"  # Broadcast address for your network CHANGE DEPENDING ON SUBNET!
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
        self.device_last_seen = {}  # Track when devices were last seen

        self.camera_urls = [5000, 5001]

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(1.0)  # Add timeout for non-blocking operations
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
            self.device_last_seen[addr[0]] = time.time()
            # set the device status to true
            if self.window and hasattr(self.window, 'network_status'):
                self.window.network_status.set_device_status(device_name, addr[0], True)
            if device_name == "Teensy":
                self.teensy_address = addr[0]
            elif device_name == "RPi":
                self.check_pi()
            return self.devices
        else:
            # otherwise send broadcast message
            try:
                self.sock.sendto(self.MESSAGE, (self.BROADCAST_IP, self.PORT))
                # print("Broadcast message sent...")
            except Exception as e:
                print(f"Error sending broadcast: {e}")
        return self.devices

    def listen_to_data(self):
        # Listen for data from devices
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                # Update last seen time for this device
                self.device_last_seen[addr[0]] = time.time()
                
                # if data starts with "I am", then it is a device name
                if data.decode().startswith("I am"):
                    device_name = data.decode().split("I am ")[1]
                    self.get_devices(device_name, addr)
                elif data.decode().startswith("data"):
                    data = parser(data.decode())
                    # Update device status as active since we received data
                    if addr[0] in self.devices and self.window and hasattr(self.window, 'network_status'):
                        self.window.network_status.set_device_status(self.devices[addr[0]], addr[0], True)
                    # if record flag is true, then log the data
                    if self.record_flag:
                        self.recorder.log_data(data)
                    # send data to update gauge
                    self.update_gauges(data)
                elif data.decode().startswith("message"):
                    # send message to the message log
                    pass
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in listen_to_data: {e}")
                time.sleep(0.1)

    def input_stream(self):
        controller = Controller()
        controller_status = controller.active
        prev_controller_values = None
        while True:
            try:
                prev_axis = dict(controller.axis)  # Copy before update
                controller.get_controller_values()
                # If axis values changed, send immediately
                if controller.active:
                    if not controller_status:
                        controller_status = True
                        if self.window and hasattr(self.window, 'network_status'):
                            self.window.network_status.set_other_status("Controller", True)
                    controller_values = ("controller: " + str(controller.axis)).encode()
                    if controller.axis != prev_axis:
                        prev_controller_values = controller_values
                        if self.teensy_address:
                            try:
                                self.sock.sendto(controller_values, (self.teensy_address, self.PORT))
                            except Exception as e:
                                print(f"Error sending to Teensy: {e}")
                else:
                    if controller_status:
                        controller_status = False
                        if self.window and hasattr(self.window, 'network_status'):
                            self.window.network_status.set_other_status("Controller", False)
                # No sleep here for maximum responsiveness
            except Exception as e:
                print(f"Error in input_stream: {e}")
                time.sleep(0.01)  # Small delay only on error

    def refresh_stuff(self):
        # print("Refreshing devices...")
        # Don't immediately set all devices to False, let the timeout handle it
        # get the devices again
        self.get_devices()
        
    def check_device_timeouts(self):
        """Check if devices haven't been seen recently and mark them as offline"""
        current_time = time.time()
        timeout_duration = 10.0  # 10 seconds timeout
        
        for addr, last_seen in list(self.device_last_seen.items()):
            if current_time - last_seen > timeout_duration:
                if addr in self.devices:
                    device_name = self.devices[addr]
                    print(f"Device {device_name} at {addr} timed out")
                    if self.window and hasattr(self.window, 'network_status'):
                        self.window.network_status.set_device_status(device_name, addr, False)
                    # Handle specific device timeouts
                    if device_name == "RPi" and self.pi_exist:
                        self.pi_exist = False
                        # Stop video feeds
                        for feed in self.video_feed:
                            feed.stop_opencv()
                        self.video_feed.clear()

    def check_pi(self):
        # check if the pi is connected
        for device in self.devices:
            if self.devices[device] == "RPi" and not self.pi_exist:
                print(f"Initializing Pi connection at {device}")
                for url in self.camera_urls:
                    full_url = f"http://{device}:5000/{url}"
                    communicator = opencv_communicator(full_url)
                    self.video_feed.append(communicator)
                self.pi_exist = True
                for feed in self.video_feed:
                    feed.start_opencv()
                # Only set Camera Feed status to True if at least one feed is running
                camera_feed_running = any(feed.running for feed in self.video_feed)
                if self.window and hasattr(self.window, 'network_status'):
                    self.window.network_status.set_other_status("Camera Feed", camera_feed_running)
                return True
        return False

    def keep_alive(self):  # (temporary solution)
        self.refresh_stuff()
        self.check_device_timeouts()

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
        
        # Wait a moment for the window to initialize
        time.sleep(0.1)
        
        # Initialize device discovery
        self.get_devices()
        
        # Connect buttons
        if hasattr(self.window, 'network_status'):
            self.window.network_status.refresh_button.clicked.connect(lambda: self.refresh_stuff())
            self.window.network_status.record_button.clicked.connect(lambda: self.record_data_switch())
        
        # run the listen_to_data function in a separate thread
        data_listener = threading.Thread(target=self.listen_to_data, daemon=True)
        data_listener.start()
        
        # run the input_stream function in a separate thread
        input_stream = threading.Thread(target=self.input_stream, daemon=True)
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
        self.window.depth_widget.set_distances(data['Depth'], data['Depth'] + 20)  # Assuming seabed is 20 units below surface

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
    main_frame.run()
