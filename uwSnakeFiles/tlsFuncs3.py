import time, os, sys, configparser
from dxlSetup.DxlServoBase import DxlServoBase
from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import closePortObject
from typing import List
from tlsFuncs2 import readKey
from dxlSetup.XL430 import XL430

defaultSpeed = 200

def extendSyr(syrArr: List[XC330]):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos

def retractSyr(syrArr: List[XC330]):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos+servo.newActDist

def percentRetraction(syrArr: List[XC330],retractionPercent):
    for servo in syrArr:
        servo.torqueEnable()
        servo.goalPos = servo.zeroPos + round(servo.newActDist*retractionPercent/100)

def syringeController(syrArr: List[XC330], counter, syrMode, retractPer = 100):
    if syrMode == 1:  ## alternating timer mode
        if counter%2 == 0:
            extendSyr(syrArr)
            print("Extending Syringes!")
        elif counter%2 == 1: 
            retractSyr(syrArr)
            print("Retracting Syringes!")
    if syrMode == 2: ## alternating timer mode with user input retraction percentage
        if counter%2 == 0:
            extendSyr(syrArr)
            print("Extending Syringes!")
        elif counter%2 == 1: 
            percentRetraction(syrArr,retractPer)
            print("Retracting Syringes!")
    if syrMode == 3: ## custom sequence with percent retractions
        if counter == 0:
            extendSyr(syrArr)
        elif counter == 1:
            newPos = 80
            percentRetraction(syrArr,newPos)
        elif counter == 5:
            newPos = 0
            percentRetraction(syrArr,newPos)
        elif counter == 10:
            newPos = 40
            percentRetraction(syrArr,newPos)
        elif counter == 11:
            newPos = 80
            percentRetraction(syrArr,newPos)
        elif counter == 14:
            newPos = 80
            percentRetraction(syrArr,newPos)

def jointCalibrator2(*bodyServos:XL430):
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
    print("Press 'j' to change joint, 'i' to change increment, 'q' to tighten left cable, 'a' to loosen left cable, "
          "'w' to tighten right cable, 's' to loosen right cable, 'e' to exit and print new zeros, or 'f' to exit w/ torque disable,"
          "'o' to exit with reboot and overwrite zeros config")
    while not endFlag:
        key = readKey()
        if key == 'j':
            userInput = int(input("\nEnter Which Joint to Edit! (1-5): \n"))
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
        elif key == 'q':
            goalPos = int(input("\nEnter left cable goal position: \n"))
            leftServo.move(goalPos,defaultSpeed)
        elif key == 'w':
            goalPos = int(input("\nEnter right cable goal position: (1-5): \n"))
            rightServo.move(goalPos,defaultSpeed)
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