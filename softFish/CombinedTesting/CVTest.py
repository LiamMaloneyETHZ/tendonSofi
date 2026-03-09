#!/usr/bin/env python3
# code mostly from Mike Yan Michelis
# measures the angle between each rectangle bounding box and the center of the frame - only good for fixed framed videos

import os
import time
import cv2
import numpy as np
from datetime import datetime
import math
import csv
import matplotlib.pyplot as plt  # added for plotting

# Function to adjust contrast
def adjust_contrast(frame, alpha, beta):
    # alpha: Contrast control (1.0-3.0), beta: Brightness control (0-100)
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

filepath = "/home/srl-slim-tim/ForceTest/20250731_1229_f3.0Hz_film_test_data.avi"
folder = os.path.dirname(filepath)
cap = cv2.VideoCapture(filepath)
fps = cap.get(cv2.CAP_PROP_FPS)  # should be 30 for all videos
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # number of frames
freq = 3.0  # hardcoded frequency for now

num_boxes = 8  # number of copper spots

# Start frame after some camera stabilization time
start_frame = 35
end_frame = total_frames
duration = (end_frame - start_frame) / fps

formatted_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

print("Select bounding boxes in TAIL-TO-HEAD order.")
while cap.isOpened():
    ret, frame = cap.read()
    framenum = 0
    if not ret:
        print("Error: Could not read frame.")
        break
    height, width = frame.shape[:2]
    y_center = height // 2
    x_center = width // 2
    start_point = (0, y_center)
    end_point = (width - 1, y_center)

    # Select bounding boxes
    bboxes = []
    for i in range(num_boxes):
        roi = cv2.selectROI(f"Select box {i+1} (tail to head)", frame, showCrosshair=True, fromCenter=False)
        bboxes.append(roi)
    break  # only do selection once
cap.release()
cv2.destroyAllWindows()

# Initialize MultiTracker
trackers = cv2.legacy.MultiTracker_create()
for box in bboxes:
    trackers.add(cv2.legacy.TrackerCSRT_create(), frame, box)

cap = cv2.VideoCapture(filepath)
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

cut_movie = cv2.VideoWriter(f"{folder}/cut_video_{freq}.mp4", fourcc, fps, (frame.shape[1], frame.shape[0]))
tracked_movie = cv2.VideoWriter(f"{folder}/tracked_video_{freq}.mp4", fourcc, fps, (frame.shape[1], frame.shape[0]))

markers = []
all_rel_metrics = []
all_rel_metrics_2 = []
all_abs_metrics = []
framenum = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or framenum > end_frame:
        break
    framenum += 1

    if framenum < start_frame:
        continue

    # Draw line across center of screen
    height, width = frame.shape[:2]
    y_center = height // 2
    start_point = (0, y_center)
    end_point = (width - 1, y_center)
    cv2.line(frame, start_point, end_point, (255, 255, 255), 1)

    # Adjust contrast and brightness
    alpha = 1
    beta = 45
    frame = adjust_contrast(frame, alpha, beta)
    cut_movie.write(frame)

    found, bboxes_new = trackers.update(frame)
    if not found:
        cv2.putText(frame, "Tracking failed", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    curr_markers = []
    for i, box in enumerate(bboxes_new):
        x, y, w, h = box
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        curr_markers.append((cx, cy))
        cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)

    # Draw tail as polyline if more than 1 marker
    if len(curr_markers) >= 2:
        points = np.array(curr_markers, dtype=np.int32)
        cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 255), thickness=2)

    markers.append(np.array(curr_markers).flatten())

    # Reference is head (last box in tail-to-head list)
    head_center = np.array(curr_markers[-1])
    rel_metrics = []
    rel_metrics_2 = []
    abs_metrics = []

    for i in range(num_boxes - 1):
        pt = np.array(curr_markers[i])
        dx = pt[0] - head_center[0]
        dy = pt[1] - head_center[1]
        distance = np.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx) * 180 / np.pi
        if angle > 0:
            angle -= 180
        else:
            angle += 180
        rel_metrics.append([framenum, i, dx, dy, distance, angle])

    total_angle_sum = 0
    for i in range(num_boxes - 1):
        pt_1 = np.array(curr_markers[i])
        pt_2 = np.array(curr_markers[i + 1])
        dx = pt_1[0] - pt_2[0]
        dy = pt_1[1] - pt_2[1]
        distance = np.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx) * 180 / np.pi
        if angle > 0:
            angle -= 180
        else:
            angle += 180

        total_angle_sum += angle
        rel_metrics_2.append([framenum, i, dx, dy, distance, angle])

    abs_metrics.append([framenum, total_angle_sum])

    all_rel_metrics.extend(rel_metrics)
    all_rel_metrics_2.extend(rel_metrics_2)
    all_abs_metrics.extend(abs_metrics)

    tracked_movie.write(frame)
    cv2.imshow("Tracker (press Q to exit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Exited early.")
        break

cap.release()
cut_movie.release()
tracked_movie.release()
cv2.destroyAllWindows()

fps = 30  # Hardcoded fps

np.savetxt(f"{folder}/markers.csv", markers, delimiter=",")

with open(f"{folder}/TailSegments_to_HeadSegments_Metrics.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Number of Boxes", "Total Time", "Start Frame", "End Frame", "Video Path", "Alpha", "Beta"])
    writer.writerow([num_boxes, (end_frame - start_frame) / fps, start_frame, end_frame, filepath, alpha, beta])
    writer.writerow(["Time (s)", "Box Index", "dx", "dy", "Distance", "Angle"])
    for framenum, i, dx, dy, distance, angle in all_rel_metrics:
        t = framenum / fps
        writer.writerow([t, i, dx, dy, distance, angle])

with open(f"{folder}/TailSegments_Relative_Metrics.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Number of Boxes", "Total Time", "Start Frame", "End Frame", "Video Path", "Alpha", "Beta"])
    writer.writerow([num_boxes, (end_frame - start_frame) / fps, start_frame, end_frame, filepath, alpha, beta])
    writer.writerow(["Frame", "Box Index", "dx (i+1 rel. i)", "dy (i+1 rel. i)", "Distance (i+1 rel. i)", "Angle (i+1 rel. i)"])
    for framenum, i, dx, dy, distance, angle in all_rel_metrics_2:
        t = framenum / fps
        writer.writerow([t, i, dx, dy, distance, angle])

times = []
angles = []

with open(f"{folder}/Total_Angle_Metrics.csv", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Number of Boxes", "Total Time", "Start Frame", "End Frame", "Video Path", "Alpha", "Beta", "Duration"])
    writer.writerow([num_boxes, (end_frame - start_frame) / fps, start_frame, end_frame, filepath, alpha, beta , duration])
    writer.writerow(["Time (s)", "Total Angle (deg)"])
    for framenum, total_angle_sum in all_abs_metrics:
        t = framenum / fps
        times.append(t)
        writer.writerow([t, total_angle_sum])
        angles.append(total_angle_sum)

# Save position plot
position_plot_path = os.path.join(folder, f"Time_vs_Frame_{formatted_datetime}.png")
plt.figure()
plt.plot(times, angles, label="Position")
plt.xlabel("Time (s)")
plt.ylabel("Angle Total")
plt.title("Time vs. Angle")
plt.grid(True)
plt.savefig(position_plot_path)
print(f"Position plot saved to {position_plot_path}")
plt.pause(10)  # Keeps plot open for 10 seconds
