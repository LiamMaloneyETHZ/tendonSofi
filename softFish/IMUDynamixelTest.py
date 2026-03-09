import time
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject, closePortObject

import board
import adafruit_bno055

# === Setup ===
openPortObject()
servo = XC330(id=11, zeroPos=0, shortBool=True)
servo.torqueEnable()

i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c)

# === Parameters ===
target_position = 4000
velocity = 400

# === Start Motion and IMU Sync ===
print("Starting motion and IMU sync...")
servo.readPos()
start_time = time.time()

print("="*100)
print(f"{'Time (s)':<10}{'Position':<10}{'Euler (°)':<40}{'Accel (m/s²)':<30}")
print("="*100)

try:
    # Start movement without waiting inside moveAndWait
    servo.goalPos = target_position
    servo.vel = velocity

    # Sample during movement
    while True:
        current_pos = servo.readPos()
        elapsed = time.time() - start_time
        euler = sensor.euler or (0.0, 0.0, 0.0)
        accel = sensor.acceleration or (0.0, 0.0, 0.0)

        print(f"{elapsed:<10.2f}{current_pos:<10.0f}({euler[0]:.1f}, {euler[1]:.1f}, {euler[2]:.1f})       ({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})")

        # Exit if close to target
        if abs(current_pos - target_position) < 20:
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Interrupted by user.")

# === Return and Clean up ===
print("Returning to start position...")
servo.moveAndWait(0, velocity)

servo.torqueDisable()
closePortObject()
