#This works with the ScaleReadingUpdate script to stream the data of the force output to the respective computer and save it in a CSV
from numpy import rint
import serial
import sys
import time
from datetime import datetime
import os

# Get the current timestamp for the start time, will be used to overlay video with force with positional control
#starts timestamp at top of all files, formatted the same way 
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
global_start_time = datetime.now().strftime("%m-%d_%H-%M-%S")
start_time=time.time()

ser = serial.Serial('/dev/ttyUSB0', 9600)  # port is hardcoded from my computer, using Arduino Uno
start=time.time()

desiredFreq=0.3

# Print the message passed from PowerShell
#if len(sys.argv) > 1:
   #freq_string=sys.argv[1]

#check to see if it is being processed
print("ForceTimeSerialComm.py started with frequency:", desiredFreq)

#had been "C:/Users/15405/OneDrive/Desktop/Career/ETHZ/ETHZ Work/HardwareOutput"
#directory arrangement, should save as . . . /2.0 or whatever frequency, then it can parse with the actual frequency script
#change output diretory
output_dir = "/home/srl-slim-tim/ForceTest/ForceTest2"

# Generate filenamec
#timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
#(YYYYMMDD_HHMM_f2Hz_servo_test_data.csv)
filename = os.path.join(output_dir, f"{timestamp}_f{desiredFreq}Hz_force_test_data.csv")
#filename = f"{desiredFreq}_{timestamp}.csv"
filepath = os.path.join(output_dir, filename)


#disregard first row of data, and then offset by first time 
count=0
with open(filepath, 'w') as f:
    #desiredFreq,commandTime,stepSize,global_start_time
    #3.0,0.08,182.04444444444442,07-31_12-48-57
    f.write(f'Desired Frequency: {desiredFreq} Hz, Start Time: {timestamp}\n')
    f.write("Force Readings (Kg), Time (s)\n")
    try:
        while True:
            time_val=time.time()-start
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            #print(line)
            #print(time_val)
            f.write(f"{line},{time_val}\n")
            #trying to flush data 
            f.flush()
    except KeyboardInterrupt:
        print("Stopped by user")




    """
    if os.path.exists("terminate.txt"):
        print("Termination signal detected. Exiting.")
        exit()


        if count >0:
            time=time.time()-start
            if count==1:
                t0=time
            realtime=time-t0
            f.write(f"{line},{realtime}\n")
        count+=1

    """

    
