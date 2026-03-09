from flask import Flask, render_template, jsonify, request
import board
import busio
import adafruit_bno055
import time
import os

app = Flask(__name__, template_folder='.')

# Set up the I2C and IMU sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

recording = False
recorded_data = []
start_time = None

@app.route("/")
def index():
    return render_template("softFish_index_visualize.html")

@app.route("/rpy")
def get_rpy():
    euler = sensor.euler  # (heading, roll, pitch)
    if None in euler:
        return jsonify({"roll": 0, "pitch": 0, "yaw": 0, "temperature": 0})

    roll, pitch, yaw = euler[1], euler[2], euler[0]
    temperature = sensor.temperature

    if recording:
        timestamp = time.time() - start_time
        recorded_data.append({
            "time": timestamp,
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw
        })

    return jsonify({
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "temperature": temperature
    })

@app.route("/start_recording", methods=["POST"])
def start_recording():
    global recording, recorded_data, start_time
    recorded_data = []
    recording = True
    start_time = time.time()
    return "", 204

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    global recording
    recording = False
    return "", 204

if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True, host='0.0.0.0')
