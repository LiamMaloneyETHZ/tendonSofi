#!/usr/bin/env python3
import serial
import time
import board
import adafruit_bno055

#from dxlControlPath import relativeDir
#relativeDir('../')

#from dxlSetup.XC330 import XC330
#from dxlSetup.portAndPackets import openPortObject, closePortObject

# === Setup ===
i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)

# === Start Motion and IMU Sync ===
print("Starting motion and IMU sync...")
start_time = time.time()

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    #ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        elapsed = time.time() - start_time
        euler = sensor.euler or (0.0, 0.0, 0.0)
        accel = sensor.acceleration or (0.0, 0.0, 0.0)

        message = (
            f"{elapsed:<10.2f}"
            f"({euler[0]:.1f}, {euler[1]:.1f}, {euler[2]:.1f})       "
            f"({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})\n"
        )
        ser.write(message.encode('utf-8'))

        line = ser.readline().decode('utf-8').rstrip()
        if line:
            print(line)

        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted by user.")
