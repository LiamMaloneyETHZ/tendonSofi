import serial
import time

port = '/dev/serial0'
baudrate = 115200
timeout = 1
ser = serial.Serial(port, baudrate, timeout=timeout)

def request_data():
    try:
        #Send a request to Arduino
        ser.write(b'R')
        time.sleep(0.5)

        #Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            return response
    except Exception as e:
        print(f"Error reading serial data: {e}")
    return None

def process_data(data):
    if data:
        print(f"Received: {data}")

def main():
    print("Starting data request loop...")
    while True:
        data = request_data()
        process_data(data)
        time.sleep(1.1)

if __name__ == "__main__":
    main()
