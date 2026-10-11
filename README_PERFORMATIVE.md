# Performative Detector

A Python program that uses computer vision to detect books through your webcam and automatically plays "Juna" (juna.mp3) when a book is detected.

## Features

- **Live Camera Feed**: Real-time video from your webcam with mirror effect
- **Advanced YOLO Detection**: Uses YOLOv8 AI model to detect books and other objects
- **Rich Detection UI**: 
  - Orange bounding boxes for all detected objects
  - Thick green boxes with filled label backgrounds for books
  - Bottom overlay showing detection count and confidence scores
  - Clean, distraction-free interface
- **Status Display**: Shows "PERFORMATIVE" (green) when book detected, "NOT PERFORMATIVE" (red) otherwise
- **Automatic Music Playback**: Plays juna.mp3 directly in the program when a book is detected
- **Smart Audio Control**: Music starts when book appears and plays until finished (doesn't stop if book is removed)
- **Music Status Indicator**: Shows "♫ Playing" on the status panel when music is playing
- **Clean Interface**: No distracting overlays - just pure detection with YOLO info at bottom

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your music file**:
   - Put `juna.mp3` in the same directory as `performative_detector.py`
   - The program will warn you if the file is not found

## Usage

Run the program:
```bash
python performative_detector.py
```

### Controls
- **Q key**: Quit the application
- **Show a book**: Hold a book in front of the camera to trigger detection

### What You'll See

```
┌─────────────────┬───────────────────────────────────────────┐
│                 │                                           │
│      NOT        │    Live Camera Feed                       │
│  PERFORMATIVE   │    [Orange boxes around objects]          │
│    (in red)     │    [Thick Green box around BOOK]          │
│                 │                                           │
│                 │  ─────────────────────────────────────    │
│                 │  YOLO DETECTIONS: 3                       │
│                 │  📚 BOOK (85%)                            │
│                 │  person (92%)                             │
│                 │  laptop (78%)                             │
└─────────────────┴───────────────────────────────────────────┘
```

**Interface Elements:**
- **Left Panel**: Red "NOT PERFORMATIVE" or Green "PERFORMATIVE" status
  - Shows "♫ Playing" indicator when music is active
- **Right Panel**: Camera feed with detection overlays
  - **Orange boxes**: All detected objects (person, laptop, chair, etc.)
  - **Thick green boxes**: Books with filled label backgrounds (confidence %)
  - **Bottom overlay**: Detection statistics showing all detected objects

**What Happens:**
- **Book detected**: Music starts playing once through
- **Book removed**: Music continues playing until finished
- **Music finishes**: Status indicator disappears
- **Book shown again (while music playing)**: Nothing (music already playing)
- **Book shown again (after music finished)**: Music starts from beginning

## Troubleshooting

### Camera not working
- Make sure no other application is using your camera
- Check camera permissions in Windows Settings

### Book not being detected
- Ensure good lighting
- Hold the book clearly in view
- Make sure the book cover is visible
- Try different angles

### Music not playing
- Make sure `juna.mp3` is in the same directory as `performative_detector.py`
- Check the console output for detailed audio system messages:
  - "✓ Audio system initialized" - audio is working
  - "✓ Found audio file" - file was found
  - "✓ Audio file loaded successfully" - file is valid
  - "🎵 Starting playback" - music is attempting to play
- Verify your system audio is not muted
- Check your system volume is turned up
- Try a different MP3 file to test if it's a file format issue
- Make sure pygame is installed: `pip install pygame`
- Some systems may require additional audio codecs

### Model download
- On first run, YOLOv8 will automatically download (~6MB)
- This only happens once

## How It Works

1. **YOLOv8**: Pre-trained AI model detects objects including books (COCO class 73)
2. **OpenCV**: Captures and processes webcam feed
3. **State Tracking**: Monitors when books appear/disappear
4. **Audio Playback**: Uses pygame.mixer to play/stop juna.mp3 based on detection state

## Requirements

- Python 3.8+
- Webcam
- juna.mp3 audio file
- System audio (speakers/headphones)

## Notes

- The program uses the YOLOv8 nano model for fast performance
- Detection confidence threshold is set to 30% for books
- Works best with clear book covers in good lighting
- The camera feed is mirrored for easier interaction
- Music plays once through when a book is detected (no looping)
- Music continues playing even if book is removed
- Can only trigger music again after current playback finishes
- Clean interface with no FPS counter or header text - just detection info
- Place juna.mp3 in the same folder as the script
- Volume is set to maximum (100%)

