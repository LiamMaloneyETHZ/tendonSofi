import sys
import DxlServoBase
from XC330 import XC330
import tlsFuncs2
##Create dynamixel objects
headLS = XC330(id=3,zeroPos=100)
tailLS = XC330(id=4,zeroPos=100)
servos = headLS,tailLS

print("extending before water entry")
tlsFuncs2.extend(*servos)
tlsFuncs2.waitForInput(*servos)

#sink
print("uniform sink")
tlsFuncs2.retract(*servos)
tlsFuncs2.waitForInput(*servos)

#head bob
print("raising head")
tlsFuncs2.extend(headLS)
tlsFuncs2.waitForInput(*servos)

#full float
print("raising both")
tlsFuncs2.extend(*servos)
tlsFuncs2.waitForInput(*servos)

# tlsFuncs2.pauseAndPrint(5)
# tlsFuncs2.extend(headLS)
# tlsFuncs2.pauseAndPrint(3)
# tlsFuncs2.extend(tailLS)
# tlsFuncs2.pauseAndPrint(3)

#end program
print("retracting to end program")
tlsFuncs2.retract(*servos)
DxlServoBase.closePort()