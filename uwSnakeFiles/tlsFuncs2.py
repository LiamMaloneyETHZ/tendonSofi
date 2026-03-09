import time, os, sys, configparser
from dxlSetup.DxlServoBase import DxlServoBase
from dxlSetup.XC330 import XC330
from dxlSetup.XL430 import XL430
from dxlSetup.portAndPackets import closePortObject
from typing import List

defaultSpeed = 200

def readKey():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode()
    else:
        import tty, termios
        return sys.stdin.read(1)

def pauseAndPrint(timePaused):
    for _ in range(timePaused):
        print(f"Sleeping for {timePaused - _} seconds...")
        time.sleep(1)  # Pause for 1 second

def readPositions(*servos:DxlServoBase):
    for servo in servos:
        print(f"Servo ID: {servo.dxlID}, Present Position: {servo.readPos()}")

def moveSyringe(*servos:XC330,extensionPercent=0):
    servo_moving = {servo: True for servo in servos}
    servo_overload = {servo: False for servo in servos}
    for servo in servos:
        servo.torqueEnable()
        desiredPos = servo.zeroPos + round(servo.actuationDistance*extensionPercent/100)
        if servo.zeroPos <= desiredPos <= servo.zeroPos+servo.actuationDistance:
            servo.move(desiredPos, defaultSpeed)
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
    currentPos = desiredPos
    return extensionPercent

def waitForInput(*servos:XC330):
    print("Press 'e' to exit, 'f' for failure, or any other key to continue")
    key = readKey()
    if key == 'e':
        moveSyringe(*servos,0)
        closePortObject()
        sys.exit()
    elif key == 'f':
        closePortObject()
        sys.exit()
    return

def keyController(frontHalf:XC330, backHalf:XC330):
    allSyringes = *frontHalf,*backHalf
    counter = 0
    actPerc = int(input("Enter actuation percentage (0-100): "))
    endingFlag = False
    print("\nPress 'i'/'k' for full body dive, 'q'/'a' for head pitch, 'w'/'s' for tail pitch, 'd' to change actuation percentage, "
          "'c' to continue with no action, 'e' to exit, 'f' for failure, 'p' to print positions, or 'r' to reboot.\n")
    while not endingFlag:
        key = readKey()
        counter += 1
        if key == 'q':
            print(f"{counter}. Head pitch button 'q' pressed\n")
            moveSyringe(*frontHalf, extensionPercent=actPerc)
        elif key == 'a':
            print(f"{counter}. Head pitch reset button 'a' pressed\n")
            moveSyringe(*frontHalf)
        elif key == 'w':
            print(f"{counter}. Tail pitch button 'w' pressed\n")
            moveSyringe(*backHalf, extensionPercent=actPerc)
        elif key == 's':
            print(f"{counter}. Tail pitch reset button 's' pressed\n")
            moveSyringe(*backHalf)
        elif key == 'i':
            print(f"{counter}. Full body dive button 'i' pressed\n")
            moveSyringe(*allSyringes, extensionPercent=actPerc)
        elif key == 'k':
            print(f"{counter}. Full body dive reset button 'k' pressed\n")
            moveSyringe(*allSyringes)
        elif key == 'c':
            print(f"{counter}. Continue button 'c' pressed\n")
            endingFlag = True
        elif key == 'd':
            print(f"{counter}. Actuation percentage change button 'd' pressed\n")
            actPerc = int(input("Enter actuation percentage (0-100): \n"))  # Re-enter actuation percentage
        elif key == 'e':
            print(f"{counter}. Exit button 'e' pressed\n")
            moveSyringe(*allSyringes)
            closePortObject()
            sys.exit()
        elif key == 'f':
            print(f"{counter}. Failure button 'f' pressed\n")
            closePortObject()
            sys.exit()
        elif key == 'p':
            print("Printing present positions:")
            readPositions(*allSyringes)
            print("\n")
        '''elif key == 'r':
            print("Enter the motor index to reboot")
            index = int(input)-1
            print(index)
        elif key == 'm':
            print("Enter the motor index to move")
            index = int(input)-1
            servo = allSyringes[index]
            print("Enter the motor position to move to")
            goalPos = int(input)
            servo.goalPos = goalPos
            servo.move(servo.goalPos,defaultSpeed)'''

def jointCalibrator(*bodyServos:XL430):
    for servo in bodyServos:
        servo.readPos()
    endFlag = False
    userInput = int(input("Enter Which Joint to Edit! (1 = head, 2 = middle, 3 = tail): \n"))
    if userInput == 1:
        leftServo = bodyServos[0]
        rightServo = bodyServos[1]
    elif userInput == 2:
        leftServo = bodyServos[2]
        rightServo = bodyServos[3]
    elif userInput == 3:
        leftServo = bodyServos[4]
        rightServo = bodyServos[5]
    elif userInput == 4:
        leftServo = bodyServos[6]
        rightServo = bodyServos[7]
    elif userInput == 5:
        leftServo = bodyServos[8]
        rightServo = bodyServos[9]
    incr = int(input("Enter movement increment: "))
    print("Press 'j' to change joint, 'i' to change increment, 'q' to tighten left cable, 'a' to loosen left cable, "
          "'w' to tighten right cable, 's' to loosen right cable, 'e' to exit and print new zeros, or 'f' to exit w/ torque disable,"
          "'o' to exit with reboot and overwrite zeros config")
    while not endFlag:
        key = readKey()
        if key == 'j':
            userInput = int(input("\nEnter Which Joint to Edit! (1 = head, 2 = middle, 3 = tail): \n"))
            if userInput == 1:
                leftServo = bodyServos[0]
                rightServo = bodyServos[1]
            elif userInput == 2:
                leftServo = bodyServos[2]
                rightServo = bodyServos[3]
            elif userInput == 3:
                leftServo = bodyServos[4]
                rightServo = bodyServos[5]
            elif userInput == 4:
                leftServo = bodyServos[6]
                rightServo = bodyServos[7]
            elif userInput == 5:
                leftServo = bodyServos[8]
                rightServo = bodyServos[9]
        elif key == 'i':
            incr = int(input("\nChange movement increment: "))
        elif key == 'q':
            print(f"\nTightening left cable by {incr}")
            leftServo.goalPos = leftServo.presPos + incr
            leftServo.moveAndWait(leftServo.goalPos,defaultSpeed)
            print(f"Servo {leftServo.dxlID} moved to {leftServo.readPos()}")
        elif key == 'w':
            print(f"\nTightening right cable by {incr}")
            rightServo.goalPos = rightServo.presPos + incr
            rightServo.moveAndWait(rightServo.goalPos,defaultSpeed)
            print(f"Servo {rightServo.dxlID} moved to {rightServo.readPos()}")
        elif key == 'a':
            print(f"\nLoosening left cable by {incr}")
            leftServo.goalPos = leftServo.presPos - incr
            leftServo.moveAndWait(leftServo.goalPos,defaultSpeed)
            print(f"Servo {leftServo.dxlID} moved to {leftServo.readPos()}")
        elif key == 's':
            print(f"\nLoosening right cable by {incr}")
            rightServo.goalPos = rightServo.presPos - incr
            rightServo.moveAndWait(rightServo.goalPos,defaultSpeed)
            print(f"Servo {rightServo.dxlID} moved to {rightServo.readPos()}")
        elif key == 'e':
            print("Exiting Program!\n")
            for servo in bodyServos:
                servo.clearMultiTurn()
                time.sleep(0.5)
                servo.zeroPos = servo.readPos()
                print(f"Servo {servo.dxlID} new zero = {servo.zeroPos}")
            endFlag = True
        elif key == 'f':
            print("Exiting program with reboot!\n")
            for servo in bodyServos:
                servo.reboot()
                time.sleep(0.5)
                servo.zeroPos = servo.readPos()
                print(f"Servo {servo.dxlID} new zero = {servo.zeroPos}")
            endFlag = True
        elif key == 'o':
            print("Overwriting Motor Zeros! Remember to git push!\n")
            for servo in bodyServos:
                servo.reboot()
                time.sleep(0.5)
                servo.zeroPos = servo.readPos()
                print(f"Servo {servo.dxlID} new zero = {servo.zeroPos}")
            # Write updated zero positions to the config file
            from dxlControlPath import motorZeroConfig
            config,config_path = motorZeroConfig()
            config['XL430']['bS1'] = str(bodyServos[0].zeroPos)
            config['XL430']['bS2'] = str(bodyServos[1].zeroPos)
            config['XL430']['bS3'] = str(bodyServos[2].zeroPos)
            config['XL430']['bS4'] = str(bodyServos[3].zeroPos)
            config['XL430']['bS5'] = str(bodyServos[4].zeroPos)
            config['XL430']['bS6'] = str(bodyServos[5].zeroPos)
            with open(config_path, 'w') as configfile:
                config.write(configfile)
            endFlag = True

def extendPos(syrArr: List[XC330]):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos+servo.actuationDistance

def retractPos(syrArr: List[XC330]):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos

def percentMove(syrArr: List[XC330],extensionPercent):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos + round(servo.actuationDistance*extensionPercent/100)

def syringeTimeSeq(syrArr: List[XC330], counter):
    if counter%2 == 0:
        extendPos(syrArr)
        print("Extending Syringes!")
    elif counter%2 == 1: 
        retractPos(syrArr)
        print("Retracting Syringes!")

def moveSyringeList(servos: List[XC330],extensionPercent=0):
    servo_moving = {servo: True for servo in servos}
    servo_overload = {servo: False for servo in servos}
    for servo in servos:
        servo.torqueEnable()
        desiredPos = servo.zeroPos + round(servo.actuationDistance*extensionPercent/100)
        if servo.zeroPos <= desiredPos <= servo.zeroPos+servo.actuationDistance:
            servo.move(desiredPos, defaultSpeed)
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
    currentPos = desiredPos
    return extensionPercent

def slowSyringeSeq(syrArr: List[XC330], counter):
    extPer = 100
    if counter == 0:
        moveSyringeList(syrArr,extPer)
    elif counter >= 1 and counter <= 10:
        newPos = extPer-counter*10
        moveSyringeList(syrArr,newPos)
        print(newPos)
    elif counter > 10 and counter <= 20:
        newPos = (counter-10)*10
        moveSyringeList(syrArr,newPos)
        print(newPos)

def newSyringeSeq(syrArr: List[XC330], counter):
    extPer = 100
    if counter == 0:
        percentMove(syrArr,extPer)
    elif counter >= 1 and counter <= 10:
        newPos = extPer-counter*10
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter > 10 and counter <= 20:
        newPos = (counter-10)*10
        percentMove(syrArr,newPos)
        print(newPos)

def syrPullback(syrArr: List[XC330], counter):
    extPer = 100
    if counter == 0:
        percentMove(syrArr,extPer)
    elif counter == 1:
        newPos = 60
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 3:
        newPos = 100
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 4:
        newPos = 80
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 5:
        newPos = 60
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 6:
        newPos = 70
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 9:
        newPos = 80
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 10:
        newPos = 0
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 12:
        newPos = 100
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 13:
        newPos = 70
        percentMove(syrArr,newPos)
        print(newPos)
    elif counter == 14:
        newPos = 100
        percentMove(syrArr,newPos)
        print(newPos)

def turningSeq(counter):
    counter = counter%6+1
    if counter == 2:
        turningFlag = True
        return turningFlag
    elif counter == 6:
        turningFlag = False
        return turningFlag
    