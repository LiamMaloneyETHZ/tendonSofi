#This is the full integration between the Arduino IDE, Raspberry Pi, Dynamixel, and the two Tiny-Zeros. One Tiny-zero is plugged into
#the computer and runs the Arduino_... script, while the other Tiny-zero is plugged into the RPI and runs the RPI_... script.
#the Dynamixel is plugged into a power source and as well as into the RPI.

import serial
import time

from dxlControlPath import relativeDirUp
relativeDirUp(levels=3)

from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject, closePortObject

# === Setup Dynamixel Port ===
openPortObject()
servo = XC330(id=11, zeroPos=0, shortBool=True)
servo.torqueEnable()

# === Parameters ===
target=45000
velocity = 150

#Makes it so, that when the key w is typed on the arduino IDE, it shoudl recognize, then turn on the dynamixel 
#Test to make sure the tinycircuits are properly outputing to the rpi IDE, via radio messages with one another 
# Update this to your actual serial port connected to the Arduino Receiver
SERIAL_PORT = '/dev/ttyACM0'  # Common for USB serial adapters
BAUD_RATE = 115200

def main():

    print("Starting oscillating motion and IMU sync...")
    start_time = time.time()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
        time.sleep(2)  # Wait for Arduino to reset after serial open

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if line:
                print("Received from Arduino Receiver:", line)
                print(line)
                if "w" in line.lower():
                    #this line isn't running
                    print(f"Moving to {target}...")
                    servo.moveAndWait(target, velocity)  # Initiate motion

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Returning to start position...")
        servo.moveAndWait(0, velocity)
        servo.torqueDisable()

        closePortObject()
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()
