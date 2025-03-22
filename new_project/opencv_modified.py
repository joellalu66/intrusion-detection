import cv2
import time
import os
from datetime import datetime
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_project.settings')
django.setup()

# Import Django models after setting up Django
from app1.models import IntrusionEvent

# Django media directory setup
MEDIA_DIR = "media"
VIDEO_DIR = os.path.join(MEDIA_DIR, "videos")
IMAGE_DIR = os.path.join(MEDIA_DIR, "images")

# Create required directories
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Load Haar Cascade for face detection
cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("Error: Could not load face cascade classifier xml file")
    exit()

# Start video capture
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Error: Could not open video camera.")
    exit()

frame_width = int(video.get(3))
frame_height = int(video.get(4))

# Generate filenames with correct paths
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
video_path = os.path.join(VIDEO_DIR, f"intrusion_{timestamp}.mp4")
video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (frame_width, frame_height))

last_capture_time = time.time()

while True:
    check, frame = video.read()
    if not check or frame is None:
        print("Error: Could not read frame.")
        break

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 255), 2, cv2.LINE_AA)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=12, minSize=(50, 50))

    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        if time.time() - last_capture_time >= 5:
            image_path = os.path.join(IMAGE_DIR, f"face_detected_{timestamp}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Image saved: {image_path}")
            last_capture_time = time.time()

    video_writer.write(frame)
    cv2.imshow("Face Detection Video", frame)

    if cv2.waitKey(1) == ord('q'):
        break

video.release()
video_writer.release()
cv2.destroyAllWindows()

# Save to database with relative paths for Django
event = IntrusionEvent(
    video=f"videos/intrusion_{timestamp}.mp4",
    image=f"images/face_detected_{timestamp}.jpg"
)
event.save()
print(f"Event saved in database with video: {video_path}")

