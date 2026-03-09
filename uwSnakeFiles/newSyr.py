from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
from uwSnakeFiles.lsFuncs import *
import time

openPortObject()
zerosConfig,_ = motorZeroConfig()
tls11 = XC330(id=11, zeroPos=int(zerosConfig['XC330']['tls11']))
tls12 = XC330(id=12, zeroPos=int(zerosConfig['XC330']['tls12']))
syringeArr = [tls11,tls12]

input("press enter to continue")
newListMove(syringeArr,100)
time.sleep(5)
newListMove(syringeArr,0)
time.sleep(5)
newListMove(syringeArr,100)
time.sleep(5)
newListMove(syringeArr,0)
time.sleep(5)
newListMove(syringeArr,100)
time.sleep(5)
newListMove(syringeArr,0)
time.sleep(5)
newListMove(syringeArr,100)
closePortObject()