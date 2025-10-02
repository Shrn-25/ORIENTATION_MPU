# ORIENTATION_MPU

# Real-Time IMU 3D Visualization-PYTHON Version

⚡ A real-time 3D IMU (Inertial Measurement Unit) visualization system built in Python with instant response to sensor movement. Translated from Processing with significant improvements for real-time performance.

![IMU Demo](demo.gif) <!-- Add a GIF of your working system -->

## 🎯 Project Overview

This project visualizes IMU sensor data (roll, pitch, yaw) as a real-time 3D rotating cube. Originally built in Processing, this Python version includes advanced buffer management for zero-lag response and professional UI design.

### ✨ Key Features

- ⚡ **Real-time response** - Zero lag through smart serial buffer management
- 🎯 **Accurate orientation mapping** - Corrected coordinate system transformations
- 📊 **Professional UI** - Clean matplotlib display with no text overlaps
- 🔄 **Dual modes** - Serial IMU data + Demo mode for testing
- 🎮 **Interactive controls** - Keyboard shortcuts for easy operation
- 📡 **Robust communication** - Handles Arduino serial data at 115200 baud

## 🛠 Hardware Requirements

- Arduino Uno/Nano/ESP32
- MPU6050 IMU sensor (or compatible 6-DOF/9-DOF sensor)
- USB cable for serial communication

## 💻 Software Requirements
- Python 3.6+
- matplotlib (3D plotting)
- numpy (mathematical operations)
- pyserial (Arduino communication)


# Real-Time IMU 3D Visualization-Arduino Processing version

🎮 The original Processing implementation of real-time IMU visualization that inspired the Python version. Features direct Arduino-to-Processing communication with 3D cube rotation based on MPU6050 sensor data.

![Processing IMU Demo](processing_demo.gif)

## 🎯 Project Overview

This is the original Processing sketch that visualizes IMU sensor orientation data as a real-time rotating 3D cube. The cube responds instantly to physical movement of the MPU6050 sensor, providing intuitive visualization of roll, pitch, and yaw rotations.

### ✨ Key Features

- 🎮 **Processing-native 3D rendering** - Smooth, responsive visualization
- ⚡ **Real-time Arduino communication** - Direct serial data streaming
- 🎯 **Accurate orientation mapping** - Roll, pitch, yaw visualization
- 🎨 **Colorful 3D cube** - Different colored faces for easy orientation reference
- 🎮 **Interactive controls** - Keyboard shortcuts for mode switching
- 📊 **Live data display** - Real-time angle values and connection status

## 🛠 Hardware Requirements

- **Arduino Uno/Nano/ESP32**
- **MPU6050 IMU Sensor** (6-DOF accelerometer + gyroscope)
- **Jumper wires** for I2C connection
- **USB cable** for Arduino-PC communication

### 🔌 Wiring Diagram

MPU6050 Arduino
VCC → 3.3V
GND → GND
SCL → A5 (SCL)
SDA → A4 (SDA)

text

## 💻 Software Requirements

- **Processing IDE** (3.5.4 or newer) - Download from [processing.org](https://processing.org/download/)
- **Arduino IDE** - For uploading sensor code
- **MPU6050 Arduino Library** - Install via Arduino Library Manager
