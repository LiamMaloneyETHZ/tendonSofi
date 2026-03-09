from threading import Thread
import time
from XC330 import XC330
import sys
import DxlServoBase

class HardwareErrorChecker:
    def __init__(self, *servos:XC330):
        self.servos = servos
        self.error_thread = Thread(target=self.check_errors)
        self.keepChecking = True
    
    def check_errors(self):
        while self.keepChecking:
            for servo in self.servos:
                errorBool = servo.checkHardwareError()
                if errorBool:
                    print("Error found, closing the program")
                    DxlServoBase.closePort()
                    sys.exit()
            time.sleep(1)  # Check every 1 second
    
    def startErrorChecking(self):
        self.error_thread.start()
    
    def stopErrorChecking(self):
        self.keepChecking = False
        self.error_thread.join()
