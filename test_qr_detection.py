import cv2
import numpy as np
import os

def get_user_input():
    """Get camera URL from user input"""
    print("\n===== QR Code Detection Test =====\n")
    
    # Get camera URL
    print("Enter camera source:")
    print("- For webcam, enter a number (e.g., 0 for default webcam)")
    print("- For IP camera, enter URL (e.g., http://192.168.1.100:8080/video)")
    camera_input = input("Camera source: ")
    
    try:
        # Check if the input is a number (webcam index)
        camera_url = int(camera_input) if camera_input.isdigit() else camera_input
    except ValueError:
        camera_url = camera_input
    
    return camera_url

def main():
    # Clear screen for better UI
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get camera URL from user
    camera_url = get_user_input()
    
    # Try to open the camera
    print(f"\nConnecting to camera {camera_url}...")
    cap = cv2.VideoCapture(camera_url)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {camera_url}")
        input("\nPress Enter to exit...")
        return
    
    # Create QR detector
    print("Creating QR Code detector...")
    
    # Try different QR code detection methods
    try:
        # Method 1: QRCodeDetector (newer OpenCV versions)
        qr_detector = cv2.QRCodeDetector()
        detection_method = "QRCodeDetector"
        print(f"Using {detection_method}")
    except (AttributeError, cv2.error) as e:
        print(f"Error with QRCodeDetector: {e}")
        print("Trying alternative method...")
        
        try:
            # Method 2: Try using zbar if installed
            import pyzbar.pyzbar as pyzbar
            detection_method = "pyzbar"
            print(f"Using {detection_method}")
        except ImportError:
            print("pyzbar not found. Please install with 'pip install pyzbar'")
            detection_method = "none"
    
    print("\nQR Code Detection Test")
    print("----------------------")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Resize frame for better performance if it's large
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            frame = cv2.resize(frame, (int(width * scale), int(height * scale)))
        
        # Display original frame
        display_frame = frame.copy()
        
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect QR codes
        detected = False
        
        if detection_method == "QRCodeDetector":
            try:
                # Detect and decode QR codes
                data, bbox, _ = qr_detector.detectAndDecode(gray)
                
                # If a QR code is found
                if bbox is not None and len(bbox) > 0:
                    detected = True
                    # Convert bbox to integer coordinates
                    bbox = bbox.astype(int)
                    
                    # Draw QR code points
                    for points in bbox:
                        # Draw polygon around QR code
                        cv2.polylines(display_frame, [points], True, (0, 255, 0), 2)
                        
                        # Draw data if available
                        if data:
                            x = points[0][0]
                            y = points[0][1]
                            cv2.putText(display_frame, data, (x, y - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error detecting QR code: {e}")
                
        elif detection_method == "pyzbar":
            try:
                # Detect and decode with pyzbar
                decoded_objects = pyzbar.decode(gray)
                for obj in decoded_objects:
                    detected = True
                    data = obj.data.decode('utf-8')
                    points = obj.polygon
                    
                    # Convert points to numpy array for drawing
                    pts = np.array(points, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                    
                    # Draw data
                    x, y, w, h = obj.rect
                    cv2.putText(display_frame, data, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error detecting QR code with pyzbar: {e}")
        
        # Add detection status to display
        status = "QR Code Detected!" if detected else "No QR Code Detected"
        cv2.putText(display_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 255) if not detected else (0, 255, 0), 2)
        
        # Display the frame
        cv2.imshow('QR Code Detection Test', display_frame)
        
        # Break loop if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    print("\nTest complete.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main() 