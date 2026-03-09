#!/usr/bin/env python3
import serial
import time

#way for rpi to communicate with arduino 
#could obviously make sure to change the information. Could relate this to the IMU 
#code from https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()

    while True:
        #could figure out how to write 
        ser.write(b"Hello from Raspberry Pi!\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)