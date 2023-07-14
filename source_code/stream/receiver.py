import cv2
import os
import datetime
import numpy as np
from simple_facerec import SimpleFacerec
import socket

images_folder = 'images1/'

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Set up a socket for network communication
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', 8485)
client_socket.connect(server_address)

while True:
    # Receive the frame from the server
    data = b''
    while True:
        packet = client_socket.recv(4096)
        data += packet
        if len(packet) < 4096:
            break

    # Convert the received data to an array of bytes
    frame_data = np.frombuffer(data, dtype=np.uint8)

    # Decode the frame
    frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

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

# Close the socket connection
client_socket.close()
cv2.destroyAllWindows()
