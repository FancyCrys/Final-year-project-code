import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# GPIO Setup
GPIO.setmode(GPIO.BCM)
signal_pins = {
    'lane1': {'red': 17, 'yellow': 27, 'green': 22},
    'lane2': {'red': 23, 'yellow': 24, 'green': 25},
    'lane3': {'red': 5, 'yellow': 6, 'green': 13}
}

for lane in signal_pins.values():
    for pin in lane.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

# Initialize Camera with proper configuration
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Corrected Lane regions (swapped lane1 and lane3)
LANE_REGIONS = [
    (430, 0, 650, 300),   # Lane 1 (x1,y1,x2,y2) - previously was lane3
    (210, 0, 410, 300),   # Lane 2 (unchanged)
    (0, 0, 200, 300)      # Lane 3 (previously was lane1)
]

# Colors for visualization
LANE_COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0)]  # Blue, Red, Cyan for lanes
VEHICLE_COLORS = [(0, 255, 0), (0, 165, 255), (255, 0, 255)]  # Green, Orange, Pink for vehicles

def detect_vehicles(frame):
    # Make a copy to draw on
    display_frame = frame.copy()
    
    # Draw lane regions with transparency
    overlay = display_frame.copy()
    for i, (x1, y1, x2, y2) in enumerate(LANE_REGIONS):
        cv2.rectangle(overlay, (x1, y1), (x2, y2), LANE_COLORS[i], -1)
    cv2.addWeighted(overlay, 0.2, display_frame, 0.8, 0, display_frame)
    
    # Draw lane region borders
    for i, (x1, y1, x2, y2) in enumerate(LANE_REGIONS):
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), LANE_COLORS[i], 2)
        cv2.putText(display_frame, f"Lane {i+1}", (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, LANE_COLORS[i], 2)
    
    # Vehicle detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    vehicle_counts = [0, 0, 0]
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # Adjust for toy car size
            continue
            
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) >= 4:
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Check which lane the vehicle is in
            lane_index = -1
            for i, (x1, y1, x2, y2) in enumerate(LANE_REGIONS):
                if x1 <= center_x <= x2 and y1 <= center_y <= y2:
                    lane_index = i
                    vehicle_counts[i] += 1
                    break
            
            # Draw rectangle with lane-specific color if in a lane
            if lane_index >= 0:
                color = VEHICLE_COLORS[lane_index]
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(display_frame, f"Car {vehicle_counts[lane_index]}", 
                           (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            else:
                # Draw vehicles outside lanes with white color
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
    
    # Display vehicle counts per lane
    for i, count in enumerate(vehicle_counts):
        cv2.putText(display_frame, f"Lane {i+1}: {count} cars", 
                   (10, 30 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, LANE_COLORS[i], 2)
    
    return vehicle_counts, display_frame

def set_signal(lane, color):
    for c in ['red', 'yellow', 'green']:
        GPIO.output(signal_pins[lane][c], GPIO.HIGH if c == color else GPIO.LOW)

try:
    while True:
        # Capture frame
        frame = picam2.capture_array()
        
        # The frame is already in RGB format due to our configuration
        # Convert from RGB to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Detect vehicles and get annotated frame
        counts, detected_frame = detect_vehicles(frame)
        
        # Show live view with detections
        cv2.imshow('Traffic Detection', detected_frame)
        if cv2.waitKey(1) == ord('q'):
            break
        
        # Traffic control logic
        max_count = max(counts)
        total = sum(counts)
        percentages = [c/max_count*100 if max_count > 0 else 0 for c in counts]
        
        highest_lane = np.argmax(percentages)
        highest_percent = percentages[highest_lane]
        
        duration = 12 if highest_percent >= 50 else 8 if highest_percent >= 25 else 4
        
        for lane_idx, lane in enumerate(['lane1', 'lane2', 'lane3']):
            for other_lane in ['lane1', 'lane2', 'lane3']:
                set_signal(other_lane, 'green' if other_lane == lane else 'red')
            
            time.sleep(duration if lane_idx == highest_lane else 4)
            set_signal(lane, 'yellow')
            time.sleep(2)

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
