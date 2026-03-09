from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
# from tokenize import Double
from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.XL430 import XL430


openPortObject()


##Create dynamixel objects
A1 = XL430(id = 2,zeroPos = 0)
B1 = XL430(id = 3,zeroPos = 0)
A2 = XL430(id = 5,zeroPos = 0)
B2 = XL430(id = 6,zeroPos = 0)
A3 = XL430(id = 8,zeroPos = 0)
B3 = XL430(id = 9,zeroPos = 0)
A4 = XL430(id = 11,zeroPos = 0)
B4 = XL430(id = 12,zeroPos = 0)
S1 = XC330(id = 1,zeroPos = 0)
S2 = XC330(id = 4,zeroPos = 0)
S3 = XC330(id = 7,zeroPos = 0)
S4 = XC330(id = 10,zeroPos = 0)

def angleChange(servo:XL430,angle):
    print('stuff')
    servo.move(int(4095/360*angle)+ servo.readPos(),200)

def angleChange2(servo:XC330,angle,speed):
    print('stuff')
    servo.move(int(4095/360*angle)+ servo.readPos(),speed)


angleChange2(S1, 45,150)
angleChange2(S2, 45,150)
angleChange2(S3, 45,150)
angleChange2(S4, 45,150)
closePortObject()
