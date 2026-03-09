import os
import time
import platform
from datetime import datetime
import pandas as pd
from dxlControlPath import relativeDir, motorZeroConfig
relativeDir('../')

from dxlSetup.XL430 import XL430
from dxlSetup.portAndPackets import openPortObject, closePortObject
import csv

# === Setup ===
openPortObject()
servo = XL430(id=1, zeroPos=0, shortBool=True)
servo.torqueEnable()

goal_freq=4.84 #goal velocity of the tail in hertz, max of 4.84
motor_max_velo=235 
motor_velo_step=.229 #unit scale
motor_velocity=motor_max_velo*motor_velo_step #rpm
motor_velocity=motor_velocity/60
gear_ratio=5.4 #for the planetary gear setup ratio of planets vs. sun +1
motor_output=goal_freq/gear_ratio
motor_freq=motor_output/motor_velo_step #divides by unit scale, gives frequency
motor_velocity=motor_freq*60 #converts to rpm
velocity=motor_velocity #casts math onto simpler variable
velocity=int(velocity) #casts

print(velocity)
if (velocity>235 or velocity<-235):
    raise ValueError('Velocity is not in the right range for the motor (-235 to 235)')

# Initialize data storage
data_records = []
start_time = time.time()


try:
    # Set movement parameters
    servo.vel = velocity           # Define velocity

    while True:
        # Collect data
        time_step = time.time() - start_time
        position = servo.readPos()
        velocity = servo.readVel()
        load = servo.readLoad()

        # Store in list of dicts for DataFrame
        data_records.append({
            "Time": time_step,
            "Position": position,
            "Velocity": velocity,
            "Load": load
        })
        if abs(time_step>=60): #if the time is greater than 60s, no longer reliant on position data
            break

        time.sleep(0.05)  # Sampling rate, can change to match the frequency of how quickly the load cell gathers data 

except KeyboardInterrupt:
    print("Data collection interrupted by user.")

finally:
    # Clean up and disable torque
    servo.torqueDisable()
    closePortObject()

# === Save Data ===
df = pd.DataFrame(data_records)

if platform.system() == "Windows":
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "OneDrive", "Desktop")
        save_dir = os.path.join(desktop, "ETHZ")
else:  # Assume Raspberry Pi (Linux)
    save_dir = "/home/uwpi/Desktop/"
    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)


valid_indices = []
for i in range(len(time_step)):
    if time_step[i] < 0:
        break
    valid_indices.append(i)

time_data = [time_step[i] for i in valid_indices]
position_data = [[int(value) for value in row] for row in position]
velocity_data = [[int(value) for value in row] for row in velocity]
load_data = [[int(value) for value in row] for row in load]

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

filename = os.path.join(save_dir, f"{goal_freq} SRL-Prototype1-Test.csv")

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
        
    header = ['Time']
    for i in range(len(position_data[0])):
        header.append(f'Pos {i+1}')
    for i in range(len(velocity_data[0])):
        header.append(f'Velocity {i+1}')
    for i in range(len(load_data[0])):
        header.append(f'Load {i+1}')
    writer.writerow(header)
        
    for i in range(len(time_data)):
        time_value = round(time_data[i], 3) if isinstance(time_data[i], (int, float)) else round(time_data[i][0], 3)
        row = [time_value]  # Append time data directly
        for j in range(len(position_data[i])):
            row.append(position_data[i][j])
        for j in range(len(velocity_data[i])):
            row.append(velocity_data[i][j])
        for j in range(len(load_data[i])):
            row.append(load_data[i][j])
        writer.writerow(row)
    
print(f"Data saved to {filename}")

