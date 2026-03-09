#!/usr/bin/env python3
import sys
import time
import math
import datetime
import os
import csv

# === Add path to IMU drivers ===
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-pressure-sensor-BMP280-BMP388"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-BerryIMU-gyro-accel-compass-filters"))# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "BerryIMU", "python-pressure-sensor-BMP280-BMP388"))

import IMU
# import LPS22HB

# === Create output folder and CSV ===
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
folder = os.path.expanduser("~/Desktop/IMU_Data")
os.makedirs(folder, exist_ok=True)
csv_file = os.path.join(folder, f"imu_log_{timestamp}.csv")

header = [
    "timestamp",
    "ACCx", "ACCy", "ACCz",
    "GYRx", "GYRy", "GYRz",
    "MAGx", "MAGy", "MAGz",
    "AccXangle", "AccYangle",
    "gyroXangle", "gyroYangle", "gyroZangle",
    "CFangleX", "CFangleY",
    "kalmanX", "kalmanY",
    "heading", "tiltCompensatedHeading",
    # "pressure", "temperature"
]

f = open(csv_file, "w", newline="")
writer = csv.writer(f)
writer.writerow(header)

# === Pressure Sensor ===
# baro = LPS22HB.lps22hb()
# baro.enableDefault()

# === Original Script Variables ===
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070
AA =  0.40
MAG_LPF_FACTOR = 0.4
ACC_LPF_FACTOR = 0.4
ACC_MEDIANTABLESIZE = 9
MAG_MEDIANTABLESIZE = 9

magXmin =  0
magYmin =  0
magZmin =  0
magXmax =  0
magYmax =  0
magZmax =  0

Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = XP_01 = XP_10 = XP_11 = 0.0
YP_00 = YP_01 = YP_10 = YP_11 = 0.0
KFangleX = KFangleY = 0.0

def kalmanFilterX(accAngle, gyroRate, DT):
    global KFangleX, x_bias, XP_00, XP_01, XP_10, XP_11
    KFangleX += DT * (gyroRate - x_bias)
    XP_00 += (-DT * (XP_10 + XP_01) + Q_angle * DT)
    XP_01 += (-DT * XP_11)
    XP_10 += (-DT * XP_11)
    XP_11 += Q_gyro * DT
    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S
    KFangleX += K_0 * x
    x_bias += K_1 * x
    XP_00 -= K_0 * XP_00
    XP_01 -= K_0 * XP_01
    XP_10 -= K_1 * XP_00
    XP_11 -= K_1 * XP_01
    return KFangleX

def kalmanFilterY(accAngle, gyroRate, DT):
    global KFangleY, y_bias, YP_00, YP_01, YP_10, YP_11
    KFangleY += DT * (gyroRate - y_bias)
    YP_00 += (-DT * (YP_10 + YP_01) + Q_angle * DT)
    YP_01 += (-DT * YP_11)
    YP_10 += (-DT * YP_11)
    YP_11 += Q_gyro * DT
    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S
    KFangleY += K_0 * y
    y_bias += K_1 * y
    YP_00 -= K_0 * YP_00
    YP_01 -= K_0 * YP_01
    YP_10 -= K_1 * YP_00
    YP_11 -= K_1 * YP_01
    return KFangleY

# === Setup ===
gyroXangle = gyroYangle = gyroZangle = 0.0
CFangleX = CFangleY = kalmanX = kalmanY = 0.0
CFangleXFiltered = CFangleYFiltered = 0.0
oldXMagRawValue = oldYMagRawValue = oldZMagRawValue = 0
oldXAccRawValue = oldYAccRawValue = oldZAccRawValue = 0
acc_medianTable1X = acc_medianTable1Y = acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2X = acc_medianTable2Y = acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
mag_medianTable1X = mag_medianTable1Y = mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2X = mag_medianTable2Y = mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE

a = datetime.datetime.now()

IMU.detectIMU()
if IMU.BerryIMUversion == 99:
    print("No BerryIMU found")
    sys.exit()
IMU.initIMU()

try:
    while True:
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()
        MAGz = IMU.readMAGz()

        b = datetime.datetime.now()
        LP = (b - a).total_seconds()
        a = b
        now = b.strftime("%H:%M:%S.%f")

        rate_gyr_x = GYRx * G_GAIN
        rate_gyr_y = GYRy * G_GAIN
        rate_gyr_z = GYRz * G_GAIN

        gyroXangle += rate_gyr_x * LP
        gyroYangle += rate_gyr_y * LP
        gyroZangle += rate_gyr_z * LP

        AccXangle = math.atan2(ACCy, ACCz) * RAD_TO_DEG
        AccYangle = (math.atan2(ACCz, ACCx) + M_PI) * RAD_TO_DEG
        if AccYangle > 90:
            AccYangle -= 270
        else:
            AccYangle += 90

        CFangleX = AA * (CFangleX + rate_gyr_x * LP) + (1 - AA) * AccXangle
        CFangleY = AA * (CFangleY + rate_gyr_y * LP) + (1 - AA) * AccYangle

        kalmanY = kalmanFilterY(AccYangle, rate_gyr_y, LP)
        kalmanX = kalmanFilterX(AccXangle, rate_gyr_x, LP)

        heading = 180 * math.atan2(MAGy, MAGx) / M_PI
        if heading < 0:
            heading += 360

        accXnorm = ACCx / math.sqrt(ACCx ** 2 + ACCy ** 2 + ACCz ** 2)
        accYnorm = ACCy / math.sqrt(ACCx ** 2 + ACCy ** 2 + ACCz ** 2)
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm / math.cos(pitch))

        if IMU.BerryIMUversion in [1, 3]:
            magXcomp = MAGx * math.cos(pitch) + MAGz * math.sin(pitch)
            magYcomp = MAGx * math.sin(roll) * math.sin(pitch) + MAGy * math.cos(roll) - MAGz * math.sin(roll) * math.cos(pitch)
        else:
            magXcomp = MAGx * math.cos(pitch) - MAGz * math.sin(pitch)
            magYcomp = MAGx * math.sin(roll) * math.sin(pitch) + MAGy * math.cos(roll) + MAGz * math.sin(roll) * math.cos(pitch)

        tiltCompensatedHeading = 180 * math.atan2(magYcomp, magXcomp) / M_PI
        if tiltCompensatedHeading < 0:
            tiltCompensatedHeading += 360

        writer.writerow([
            now,
            ACCx, ACCy, ACCz,
            GYRx, GYRy, GYRz,
            MAGx, MAGy, MAGz,
            AccXangle, AccYangle,
            gyroXangle, gyroYangle, gyroZangle,
            CFangleX, CFangleY,
            kalmanX, kalmanY,
            heading, tiltCompensatedHeading,
            # pressure, temperature
        ])
        f.flush()
        time.sleep(0.03)

except KeyboardInterrupt:
    print("Recording stopped by user.")

finally:
    f.close()
    print(f"Data saved to: {csv_file}")
