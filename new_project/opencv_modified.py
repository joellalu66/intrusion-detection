import cv2
import time
import os
from datetime import datetime
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_project.settings')  # Replace 'ids' with your project name
django.setup()

# Import Django models after setting up Django
from app1.models import IntrusionEvent

# Django media directory
MEDIA_DIR = "media/videos/"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# Load Haar Cascade for face detection
cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("Error: Could not load face cascade classifier xml file")
    exit()

# Start video capture
video = cv2.VideoCapture(0)  # Use 0 for default camera

# Ensure the camera opened successfully
if not video.isOpened():
    print("Error: Could not open video camera.")
    exit()

# Get frame width and height for video recording
frame_width = int(video.get(3))
frame_height = int(video.get(4))

# Generate a unique filename for the video
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
video_filename = f"{MEDIA_DIR}intrusion_{timestamp}.mp4"

# Define the video codec and create a VideoWriter object (MP4 format)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(video_filename, fourcc, 10, (frame_width, frame_height))

last_capture_time = time.time()

while True:
    check, frame = video.read()
    if not check or frame is None:
        print("Error: Could not read frame.")
        break

    # Get current date and time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Overlay the date and time on the video frame
    cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 255), 2, cv2.LINE_AA)

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=12, minSize=(50, 50))

    # Draw rectangles around detected faces
    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Capture an image every 5 seconds if a face is detected
        if time.time() - last_capture_time >= 5:
            image_filename = f"media\images/face_detected_{timestamp}.jpg"
            cv2.imwrite(image_filename, frame)
            print(f"Image saved: {image_filename}")
            last_capture_time = time.time()

    # Write frame to video file
    video_writer.write(frame)

    # Show video feed
    cv2.imshow("Face Detection Video", frame)

    # Exit condition: Press 'q' to quit
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# After video capture loop ends
video.release()
video_writer.release()
cv2.destroyAllWindows()

# Save Video to Django Database
event = IntrusionEvent(video=video_filename, image=image_filename)
event.save()
print(f"Video saved in Django: {video_filename}")
