import socket
from scapy.all import ARP, Ether, srp
import os
import re


def get_host_ip(starts_with):
    # find all ip addresses using terminal command
    command = "ip addr show"
    process = os.popen(command)
    results = str(process.read())
    process.close()

    # extract the ip address using regular expressions
    ip = re.findall(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", results)
    host_ip = ""
    for i in ip:
        if i.startswith(starts_with):
            host_ip = i
            break

    return host_ip
def scan_network(network):
    # Create an ARP request packet
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract and print the IP addresses from the response
    devices = []
    for sent, received in result:
        devices.append({"ip": received.psrc, "mac": received.hwsrc})

    return devices


# Define the network range to scan
network = "169.254.95.0/24"
devices = scan_network(network)

# Add the host machine's IP address to the list of devices
ip_start = "169.254.95"
host_ip = get_host_ip(ip_start)
devices.append({"ip": host_ip, "mac": "N/A (Host Machine)"})

print("Available devices in the network:")
for device in devices:
    print(f"IP: {device['ip']}, MAC: {device['mac']}")*