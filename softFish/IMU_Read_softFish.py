# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_bno055

# Initialize I2C communication
i2c = board.I2C()  # Uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bno055.BNO055_I2C(i2c)

# If you are going to use UART, uncomment these lines:
# uart = board.UART()
# sensor = adafruit_bno055.BNO055_UART(uart)

last_val = 0xFFFF

def temperature():
    #"""Retrieve and filter temperature data from the sensor."""
    global last_val  # noqa: PLW0603
    result = sensor.temperature

    if abs(result - last_val) == 128:
        result = sensor.temperature

    if abs(result - last_val) == 128:
        return 0b00111111 & result

    last_val = result
    return result

# Print table header (only once)
print("="*100)
print(f"{'Temperature (°C)':<15}{'Accel (m/s^2)':<25}{'Magnet (µT)':<25}{'Gyro (rad/sec)':<25}{'Euler Angles':<25}")
print("="*100)

# Main loop: continuously print sensor data as rows
while True:
    print("{:<15.3f} {:<25} {:<25} {:<25} {:<25}".format(
        sensor.temperature, 
        f"({sensor.acceleration[0]:.3f}, {sensor.acceleration[1]:.3f}, {sensor.acceleration[2]:.3f})",
        f"({sensor.magnetic[0]:.3f}, {sensor.magnetic[1]:.3f}, {sensor.magnetic[2]:.3f})",
        f"({sensor.gyro[0]:.3f}, {sensor.gyro[1]:.3f}, {sensor.gyro[2]:.3f})",
        f"({sensor.euler[0]:.3f}, {sensor.euler[1]:.3f}, {sensor.euler[2]:.3f})"
    ))
    time.sleep(0.1)  # Delay to prevent excessive printing
#am I going out without the keyboard escape?