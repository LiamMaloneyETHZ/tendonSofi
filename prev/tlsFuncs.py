import dxlFuncs
import time
defaultSpeed = 200

#Disable torques to prevent overheating
def pauseAndPrint(timePaused):
    for _ in range(timePaused):
        print(f"Sleeping for {timePaused - _} seconds...")
        time.sleep(1)  # Pause for 1 second

def extend(*servos:dxlFuncs.dxlServo):
    servo_moving = {servo: True for servo in servos}
    for servo in servos:
        servo.torqueEnable()
        servo.move(servo.extendedPos, defaultSpeed)
    time.sleep(0.1)
    while any(servo_moving.values()):
        for servo in servos:
            if servo_moving[servo]:
                presVel = servo.readVel()
                if 0 <= abs(presVel) <= 1:
                    servo_moving[servo] = False
                    servo.torqueDisable()

def retract(*servos:dxlFuncs.dxlServo):
    servo_moving = {servo: True for servo in servos}
    for servo in servos:
        servo.torqueEnable()
        servo.move(servo.retractedPos, defaultSpeed)
    time.sleep(0.1)
    while any(servo_moving.values()):
        for servo in servos:
            if servo_moving[servo]:
                presVel = servo.readVel()
                if 0 <= abs(presVel) <= 1:
                    servo_moving[servo] = False
                    servo.torqueDisable()