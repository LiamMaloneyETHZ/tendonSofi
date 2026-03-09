import depthai as dai
import cv2
import time
import os

#same ideas as CameraControl, however it has a different camera and can no longer write camera specs with cv2
start = time.time()
# Oak-D camera
# has maximum FPS up to 60

# Create a pipeline
pipeline = dai.Pipeline()

width = 1920
height = 1080

#video output roughly 1:1 at 20 fps, want higher resolution and can post process so will do 45 
fps = 45

# Define a color camera node
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(width, height)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

# Create an XLink output node
xout = pipeline.createXLinkOut()
xout.setStreamName("video")
cam_rgb.preview.link(xout.input)

output_folder = f"/home/srl-slim-tim/ForceTest"
freq = 2.0

output_path = os.path.join(output_folder, f"output_{freq}.avi")

# Define absolute paths for sync files
signal_dir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
camera_started_file = os.path.join(signal_dir, "camera_started.txt")
stop_signal_file = os.path.join(signal_dir, "stop_signal.txt")

with dai.Device(pipeline) as device:
    with open(camera_started_file, "w") as f:
        f.write("Camera started\n")
        f.flush()
        os.fsync(f.fileno())

    video_queue = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))  # 45 FPS, frame size

    try:
        while True:
            in_frame = video_queue.get()
            frame = in_frame.getCvFrame()
            current_time = time.time() - start
            # Write the frame to the video file
            cv2.putText(frame, f"Now: {current_time}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
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

    out.release()

cv2.destroyAllWindows()
print(f"-> Video saved at: {output_path}")
