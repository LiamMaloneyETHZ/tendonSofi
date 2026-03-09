from dxlControlPath import relativeDir, motorZeroConfig
relativeDir('../')
from dxlSetup.XL430 import XL430
from tlsFuncs2 import *
from dxlSetup.portAndPackets import openPortObject,closePortObject
from gaitFuncs import torqueEnable
config,_ = motorZeroConfig('new_motor_zeros.ini')
openPortObject()

bodyServo1 = XL430(id=1, zeroPos=int(config['XL430']['bS1']))
bodyServo2 = XL430(id=2, zeroPos=int(config['XL430']['bS2']))
bodyServo3 = XL430(id=3, zeroPos=int(config['XL430']['bS3']))
bodyServo4 = XL430(id=4, zeroPos=int(config['XL430']['bS4']))
bodyServo5 = XL430(id=5, zeroPos=int(config['XL430']['bS5']))
bodyServo6 = XL430(id=6, zeroPos=int(config['XL430']['bS6']))
bodyServo7 = XL430(id=7, zeroPos=int(config['XL430']['bS7']))
bodyServo8 = XL430(id=8, zeroPos=int(config['XL430']['bS8']))
bodyServo9 = XL430(id=9, zeroPos=int(config['XL430']['bS9']))
bodyServo10 = XL430(id=10, zeroPos=int(config['XL430']['bS10']))
bodyServos = bodyServo1,bodyServo2,bodyServo3,bodyServo4,bodyServo5,bodyServo6,bodyServo7,bodyServo8,bodyServo9,bodyServo10

torqueEnable(*bodyServos)    
jointCalibrator(*bodyServos)

closePortObject()