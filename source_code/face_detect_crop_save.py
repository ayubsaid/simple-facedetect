import cv2
import os
import datetime
import csv
from simple_facerec import SimpleFacerec

images_folder = 'images1/'
csv_file = 'unknown_faces.csv'
time_limit = datetime.timedelta(seconds=20)

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Load Camera
cap = cv2.VideoCapture(0)  # Set the appropriate device index or video file path
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the desired width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the desired height

known_faces = {}  # Dictionary to store the names and last detection times of already detected faces

# Create or append to the CSV file
with open(csv_file, 'a') as f:
    writer = csv.writer(f)
    # Check if the file is empty
    if os.stat(csv_file).st_size == 0:
        writer.writerow(['Time', 'Size', 'Name'])

    try:
        while True:
            ret, frame = cap.read()

            # Perform face recognition
            face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.50)

            current_time = datetime.datetime.now()

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                if not name:
                    name = 'Unknown'

                # Draw a rectangle around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Create folder if it doesn't exist
                folder_path = os.path.join(images_folder, name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Check if the face is already known and detected
                if name in known_faces:
                    last_detection_time = known_faces[name]
                    time_difference = current_time - last_detection_time

                    # Check if the face has not been detected within the time limit
                    if time_difference >= time_limit:
                        # Generate filename with timestamp
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                        # Crop the face region
                        crop_img = frame[top:bottom, left:right]

                        # Save the cropped image
                        cv2.imwrite(filename, crop_img)
                        print(f"Saved updated face image to: {filename}")

                        # Update the last detection time for the face
                        known_faces[name] = current_time

                        # Write the details to the CSV file
                        writer.writerow([timestamp, name, os.path.getsize(filename)])

                else:
                    # Generate filename with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                    # Crop the face region
                    crop_img = frame[top:bottom, left:right]

                    # Save the cropped image
                    cv2.imwrite(filename, crop_img)
                    print(f"Saved new face image to: {filename}")

                    # Add the face and detection time to the known_faces dictionary
                    known_faces[name] = current_time

                    # Write the details to the CSV file
                    writer.writerow([timestamp, name, os.path.getsize(filename)])

                # Display the name on the rectangle
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # Display the resulting frame
            cv2.imshow("Frame", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
