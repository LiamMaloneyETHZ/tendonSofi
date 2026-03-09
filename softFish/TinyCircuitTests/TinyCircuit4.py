#!/usr/bin/env python3
import time
import serial
import board
import adafruit_bno055

from dxlControlPath import relativeDirUp
relativeDirUp(levels=3)

from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject, closePortObject

# === Setup Dynamixel Port ===
openPortObject()
servo = XC330(id=11, zeroPos=0, shortBool=True)
servo.torqueEnable()

# === Setup IMU ===
i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)

# === Setup Arduino Serial Port ===
try:
    arduino_serial = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    arduino_serial.reset_input_buffer()
except serial.SerialException as e:
    print(f"Failed to connect to Arduino on /dev/ttyACM0: {e}")
    closePortObject()
    exit(1)

# === Parameters ===
target_position = 4000
velocity = 400

# === Start Motion and IMU Sync ===
print("Starting motion and IMU sync...")
servo.readPos()
start_time = time.time()

try:
    # Start movement
    servo.goalPos = target_position
    servo.vel = velocity

    while True:
        current_pos = servo.readPos()
        elapsed = time.time() - start_time

        euler = sensor.euler or (0.0, 0.0, 0.0)
        accel = sensor.acceleration or (0.0, 0.0, 0.0)

        message = (
            f"{elapsed:<10.2f}"
            f"({euler[0]:.1f}, {euler[1]:.1f}, {euler[2]:.1f}) "
            f"{current_pos:.2f} "
            f"({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})\n"
        )

        arduino_serial.write(message.encode('utf-8'))

        line = arduino_serial.readline().decode('utf-8').strip()
        if line:
            print(f"Arduino: {line}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    print("Returning to start position...")
    servo.moveAndWait(0, velocity)
    servo.torqueDisable()
    arduino_serial.close()
    closePortObject()
