import cv2
import numpy as np
from ultralytics import YOLO
import time
import pygame
import os

class PerformativeDetector:
    def __init__(self):
        # Load YOLOv8 model
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')  # Using nano model for speed
        
        # Initialize pygame mixer for audio
        print("Initializing audio system...")
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("✓ Audio system initialized")
        except Exception as e:
            print(f"⚠️ Error initializing audio: {e}")
        
        # Check if juna.mp3 exists
        self.audio_file = "juna.mp3"
        if not os.path.exists(self.audio_file):
            print(f"⚠️ WARNING: {self.audio_file} not found in current directory!")
            print(f"   Current directory: {os.getcwd()}")
            print(f"   Please place juna.mp3 in this folder")
            self.audio_available = False
        else:
            print(f"✓ Found audio file: {self.audio_file}")
            try:
                pygame.mixer.music.load(self.audio_file)
                print(f"✓ Audio file loaded successfully")
                # Set volume to maximum
                pygame.mixer.music.set_volume(1.0)
                self.audio_available = True
            except Exception as e:
                print(f"⚠️ Error loading audio file: {e}")
                self.audio_available = False
        
        # Initialize camera
        print("Opening camera...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        
        print("Camera opened successfully!")
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Test read a frame
        ret, test_frame = self.cap.read()
        if ret:
            print(f"Camera working! Frame size: {test_frame.shape}")
        else:
            raise Exception("Could not read from camera")
        
        # State tracking
        self.book_detected = False
        self.music_playing = False
        
        # Window name
        self.window_name = "Performative Detector"
        
        # Book class ID in COCO dataset is 73
        self.book_class_id = 73
        
    def play_music(self):
        """Start playing music once"""
        if not self.audio_available:
            print("⚠️ Audio not available - cannot play music")
            return
        
        if not self.music_playing:
            try:
                print("🎵 Starting playback of juna.mp3...")
                pygame.mixer.music.play(0)  # 0 means play once (no looping)
                self.music_playing = True
                print("✓ Music is now playing!")
            except Exception as e:
                print(f"❌ Error playing music: {e}")
    
    def update_music_status(self):
        """Check if music is still playing"""
        if self.music_playing and not pygame.mixer.music.get_busy():
            # Music has finished playing
            self.music_playing = False
            print("✓ Music finished")
    
    def create_status_panel(self, height, width=400):
        """Create the status panel showing performative/not performative"""
        panel = np.zeros((height, width, 3), dtype=np.uint8)
        
        if self.book_detected:
            # Green background for performative
            panel[:] = (0, 100, 0)  # Dark green
            text = "PERFORMATIVE"
            color = (0, 255, 0)  # Bright green
        else:
            # Dark background for not performative
            panel[:] = (0, 0, 50)  # Dark red
            text = "NOT"
            text2 = "PERFORMATIVE"
            color = (0, 0, 255)  # Red
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        if self.book_detected:
            # Single line for "PERFORMATIVE"
            text_size = cv2.getTextSize(text, font, 1.5, 3)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            cv2.putText(panel, text, (text_x, text_y), font, 1.5, color, 3)
        else:
            # Two lines for "NOT PERFORMATIVE"
            text_size1 = cv2.getTextSize(text, font, 1.8, 3)[0]
            text_size2 = cv2.getTextSize(text2, font, 1.2, 3)[0]
            
            text_x1 = (width - text_size1[0]) // 2
            text_x2 = (width - text_size2[0]) // 2
            
            text_y1 = (height - 50) // 2
            text_y2 = (height + 50) // 2
            
            cv2.putText(panel, text, (text_x1, text_y1), font, 1.8, color, 3)
            cv2.putText(panel, text2, (text_x2, text_y2), font, 1.2, color, 3)
        
        # Add music status indicator
        if self.music_playing:
            music_text = "♫ Playing"
            cv2.putText(panel, music_text, (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return panel
    
    def detect_books(self, frame):
        """Detect books in the frame using YOLO"""
        # Run YOLO detection
        results = self.model(frame, verbose=False)
        
        book_detected = False
        detection_info = []
        total_detections = 0
        
        # Process detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class ID
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names[class_id]
                
                # Only show detections with decent confidence
                if confidence > 0.25:
                    total_detections += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Check if it's a book
                    if class_id == self.book_class_id and confidence > 0.3:
                        book_detected = True
                        
                        # Draw thick green bounding box for books
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                        
                        # Draw filled background for label
                        label = f"BOOK {confidence:.2%}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        cv2.putText(frame, label, (x1, y1 - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
                        
                        # Add pulsing effect
                        cv2.circle(frame, (x1 + 10, y1 + 10), 8, (0, 255, 0), -1)
                        
                        detection_info.append(f"📚 BOOK ({confidence:.1%})")
                    else:
                        # Draw colored box for other objects
                        color = (255, 165, 0)  # Orange for other objects
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Draw label
                        label = f"{class_name} {confidence:.0%}"
                        cv2.putText(frame, label, (x1, y1 - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        detection_info.append(f"{class_name} ({confidence:.0%})")
        
        # Draw detection info overlay at the bottom
        overlay_height = 150
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, frame.shape[0] - overlay_height), 
                     (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Add detection statistics
        stats_y = frame.shape[0] - overlay_height + 30
        cv2.putText(frame, f"YOLO DETECTIONS: {total_detections}", 
                   (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show detected objects
        for i, info in enumerate(detection_info[:4]):  # Show max 4 objects
            cv2.putText(frame, info, (10, stats_y + 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        if len(detection_info) > 4:
            cv2.putText(frame, f"... +{len(detection_info) - 4} more", 
                       (10, stats_y + 30 + 4 * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        return frame, book_detected
    
    def run(self):
        """Main detection loop"""
        print("Starting Performative Detector...")
        print("Press 'q' to quit")
        print("Opening window...")
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            frame_count += 1
            if frame_count == 1:
                print("First frame captured! Window should be visible now.")
            
            # Calculate FPS
            elapsed_time = time.time() - start_time
            if elapsed_time > 1:
                fps = frame_count / elapsed_time
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect books
            frame, book_detected_now = self.detect_books(frame)
            
            # Update state
            previous_state = self.book_detected
            self.book_detected = book_detected_now
            
            # Control music based on book detection
            if self.book_detected and not previous_state:
                print("📚 BOOK DETECTED! Starting music...")
                self.play_music()
            elif not self.book_detected and previous_state:
                print("❌ Book no longer detected (music continues playing)")
            
            # Update music status (check if finished)
            self.update_music_status()
            
            # Create status panel
            status_panel = self.create_status_panel(frame.shape[0], width=400)
            
            # Combine status panel (left) and camera feed (right)
            combined = np.hstack([status_panel, frame])
            
            # Add FPS counter to console only (removed from display)
            if frame_count % 30 == 0:
                print(f"Running... Frame {frame_count} | FPS: {fps:.1f} | Book detected: {self.book_detected}")
            
            # Display
            cv2.imshow(self.window_name, combined)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        print("\nCleaning up...")
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.cap.release()
        cv2.destroyAllWindows()

def main():
    try:
        detector = PerformativeDetector()
        detector.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. A working camera")
        print("2. Required packages: pip install -r requirements.txt")
        print("3. juna.mp3 file in the same directory as this script")

if __name__ == "__main__":
    main()

