from flask import Flask, render_template, Response, request, jsonify
import threading, time, math, os, sys, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-pressure-sensor-BMP280-BMP388"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BerryIMU", "python-BerryIMU-gyro-accel-compass-filters"))
import IMU

app = Flask(__name__)

# === IMU Filter Constants ===
RAD_TO_DEG = 57.29578
G_GAIN = 0.070
AA = 0.90
M_PI = 3.14159265358979323846

# === State Variables ===
current_rpy = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
recording = False
recorded_data = []

# === Unwrap helpers ===
last_roll = 0.0
last_pitch = 0.0
last_yaw = 0.0

def unwrap_angle(new_angle, last_angle):
    delta = new_angle - last_angle
    if delta > 180:
        new_angle -= 360
    elif delta < -180:
        new_angle += 360
    return new_angle

def imu_loop():
    global current_rpy, recording, recorded_data
    global last_roll, last_pitch, last_yaw

    gyroXangle = gyroYangle = gyroZangle = 0.0
    CFangleX = CFangleY = 0.0

    IMU.detectIMU()
    if IMU.BerryIMUversion == 99:
        print("No BerryIMU found")
        return
    IMU.initIMU()

    a = datetime.datetime.now()

    while True:
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()

        b = datetime.datetime.now()
        LP = (b - a).total_seconds()
        a = b

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

        # === Small Tweak: Dynamic Complementary Filter weight ===
        tilt_magnitude = math.sqrt(AccXangle**2 + AccYangle**2)
        dynamic_aa = AA
        if tilt_magnitude > 75:
            dynamic_aa = 0.98
        elif tilt_magnitude > 60:
            dynamic_aa = 0.95

        CFangleX = dynamic_aa * (CFangleX + rate_gyr_x * LP) + (1 - dynamic_aa) * AccXangle
        CFangleY = dynamic_aa * (CFangleY + rate_gyr_y * LP) + (1 - dynamic_aa) * AccYangle

        # === Unwrap Roll, Pitch, Yaw ===
        roll = unwrap_angle(CFangleX, last_roll)
        pitch = unwrap_angle(CFangleY, last_pitch)
        yaw = unwrap_angle(gyroZangle, last_yaw)

        last_roll = roll
        last_pitch = pitch
        last_yaw = yaw

        current_rpy = {"roll": roll, "pitch": pitch, "yaw": yaw}

        if recording:
            recorded_data.append({
                "time": time.time(),
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw
            })

        time.sleep(0.03)  # ~30 Hz

@app.route('/')
def index():
    return render_template('index_visualize.html')

@app.route('/rpy')
def get_rpy():
    return jsonify(current_rpy)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, recorded_data
    recorded_data = []
    recording = True
    return '', 204

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording
    recording = False
    return jsonify(recorded_data)

if __name__ == '__main__':
    threading.Thread(target=imu_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, threaded=True)
