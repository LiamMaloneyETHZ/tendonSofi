#!/usr/bin/env python3
import serial
import time
import board
import adafruit_bno055

from dxlControlPath import relativeDirUp
relativeDirUp(levels=3)

from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject, closePortObject

# === Setup ===
openPortObject()
servo = XC330(id=11, zeroPos=0, shortBool=True)
servo.torqueEnable()

# === IMU Setup ===
i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)

# === Parameters ===
target_position = 4000
velocity = 400

# === Start Motion and IMU Sync ===
print("Starting motion and IMU sync...")
start_time = time.time()

try:
    # Start movement without waiting inside moveAndWait
    servo.goalPos = target_position
    servo.vel = velocity

    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        elapsed = time.time() - start_time
        print(f"Time elapsed: {elapsed:.2f} s")  # Basic heartbeat to show loop is alive

        current_pos = servo.readPos()

        euler = sensor.euler or (0.0, 0.0, 0.0)
        accel = sensor.acceleration or (0.0, 0.0, 0.0)

        message = (
            f"{elapsed:<10.2f}"
            f"({euler[0]:.1f}, {euler[1]:.1f}, {euler[2]:.1f}) "
            f"{current_pos:.2f} "
            f"({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})\n"
        )
        ser.write(message.encode('utf-8'))

        line = ser.readline().decode('utf-8').rstrip()
        if line:
            print(line)

        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted by user.")

# === Return and Clean up ===
print("Returning to start position...")
servo.moveAndWait(0, velocity)

servo.torqueDisable()
closePortObject()
