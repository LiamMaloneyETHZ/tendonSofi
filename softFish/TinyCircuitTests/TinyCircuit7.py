import serial
import time
import sys
import os

from dxlControlPath import relativeDirUp
relativeDirUp(levels=3)

import board
import adafruit_bno055

from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject, closePortObject

# === Setup Dynamixel Port ===
openPortObject()
servo = XC330(id=11, zeroPos=0, shortBool=True)
servo.torqueEnable()

# === Parameters ===
pos_a = 4000
pos_b = -4000
velocity = 100

# Serial parameters
SERIAL_PORT = '/dev/ttyACM0'  # Adjust if necessary
BAUD_RATE = 115200

def main():

    print("Starting oscillating motion and IMU sync...")
    start_time = time.time()

    current_target = pos_a  # Initialize here

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
        time.sleep(2)  # Wait for Arduino reset

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Moving to {current_target}...")
            servo.moveAndWait(current_target, velocity)
            if line:
                print("Received from Arduino Receiver:", line)

            current_target = pos_a if current_target == pos_b else pos_b

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Returning to start position...")
        servo.moveAndWait(0, velocity)
        servo.torqueDisable()

        closePortObject()
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()
