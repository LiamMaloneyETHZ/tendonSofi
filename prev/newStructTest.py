from dxlSetup.portAndPackets import closePortObject
import time
from dxlSetup.XC330 import XC330

servo = XC330(id=0,zeroPos=0)
servo.move(goal_pos = 1000, prof_vel = 200)
time.sleep(5)
servo.move(goal_pos = servo.zeroPos, prof_vel = 200)
closePortObject()