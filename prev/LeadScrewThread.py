from dxlControlPath import relativeDir
relativeDir('../')
from threading import Thread
from dxlSetup.XC330 import XC330
from tlsFuncs2 import *
import configparser

config = configparser.ConfigParser()
config.read('uwSnakeFiles/motor_zeros.ini')

class LeadScrewThread:
    def __init__(self):
        self.tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']))
        self.tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
        self.tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
        self.tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']), shortBool=True)
        self.frontHalf = self.tls1, self.tls2
        self.backHalf = self.tls3, self.tls4
        self.LSthread = Thread(target=keyController, args=(self.frontHalf, self.backHalf))

    def startControl(self):
        self.LSthread.start()
    
    def endControl(self):
        self.LSthread.join()
