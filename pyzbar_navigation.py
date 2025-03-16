import cv2
import numpy as np
import serial
import time
import os
try:
    import pyzbar.pyzbar as pyzbar
except ImportError:
    print("pyzbar not installed. Please install with: pip install pyzbar")
    print("Note: On Windows, you may also need to install the Visual C++ Redistributable.")
    exit(1)

def get_user_input():
    """Get configuration from user input"""
    print("\n===== QR Code Auto Navigation Robot (pyzbar) =====\n")
    
    # Get camera URL
    camera_url = input("Enter IP Camera URL (e.g., http://192.168.29.56:8080/video): ")
    
    # Get Arduino port
    default_port = "COM3"
    port_input = input(f"Enter Arduino serial port (default: {default_port}): ")
    port = port_input if port_input.strip() else default_port
    
    # Get baud rate
    default_baud = 9600
    baud_input = input(f"Enter baud rate (default: {default_baud}): ")
    try:
        baud_rate = int(baud_input) if baud_input.strip() else default_baud
    except ValueError:
        print(f"Invalid baud rate, using default: {default_baud}")
        baud_rate = default_baud
    
    # Get frame width
    default_width = 640
    width_input = input(f"Enter frame processing width (smaller = faster) (default: {default_width}): ")
    try:
        frame_width = int(width_input) if width_input.strip() else default_width
    except ValueError:
        print(f"Invalid width, using default: {default_width}")
        frame_width = default_width
    
    # Get frame skip
    default_skip = 2
    skip_input = input(f"Enter frame skip factor (higher = faster) (default: {default_skip}): ")
    try:
        skip_frames = int(skip_input) if skip_input.strip() else default_skip
    except ValueError:
        print(f"Invalid skip factor, using default: {default_skip}")
        skip_frames = default_skip
    
    print("\nStarting QR code navigation with these settings:")
    print(f"Camera URL: {camera_url}")
    print(f"Arduino Port: {port}")
    print(f"Baud Rate: {baud_rate}")
    print(f"Frame Width: {frame_width}")
    print(f"Frame Skip: {skip_frames}")
    
    return {
        'camera_url': camera_url,
        'port': port,
        'baud_rate': baud_rate,
        'frame_width': frame_width,
        'skip_frames': skip_frames
    }

class QRNavigationRobot:
    def __init__(self, camera_url, arduino_port, baud_rate=9600, resize_width=640, skip_frames=2):
        # Connect to camera
        print(f"\nConnecting to camera at {camera_url}...")
        self.cap = cv2.VideoCapture(camera_url)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video stream from {camera_url}")
        
        # Performance optimizations
        self.resize_width = resize_width
        self.skip_frames = max(1, skip_frames)
        self.frame_count = 0
        
        # Get frame dimensions
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.aspect_ratio = self.frame_height / self.frame_width
        self.resize_height = int(self.resize_width * self.aspect_ratio)
        
        print(f"Original camera resolution: {self.frame_width}x{self.frame_height}")
        print(f"Processing at resolution: {self.resize_width}x{self.resize_height}")
        print(f"Processing every {self.skip_frames} frame(s)")
        
        # Connect to Arduino
        try:
            print(f"Connecting to Arduino on {arduino_port}...")
            self.arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
            time.sleep(2)  # Wait for connection to establish
            print(f"Connected to Arduino on {arduino_port}")
        except Exception as e:
            self.arduino = None
            print(f"Warning: Could not connect to Arduino: {e}")
            print("Running in simulation mode (no Arduino control)")
        
        # Navigation parameters
        self.frame_center_x = self.resize_width // 2
        self.center_threshold = int(self.resize_width * 0.1)  # 10% of frame width
        
        # Control parameters
        self.last_command = None
        self.command_history = []
        self.qr_data = None  # Store the most recent QR code data
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.fps = 0
        
        # Display controls
        print("\nPress 'q' to quit")
        
    def detect_qr_codes(self, frame):
        """
        Detect QR codes using pyzbar
        
        Args:
            frame: Input video frame
            
        Returns:
            processed_frame: Frame with detection markers
            objects: List of QR codes as (x, y, w, h) tuples
        """
        # Make a copy for drawing
        processed_frame = frame.copy()
        
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect QR codes
        decoded_objects = pyzbar.decode(gray)
        
        # List to store QR code locations
        objects = []
        
        for obj in decoded_objects:
            # Get data and bounding box
            data = obj.data.decode('utf-8')
            x, y, w, h = obj.rect
            
            # Store QR code data
            self.qr_data = data
            
            # Add to objects list
            objects.append((x, y, w, h))
            
            # Draw rectangle around QR code
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(processed_frame, (center_x, center_y), 3, (0, 0, 255), -1)
            
            # Draw data
            cv2.putText(processed_frame, data, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw QR code corners
            points = obj.polygon
            if points and len(points) >= 4:
                # Convert points to numpy array for drawing
                pts = np.array(points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(processed_frame, [pts], True, (255, 0, 0), 2)
        
        return processed_frame, objects
        
    def navigate(self, objects):
        if not objects:
            # No QR codes detected, stop
            self.send_command('S')
            return "No QR code detected", None
        
        # For simplicity, track the largest QR code (by area)
        largest_object = max(objects, key=lambda obj: obj[2] * obj[3])
        x, y, w, h = largest_object
        
        # Calculate center of QR code
        object_center_x = x + w // 2
        
        # Calculate distance from center
        distance_from_center = object_center_x - self.frame_center_x
        
        # Determine direction to move
        if abs(distance_from_center) < self.center_threshold:
            # QR code is centered, move forward
            command = 'F'
            status = "QR centered - Moving forward"
        elif distance_from_center < 0:
            # QR code is to the left, turn left
            command = 'L'
            status = "QR left - Turning left"
        else:
            # QR code is to the right, turn right
            command = 'R'
            status = "QR right - Turning right"
        
        # Send command to Arduino
        self.send_command(command)
        
        return status, largest_object
    
    def send_command(self, command):
        # Only send if command is different from last one
        if command != self.last_command:
            if self.arduino:
                self.arduino.write(command.encode())
                time.sleep(0.05)  # Reduced delay for better responsiveness
            
            # Update command history (keep last 3)
            self.command_history.append((time.time(), command))
            if len(self.command_history) > 3:
                self.command_history.pop(0)
            
            self.last_command = command
    
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to retrieve frame from camera")
                break
            
            # Frame skipping for performance
            self.frame_count += 1
            if self.frame_count % self.skip_frames != 0:
                # Update FPS display but skip processing
                if time.time() - self.last_frame_time >= 1.0:
                    self.fps = self.frame_count
                    self.frame_count = 0
                    self.last_frame_time = time.time()
                
                # Just show the frame with minimal processing
                small_frame = cv2.resize(frame, (self.resize_width, self.resize_height))
                cv2.putText(small_frame, f"FPS: {self.fps}", (10, self.resize_height - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                cv2.imshow("QR Navigation", small_frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                continue
            
            # Resize for faster processing
            small_frame = cv2.resize(frame, (self.resize_width, self.resize_height))
            
            # Detect QR codes
            processed_frame, objects = self.detect_qr_codes(small_frame)
            
            # Navigate based on detected QR codes
            status, tracked_object = self.navigate(objects)
            
            # Calculate FPS
            if time.time() - self.last_frame_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_frame_time = time.time()
            
            # Draw navigation information
            self._draw_navigation_info(processed_frame, status, tracked_object)
            
            # Show processed frame
            cv2.imshow("QR Navigation", processed_frame)
            
            # Break loop if 'q' is pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Clean up
        self.cap.release()
        cv2.destroyAllWindows()
        if self.arduino:
            # Send stop command before closing
            self.send_command('S')
            self.arduino.close()
    
    def _draw_navigation_info(self, frame, status, tracked_object):
        # Draw center line
        cv2.line(frame, (self.frame_center_x, 0), (self.frame_center_x, self.resize_height), 
                 (255, 0, 0), 1)
        
        # Draw center threshold zone
        left_threshold = self.frame_center_x - self.center_threshold
        right_threshold = self.frame_center_x + self.center_threshold
        cv2.line(frame, (left_threshold, 0), (left_threshold, self.resize_height), 
                 (255, 0, 0), 1)
        cv2.line(frame, (right_threshold, 0), (right_threshold, self.resize_height), 
                 (255, 0, 0), 1)
        
        # Draw status text and FPS
        cv2.putText(frame, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"FPS: {self.fps}", (10, self.resize_height - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Draw command history (reduced for optimization)
        for i, (timestamp, cmd) in enumerate(self.command_history[-2:]):
            elapsed = time.time() - timestamp
            cmd_text = f"{cmd}: {elapsed:.1f}s ago"
            cv2.putText(frame, cmd_text, (10, 50 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.4, (0, 255, 0), 1)
        
        # Draw tracked object info if available
        if tracked_object:
            x, y, w, h = tracked_object
            object_center_x = x + w // 2
            
            # Draw object center position info
            distance_text = f"Offset: {object_center_x - self.frame_center_x:+d}px"
            cv2.putText(frame, distance_text, (frame.shape[1] - 150, frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

def main():
    # Clear screen for better UI
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get user input for configuration
    config = get_user_input()
    
    # Create and run the navigation system
    nav = QRNavigationRobot(
        camera_url=config['camera_url'],
        arduino_port=config['port'],
        baud_rate=config['baud_rate'],
        resize_width=config['frame_width'],
        skip_frames=config['skip_frames']
    )
    
    # Run the navigation
    try:
        nav.run()
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 