#This works with the ScaleReadingUpdate script to stream the data of the force output to the respective computer and save it in a CSV
import serial
import sys
import time
from datetime import datetime
import os

# Get the current timestamp for the start time, will be used to overlay video with force with positional control
global_start_time = datetime.now().strftime("%m-%d_%H-%M-%S")
start_time=time.time()

ser = serial.Serial('/dev/ttyUSB0', 9600)  # COM 9 is hardcoded from my computer, using Arduino Uno
start=time.time()

# Print the message passed from PowerShell
#f len(sys.argv) > 1:
   #freq_string=sys.argv[1]

#check to see if it is being processed
print("ForceTimeSerialComm.py started with frequency:", 2)

#had been "C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput"
#directory arrangement, should save as . . . /2.0 or whatever frequency, then it can parse with the actual frequency script
output_dir = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting"
filename = f"{2}.csv"
filepath = os.path.join(output_dir, filename)

with open(filepath, 'w') as f:
    f.write(f'Force(N),Time (s)-{global_start_time}\n')  # CSV header
    try:
        while True:
            time_val=time.time()-start
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(line)
            print(time_val)
            f.write(f"{line},{time_val}\n")
            #trying to flush data 
            f.flush()
    except KeyboardInterrupt:
        print("Stopped by user")