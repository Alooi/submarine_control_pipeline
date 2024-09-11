#include <QNEthernet.h>
#include <Wire.h>
#include "MS5837.h"
using namespace qindesign::network;

EthernetUDP Udp;
const unsigned int localPort = 5005;

MS5837 sensor;

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

void setup()
{
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

  // Initialize the sensor
  Wire.begin();
  if (!sensor.init())
  {
    Serial.println("Failed to initialize sensor!");
    Serial.println("Retrying in 2 seconds...");
    delay(2000);
  }
  if (sensor.init())
  {
    Serial.println("Sensor initialized!");
    depthStatus = true;
  }
  else
  {
    Serial.println("Failed to initialize sensor!");
    depthStatus = false;
  }
  // ----------------------------

  // Initialize the IMU TODO
  
  // ----------------------------
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
  // Send sensor data to the pc
  sensor.read();
  // make string to store sensor data
  String data = String(
    "data" + String("\n") +
    "Pressure: " + String(sensor.pressure()) + String("\n") +
    "Temperature: " + String(sensor.temperature()) + String("\n") +
    "Depth: " + String(sensor.depth()) + String("\n") +
    "Altitude: " + String(sensor.altitude()) + String("\n")
    );
  Serial.println(data);
  const char* dataChar = data.c_str();
  if (!pc_connection)
  {
  }
  else
  {
    Udp.beginPacket(pcIP, pcPort);
    Udp.write(dataChar);
    Udp.endPacket();
  }

  // ----------------------------

  // Send IMU data to the pc TODO
  // ----------------------------
}
