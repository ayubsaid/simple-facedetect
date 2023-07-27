import cv2
import socket
import time

#print(cv2.getBuildInformation())

# Open a video capture device (e.g., webcam)
cap = cv2.VideoCapture(0)

# Create a socket for network communication
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', 10050)
client_socket.connect(server_address)

while True:
    # Read a frame from the video capture device
    ret, frame = cap.read()

    # Check if the frame was successfully capturedpyth  
    if not ret:
        break

    # Encode the frame into a video format (e.g., MJPEG or H.264)
    _, encoded_frame = cv2.imencode('.jpg', frame)
    
    #cv2.imshow('Received Frame', frame)

    client_socket.sendall(encoded_frame.tobytes())
    time.sleep(0.1) 

# Release the resources
cap.release()
client_socket.close()
cv2.destroyAllWindows()
