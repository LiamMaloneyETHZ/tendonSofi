import time, numpy as np
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from datetime import datetime
import sys
import os 

#tank is smallscale fluid dynamic test bench, 3d printed a funnel so the waer can come up and down, laminar flow veins to make sure verything everything goes around is laminar
#propellers propel water, powered outside glass, magnetics coupled with magnets

openPortObject()
#starts timestamp at top of all files, formatted the same way 
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

desiredFreq=0.3

# Get the current timestamp for the start time, will be used to overlay video with force with positional control
global_start_time = datetime.now().strftime("%m-%d_%H-%M-%S")

#might be keeping the zero position from the other scripts 
## Servo Setup ##
servo = XL430(id=1,zeroPos=0)
motorVel = 235 #max in DXL units
servo.zeroPos = 1238 #found with positionFind.py. This is the closest point to the base of the tail


#not returning back to the zero position at the beginning, which is weird
servo.torqueEnable()

pos1 = servo.readPos()
print(f"Position before multiturn clear = {pos1}")
servo.clearMultiTurn()
pos2 = servo.readPos()
print(f"Position after multiturn clear = {pos2}")
servo.goalPos = servo.zeroPos
servo.move(goal_pos = servo.goalPos, prof_vel = motorVel)
#print(f'Original Position = {servo.goalPos}')
time.sleep(5)
## Trial Adjustable Parameters ##
#desiredFreq = 2 #Hz or rev/s, max of 4.84335
commandTime = 0.08 #seconds
numCycles = 30 # or ctrl+c to end early
saveData = True #bool for saving

## Trial Constants ##
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




"""
#could take 4096%360 then set that as the goal position
## Move motor back to zero position before cleanup ##
zero_pos = servo.zeroPos if hasattr(servo, 'zeroPos') else 0
servo.move(goal_pos=int(zero_pos), prof_vel=80)while abs(servo.readPos() - zero_pos) > 10:    ## Clean up ##
    time.sleep(1)
    servo.torqueDisable()
    closePortObject()


"""

#from here on, it is cleaning up and flushing positional data
time.sleep(5)
print("Returning back to zero position")
pos1 = servo.readPos()
print(f"Position before multiturn clear = {pos1}")
servo.clearMultiTurn()
time.sleep(1)
servo.goalPos = servo.zeroPos
#changes to much lower motor speed 
servo.move(goal_pos = servo.goalPos, prof_vel = 60)
time.sleep(1)
pos2 = servo.readPos()
print(f"Position after multiturn clear = {pos2}")
time.sleep(2)
servo.torqueDisable()
closePortObject()

time_data -= initial_time
## Data Saving ##
if saveData:
    import os, csv, platform
    from datetime import datetime

    #had been r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput"
    save_dir= "/home/srl-slim-tim/ForceTest/ForceTest2"
    

    # Generate filenamec
    #timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    #(YYYYMMDD_HHMM_f2Hz_servo_test_data.csv)
    filename = os.path.join(save_dir, f"{timestamp}_f{desiredFreq}Hz_servo_test_data.csv")

    # Write data
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Metadata (row 1: keys, row 2: values)
        writer.writerow(['desiredFreq', 'commandTime', 'stepSize', 'global_start_time'])
        writer.writerow([desiredFreq, commandTime, stepSize, global_start_time])

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


"""

# Define the absolute or relative path to the target folder
folder_path_stop= "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"

# Join it with the filename
terminate_file = os.path.join(folder_path_stop, "terminate.txt")

# Write the file
with open(terminate_file, "w") as f:
    f.write("stop")
    print("STOP SIGNAL SENT")
"""


sys.exit()

#at this point, the other scripts get message to terminate

