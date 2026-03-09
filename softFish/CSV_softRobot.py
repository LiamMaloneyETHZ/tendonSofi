import csv

# Open CSV file for writing
with open("imu_data.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Temperature", "Accel_X", "Accel_Y", "Accel_Z", "Mag_X", "Mag_Y", "Mag_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Euler_X", "Euler_Y", "Euler_Z"])

    while True:
        timestamp = time.time()
        writer.writerow([
            timestamp,
            sensor.temperature, 
            sensor.acceleration[0], sensor.acceleration[1], sensor.acceleration[2],
            sensor.magnetic[0], sensor.magnetic[1], sensor.magnetic[2],
            sensor.gyro[0], sensor.gyro[1], sensor.gyro[2],
            sensor.euler[0], sensor.euler[1], sensor.euler[2]
        ])
        print(f"Logged Data at {timestamp:.2f}s")
        time.sleep(0.1)  # Delay for stable logging
