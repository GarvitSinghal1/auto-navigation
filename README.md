# QR Code Autonomous Navigation Robot

This project implements an autonomous navigation system for an Arduino-based robot. The robot uses a smartphone's camera, streaming video over Wi-Fi, to detect and track QR codes. It centers the QR code in its view and moves towards it, enabling simple object-following behavior.

The system also includes an alternative wireless control method using NRF24L01 modules for manual testing.

## Features

-   **Autonomous Navigation:** The robot navigates towards a designated QR code target.
-   **Computer Vision:** Utilizes `pyzbar` and `OpenCV` for robust QR code detection and tracking from a live video stream.
-   **IP Camera Integration:** Streams video from a smartphone app, eliminating the need for a dedicated camera on the robot.
-   **Serial Communication:** A Python script on a host computer sends navigation commands to the Arduino via a USB serial connection.
-   **Visual Feedback:** The video stream is annotated with detection boxes, center lines, and status information for real-time monitoring.
-   **Modular Utilities:** Includes scripts for generating custom QR codes and testing camera detection.

## How It Works

The system operates based on a simple control loop:

1.  **Video Stream:** A smartphone running an IP camera app streams video over the local Wi-Fi network.
2.  **Processing:** A Python script (`pyzbar_navigation.py`) running on a computer connects to the video stream.
3.  **Detection:** For each frame, the script detects a QR code using the `pyzbar` library.
4.  **Navigation Logic:** The script calculates the horizontal position of the detected QR code's center.
    -   If the QR code is in the center of the frame, it sends a 'Forward' command.
    -   If the QR code is to the left, it sends a 'Turn Left' command.
    -   If the QR code is to the right, it sends a 'Turn Right' command.
    -   If no QR code is detected, it sends a 'Stop' command.
5.  **Motor Control:** The command is sent to the Arduino via a USB serial connection. The Arduino (`arduino_controller.ino`) interprets the command and controls the motors through an L298N driver.

## Hardware Requirements

-   Arduino board (e.g., Arduino Uno, Nano)
-   L298N Motor Driver Module
-   Robot Chassis with two DC motors and wheels
-   Smartphone with an IP camera app installed (e.g., "IP Webcam" for Android)
-   Computer (PC/Mac/Linux) or Raspberry Pi to run the Python scripts
-   USB cable to connect the Arduino to the computer

## Software & Setup

### 1. Install Python Dependencies

Ensure you have Python 3 installed. Clone the repository and install the required libraries:

```bash
git clone https://github.com/garvitsinghal1/auto-navigation.git
cd auto-navigation
pip install -r requirements.txt
```

### 2. Upload Arduino Code

-   Connect your Arduino board to the computer via USB.
-   Open `arduino_controller/arduino_controller.ino` in the Arduino IDE.
-   Select your board and port from the `Tools` menu.
-   Upload the sketch to your Arduino.

### 3. Set Up IP Camera

-   Install an IP camera app on your smartphone.
-   Connect your smartphone to the same Wi-Fi network as your computer.
-   Start the camera server in the app and note the video stream URL (e.g., `http://192.168.1.5:8080/video`).

## Wiring

Connect the L298N motor driver to the Arduino as follows. These pins are defined in `arduino_controller.ino`.

| L298N Pin | Function      | Arduino Pin |
| :-------- | :------------ | :---------- |
| ENA       | Left Motor PWM Speed    | Pin 3       |
| IN1       | Left Motor Direction    | Pin 2       |
| IN2       | Left Motor Direction    | Pin 4       |
| ENB       | Right Motor PWM Speed   | Pin 6       |
| IN3       | Right Motor Direction   | Pin 5       |
| IN4       | Right Motor Direction   | Pin 7       |

**Note:** Ensure your L298N motor driver is powered correctly, typically with a separate power supply for the motors. The Arduino and motor driver must share a common ground (GND).

## Usage

### Step 1: Generate a QR Code (Optional)

You can use any QR code, but a custom one is easy to generate. This script creates a `robot_target.png` file.

```bash
python generate_qr_code.py --data "ROBOT_TARGET"
```
Print the generated QR code. For best results, make it at least 10x10 cm.

### Step 2: Test QR Code Detection

Before running the full navigation, you can test your camera setup and QR code visibility.

```bash
python test_qr_detection.py
```
The script will ask for your camera source. Enter the IP camera URL. A window will open showing the camera feed. Hold up your printed QR code to verify that it is detected.

### Step 3: Run Autonomous Navigation

Run the main navigation script.

```bash
python pyzbar_navigation.py
```

The script will prompt you to enter the following:
-   **IP Camera URL:** The URL from your smartphone app.
-   **Arduino Serial Port:** The port your Arduino is connected to (e.g., `COM3` on Windows, `/dev/ttyACM0` on Linux).
-   **Baud Rate:** (Default: 9600)
-   **Frame Width & Skip:** Performance-tuning options. Defaults are usually fine.

A window will appear showing the video feed with navigation overlays. Place the robot on the floor and show it the QR code to begin navigation. Press `q` in the video window to quit.

## Arduino Command System

The `arduino_controller.ino` sketch listens for single-character commands over serial:
-   `F`: Move forward
-   `B`: Move backward
-   `L`: Turn left (pivots left)
-   `R`: Turn right (pivots right)
-   `S`: Stop motors

## Alternative Wireless Control (NRF24L01)

This repository includes an alternative control system using NRF24L01 wireless modules, which is useful for testing the robot's hardware without the vision system.

-   **Transmitter (`sender/sender.ino`):** Upload this to an Arduino connected to your computer. It reads commands (`F`, `B`, `L`, `R`, `S`) from the Serial Monitor and transmits them wirelessly.
-   **Receiver (`test_car/test_car.ino`):** Upload this to the Arduino on your robot. It listens for wireless commands and controls the motors accordingly.

This setup allows for direct manual control of the robot, bypassing the Python script.

## Troubleshooting

-   **Cannot connect to camera:** Double-check that your phone and computer are on the same Wi-Fi network. Verify the IP address and port number are correct.
-   **Arduino not found / Access Denied:** Ensure you have selected the correct serial port. Check if another program (like the Arduino IDE's Serial Monitor) is using the port.
-   **Motors not responding:** Check all wiring connections. Make sure the L298N motor driver has a sufficient power supply and a common ground with the Arduino.
-   **QR code not detected:** Ensure the QR code is well-lit, flat, and not subject to glare. A larger QR code is easier to detect from a distance. The `test_qr_detection.py` script is useful for debugging this.
