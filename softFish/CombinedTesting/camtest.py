from datetime import datetime
import depthai as dai
import cv2
import time
import os
import sys
import subprocess

#starts timestamp at top of all files, formatted the same way 
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

#same ideas as CameraControl, however it has a different camera and can no longer write camera specs with cv2
start = time.time()
# Oak-D camera
# has maximum FPS up to 60

# Create a pipeline
pipeline = dai.Pipeline()

width = 1920
height = 1080

#video output roughly 1:1 at 20 fps, want higher resolution and can post process so will do 40
fps = 30

# Define a color camera node
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(width, height)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

#formally sets the fps to desired fps
cam_rgb.setFps(fps)

# Create an XLink output node
xout = pipeline.createXLinkOut()
xout.setStreamName("video")
cam_rgb.preview.link(xout.input)

desiredFreq=0.3

output_dir = "/home/srl-slim-tim/ForceTest/ForceTest2"

# Generate filename
#(YYYYMMDD_HHMM_f2Hz_servo_test_data.csv)
#filename = os.path.join(output_dir, f"{timestamp}_{desiredFreq}_film_test_data.avi")
filename = os.path.join(output_dir, f"{timestamp}_f{desiredFreq}Hz_film_test_data.avi")
#filename = f"{desiredFreq}_{timestamp}.csv"
filepath = os.path.join(output_dir, filename)

#creates pathway to save as mp4
#filenamemp4=os.path.join(output_dir, f"{timestamp}_f{desiredFreq}Hz_film_test_data.mp4")
#filepathmp4 = os.path.join(output_dir, filenamemp4)

print("Starting now")

# Define absolute paths for sync files
signal_dir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
camera_started_file = os.path.join(signal_dir, "camera_started.txt")
stop_signal_file = os.path.join(signal_dir, "stop_signal.txt")

#starts other devices 
with dai.Device(pipeline) as device:
    with open(camera_started_file, "w") as f:
        log_file_path = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting.txt"
        sys.stdout = open(log_file_path, "w")
        sys.stderr = sys.stdout

        log_file_path_2= "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting_2.txt"
        sys.stdout = open(log_file_path_2, "w")
        sys.stderr = sys.stdout


    video_queue = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    #not openinging videowriter. . . could be an issue of h264 type
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # or 'mp4v'
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    try:
        while True:
            in_frame = video_queue.get()
            frame = in_frame.getCvFrame()
            current_time = time.time() - start
            out.write(frame)
            cv2.imshow("OAK-D RGB Preview", frame)

            if os.path.exists(stop_signal_file):
                print("Exit signal received. Closing camera.")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Recording stopped by user.")
                break

    except KeyboardInterrupt:
        print("Recording interrupted by user.")

    finally:
        cv2.destroyAllWindows()

    out.release()

"""


#all new method to convert from h264 file to an mp4 file
print("convering to an mp4 file")
try:
    subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", filepath,
            "-c:v", "copy", filenamemp4
        ], check=True)
    print(f"[INFO] Conversion complete: {filepathmp4}")
    os.remove(filepath)
    print(f"[INFO] Original file removed: {filepath}")
except subprocess.CalledProcessError:
        print("[ERROR] ffmpeg conversion failed.")


"""



cv2.destroyAllWindows()
#had previously just been filepath, now filepathmp4
print(f"-> Video saved at: {filepath}")
