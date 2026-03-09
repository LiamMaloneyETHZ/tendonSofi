from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
from dxlSetup.portAndPackets import openPortObject,closePortObject
import time

config,_ = motorZeroConfig('new_motor_zeros.ini')
openPortObject()

tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']), shortBool=True)
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']))
tls5 = XC330(id=15, zeroPos=int(config['XC330']['tls5']))
tls6 = XC330(id=16, zeroPos=int(config['XC330']['tls6']), shortBool=True)
tlsList = [tls1, tls2, tls3, tls4, tls5, tls6]

i = 1
for tls in tlsList:
    print(f"tls{i} current position is: {tls.readPos()}\n")
    i += 1

syringeNum = int(input("\nPick syringe (1-6): "))-1

print(tlsList[syringeNum].readPos())

rebootVal = int(input("\nReboot? 0 or 1: "))
if rebootVal == 1:
    tlsList[syringeNum].reboot()
    time.sleep(.5)
    print(tlsList[syringeNum].readPos())

retractVal = int(input("\nAttempt Retract? 0 or 1: "))
if retractVal == 1:
    print(tlsList[syringeNum].readPos())
    tlsList[syringeNum].torqueEnable()
    tlsList[syringeNum].move(tlsList[syringeNum].presPos-tlsList[syringeNum].newActDist,defaultSpeed)
    time.sleep(5)
    print(tlsList[syringeNum].readPos())
    tlsList[syringeNum].torqueDisable


extendVal = int(input("\nAttempt Extend? 0 or 1: "))
if extendVal == 1:
    print(tlsList[syringeNum].readPos())
    tlsList[syringeNum].torqueEnable()
    tlsList[syringeNum].move(tlsList[syringeNum].presPos+tlsList[syringeNum].newActDist,defaultSpeed)
    time.sleep(5)
    print(tlsList[syringeNum].readPos())
    tlsList[syringeNum].torqueDisable

jogVal = int(input("\nAttempt backwards jog mode? 0 or 1: "))
if jogVal == 1:
    jogBool = True
    tlsList[syringeNum].torqueEnable()
    while jogBool:
        keepJogging = int(input("\nKeep Jogging? 0 or 1: "))
        if keepJogging == 1:
            print(tlsList[syringeNum].readPos())
            tlsList[syringeNum].move(tlsList[syringeNum].presPos-200,defaultSpeed)
        elif keepJogging == 0:
            print(tlsList[syringeNum].readPos())
            tlsList[syringeNum].torqueDisable
            jogBool = False
jogVal = int(input("\nAttempt forward jog mode? 0 or 1: "))
if jogVal == 1:
    jogBool = True
    tlsList[syringeNum].torqueEnable()
    while jogBool:
        keepJogging = int(input("\nKeep Jogging? 0 or 1: "))
        if keepJogging == 1:
            print(tlsList[syringeNum].readPos())
            tlsList[syringeNum].move(tlsList[syringeNum].presPos+200,defaultSpeed)
        elif keepJogging == 0:
            print(tlsList[syringeNum].readPos())
            tlsList[syringeNum].torqueDisable
            jogBool = False
closePortObject()