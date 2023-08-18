import cv2
import os
import datetime
import psycopg2
from simple_facerec import SimpleFacerec
import time
import requests
import json
import uuid
import base64

images_folder = 'images1/'
time_limit = datetime.timedelta(seconds=20)


# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Load Camera
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the desired width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the desired height

known_faces = {}  # Dictionary to store the names and last detection times of already detected faces

# ----------------------------------------------------------------------------------------------------------

def send_face_values_to_api(face_values):
    api_url = "https://face.taqsim.uz/api/face-recognitons"
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJZCI6IjIiLCJyb2xlIjoiQWRtaW4iLCJ1bmlxdWVfbmFtZSI6InN0cmluZyIsIm5iZiI6MTY5MjM1NzA5OSwiZXhwIjoxNjkyMzY0Mjk5LCJpYXQiOjE2OTIzNTcwOTksImlzcyI6Imh0dHBzOi8vZmFjZXByb2ZpbGUudXoiLCJhdWQiOiJodHRwczovL2ZhY2Vwcm9maWxlLnV6In0.fxMRA6n2PGFXZ5OWblMBAfJYo41bE43438vC9npoyLI",
        "Content-Type": "application/json"
    }

    for face_value in face_values:
        response = requests.post(api_url, data=json.dumps(face_value), headers=headers, verify=False)

        if response.status_code == 200:
            print("Face values sent successfully to the API.")
        else:
            print(f"Failed to send face values to the API. Status code: {response.status_code}")

# ----------------------------------------------------------------------------------------------------------

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )
    cur = conn.cursor()
    # Create the face_recognition table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS face_recognition1 (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP,
            name VARCHAR(255),
            image_data BYTEA
        )
    """)
    conn.commit()

    while True:
        ret, frame = cap.read()
        face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.50)

        current_time = datetime.datetime.now()

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            if not name:
                name = 'Unknown'

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            crop_img_gray = cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
            folder_path = os.path.join(images_folder, name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Check if the face is already known and detected
            if name in known_faces:
                last_detection_time = known_faces[name]
                time_difference = current_time - last_detection_time

                # Check if the face has not been detected within the time limit
                if time_difference >= time_limit:
                    # Generate timestamp in standard format
                    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                    # Save the grayscale image
                    cv2.imwrite(filename, crop_img_gray)  # Save the grayscale image
                    print(f"Saved new grayscale face image to: {filename}")

                    # Read the image file as binary data
                    with open(filename, 'rb') as img_file:
                        image_data = img_file.read()

                    # Update the last detection time for the face
                    known_faces[name] = current_time

                    # Insert the details into the PostgreSQL database
                    cur.execute("""
                        INSERT INTO face_recognition1 (time, name, image_data)
                        VALUES (%s, %s, %s)
                    """, (timestamp, name, psycopg2.Binary(image_data)))
                    conn.commit()

            else:
                # Generate timestamp in standard format
                timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

                # Crop the face region
                crop_img = frame[top:bottom, left:right]

                # Capture a burst of images
                face_values = []  # List to store captured face values

                # Capture a burst of images
                for i in range(5):
                    filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")
                    # Save the grayscale image
                    cv2.imwrite(filename, crop_img_gray)
                    print(f"Saved new grayscale face image to: {filename}")

                    # Read the image file as binary data
                    with open(filename, 'rb') as img_file:
                        image_data = img_file.read()

                    # Add the face and detection time to the known_faces dictionary
                    known_faces[name] = current_time

                    # Insert the details into the PostgreSQL database
                    cur.execute("""
                        INSERT INTO face_recognition1 (time, name, image_data)
                        VALUES (%s, %s, %s)
                        """, (timestamp, name, psycopg2.Binary(image_data)))
                    conn.commit()

                    # Add a small delay between captures
                    time.sleep(0.1)

                    # Generate a unique GUID for each set of images
                    unique_guid = str(uuid.uuid4())

                    # Encode the image data in base64
                    with open(filename, 'rb') as img_file:
                        base64_encoded_image_data = base64.b64encode(img_file.read()).decode('utf-8')

                    # Create the face value dictionary
                    face_value = {
                        "guid": unique_guid,
                        "imageBase64": base64_encoded_image_data,
                        "date": datetime.datetime.now().isoformat()
                    }
                    face_values.append(face_value)

                # Send face values to Swagger UI API
                send_face_values_to_api(face_values)

            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            cv2.imshow("Frame", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    cap.release()
    cv2.destroyAllWindows()
    conn.close()
