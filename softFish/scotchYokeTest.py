from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.XC330 import XC330
from dxlSetup.portAndPackets import openPortObject,closePortObject
import time

openPortObject()

velo=400 
#setmotor zero in code, no config
servo1 = XC330(id=11, zeroPos=0, shortBool=True)
servo1.torqueEnable()

servo1.readPos()
print(f'Starting Pos = {servo1.presPos}')

servo1.moveAndWait(4000,velo)
servo1.moveAndWait(0, velo)

servo1.torqueDisable()
closePortObject()

#figure out how to read IMU in scotch yoke 