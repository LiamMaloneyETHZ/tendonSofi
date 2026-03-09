import time, numpy as np
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from datetime import datetime
import sys


# Get the current timestamp for the start time, will be used to overlay video with force with positional contorl
#start_time = datetime.now().strftime("%m-%d_%H-%M-%S")

openPortObject()

## Servo Setup ##
servo = XL430(id=1,zeroPos=0)
servo.torqueEnable()
servo.goalPos = servo.readPos()
#print(f'Original Position = {servo.goalPos}')
time.sleep(5)
## Trial Adjustable Parameters ##
desiredFreq = 2 #Hz or rev/s, max of 4.84335
commandTime = 0.08 #seconds
numCycles = 30 # or ctrl+c to end early
saveData = True #bool for saving

## Trial Constants ##
motorVel = 235 #max in DXL units
gearRatio = 5.4
motorTicks = 4096 #DXL units per revolution
stepSize = motorTicks*(desiredFreq/gearRatio)*commandTime
all_steps = int((numCycles/desiredFreq)/commandTime)
#print(f'Stepsize = {stepSize}')
## Data Initialization ##
position_data = np.zeros((all_steps+1,1))
load_data = np.zeros((all_steps+1,1))
vel_data = np.zeros((all_steps+1,1))
time_data = np.zeros((all_steps+1,1))
goal_pos_data = np.zeros((all_steps+2,1))

try:
    #initial data capture ##
    position_data[0] = servo.readPos()
    vel_data[0] = servo.readVel()
    load_data[0] = servo.readLoad()
    goal_pos_data[0:2] = servo.goalPos

    #input("Press enter to start!")
    initial_time = time.time()
    time_data[0] = initial_time
    for step in range(all_steps):
        start_time = time.time()
        servo.goalPos = servo.goalPos + stepSize
        #print(f'Goal Pos = {servo.goalPos}')
        servo.move(goal_pos = int(round(servo.goalPos)), prof_vel = motorVel)

        position_data[step+1] = servo.readPos()
        vel_data[step+1] = servo.readVel()
        load_data[step+1] = servo.readLoad()
        goal_pos_data[step+2] = servo.goalPos

        stop_time = time.time()
        time_data[step+1] = stop_time
        if (stop_time - start_time) < commandTime:
            time.sleep(commandTime - (stop_time - start_time))

except KeyboardInterrupt:
    pass

## Clean up ##
time.sleep(1)
servo.torqueDisable()
closePortObject()

time_data -= initial_time
## Data Saving ##
if saveData:
    import os, csv, platform
    from datetime import datetime

    # Determine save directory
    if platform.system() == "Windows":
        home = os.path.expanduser("~")
        documents = os.path.join(home, "Documents")
        save_dir = os.path.join(documents, "SRL", "SOFI_Test_Data")
    else:
        save_dir = "/home/sofi/Desktop/Testing_Data/"
    os.makedirs(save_dir, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = os.path.join(save_dir, f"{timestamp}_servo_test_data_{desiredFreq}.csv")

    # Write data
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Metadata (row 1: keys, row 2: values)
        writer.writerow(['desiredFreq', 'commandTime', 'stepSize'])
        writer.writerow([desiredFreq, commandTime, stepSize])

        # Header row
        writer.writerow(['Time (s)', 'Position', 'GoalPosition', 'Velocity', 'Load'])

        for i in range(len(time_data)):
            if time_data[i, 0] < 0:
                break
            writer.writerow([
                round(float(time_data[i, 0]), 4),
                int(position_data[i, 0]),
                int(goal_pos_data[i, 0]),
                int(vel_data[i, 0]),
                int(load_data[i, 0])
            ])
print(f"Data saved to {filename}")
