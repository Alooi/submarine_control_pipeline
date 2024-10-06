import socket
import os

# Set up the UDP listener
# setup the ip dhcp
os.system("sudo dhclient eth0")
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005  # Set your port

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

pc_connection = False
pcIP = None
pcPort = None

while True:
    # Listen for incoming packets
    packet, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
    packet = packet.decode("utf-8")  # Decode the bytes to a string
    print(f"Received packet: {packet} from {addr}")

    if packet == "Who are you?":
        # Store the PC IP and port
        pcIP = addr[0]
        pcPort = addr[1]
        pc_connection = True

        # Send the response back to the sender
        response = "I am RPi"
        sock.sendto(response.encode("utf-8"), addr)
        print(f"Sent response: {response}")