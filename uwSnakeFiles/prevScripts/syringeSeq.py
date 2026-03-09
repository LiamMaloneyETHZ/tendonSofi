from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
from dxlSetup.portAndPackets import openPortObject,closePortObject

config,_ = motorZeroConfig()
openPortObject()

tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']))
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']), shortBool=True)
frontHalf = tls1,tls2
backHalf = tls3,tls4
allSyringes = *frontHalf,*backHalf
for servo in allSyringes:
    servo.torqueDisable()

tensionVal = int(input("\nTension Cables? 0 or 1: "))
if tensionVal == 1:
    bS1Zero = 3926
    bS2Zero = 721
    bS3Zero = 3011
    bS4Zero = 877
    bS5Zero = 2174
    bS6Zero = 4000
    bodyServo1 = XL430(1,bS1Zero)
    bodyServo2 = XL430(2,bS2Zero)
    bodyServo3 = XL430(3,bS3Zero)
    bodyServo4 = XL430(4,bS4Zero)
    bodyServo5 = XL430(5,bS5Zero)
    bodyServo6 = XL430(6,bS6Zero)
    bodyServos = bodyServo1,bodyServo2,bodyServo3,bodyServo4,bodyServo5,bodyServo6
    for servo in bodyServos:
        servo.move(servo.zeroPos,defaultSpeed)
    tensionedFlag = True

print("Press any key to begin!")
readKey()
print("Sequence beginning...")

#Extend all (float)
moveSyringe(*allSyringes,extensionPercent=100)
time.sleep(10)

#retract all (sink)
moveSyringe(*allSyringes)
time.sleep(10)

#Extend all (float)
moveSyringe(*allSyringes,extensionPercent=100)
time.sleep(10)

#retract all (sink)
moveSyringe(*allSyringes)
time.sleep(10)

#Extend all (float)
moveSyringe(*allSyringes,extensionPercent=100)
time.sleep(10)

#retract all (sink)
moveSyringe(*allSyringes)
time.sleep(10)

#Extend all (float)
moveSyringe(*allSyringes,extensionPercent=100)
time.sleep(10)

# #extend head (pitch down)
# moveSyringe(*frontHalf)
# time.sleep(10)

# #extend tail (equalize down)
# moveSyringe(*backHalf)
# time.sleep(10)

# #extend head (pitch up)
# moveSyringe(*backHalf, extensionPercent=100)
# time.sleep(10)

# #extend tail (equalize up)
# moveSyringe(*frontHalf, extensionPercent=100)
# time.sleep(10)

#retract all before ending program
moveSyringe(*allSyringes)

if tensionedFlag:
    for servo in bodyServos:
        servo.torqueDisable()

closePortObject()