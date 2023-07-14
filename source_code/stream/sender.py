import cv2
import socket
import numpy as np

print(cv2.getBuildInformation())

# Open a video capture device (e.g., webcam)
cap = cv2.VideoCapture()
cap.open('rtsp://admin:asd123()@192.168.0.64:554/Streaming/channels/2/')

# Create a socket for network communication
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('185.183.242.198', 10050)
client_socket.connect(server_address)

while True:
    # Read a frame from the video capture device
    ret, frame = cap.read()

    # Check if the frame was successfully captured
    if not ret:
        break

    # Encode the frame into a video format (e.g., MJPEG or H.264)
    _, encoded_frame = cv2.imencode('.mp4', frame)
    
    cv2.imshow('Received Frame', frame)
    # Convert the encoded frame to bytes
    frame_bytes = encoded_frame.tobytes()

    # Send the frame bytes over the network
    client_socket.sendall(frame_bytes)

# Release the resources
cap.release()
client_socket.close()
cv2.destroyAllWindows()
