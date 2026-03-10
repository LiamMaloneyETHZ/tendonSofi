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
    parser = argparse.ArgumentParser(description="System ID data collection using a Velocity Chirp (frequency sweep).")
    parser.add_argument("--freq_start", type=float, required=True, help="Starting frequency in Hz (rev/s).")
    parser.add_argument("--freq_end", type=float, required=True, help="Ending frequency in Hz (rev/s).")
    parser.add_argument("--duration", type=float, required=True, help="Duration of the chirp experiment in seconds.")
    args = parser.parse_args()

    start_freq = args.freq_start
    end_freq = args.freq_end
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

    # Memory pre-allocation for high-speed loop
    timestamps = []
    target_freqs = []
    commanded_vels = []
    positions = []
    velocities = []
    loads = []

    print(f"Starting chirp from {start_freq} Hz to {end_freq} Hz over {duration} seconds...")
    start_time = time.time()
    
    try:
        # High-frequency control loop
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                break
            
            # Calculate the current target frequency for this exact moment (linear interpolation)
            current_freq = start_freq + (end_freq - start_freq) * (elapsed_time / duration)
            
            # Calculate goal velocity
            current_goalVel = int(round(current_freq / (gearRatio * velScale) * 60))
            
            # Update the motor with the new velocity
            servo.velMove(current_goalVel)
            
            # Read current actual values from Dynamixel
            pos = servo.readPos()
            vel = servo.readVel()
            load = servo.readLoad()
            
            # Store data to memory lists
            timestamps.append(elapsed_time)
            target_freqs.append(current_freq)
            commanded_vels.append(current_goalVel)
            positions.append(pos)
            velocities.append(vel)
            loads.append(load)

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
        filename = f"sysID_chirp_{start_freq}to{end_freq}Hz_{duration}s_{timestamp_str}.csv"
        
        print(f"Saving data to {filename}...")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time (s)", "Target Freq (Hz)", "Commanded Vel (raw)", "Measured Pos (raw)", "Measured Vel (raw)", "Measured Load (raw)"])
            for t, tf, cv, p, v, l in zip(timestamps, target_freqs, commanded_vels, positions, velocities, loads):
                writer.writerow([t, tf, cv, p, v, l])
                
        print(f"Data successfully saved! Total samples: {len(timestamps)}")

if __name__ == "__main__":
    main()