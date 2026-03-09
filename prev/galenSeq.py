import DxlServoBase
from XC330 import XC330
import tlsFuncs2
##Create dynamixel objects
headLS = XC330(id=1,zeroPos=100)
tailLS = XC330(id=4,zeroPos=100)

tlsFuncs2.extend(headLS)
tlsFuncs2.retract(headLS)

#   Uniform dive
print('Uniform Dive Start')
tlsFuncs2.retract(headLS,tailLS)
print('Uniform Dive End')
tlsFuncs2.pauseAndPrint(5)

#   Uniform rise
print('Uniform Rise Start')
tlsFuncs2.extend(headLS,tailLS)
print('Uniform Rise End')
tlsFuncs2.pauseAndPrint(5)

#   Headfirst dive
print('Headfirst Dive Start')
tlsFuncs2.retract(headLS)
tlsFuncs2.pauseAndPrint(1)
tlsFuncs2.retract(tailLS)
print('Headfirst Dive End')
tlsFuncs2.pauseAndPrint(5)

#   Headfirst rise
print('Headfirst Rise Start')
tlsFuncs2.extend(headLS)
tlsFuncs2.pauseAndPrint(1)
tlsFuncs2.extend(tailLS)
print('Headfirst Rise End')
tlsFuncs2.pauseAndPrint(5)

#   Tailfirst dive
print('Tailfirst Dive Start')
tlsFuncs2.retract(tailLS)
tlsFuncs2.pauseAndPrint(1)
tlsFuncs2.retract(headLS)
print('Tailfirst Dive End')
tlsFuncs2.pauseAndPrint(5)

#   Tailfirst rise
print('Tailfirst Rise Start')
tlsFuncs2.extend(tailLS)
tlsFuncs2.pauseAndPrint(1)
tlsFuncs2.extend(headLS)
print('Tailfirst Rise End')
tlsFuncs2.pauseAndPrint(5)

tlsFuncs2.retract(headLS,tailLS)

DxlServoBase.closePort()
