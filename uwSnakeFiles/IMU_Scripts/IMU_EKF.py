import sys, time, math, datetime, os, csv, threading, termios, tty, signal

# === Add path to IMU drivers ===
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-pressure-sensor-BMP280-BMP388"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-BerryIMU-gyro-accel-compass-filters"))

import IMU
from bmp388 import BMP388
from ahrs.filters import EKF
from ahrs.common.orientation import q2euler
import numpy as np

# === Setup for raw key reading (non-blocking) ===
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# === Cleanup handler ===
def handle_exit(signum, frame):
    global recording, f
    print("\n[INFO] Terminating...")
    if recording:
        recording = False
        if f:
            f.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# === Main Setup ===
print("Press 's' to START recording, 'e' to END recording, and 'q' to QUIT.")

IMU.detectIMU()
if IMU.BerryIMUversion == 99:
    print("No BerryIMU found")
    sys.exit()
IMU.initIMU()
baro = BMP388()
ekf = EKF()
q = np.array([1.0, 0.0, 0.0, 0.0])

recording = False
f = None
writer = None

a = datetime.datetime.now()

try:
    import select
    while True:
        # Non-blocking key read
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if dr:
            ch = get_key()
            if ch.lower() == 's' and not recording:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                folder = os.path.expanduser("~/Desktop/IMU_Data")
                os.makedirs(folder, exist_ok=True)
                csv_file = os.path.join(folder, f"imu_log_{timestamp}.csv")
                f = open(csv_file, "w", newline="")
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "ACCx", "ACCy", "ACCz", "GYRx", "GYRy", "GYRz",
                    "MAGx", "MAGy", "MAGz", "AccXangle", "AccYangle",
                    "gyroXangle", "gyroYangle", "gyroZangle", "CFangleX", "CFangleY",
                    "kalmanX", "kalmanY", "heading", "tiltCompensatedHeading",
                    "temperature", "pressure", "altitude", "EKF_roll", "EKF_pitch", "EKF_yaw"
                ])
                recording = True
                print("[INFO] Started recording...")

            elif ch.lower() == 'e' and recording:
                recording = False
                if f:
                    f.close()
                    f = None
                    writer = None
                print("[INFO] Stopped recording.")

            elif ch.lower() == 'q':
                print("[INFO] Exiting...")
                if recording and f:
                    f.close()
                break

        # Read sensors
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

        rate_gyr_x = GYRx * 0.070
        rate_gyr_y = GYRy * 0.070
        rate_gyr_z = GYRz * 0.070

        AccXangle = math.atan2(ACCy, ACCz) * 57.29578
        AccYangle = (math.atan2(ACCz, ACCx) + math.pi) * 57.29578
        if AccYangle > 90: AccYangle -= 270
        else: AccYangle += 90

        heading = 180 * math.atan2(MAGy, MAGx) / math.pi
        if heading < 0: heading += 360

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

        tiltCompensatedHeading = 180 * math.atan2(magYcomp, magXcomp) / math.pi
        if tiltCompensatedHeading < 0: tiltCompensatedHeading += 360

        temperature, pressure, altitude = baro.get_temperature_and_pressure_and_altitude()
        acc = np.array([ACCx, ACCy, ACCz], dtype=float)
        gyr = np.radians(np.array([GYRx, GYRy, GYRz], dtype=float))
        mag = np.array([MAGx, MAGy, MAGz], dtype=float)
        q = ekf.update(q, gyr=gyr, acc=acc, mag=mag)
        rpy = np.degrees(q2euler(q))

        if recording and writer is not None:
            writer.writerow([
                now, ACCx, ACCy, ACCz, GYRx, GYRy, GYRz,
                MAGx, MAGy, MAGz, AccXangle, AccYangle,
                rate_gyr_x * LP, rate_gyr_y * LP, rate_gyr_z * LP,
                0, 0, 0, 0, heading, tiltCompensatedHeading,
                temperature / 100.0, pressure / 100.0, altitude / 100.0,
                rpy[0], rpy[1], rpy[2]
            ])
            f.flush()

        time.sleep(0.03)

except KeyboardInterrupt:
    print("\nInterrupted by user. Exiting...")
    if f: f.close()
