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

# === Parameters ===
pos_a = 4000
pos_b = -4000
velocity = 100

# === Setup Arduino Serial Port ===
try:
    arduino_serial = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    arduino_serial.reset_input_buffer()
except serial.SerialException as e:
    print(f"Failed to connect to Arduino on /dev/ttyACM0: {e}")
    closePortObject()
    exit(1)

print("Starting oscillating motion and IMU sync...")
start_time = time.time()

try:
    servo.vel = velocity
    current_target = pos_b

    while True:
        print(f"Moving to {current_target}...")
        servo.moveAndWait(current_target, velocity)  # Initiate motion

        while True:
            current_pos = servo.readPos()
            elapsed = time.time() - start_time
            euler = sensor.euler or (0.0, 0.0, 0.0)
            accel = sensor.acceleration or (0.0, 0.0, 0.0)

            message = f"{current_pos:.2f} "
            arduino_serial.write(message.encode('utf-8'))

            line = arduino_serial.readline().decode('utf-8').strip()
            if line:
                print(f"Arduino: {line}")

            if abs(current_pos - current_target) < 20:
                break

            time.sleep(0.05)

        # Final position adjustment, optional for precision
        servo.moveAndWait(current_target, velocity)

        # Alternate direction
        current_target = pos_a if current_target == pos_b else pos_b

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    print("Returning to start position...")
    servo.moveAndWait(0, velocity)
    servo.torqueDisable()
    arduino_serial.close()
    closePortObject()
