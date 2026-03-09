import time, numpy as np
from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430

## Servo Setup ##
openPortObject()
servo = XL430(id=1,zeroPos=0)
servo.setOpMode(1) # Velocity Control mode
servo.torqueEnable()

## Trial Adjustable Parameters ##
desiredFreq = 2 #Hz or rev/s, max of 4.84335

## Trial Constants ##
gearRatio = 5.4
velScale = 0.229
goalVel = int(round(desiredFreq/(gearRatio*velScale)*60))
runFlag = True
try:
    servo.velMove(goalVel)
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