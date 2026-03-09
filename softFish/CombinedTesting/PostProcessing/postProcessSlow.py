import subprocess
import pandas as pd
import numpy as np

#goal of this script is to use ffmpeg and the length of the associated csv and video to slow down the frame rate to match real-time
#bandwidth is causing video to speed up to a faster than normal rate 

def slow_down_video(input_path, output_path, speed_factor):
    # speed_factor = recorded_duration / actual_duration (<1 to slow down)
    command = [
        'ffmpeg',
        '-i', input_path,
        '-filter:v', f"setpts=PTS/{speed_factor}",
        '-an',  # Remove audio (optional)
        output_path
    ]
    subprocess.run(command)

def get_video_duration(filename):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

def load_video (freq):
    freq = round(freq, 1)
    input_video = f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/{freq}.avi"
    input_csv=f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/{freq}.csv"
    output_video = f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/{freq}_slowed.avi"


    duration_seconds = get_video_duration(input_video)
    print(f"Duration: {duration_seconds} seconds")


    # Read the whole CSV into a DataFrame
    df = pd.read_csv(input_csv)

    column_data = df.iloc[:, 1]
    # Assuming you want the first non-zero or True value in column_data
    first_true_index = column_data.ne(0).idxmax()  # index of first non-zero
    first_true_index+=2 #gives actual data rather than unintended time
    t0 = float(column_data.loc[first_true_index])

    # Get last value in the column
    tf = float(column_data.iloc[-1])  # last value

    delta_t = tf - t0
    print("T0:", t0)
    print("Tf:", tf)
    print("The actual time should be", delta_t)

    recorded_duration = duration_seconds  # seconds (your current video length)
    actual_duration = delta_t   # seconds (should be)

    speed = recorded_duration / actual_duration  # 8 / 14 ≈ 0.57
    print(f"Speed: {speed}")

    #need to figure out how to import csv and parse through the data to find the time 
    slow_down_video(input_video, output_video, speed)


for freq in np.arange(1.0, 2.0, 0.2): #1-2 inclusive
    load_video(freq)