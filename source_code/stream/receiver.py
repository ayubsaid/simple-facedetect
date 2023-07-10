import cv2
import socket
import numpy as np

# Create a socket for network communication
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', 8485)
server_socket.bind(server_address)
server_socket.listen(1)

# Accept a client connection
client_socket, client_address = server_socket.accept()

while True:
    # Receive the encoded frame from the client
    encoded_data = client_socket.recv(4096)

    if not encoded_data:
        # No more data received, break the loop
        break

    # Convert the received data back to a numpy array
    encoded_frame = np.frombuffer(encoded_data, dtype=np.uint8)

    # Decode the frame into an image format
    frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)

    # Process and display the frame or save it as a video file
    # ...

    # Show the frame
    cv2.imshow('Received Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
