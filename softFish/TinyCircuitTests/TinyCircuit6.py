import serial
import time

#Test to make sure the tinycircuits are properly outputing to the rpi IDE, via radio messages with one another 
# Update this to your actual serial port connected to the Arduino Receiver
SERIAL_PORT = '/dev/ttyACM0'  # Common for USB serial adapters
BAUD_RATE = 115200

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
        time.sleep(2)  # Wait for Arduino to reset after serial open

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("Received from Arduino Receiver:", line)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
