import time
import argparse
import csv
from datetime import datetime
import os
import sys

from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject, closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430

def main():
    parser = argparse.ArgumentParser(description="System ID data collection using Velocity Control.")
    parser.add_argument("--freq", type=float, required=True, help="Target frequency in Hz (rev/s).")
    parser.add_argument("--duration", type=float, required=True, help="Duration of the experiment in seconds.")
    args = parser.parse_args()

    desiredFreq = args.freq
    duration = args.duration

    # Servo Setup
    print("Initializing Servo...")
    openPortObject()
    servo = XL430(id=1, zeroPos=0)
    servo.setOpMode(1)  # 1 = Velocity Control mode
    servo.torqueEnable()

    # Trial Constants
    gearRatio = 5.4
    velScale = 0.229
    
    # Calculate goal velocity (using the original script's conversion logic)
    goalVel = int(round(desiredFreq / (gearRatio * velScale) * 60))
    print(f"Target Frequency: {desiredFreq} Hz")
    print(f"Calculated Goal Velocity (raw): {goalVel}")

    # Memory pre-allocation for high-speed loop
    timestamps = []
    positions = []
    velocities = []
    loads = []

    print(f"Starting experiment for {duration} seconds...")
    start_time = time.time()
    
    try:
        servo.velMove(goalVel)
        
        # High-frequency control loop
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                break
            
            # Read current actual values from Dynamixel
            pos = servo.readPos()
            vel = servo.readVel()
            load = servo.readLoad()
            
            # Store data to memory lists
            timestamps.append(elapsed_time)
            positions.append(pos)
            velocities.append(vel)
            loads.append(load)
            
            # The Dynamixel read commands themselves provide a small inherent delay,
            # so no additional sleep is necessary to achieve a high polling rate.

    except KeyboardInterrupt:
        print("\nExperiment manually interrupted by user (Ctrl+C).")
    
    finally:
        # Stop and Clean up
        print("Stopping motor and disabling torque...")
        servo.velMove(0)
        time.sleep(0.5)
        servo.torqueDisable()
        closePortObject()
        
        # Save collected data
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Ensure filename contains requested parameters
        filename = f"sysID_velControl_{desiredFreq}Hz_{duration}s_{timestamp_str}.csv"
        
        print(f"Saving data to {filename}...")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time (s)", "Target Freq (Hz)", "Commanded Vel (raw)", "Measured Pos (raw)", "Measured Vel (raw)", "Measured Load (raw)"])
            for t, p, v, l in zip(timestamps, positions, velocities, loads):
                writer.writerow([t, desiredFreq, goalVel, p, v, l])
                
        print(f"Data successfully saved! Total samples: {len(timestamps)}")

if __name__ == "__main__":
    main()