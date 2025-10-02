
/*
IMU-Controlled 3D Object - Arduino/ESP32 Code for MPU6050
Reads gyroscope and accelerometer data, applies complementary filter,
and sends orientation data via serial communication.
*/

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Gyroscope and accelerometer raw data
int16_t ax, ay, az;
int16_t gx, gy, gz;

// Gyroscope offset values (calibrated)
float gyroXoffset, gyroYoffset, gyroZoffset;

// Angle calculations
float gyroAngleX, gyroAngleY, gyroAngleZ;
float accAngleX, accAngleY;
float roll, pitch, yaw;

// Complementary filter coefficient
float alpha = 0.96;

// Timing variables
unsigned long timer;
float timeStep, time;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pinMode(LED_BUILTIN,OUTPUT);

  // Initialize MPU6050
  mpu.initialize();

  // Check connection
  if (mpu.testConnection()) {
    Serial.println("MPU6050 connection successful");
  } else {
    Serial.println("MPU6050 connection failed");
  }

  // Configure gyroscope and accelerometer sensitivity
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_500);
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);

  // Calibrate gyroscope
  calibrateGyro();

  timer = millis();
}

void loop() {
  // Calculate time step
  timeStep = (millis() - timer) / 1000.0;
  timer = millis();

  // Read raw accelerometer and gyroscope data
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Convert raw data to degrees
  float gyroX = (gx / 65.5) - gyroXoffset;  // 65.5 LSB/°/s for ±500°/s
  float gyroY = (gy / 65.5) - gyroYoffset;
  float gyroZ = (gz / 65.5) - gyroZoffset;

  // Calculate accelerometer angles
  accAngleX = (atan2(ay, sqrt(pow(ax, 2) + pow(az, 2))) * 180 / PI) - 1.15; // -1.15 is offset
  accAngleY = (atan2(-ax, sqrt(pow(ay, 2) + pow(az, 2))) * 180 / PI) + 0.25; // +0.25 is offset

  // Apply complementary filter
  roll = alpha * (roll + gyroX * timeStep) + (1 - alpha) * accAngleX;
  pitch = alpha * (pitch + gyroY * timeStep) + (1 - alpha) * accAngleY;
  yaw += gyroZ * timeStep; // Yaw is calculated by integration only

  // Keep yaw within ±180 degrees
  if (yaw > 180) yaw -= 360;
  if (yaw < -180) yaw += 360;

  // Send data via serial (CSV format)
  Serial.print(roll, 2);
  Serial.print(",");
  Serial.print(pitch, 2);
  Serial.print(",");
  Serial.println(yaw, 2);

  delay(10); // 100 Hz update rate
}

void calibrateGyro() {
  Serial.println("Calibrating gyroscope... Keep sensor still!");
  delay(2000);

  int calibrationSamples = 2000;
  float gyroXsum = 0, gyroYsum = 0, gyroZsum = 0;

  for (int i = 0; i < calibrationSamples; i++) {
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    gyroXsum += gx / 65.5;
    gyroYsum += gy / 65.5;
    gyroZsum += gz / 65.5;
    delay(5);
  }

  gyroXoffset = gyroXsum / calibrationSamples;
  gyroYoffset = gyroYsum / calibrationSamples;
  gyroZoffset = gyroZsum / calibrationSamples;

  Serial.println("Gyroscope calibration complete!");
  Serial.print("X offset: "); Serial.println(gyroXoffset);
  Serial.print("Y offset: "); Serial.println(gyroYoffset);
  Serial.print("Z offset: "); Serial.println(gyroZoffset);
  digitalWrite(LED_BUILTIN,HIGH);

}
