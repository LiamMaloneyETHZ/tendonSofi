import time, numpy as np
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430

## Servo Setup ##
openPortObject()
servo = XL430(id=1,zeroPos=0)
servo.setOpMode(16) # Velocity Control mode
servo.torqueEnable()

## Trial Adjustable Parameters ##
desiredFreq = 2 #Hz or rev/s, max of 4.84335
## Trial Constants ##
gearRatio = 5.4
velScale = 0.229
maxFreq = 4.84335
maxPWM = 885
goalPWM = int(round(desiredFreq/maxFreq*maxPWM))
runFlag = True
try:
    servo.pwmMove(goalPWM)
    while (runFlag):
        time.sleep(0.1)

except KeyboardInterrupt:
    servo.velMove(0)
    runFlag = False
    pass

## Clean up ##
time.sleep(1)
servo.torqueDisable()
closePortObject()