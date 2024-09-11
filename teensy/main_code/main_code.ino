#include <Wire.h>

// include myAHRS+ library
#include "myAHRS_plus.h"

#define MYAHRS_I2C_ADDR 0x20 // Change if your sensor uses a different I2C address

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
  Wire1.begin();
  Serial.begin(115200);

  // Scan I2C bus for devices
  Serial.println("Scanning I2C bus...");
  scanI2CBus(Wire1);

  // Initialize sensor
  if (sensor_init())
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
  // Read sensor data
  // using read_euler
  // returns {roll, pitch, yaw};
  float euler[3];
  read_euler(euler);
  Serial.print("Roll: ");
  Serial.println(euler[0]);
  Serial.print(" Pitch: ");
  Serial.println(euler[1]);
  Serial.print(" Yaw: ");
  Serial.println(euler[2]);

  delay(100);
}