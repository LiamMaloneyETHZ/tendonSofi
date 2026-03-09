import time, numpy as np
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from datetime import datetime
import sys
import os 



openPortObject()

signal_dir =  "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
motor_ended_file = os.path.join(signal_dir, "motor_control_ended.txt")

# Print the message passed from PowerShell
if len(sys.argv) > 1:
    freq_string=sys.argv[1]

    desiredFreq = round(float(freq_string), 1) 


#might be keeping the zero position from the other scripts 
## Servo Setup ##
servo = XL430(id=1,zeroPos=0)
servo.torqueEnable()
servo.goalPos = servo.readPos()
#print(f'Original Position = {servo.goalPos}')
time.sleep(5)
## Trial Adjustable Parameters ##
#desiredFreq = 2 #Hz or rev/s, max of 4.84335
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

#adding a flag to stop the other controllers when the motor reaches its goal position
# Once the motor control ends, create the stop signal file
with open(motor_ended_file, "w") as f:
    f.write("Motor Control Ended")
    f.flush()
    os.fsync(f.fileno())

#would send the flag here to return, also remember to comment out the desiredFreq
print("Returning back to zero position")
time.sleep(10)
## Move motor back to zero position before cleanup ##
zero_pos = servo.zeroPos if hasattr(servo, 'zeroPos') else 0
servo.move(goal_pos=int(zero_pos), prof_vel=motorVel)

# Wait for motor to reach zero (with timeout)
while abs(servo.readPos() - zero_pos) > 10:  # 10 ticks threshold
    print("Servo position:",servo.readPos())
    time.sleep(0.05)

## Clean up ##
time.sleep(1)
servo.torqueDisable()
closePortObject()


time_data -= initial_time
## Data Saving ##
if saveData:
    import os, csv, platform
    from datetime import datetime

    #had been r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HardwareOutput"
    save_dir= "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
    

    # Generate filenamec
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = os.path.join(save_dir, f"Servo_{desiredFreq}.csv")

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
