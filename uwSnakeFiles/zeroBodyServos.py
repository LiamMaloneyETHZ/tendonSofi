from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from tlsFuncs2 import *
from gaitFuncs import *

###### INITIALIZATIONS #######
openPortObject()
config,_ = motorZeroConfig('new_motor_zeros.ini')


flipped_bodyServos = tuple(XL430(id=i, zeroPos=int(config['XL430'][f'bS{i}'])) for i in range(1,11))
bodyServos = flipped_bodyServos[::-1]
bodyServosList = list(bodyServos)
bodyGroupReadPos, bodyGroupReadLoad, bodyGroupWrite = initializeSyncs(bodyServos[0])
groupReadSetup(bodyGroupReadPos,*bodyServos)
groupReadSetup(bodyGroupReadLoad,*bodyServos)

input("Press any key to zero body servos!")
torqueEnable(*bodyServos)    
zeroBodyServos(bodyGroupWrite,*bodyServos)

closePortObject()