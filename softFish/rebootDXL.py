from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.XL430 import XL430
openPortObject()
servo = XL430(id=1,zeroPos=0)
servo.reboot()
closePortObject()
