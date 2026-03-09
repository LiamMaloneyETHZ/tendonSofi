# !/usr/bin/env python3
#code almost entirely from Mike Yan Michelis
#Working on developing a function to compute the angle between the fish_head (first bounding box) and a stationary bounding box:
#could work on making stationary bounding box permanent to the frame 

"""Track bounding boxes within video.

Usage: python3 track_markers.py -f <filepath> -n <num_boxes> -s <start_frame> -e <end_frame>

Example: python3 track_markers.py -f ~/Downloads/tracking/vid.mp4 -n 2 -s 10 -e 50

Script for tracking N manually chosen bounding boxes within video. Point this script to the video file you would like to track and choose how many N bounding boxes are desired. These bounding box centers (markers) are stored in a CSV file afterwards. Two videos are created as well, one is the original video cut to [start_frame, end_frame], and the other is with the tracking bounding boxes displayed. If you for some reason desire to quite the tracking earlier than end_frame, you can press q to exit out.

Note: OpenCV installation can sometimes have trouble with cv2.legacy.MultiTracker_create(), the version that worked is:
opencv-contrib-python 4.5.2.52

Should be able to parse through all of the videos in a for loop. Need to do 2 boxes with the first box being something stationary
The second box should be the head of the fish at a standardized position

"""

import os
import time
import click
import cv2
import numpy as np
from datetime import datetime
import math
import csv
import matplotlib.pyplot as plt

# Function to adjust contrast
def adjust_contrast(frame, alpha, beta):
    # alpha: Contrast control (1.0-3.0), beta: Brightness control (0-100)
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)


def track_markers(filepath: str, num_boxes: int, start_frame: int,  freq: float):
    folder=r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput\Live-Tests"
    filepath=f"C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput/Live-Tests/{freq}.avi"
    
    
    
    cap = cv2.VideoCapture(filepath)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end_frame=start_frame+total_frames
    
    framenum = 0
    print("Select bounding boxes in TAIL-TO-HEAD order.")
    while cap.isOpened():
        ret, frame = cap.read()
        framenum += 1
        if framenum < start_frame:
            continue
        if not ret:
            print("Error: Could not read frame.")
            return
        
        height, width = frame.shape[:2]
        y_center = height // 2
        x_center = width // 2
        start_point = (0, y_center)
        end_point = (width - 1, y_center)

        bboxes = []
        for i in range(num_boxes):
            roi = cv2.selectROI(f"Select box {i+1} (tail to head)", frame)
            bboxes.append(roi)
        break
    cap.release()
    cv2.destroyAllWindows()

    # Initialize MultiTracker
    trackers = cv2.legacy.MultiTracker_create()
    #trackers = cv2.MultiTracker_create()
    for box in bboxes:
        trackers.add(cv2.legacy.TrackerCSRT_create(), frame, box)

    cap = cv2.VideoCapture(filepath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    
    cut_movie = cv2.VideoWriter(f"{folder}/CV_Tail_Track/cut_movie_{freq}_HZ.avi", fourcc, fps, (frame.shape[1], frame.shape[0]))
    tracked_movie = cv2.VideoWriter(f"{folder}/CV_Tail_Track/CV_movie_{freq}_HZ.avi", fourcc, fps, (frame.shape[1], frame.shape[0]))

    #arrays for the markers, the metrics of the tail segments relative to the head, tail segments relative to each other, and the total tail-segment data
    markers = []
    all_rel_metrics = []
    all_rel_metrics_2=[]
    all_abs_metrics=[]
    framenum = 0

    while cap.isOpened():
        ret, frame = cap.read()
        framenum += 1
        if not ret or framenum > end_frame:
            break
        #draws line across the center of the screen
        cv2.line(frame, start_point, end_point, color=(255, 255, 255), thickness=1)
        if framenum < start_frame:
            continue
        
        #processes all of the images to make them easier to "read" for the CV algorithm, had been 1-75
        alpha=1
        beta=45
        frame = adjust_contrast(frame, alpha, beta)
        cut_movie.write(frame)

        height, width = frame.shape[:2]
        y_center = height // 2
        start_point = (0, y_center)
        end_point = (width - 1, y_center)
        cv2.line(frame, start_point, end_point, (255, 255, 255), 1)

        found, bboxes_new = trackers.update(frame)
        if not found:
            cv2.putText(frame, "Tracking failed", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        curr_markers = []
        for i, box in enumerate(bboxes_new):
            x, y, w, h = box
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            curr_markers.append((cx, cy))
            # Draw bounding boxes
            cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)

        # Draws tail as polyline
        if len(curr_markers) >= 2:
            points = np.array(curr_markers, dtype=np.int32)
            cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 255), thickness=2)

        markers.append(np.array(curr_markers).flatten())

        # Reference is head (last box in tail-to-head list)
        head_center = np.array(curr_markers[-1])
        rel_metrics = []
        #measures angle, distance, etc. via the last rectangular object ('the head')
        for i in range(num_boxes - 1):
            pt = np.array(curr_markers[i])
            dx = pt[0] - head_center[0]
            dy = pt[1] - head_center[1]
            distance = np.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx) * 180 / np.pi
            #if (angle>0):
                #angle=angle-180
            #else:
                #angle=angle+180
            rel_metrics.append([framenum, i, dx, dy, distance, angle])

        #adds to a new array
        all_rel_metrics.extend(rel_metrics)

        tracked_movie.write(frame)

    cap.release()
    cut_movie.release()
    tracked_movie.release()
    cv2.destroyAllWindows()


    np.savetxt(f"{folder}/markers_{freq}.csv", markers, delimiter=",")
    with open(f"{folder}/HeadSegement_rel_Stationary_{freq}.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        #adds meta data to the top of the CSV
        writer.writerow(["Number of Boxes","Start Frame","End Frame","Video Path","Alpha","Beta"])
        writer.writerow([num_boxes,start_frame,end_frame,filepath,alpha,beta])

        #adds real formatting for data
        writer.writerow(["dx", "dy", "Distance", "Angle"])
        for framenum,dx,dy,distance,angle in all_rel_metrics:
            #times.append(t)
            writer.writerow([t,dx,dy,distance,angle])


if __name__ == "__main__":
    #for freq in np.arange(0.6, 2.1, 0.1): 
    for freq in np.arange(2.0, 4.2, 0.2): #2-4-inclusive
        freq = round(freq, 1)

        track_markers(

            filepath="",         # avoids having to use commands in prompt shell
            num_boxes=2,
            start_frame=0,
            freq=freq
        )
