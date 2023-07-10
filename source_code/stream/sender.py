import cv2
import socket
import numpy as np

# Open a video capture device (e.g., webcam)
cap = cv2.VideoCapture()
cap.open(${{ secrets.RTSPCAM }})

# Create a socket for network communication
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (${{secrets.IP}}, 8485)
client_socket.connect(server_address)

# Video encoding parameters
fourcc = cv2.VideoWriter_fourcc(*'H264')
out = cv2.VideoWriter('encoded_video.mp4', fourcc, 20.0, (640, 480))

while True:
    # Read a frame from the video capture device
    ret, frame = cap.read()

    # Encode the frame into H.264 format
    _, encoded_frame = cv2.imencode('.mp4', frame)

    # Convert the encoded frame to a byte array
    encoded_data = np.array(encoded_frame).tobytes()

    # Send the encoded frame over the network
    client_socket.sendall(encoded_data)

    # Write the encoded frame to the output file
    #out.write(frame)

    # Break the loop if needed (e.g., press 'q' to quit)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
out.release()
client_socket.close()
cv2.destroyAllWindows()
