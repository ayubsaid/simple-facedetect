import cv2
import subprocess

# Open a video capture device (e.g., webcam)
cap = cv2.VideoCapture()
cap.open('rtsp://admin:asd123()@192.168.0.64:554/Streaming/channels/2/')

# Define the FFmpeg command for encoding
ffmpeg_cmd = [
    'ffmpeg',
    '-y',  # Overwrite output files without asking
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-video_size', '704x480',  # Set the video size
    '-pix_fmt', 'bgr24',  # Pixel format
    '-r', '30',  # Output frame rate
    '-i', '-',  # Read input from stdin
    '-c:v', 'libx264',  # Video codec
    '-preset', 'ultrafast',  # Encoding preset
    '-tune', 'zerolatency',  # Tune encoding for low-latency streaming
    '-crf', '23',  # Constant Rate Factor (quality)
    '-f', 'flv',  # Output format (FLV)
    'rtmp://185.183.242.198:10050/live/stream_key'  # Replace with your RTMP server address and stream key
]

# Create a subprocess for FFmpeg
ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

while True:
    # Read a frame from the video capture device
    ret, frame = cap.read()

    # Check if the frame was successfully captured
    if not ret:
        print("Failed to capture frame.")
        break

    # Encode the frame and write it to the stdin of the FFmpeg process
    ffmpeg_process.stdin.write(frame.tobytes())
    print("Frame sent to FFmpeg process.")

    # Display the frame
    cv2.imshow('Frame', frame)

    # Check for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
ffmpeg_process.stdin.close()
ffmpeg_process.wait()
cv2.destroyAllWindows()

