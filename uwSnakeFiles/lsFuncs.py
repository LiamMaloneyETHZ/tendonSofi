from dxlSetup.XC330 import XC330
from typing import List
from tlsFuncs2 import *

motorSpeed = 400

def newListMove(servos: List[XC330],extensionPercent=0):
    servo_moving = {servo: True for servo in servos}
    servo_overload = {servo: False for servo in servos}
    for servo in servos:
        servo.torqueEnable()
        desiredPos = servo.zeroPos + round(servo.newActDist*extensionPercent/100)
        servo.move(desiredPos, motorSpeed)
    time.sleep(0.1)
    while any(servo_moving.values()):
        for servo in servos:
            if servo_moving[servo]:
                presVel = servo.readVel()
                if 0 <= abs(presVel) <= 1:
                    servo_moving[servo] = False
                    servo.torqueDisable()
            if not servo_overload[servo]:
                errorBool = servo.checkHardwareError()
                if errorBool:
                    servo_overload[servo] = True
        time.sleep(0.1) ##control loop rate
    if any(servo_overload.values()):
        print("Hardware Error! Press any key to quit program")
        readKey()
        sys.exit
    return extensionPercent
