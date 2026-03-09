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

syringeNum = int(input("\nPick syringe (1-6): "))-1

endFlag = False
print("Press 'i' to move to a specified position, 'j' to switch selected servo, 'r' to reboot, or 'f' to exit")
while not endFlag:
    key = readKey()
    if key == 'i':
        newPos = int(input("\nEnter new position: "))
        tlsList[syringeNum].torqueEnable()
        tlsList[syringeNum].move(newPos,defaultSpeed)
        time.sleep(5)
        tlsList[syringeNum].torqueDisable
    elif key == 'j': 
        syringeNum = int(input("\nSwitch Servo to (1-6): "))
    elif key == 'r':
        tlsList[syringeNum].reboot()
        time.sleep(.5)
    elif key == 'f':
        print("Exiting program!\n")
        endFlag = True

closePortObject()