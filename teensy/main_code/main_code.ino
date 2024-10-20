// include myAHRS+ library
#include "myAHRS_plus.h"
#include "eigen.h"      // Calls main Eigen matrix class library
#include <Eigen/LU>     // Calls inverse, determinant, LU decomp., etc.

#include "Servo.h"
#include <QNEthernet.h>
#include <Wire.h>
#include "MS5837.h"
#include <iostream>
#include <string>
#include <sstream>
#include <regex>
#include <vector>
using namespace qindesign::network;

EthernetUDP Udp;
const unsigned int localPort = 5005;

MS5837 sensor;



#define MYAHRS_I2C_ADDR 0x20 // Change if your sensor uses a different I2C address

// variables to store the status of components
bool serialStatus = false;
bool depthStatus = false;
bool imuStatus = false;
bool ethernetStatus = false;
bool udpStatus = false;
bool pc_connection = false;

// variable to store top pc ip once received in the loop
IPAddress pcIP;
// variable to store the port
int pcPort;

#define SERVO1_PWM_PIN 2 // MAIN SERVO
#define SERVO2_PWM_PIN 3 // TAIL SERVO TOP
#define SERVO3_PWM_PIN 4 // TAIL SERVO BOTTOM LEFT (LOOKING FORWARD ORIENTATION)
#define SERVO4_PWM_PIN 5 // TAIL SERVO BOTTOM RIGHT (LOOKING FORWARD ORIENTATION)
#define SERVO5_PWM_PIN 6 // SPARE PWM

Servo servo1_;
Servo servo2_;
Servo servo3_;
Servo servo4_;
Servo servo5_;



// function to to control the sub
void controlSub(std::vector<double> values)
{
  Serial.println("Pitch: " + String(values[0]));
  Serial.println("Roll: " + String(values[1]));
  Serial.println("Yaw: " + String(values[2]));

  // Define joystick input as a 3x1 vector (yaw, pitch, roll)
  Eigen::Vector3f joystickInput;
  joystickInput << float(values[0]), float(values[1]), float(values[2]);

        // Define the 4x3 transformation matrix for yaw, pitch, and roll mapping
        Eigen::Matrix<float, 4, 3> A;
        A <<  1,  -1,  -1,   // Servo 1
             -1,  -1, -1,   // Servo 2
              1,  1, -1,   // Servo 3
             -1,  1,  -1;   // Servo 4

        // Perform matrix multiplication to get servo commands (4x1 vector)
  Eigen::Vector4f servoCommands = A * joystickInput;

        // Map the servo commands to appropriate PWM values (1000–2000 µs typical range)
  float pwm_min = 1000.0;
  float pwm_max = 2000.0;
  float pwm_neutral = 1500.0;  // Neutral position

  for (int i = 0; i < 4; i++) {
    // Scale the commands to the PWM range
    servoCommands[i] = pwm_neutral + (servoCommands[i] * (pwm_max - pwm_min) / 2);
    }

    // Update the servos with calculated commands (scaled to PWM)
    servo1_.writeMicroseconds(servoCommands[0]);  // Send command to Servo 1
    servo2_.writeMicroseconds(servoCommands[1]);  // Send command to Servo 2
    servo3_.writeMicroseconds(servoCommands[2]);  // Send command to Servo 3
    servo4_.writeMicroseconds(servoCommands[3]);  // Send command to Servo 4

    // Debugging output
    // Serial.println("Servo Commands: ");
    // Serial.println(servoCommands[0]);
    // Serial.println(servoCommands[1]);
    // Serial.println(servoCommands[2]);
    // Serial.println(servoCommands[3]);
}

// function to extract the values of the controller
std::vector<double> extractDictionaryValues(const std::string &input)
{
  std::vector<double> values;
  std::regex valueRegex(R"(-?\d+\.\d+)"); // Regular expression to match floating-point numbers, including negative values
  std::smatch match;

  std::string::const_iterator searchStart(input.cbegin());
  while (std::regex_search(searchStart, input.cend(), match, valueRegex))
  {
    double value = std::stod(match[0]); // Convert matched string to double
    if (value >= -1.0 && value <= 1.0)  // Check if the value is within the range [-1.0, 1.0]
    {
      values.push_back(value);
    }
    searchStart = match.suffix().first; // Move search start position forward
  }

  return values;
}

// function to get what comamnd is sent from the pc
bool get_command(const std::string &input, const std::string &compareTo)
{
  std::stringstream ss(input);
  std::string firstPart;

  // Split the string by ':'
  if (std::getline(ss, firstPart, ':'))
  {
    // Compare the first part to the given string
    return firstPart == compareTo;
  }

  return false; // Return false if splitting fails
}

// Function to scan an I2C bus for devices
bool scanI2CBus(TwoWire &wire)
{
  for (byte address = 1; address < 127; address++)
  {
    wire.beginTransmission(address);
    if (wire.endTransmission() == 0)
    {
      Serial.print("Found I2C device at address 0x");
      Serial.println(address, HEX);
      return true;
    }
  }
  return false;
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

  depthStatus = scanI2CBus(Wire);
  imuStatus = scanI2CBus(Wire1);

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

  servo1_.attach(SERVO1_PWM_PIN);    // attaches the servo on pin
  servo2_.attach(SERVO2_PWM_PIN);    // attaches the servo on pin
  servo3_.attach(SERVO3_PWM_PIN);    // attaches the servo on pin
  servo4_.attach(SERVO4_PWM_PIN);    // attaches the servo on pin
  servo5_.attach(SERVO5_PWM_PIN);    // attaches the servo on pin


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

    // Serial.print("Received packet: ");
    // Serial.println(packetBuffer);

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
    else if (get_command(packetBuffer, "controller"))
    {
      // Send controller data to control functions TODO
      std::vector<double> values = extractDictionaryValues(packetBuffer);
      for (int i = 0; i < values.size(); i++)
      {
        controlSub(values);
      }
      // ----------------------------
    }
    else if (strcmp(packetBuffer, "refresh") == 0)
    {
      // recheck status of sensors
      depthStatus = scanI2CBus(Wire);
      imuStatus = scanI2CBus(Wire1);
    }

  }
  // Send depth sensor data to the pc
  sensor.read();
  // check if the data from the sensor is valid
  if (sensor.depth() > 100 or sensor.depth() < -100)
  {
    depthStatus = false;
  }
  else
  {
    depthStatus = true;
  }
  // Read IMU sensor data
  // using read_euler
  // returns {roll, pitch, yaw};
  float euler[3];
  imuStatus = read_euler(euler);
  // make string to store sensor data
  String data = String(
    "data" + String("\n") +
    "Pressure: " + String(sensor.pressure()) + String("\n") +
    "Temperature: " + String(sensor.temperature()) + String("\n") +
    "Depth: " + String(sensor.depth()) + String("\n") +
    "Altitude: " + String(sensor.altitude()) + String("\n") +
    "Roll: " + String(euler[0]) + String("\n") +
    "Pitch: " + String(euler[1]) + String("\n") +
    "Yaw: " + String(euler[2]) + String("\n") +
    "depthStatus: " + String(depthStatus) + String("\n") +
    "imuStatus: " + String(imuStatus) + String("\n")
  );
  const char* dataChar = data.c_str();
  if (!pc_connection)
  {
    Serial.println("No PC connection");
    delay(2000);
  }
  else
  {
    Udp.beginPacket(pcIP, pcPort);
    Udp.write(dataChar);
    Udp.endPacket();
  }
}
