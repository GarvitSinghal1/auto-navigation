# QR Code Autonomous Navigation Robot

This project implements an autonomous navigation system for an Arduino-based robot using a smartphone camera as a visual sensor. The robot detects QR codes, centers them in its field of view, and navigates toward them.

## Features

- Video streaming from IP Camera smartphone app
- QR code detection and tracking
- Arduino-based motor control for navigation
- Visual feedback with navigation information
- QR code generation utility

## Hardware Requirements

- Arduino board (e.g., Arduino Uno, Nano, Mega)
- L298N or similar motor driver for DC motors
- Chassis with DC motors
- Smartphone with IP Camera app
- Computer or Raspberry Pi to run the Python code
- USB cable to connect Arduino to computer
- Printed QR code(s) to track

## Wiring

Connect your Arduino to the motor driver as follows:

- **Arduino Pin 3** → Motor Driver ENA (Left Motor PWM)
- **Arduino Pin 2** → Motor Driver IN1 (Left Motor Direction)
- **Arduino Pin 4** → Motor Driver IN2 (Left Motor Direction)
- **Arduino Pin 6** → Motor Driver ENB (Right Motor PWM)
- **Arduino Pin 5** → Motor Driver IN3 (Right Motor Direction)
- **Arduino Pin 7** → Motor Driver IN4 (Right Motor Direction)

Note: Pins 3 and 6 are PWM pins needed for speed control of the motors.

## Software Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Upload the Arduino code:
   - Open `arduino_controller/arduino_controller.ino` in the Arduino IDE
   - Upload to your Arduino board

3. Download an IP Camera app on your smartphone:
   - For Android: "IP Webcam" is recommended
   - For iOS: "IP Camera Lite" or similar
   - Start the camera server and note the URL (typically http://your-phone-ip:8080/video)

4. Generate and print QR codes (optional):
   ```
   python generate_qr_code.py
   ```
   - You can use the defaults or specify parameters to customize your QR code

## Usage

### Testing QR Code Detection

Before starting navigation, test if your camera can detect QR codes:

```
python test_qr_detection.py
```

Enter your camera URL and show a QR code to the camera to verify it's detected correctly.

### QR Code Navigation

Run the navigation system:

```
python pyzbar_navigation.py
```

The script will prompt you for:
- Camera URL (from your phone's IP camera app)
- Arduino serial port (e.g., COM3, COM6)
- Other configuration options

### Controls

- Press 'q' to quit

## QR Code Setup

For best results:
- Print your QR code on white paper
- Make it reasonably large (at least 10x10 cm)
- Ensure good lighting without glare
- Place it on a flat surface or attach it to the object you want the robot to follow

## Troubleshooting

1. **Cannot connect to camera**: Ensure your phone and computer are on the same Wi-Fi network and the IP camera app is running.

2. **Arduino not found**: Check the serial port and ensure the Arduino is properly connected. Use the full port name (e.g., "COM6" not just "6").

3. **Motors not responding**: Verify the wiring connections and ensure the motor driver has proper power supply.

4. **QR code not detected**: Improve lighting, reduce glare, ensure the QR code is within view and large enough.

5. **pyzbar warnings**: Warnings about the PDF417 decoder can be safely ignored, they don't affect QR code detection.

## Command System

The Arduino code responds to the following commands:

- 'F': Move forward
- 'B': Move backward
- 'L': Turn left
- 'R': Turn right
- 'S': Stop

## License

This project is open source and available under the MIT License. 