from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *


config,_ = motorZeroConfig()
openPortObject()

tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']))
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']), shortBool=True)
tlsList = [tls1, tls2, tls3, tls4]
syringeTuple = tls1,tls2,tls3,tls4
syrGroupReadPos, syrGroupReadLoad, syrGroupWrite = initializeSyncs(tlsList[0])

i = 1
for tls in tlsList:
    print(f"tls{i} current position is: {tls.readPos()}\n")
    i += 1

input("\nPress enter to retract all syringes?")

retractPos(tlsList)
groupMove(syrGroupWrite,*syringeTuple)
time.sleep(5)
for servo in tlsList: servo.torqueDisable()

closePortObject()