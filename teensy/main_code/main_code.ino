// include myAHRS+ library
#include "myAHRS_plus.h"

#include <QNEthernet.h>
#include <Wire.h>
#include "MS5837.h"
using namespace qindesign::network;

EthernetUDP Udp;
const unsigned int localPort = 5005;

MS5837 sensor;



#define MYAHRS_I2C_ADDR 0x20 // Change if your sensor uses a different I2C address

// variables to store the status of components
bool serialStatus = false;
bool depthStatus = false;
bool ethernetStatus = false;
bool udpStatus = false;
bool pc_connection = false;

// variable to store top pc ip once received in the loop
IPAddress pcIP;
// variable to store the port
int pcPort;

// Function to scan an I2C bus for devices
void scanI2CBus(TwoWire &wire)
{
  for (byte address = 1; address < 127; address++)
  {
    wire.beginTransmission(address);
    if (wire.endTransmission() == 0)
    {
      Serial.print("Found I2C device at address 0x");
      Serial.println(address, HEX);
    }
  }
}

void setup()
{
  Wire.begin();
  Wire1.begin();
  // serial communication
  Serial.begin(9600);
  if (!Serial)
  {
    delay(1000);
  }
  if (!Serial)
  {
    serialStatus = false;
  }
  else
  {
    serialStatus = true;
  }
  // ----------------------------

  // Scan I2C bus for devices
  Serial.println("Scanning I2C bus...");
  scanI2CBus(Wire);
  scanI2CBus(Wire1);

  // Start Ethernet and try to get an IP address via DHCP
  if (!Ethernet.begin())
  {
    Serial.println("Failed to configure Ethernet using DHCP");
  }

  // Start UDP
  Udp.begin(localPort);
  Serial.println("Udp Began");
  Serial.println(Ethernet.localIP());
  // ----------------------------

  // Initialize the sensors
  // depth sensor
  if (!sensor.init())
  {
    Serial.println("Failed to initialize sensor!");
    Serial.println("Retrying in 2 seconds...");
    delay(2000);
  }
  // IMU sensor
  if (sensor.init())
  {
    Serial.println("Sensor initialized successfully");
  }
  else
  {
    Serial.println("Sensor initialization failed");
  }

}

void loop()
{
  int packetSize = Udp.parsePacket();
  if (packetSize > 0)
  {
    // Allocate a buffer to hold the incoming packet
    char packetBuffer[packetSize + 1]; // Plus one for the null terminator

    // Read the packet into the buffer
    Udp.read(packetBuffer, packetSize);

    // Null-terminate the string
    packetBuffer[packetSize] = '\0';

    Serial.print("Received packet: ");
    Serial.println(packetBuffer);

    // if MESSAGE = b"Who are you?", send back "Teensy"
    if (strcmp(packetBuffer, "Who are you?") == 0)
    {
      // store the pc ip and port
      pcIP = Udp.remoteIP();
      pc_connection = true;
      pcPort = Udp.remotePort();
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("I am Teensy");
      Udp.endPacket();
    }
    // if controller command
    else if (strcmp(packetBuffer, "Controller") == 0)
    {
      // Send controller data to control functions TODO
      // ----------------------------
    }

  }
  // Send depth sensor data to the pc
  sensor.read();
  // Read IMU sensor data
  // using read_euler
  // returns {roll, pitch, yaw};
  float euler[3];
  read_euler(euler);
  // make string to store sensor data
  String data = String(
    "data" + String("\n") +
    "Pressure: " + String(sensor.pressure()) + String("\n") +
    "Temperature: " + String(sensor.temperature()) + String("\n") +
    "Depth: " + String(sensor.depth()) + String("\n") +
    "Altitude: " + String(sensor.altitude()) + String("\n") +
    "Roll: " + String(euler[0]) + String("\n") +
    "Pitch: " + String(euler[1]) + String("\n") +
    "Yaw: " + String(euler[2]) + String("\n")
    );
  const char* dataChar = data.c_str();
  if (!pc_connection)
  {
    Serial.println("No PC connection");
  }
  else
  {
    Udp.beginPacket(pcIP, pcPort);
    Udp.write(dataChar);
    Udp.endPacket();
  }
}
