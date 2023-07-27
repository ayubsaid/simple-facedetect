import cv2
import socket
import numpy as np
from simple_facerec import SimpleFacerec
import os
import datetime

images_folder = 'images1/'

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Create a socket for network communication
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', 10050)
server_socket.bind(server_address)
server_socket.listen(1)

# Accept a client connection
client_socket, client_address = server_socket.accept()

while True:
    print(0)
    # Receive the encoded frame from the client
    encoded_data = client_socket.recv(4096)
    print(1)
    if not encoded_data:
        # No more data received, break the loop
        break
    try:
        # Convert the received data back to a numpy array
        encoded_frame = np.frombuffer(encoded_data, dtype=np.uint8)
        print(2)
        # Decode the frame into an image format
        frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)

        # Process and display the frame or save it as a video file
        print('Perform face recognition')
        # Check if the image decoding was successful
        if frame is not None:
            face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.50)
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                if not name:
                    continue
                print('Draw a rectangle around the face')
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                print('Create folder if it doesnt exist')
                folder_path = os.path.join(images_folder, name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                print('Generate filename with timestamp')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                print('Crop the face region')
                crop_img = frame[top:bottom, left:right]

                # Save the cropped image
                cv2.imwrite(filename, crop_img)
                print(f"Saved cropped face to: {filename}")
            # Show the frame
            #cv2.imshow('Received Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error decoding frame")
    except Exception as e:
        print("Exception during decoding:", e)
# Release the resources
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
