import socket
import time
import threading
import sys
from controller import Controller

class BigBoyControl:
    def __init__(self):
        # Broadcast address and port
        self.BROADCAST_IP = "192.168.1.255"  # Broadcast address for your network
        self.PORT = 5005
        self.MESSAGE = b"Who are you?"
        self.use_controller = False

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.devices = {}  # Dictionary to store IP and device names

    def get_devices(self, device_name="", addr=None):
        if device_name:
            print(f"Device found: {device_name} at {addr[0]}")
            self.devices[device_name] = addr[0]
            return self.devices
        else:
            # otherwise send broadcast message
            self.sock.sendto(self.MESSAGE, (self.BROADCAST_IP, self.PORT))

            print("Waiting for responses from devices...")
        return self.devices

    def listen_to_data(self):
        # Listen for data from devices
        while True:
            data, addr = self.sock.recvfrom(1024)
            # send to functions
            # if data starts with "I am", then it is a device name
            if data.decode().startswith("I am"):
                device_name = data.decode().split("I am ")[1]
                self.get_devices(device_name, addr)
            elif data.decode().startswith("data"):
                print(data.decode())
                # pass
                # do something with the data
                
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

    def run(self):
        self.devices = self.get_devices()
        # run the listen_to_data function in a separate thread
        data_listener = threading.Thread(target=self.listen_to_data)
        data_listener.start()
        # run the input_stream function in a separate thread
        input_stream = threading.Thread(target=self.input_stream)
        input_stream.start()
        while True:
            pass
        
        

if __name__ == "__main__":
    main_frame = BigBoyControl()
    main_frame.run()