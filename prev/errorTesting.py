import DxlServoBase
from XC330 import XC330
from HardwareErrorChecker import HardwareErrorChecker
import tlsFuncs2
servo1 = XC330(id=1,zeroPos=0)

# Create the hardware error checker object
error_checker = HardwareErrorChecker(servo1)

# Start checking hardware errors in a separate thread
error_checker.startErrorChecking()
servo1.move(3000,200)
tlsFuncs2.waitForInput()
#tlsFuncs2.pauseAndPrint(5)
servo1.move(0,200)
tlsFuncs2.waitForInput()

tlsFuncs2.pauseAndPrint(5)

error_checker.stopErrorChecking()
DxlServoBase.closePort()
