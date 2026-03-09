import cv2
import sys
import time
import os

start = time.time()


camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # or CAP_MSMF
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

#sets camera to maximum width and height resoultion, changes file to MJPG
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))


#2592 × 1944
#width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
#height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

#sets FPS to maximum rate of IMX335 
fps = 30

# message from powershell script to recieve the intended frequency
if len(sys.argv) > 1:
    freq_string=sys.argv[1]

#/home/srl-slim-tim//
#video_filename=f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/{freq_string}.avi"
video_filename=f"/home/srl-slim-tim/ForceTest/video_{freq_string}.avi"
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#had arbitrarily been using 20 
out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))


# Define absolute paths for sync files
signal_dir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
#signal_dir = "C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/Dynamixel_Control/softFish/CombinedTesting"
camera_started_file = os.path.join(signal_dir, "camera_started.txt")
stop_signal_file = os.path.join(signal_dir, "stop_signal.txt")

try:
    # Once the camera opens, create the start signal file
    with open(camera_started_file, "w") as f:
        f.write("Camera started")
        f.flush()
        os.fsync(f.fileno())

    while True:
        ret, frame = camera.read()
        current_time=time.time()-start
        if not ret:
            print("Error: Failed to capture frame.")
            break
        cv2.putText(frame, f"Now: {current_time}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    
        # Save to disk
        out.write(frame)
        cv2.imshow('Recording', frame)

        if os.path.exists(stop_signal_file):
            print("Exit signal received. Closing camera.")
            break

        # Break if 'q' pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Recording stopped by user.")
            break
except KeyboardInterrupt:
    print("Recording interrupted by user.")


camera.release()
out.release()
cv2.destroyAllWindows()

print(f"-> Video: {video_filename}")