from dynamixel_sdk import COMM_SUCCESS
from .portAndPackets import portHandler, packetHandler
import time

class DxlServoBase:
    def __init__(self, id, zeroPos, addr_table):
        self.addrTable = addr_table
        self.dxlID = id
        self.baudRateNum = 3 #1Mbps
        self.torqEn = 1
        self.torqDis = 0
        self.zeroPos = zeroPos
        self.goalPos = None
        self.presCurrent = None
        self.presPos = None
        self.presLoad = None
        self.presVel = None
        self.highTorqueCounter = 0
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_TORQUE_ENABLE'], self.torqDis)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")

    def setOpMode(self, opNum):
        packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_OP_MODE'], opNum)
        
    def move(self, goal_pos, prof_vel):
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_PROF_VEL'], prof_vel)
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_GOAL_POSITION'], goal_pos)

    def velMove(self, goal_vel):
        goal_raw = goal_vel & 0xFFFFFFFF
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_GOAL_VEL'], goal_raw)

    def pwmMove(self, goal_PWM):
        goal_raw = goal_PWM & 0xFFFFFFFF
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_GOAL_PWM'], goal_raw)

    def moveAndWait(self, goal_pos, prof_vel):
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_PROF_VEL'], prof_vel)
        packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_GOAL_POSITION'], goal_pos)
        servoMoving = True
        time.sleep(0.1)
        while servoMoving:
                presVel = self.readVel()
                if 0 <= abs(presVel) <= 1:
                    servoMoving = False

    def readPos(self):
        dxl_present_position, _, _ = packetHandler.read4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_PRESENT_POSITION'])
        self.presPos = twos_complement_to_decimal(dxl_present_position)
        return self.presPos  # Convert to decimal
    
    def readVel(self):
        dxl_present_velocity, _, _ = packetHandler.read4ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_PRES_VEL'])
        self.presVel = twos_complement_to_decimal(dxl_present_velocity)
        return self.presVel  # Convert to decimal
    
    def readLoad (self):
        dxl_present_current, _, _ =packetHandler.read2ByteTxRx(portHandler, self.dxlID, self.addrTable["ADDR_PRESENT_LOAD"])
        return twos_complement_to_decimal(dxl_present_current) #Convert to decimal

    def torqueDisable(self):
        packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_TORQUE_ENABLE'], self.torqDis)

    def torqueEnable(self):
        packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_TORQUE_ENABLE'], self.torqEn)

    def checkHardwareError(self):
        hardware_error, _, _ = packetHandler.read1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_HARDWARE_ERROR_STATUS'])
        if hardware_error & 0x20:
            print(f"Servo ID {self.dxlID}: Overload Error")
            return True
        elif hardware_error & 0x10:
            print(f"Servo ID {self.dxlID}: Electrical Shock Error")
            return True
        elif hardware_error & 0x04:
            print(f"Servo ID {self.dxlID}: Overheating Error")
            return True
        elif hardware_error & 0x01:
            print(f"Servo ID {self.dxlID}: Input Voltage Error")
            return True
        else:
            return False
        
    def clearMultiTurn(self):
        packetHandler.clearMultiTurn(portHandler,self.dxlID)

    def reboot(self):
        self.presPos = self.readPos()
        dxl_comm_result, dxl_error = packetHandler.reboot(portHandler, self.dxlID)
        print("[ID:%03d] rebooted" % self.dxlID)

    def checkVoltage(self):
        present_voltage, _, _ = packetHandler.read2ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_PRES_VOLT'])
        print(f'Voltage = {present_voltage/10+0.5} V')


def twos_complement_to_decimal(value):
    if value & (1 << 31):
        return -((value ^ 0xFFFFFFFF) + 1)
    elif value & (1 << 15):
        return -((value ^ 0xFFFF) + 1)
    else:
        return value

#function not working, unable to write to this address?
'''    def changeBaudRate(self,baudRateNum):
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.addrTable['ADDR_BAUD_RATE'], baudRateNum )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("DXL Baudrate Changed!")'''