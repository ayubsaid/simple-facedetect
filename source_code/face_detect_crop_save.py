import base64
import cv2
import os
import datetime
import psycopg2
from simple_facerec import SimpleFacerec
import uuid
import requests
import json

images_folder = 'face_database/'
time_limit = datetime.timedelta(seconds=20)


# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("face_database/")

# Load Camera
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the desired width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the desired height

known_faces = {}  # Dictionary to store the names and last detection times of already detected faces

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1234"
)
cur = conn.cursor()

# Function to send face values to Swagger API
def send_face_values_to_api(face_values):
    api_url = "https://face.taqsim.uz/api/face-recognitons"
    headers = {
        "accept": "*/*",
        "Content-Type": "application/json"
    }

    for face_value in face_values:
        response = requests.post(api_url, json=face_value, headers=headers, verify=True)

        print("Request Body:", json.dumps(face_value, indent=2))  # Print the request body
        print("Status Code:", response.status_code)  # Print the status code

        try:
            response_json = response.json()
            print("Response Body:", json.dumps(response_json, indent=2))  # Print the response body
        except json.JSONDecodeError:
            print("Failed to decode response JSON.")

        if response.status_code == 200:
            print("Face values sent successfully to the API.")
        else:
            print(f"Failed to send face values to the API. Status code: {response.status_code}")


try:

    while True:
        ret, frame = cap.read()
        # Perform face recognition
        face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.50)

        current_time = datetime.datetime.now()

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            if not name:
                name = str(uuid.uuid4())

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Convert the cropped image to grayscale
            crop_img_gray = cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2GRAY)

            # Create folder if it doesn't exist
            folder_path = os.path.join(images_folder, name)

            if name == 'Unknown':
                folder_path = os.path.join(images_folder, str(uuid.uuid4()))


            # Check if the face is already known and detected
            if name in known_faces:
                last_detection_time = known_faces[name]
                time_difference = current_time - last_detection_time


                # Check if the face has not been detected within the time limit
                if time_difference >= time_limit:
                    sfr.load_encoding_images(images_folder)
                    # Generate timestamp in standard format
                    timestamp = current_time.strftime("%Y-%m-%d_%H:%M:%S")
                    filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                    # Crop the face region
                    crop_img = frame[top:bottom, left:right]

                    # Save the cropped image
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    cv2.imwrite(filename, crop_img)
                    print(f"Saved updated face image to: {filename}")
                    # Send face values to Swagger UI API
                    # Encode the image data in base64
                    with open(filename, 'rb') as img_file:
                        send_face_values_to_api([{"guid": name, "imageBase64": base64.b64encode(img_file.read()).decode('utf-8')}])


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
                timestamp = current_time.strftime("%Y-%m-%d_%H:%M:%S")
                filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

                # Crop the face region
                crop_img = frame[top:bottom, left:right]

                # Save the grayscale image
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                cv2.imwrite(filename, crop_img_gray)
                print(f"Saved new grayscale face image to: {filename}")
                # Send face values to Swagger UI API

                # Encode the image data in base64
                with open(filename, 'rb') as img_file:
                    send_face_values_to_api([{"guid": name, "imageBase64": base64.b64encode(img_file.read()).decode('utf-8')}])

                # Read the grayscale image file as binary data
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
    conn.close()