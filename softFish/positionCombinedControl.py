import serial
import time
from datetime import datetime
import numpy as np
import cv2
import os
# Dynamixel control setup
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject, closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430

#need to write the images afterwards

#need to figure out why the motor hardware isn't working, everything else seems to be working fine

# ---------------------- Configuration ----------------------
desiredFreq = 2                 # Hz (cycle frequency)
commandTime = 0.08               # seconds between servo commands
numCycles = 30                   # number of movement cycles
saveData = True
motorVel = 235                   # DXL velocity
gearRatio = 5.4
motorTicks = 4096
stepSize = motorTicks * (desiredFreq / gearRatio) * commandTime
all_steps = int((numCycles / desiredFreq) / commandTime)

# ---------------------- Initialize Data ----------------------
position_data = np.zeros((all_steps + 1, 1))
load_data = np.zeros((all_steps + 1, 1))
vel_data = np.zeros((all_steps + 1, 1))
time_data = np.zeros((all_steps + 1, 1))
goal_pos_data = np.zeros((all_steps + 2, 1))


# ---------------------- Time & File Setup ----------------------
output_dir = r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput"
os.makedirs(output_dir, exist_ok=True)

global_start_time = datetime.now().strftime("%m-%d_%H-%M-%S")

#converts it to a float with one decimal 
desiredFreq = float(f"{desiredFreq:.1f}")
video_filename = os.path.join(output_dir, f'{desiredFreq}.avi')
csv_filename = os.path.join(output_dir, f'{desiredFreq}.csv')

# ---------------------- Open Camera ----------------------
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))

# ---------------------- Open Serial ----------------------
ser = serial.Serial('COM12', 9600)
start = time.time()

# ---------------------- Open Dynamixel ----------------------
openPortObject()
servo = XL430(id=1, zeroPos=0)
servo.torqueEnable()
servo.goalPos = servo.readPos()
time.sleep(2)

print("Recording... Press 'q' to stop.")

# ---------------------- Start Trial ----------------------
with open(csv_filename, 'w') as f:
    f.write(f"Frequency-Intended {desiredFreq}, Start Time {global_start_time}, Number of cycle {numCycles}, Gear Ratio {gearRatio}\n")
    f.write("Time (s), Force, GoalPos, ServoPos, Load, Velocity\n")

    try:
        initial_time = time.time()
        position_data[0] = servo.readPos()
        vel_data[0] = servo.readVel()
        load_data[0] = servo.readLoad()
        goal_pos_data[0:2] = servo.goalPos
        time_data[0] = initial_time

        for step in range(all_steps):
            loop_start = time.time()

            # Servo command
            servo.goalPos = servo.goalPos + stepSize
            servo.move(goal_pos=int(round(servo.goalPos)), prof_vel=motorVel)
            goalPosition=servo.goalPos

            # Read sensors
            position = servo.readPos()
            velocity = servo.readVel()
            load = servo.readLoad()
            timestamp = time.time() - start

            # Store data
            position_data[step + 1] = position
            vel_data[step + 1] = velocity
            load_data[step + 1] = load
            goal_pos_data[step + 2] = servo.goalPos
            time_data[step + 1] = time.time()

            # Read serial (force)
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            # Video frame
            ret, frame = camera.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Overlay force & timestamps
            current_time = datetime.now().strftime("%m-%d %H:%M:%S")
            cv2.putText(frame, f"Start: {global_start_time} | Now: {current_time}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Force: {line}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Motor Goal-Position: {servo.goalPos}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

            # Save to disk
            out.write(frame)
            cv2.imshow('Recording', frame)
            f.write(f"{timestamp:.2f},{line},{goalPosition},{position},{load},{velocity}\n")

            # Break if 'q' pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Recording stopped by user.")
                break

            # Wait for next cycle
            loop_duration = time.time() - loop_start
            if loop_duration < commandTime:
                time.sleep(commandTime - loop_duration)

    except KeyboardInterrupt:
        print("Interrupted by user.")

# ---------------------- Cleanup ----------------------
camera.release()
out.release()
cv2.destroyAllWindows()
closePortObject()

print("Done. Files saved:")
print(f"  → Video: {video_filename}")
print(f"  → Force CSV: {csv_filename}")
