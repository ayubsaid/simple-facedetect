import cv2
import os
import datetime 
from simple_facerec import SimpleFacerec

images_folder = 'images1/'

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Load Camera
cap = cv2.VideoCapture()  # Set the appropriate device index or video file path
cap.open("rtsp://admin:asd123()@192.168.0.64:554/Streaming/channels/2/")

while True:
    ret, frame = cap.read()

    # Perform face recognition
    face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.50)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if not name:
            continue

        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        
        # Create folder if it doesn't exist
        folder_path = os.path.join(images_folder, name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

        # Crop the face region
        crop_img = frame[top:bottom, left:right]

        # Save the cropped image
        cv2.imwrite(filename, crop_img)
        print(f"Saved cropped face to: {filename}")

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

