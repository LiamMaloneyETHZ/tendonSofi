#!/usr/bin/env python3
import serial
import time

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # Give Arduino time to reset and start sending

    print("Listening for Arduino messages...\n")
    
    while True:
        try:
            line = ser.readline().decode('utf-8').rstrip()
            if line:
                print(line)
        except serial.SerialException as e:
            print(f"[Serial Error] {e}")
            break
        time.sleep(0.05)  # Reduce CPU usage slightly
except serial.SerialException as conn_error:
    print(f"[Connection Error] Could not open serial port: {conn_error}")
