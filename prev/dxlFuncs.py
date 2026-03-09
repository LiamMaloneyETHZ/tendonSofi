import sys
sys.path.append('/path/to/dxl_sdk')

from dynamixel_sdk import * #Uses Dynamixel SDK Library

portHandler = PortHandler('COM9')

class dxlServo:
    """Containter class for servo commands"""
    def __init__(self, id, ext, ret):
        import os
        if os.name == 'nt':
            import msvcrt
            def getch():
                return msvcrt.getch().decode()
        else:
            import sys
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            def getch():
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
        self.extendedPos = ext
        self.retractedPos = ret
        
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_POSITION = 132
        self.ADDR_PROF_VEL = 112
        self.ADDR_PRES_VEL = 128
        self.ADDR_OP_MODE = 11
        BAUDRATE = 57600
        PROTOCOL_VERSION = 2.0
        self.dxlID = id
        self.TORQUE_ENABLE = 1
        self.TORQUE_DISABLE = 0
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        if portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()
        if portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")

    def twos_complement_to_decimal(self, value):
        if value & (1 << 31):
            return -((value ^ 0xFFFFFFFF) + 1)
        else:
            return value     
## 0 Current, 1 Velocity, 3 Position (Default), 4 Extended position, 5 current-based position, 16 PWM for DXL330
    def setOpMode(self, opNum):
        self.packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.ADDR_OP_MODE, opNum)
        
    def move(self, goal_pos, prof_vel):
        self.packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.ADDR_PROF_VEL, prof_vel)
        self.packetHandler.write4ByteTxRx(portHandler, self.dxlID, self.ADDR_GOAL_POSITION, goal_pos)
        
    def readPos(self):
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(portHandler, self.dxlID, self.ADDR_PRESENT_POSITION)
        return self.twos_complement_to_decimal(dxl_present_position)  # Convert to decimal
    
    def readVel(self):
        dxl_present_velocity, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(portHandler, self.dxlID, self.ADDR_PRES_VEL)
        return self.twos_complement_to_decimal(dxl_present_velocity)  # Convert to decimal
    
    def torqueDisable(self):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)

    def torqueEnable(self):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(portHandler, self.dxlID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
        
def closePort():
    portHandler.closePort()
