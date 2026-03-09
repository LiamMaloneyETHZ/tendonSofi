import numpy as np
import cv2
import pandas as pd

#slows down all of my force testing videos to get them back to normal speed

for freq in np.arange(1.0, 4.2, 0.2): #1-4-inclusive
    freq = round(freq, 1)

    folder=r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput"
    filepath=f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/{freq}.avi"

    output_path=f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/Live-Tests/{freq}_normal.avi"

    cap = cv2.VideoCapture(filepath)

    # Get total frame count and frame rate
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Frame count",frame_count)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS",fps)

    video_time=frame_count/fps
    print("Video_time",video_time)

    time_initial=2.2871804237365723
    time_final=27.648216247558594
    actual_time=time_final-time_initial

    new_fps=int(actual_time/video_time)
    #new_fps=1/new_fps #slow rate
    #print("new fps",new_fps)

    #new_fps=int(video_time/actual_time)
    #print(1/new_fps)


    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))   

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can also try 'XVID'
    out = cv2.VideoWriter(output_path, fourcc, new_fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"Saved slowed-down video to {output_path}")