from dxlControlPath import relativeDir
relativeDir('../')
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
from dxlSetup.portAndPackets import openPortObject,closePortObject
import configparser

config = configparser.ConfigParser()
config.read('uwSnakeFiles/motor_zeros.ini')
openPortObject()

tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']))
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']), shortBool=True)
 
frontHalf = tls1,tls2
backHalf = tls3,tls4
keyController(frontHalf,backHalf)

closePortObject()