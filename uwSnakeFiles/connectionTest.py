from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from dxlSetup.XC330 import XC330
import time
from gaitFuncs import *
openPortObject()
config,_ = motorZeroConfig('new_motor_zeros.ini')

# Body Servo Initialization
flipped_bodyServos = tuple(XL430(id=i, zeroPos=int(config['XL430'][f'bS{i}'])) for i in range(1,11))
bodyServos = flipped_bodyServos[::-1]
bodyServosList = list(bodyServos)
bodyGroupReadPos, bodyGroupReadLoad, bodyGroupWrite = initializeSyncs(bodyServos[0])
groupReadSetup(bodyGroupReadPos,*bodyServos)
groupReadSetup(bodyGroupReadLoad,*bodyServos)

torqueEnable(*bodyServos)    

try:
    while True:
        readGroupPos(bodyGroupReadPos, *bodyServos)
        readGroupLoad(bodyGroupReadLoad, *bodyServos)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

time.sleep(1)
closePortObject()