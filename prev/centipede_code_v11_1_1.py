import picamera
import subprocess
# from pyPS4Controller.controller import Controller

import os
import signal
#~ import math
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
import serial
import RPi.GPIO as GPIO
from ads1015 import ADS1015

motorSTBY = 36 # GPIO16 
motorPWM_pin = 32 # GPIO12 PWM0
motorA = 31 # AIN1 (black line) (GPIO6)
motorB = 29 # AIN2 (red line) (GPIO5)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motorSTBY,GPIO.OUT)
GPIO.setup(motorA,GPIO.OUT)
GPIO.setup(motorB,GPIO.OUT)
GPIO.setup(motorPWM_pin,GPIO.OUT)
motorPWM = GPIO.PWM(motorPWM_pin,1000)
motorPWM.start(0)



if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *  

controlTable_XL430 = dict([('protocol', 2.0), ('ID_1byte', 7), ('returnDelayTime_1byte', 9) , \
('driveMode_1byte', 10), ('operatingMode_1byte', 11), ('protocolType_1byte', 13), \
('movingThreshold_4byte', 24) , ('PWM_limit_2byte', 36), ('vel_limit_4byte', 44), \
('maxPosition_limit_4byte', 48) , ('minPosition_limit_4byte', 52), \
('torqueEnable_1byte', 64) , ('LED_1byte', 65), ('goalSpeed_4byte', 104) ,  \
('goalPos_4byte', 116) ,('presentPos_4byte', 132) , ('profileVel_4byte',112), ('profileAcc_4byte',108), \
('presentSpeed_2byte', 128) ,('presentLoad_2byte', 126) ,('registered_1byte', 69) , \
('moving_1byte', 122) ,('hardwareError_1byte', 70) , ('presentVoltage_2byte', 144)])


BAUDRATE                    = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller

portHandler = PortHandler(DEVICENAME)


packetHandler_XL = PacketHandler(2.0)

group_XL_pos = GroupSyncWrite(portHandler, packetHandler_XL, controlTable_XL430['goalPos_4byte'], 4)



if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()


# IDs_legStep =   [8, 14, 20, 26]#, 32]
# IDs_legRot =  [7, 13, 19, 25]#, 31]
# ID_body = [[9,10,11,12], [15,16,17,18], [21,22,23,24] ] #, [27,28,29,30]] # [left, top, right, bottom]

IDs_legStep =   [8, 14, 20 , 32]
IDs_legRot =  [7, 13, 19 , 31]
ID_body = [[9,10,11,12], [15,16,17,18], [27,28,29,30]] # [left, top, right, bottom]
# IDs_legStep =   [8, 14,]
# IDs_legRot =  [7, 13]
# ID_body = [[9,10,11,12]] # [left, top, right, bottom]

joint_address = [0x48, 0x49, 0x4a]
joint0 = ADS1015(i2c_addr = joint_address[0])
joint1 = ADS1015(i2c_addr = joint_address[1])
joint2 = ADS1015(i2c_addr = joint_address[2])

jointSensors = [joint0, joint1, joint2]
# jointSensors = [joint0]
for i in range(0,len(jointSensors)):
    jointSensors[i].set_sample_rate(1600)
    jointSensors[i].set_programmable_gain(4.096)

ads1015 = ADS1015()
chip_type = ads1015.detect_chip_type()
CHANNELS = ['in0/gnd', 'in1/gnd']

reference = 3.3
radVal = np.ones(len(CHANNELS))

# IDs_legStep =   [37, 8, 2,  14, 20, 26]
# IDs_legRot =  [36, 7, 1,  13, 19, 25]
# ID_body = [[3,4,5,6],[27,28,29,30],  [9,10,11,12], [15,16,17,18], [21,22,23,24]] # [left, top, right, bottom]
ID_jaw = 39

legRotOffsets = {}
legStepOffsets = {}
for i in range(0,len(IDs_legStep)): # 0,4
    legStepOffsets[IDs_legStep[i]] = 0
    legRotOffsets[IDs_legRot[i]] = 0
    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, IDs_legStep[i], controlTable_XL430['driveMode_1byte'], 4) # 4
    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, IDs_legRot[i], controlTable_XL430['driveMode_1byte'], 4) # 4

bodyOffsets = {}
for i in range(0,len(ID_body)): # 0,4
    for j in range(0,4):
        bodyOffsets[ID_body[i][j]] = 0

for i in range(0,len(ID_body)):    
    for j in range(0,len(ID_body[i])):
        dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['driveMode_1byte'], 4) # 4
        if dxl_comm_result != COMM_SUCCESS:
           print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
           print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
        else:
           print("Dynamixel#%d has been changed to time profile" % ID_body[i][j])

for i in range(0,len(ID_body)):    
    for j in range(0,len(ID_body[i])):
        dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['operatingMode_1byte'], 4) # 4
        if dxl_comm_result != COMM_SUCCESS:
           print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
           print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
        else:
           print("Dynamixel#%d has been changed to extended position mode" % ID_body[i][j])
   
degPerPulse_XL = 0.088
degPerSecPerPulse_XL = 0.229 * 6 
posBody1_zeros = np.array([1334 , 1387 , 3493 , 3109 ]) 
posBody2_zeros = np.array([937 , 2711 , 729 , 233 ])  
posBody3_zeros = np.array([2997 , 2009 , 1365 , 1875 ])
posBody4_zeros = np.array([1800, 3200, 2500, 2400])
posBody_zeros = [posBody1_zeros, posBody2_zeros, posBody3_zeros, posBody4_zeros]

#posBody4_zeros = np.array([1700, 3100, 2800, 2300])
# posBody3_zeros = np.array([1000, 1000, 1000, 1000]) 
# posBody4_zeros = np.array([1000, 1000, 1000, 1000])
# posBody5_zeros = np.array([1000, 1000, 1000, 1000])

# posBody1_zeros = np.array([1100, 1100, 1600, 1100]) 
# posBody2_zeros = np.array([2400, 2900, 2600, 2300])  
# posBody3_zeros = np.array([1200, 2200, 2500, 2000])


dutyFactor = 0.5


def getLengths(a_lat, a_sag):
    # inputs in radians
    
    d = 0.7;
    L1 = 4.994; # 5.0
    c = 0.75;
    dx_m = 5.55; 
    dy_m = 2.55;

    dx_h = 4.0;
    dy_h = 2.55;

    L_a = np.sqrt(np.square(L1 + d*np.cos(a_lat) - dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) - dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) - d*np.sin(a_lat) - L1*np.cos(a_sag)*np.sin(a_lat) + c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m - L1*np.sin(a_sag) - dy_h*np.cos(a_sag) + c*np.sin(a_sag)));
    L_b = np.sqrt(np.square(L1 + d*np.cos(a_lat) - dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) + dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_h*np.cos(a_lat) - dx_m + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m + L1*np.sin(a_sag) - dy_h*np.cos(a_sag) - c*np.sin(a_sag)));
    L_c = np.sqrt(np.square(L1 + d*np.cos(a_lat) + dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) + dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m + L1*np.sin(a_sag) - dy_h*np.cos(a_sag) - c*np.sin(a_sag)));
    L_d = np.sqrt(np.square(L1 + d*np.cos(a_lat) + dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) - dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) - dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m - L1*np.sin(a_sag) - dy_h*np.cos(a_sag) + c*np.sin(a_sag)));
    
    return [L_a, L_b, L_c, L_d] # [left, top, right, bottom]

def getLength_A(a_lat, a_sag):
    d = 0.7;
    L1 = 4.994; # 5.0
    c = 0.75;
    dx_m = 5.55; 
    dy_m = 2.55;

    dx_h = 4.0;
    dy_h = 2.55;
    L_a = np.sqrt(np.square(L1 + d*np.cos(a_lat) - dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) - dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) - d*np.sin(a_lat) - L1*np.cos(a_sag)*np.sin(a_lat) + c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m - L1*np.sin(a_sag) - dy_h*np.cos(a_sag) + c*np.sin(a_sag)));
    return L_a
def getLength_B(a_lat, a_sag):
    d = 0.7;
    L1 = 4.994; # 5.0
    c = 0.75;
    dx_m = 5.55; 
    dy_m = 2.55;

    dx_h = 4.0;
    dy_h = 2.55;
    L_b = np.sqrt(np.square(L1 + d*np.cos(a_lat) - dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) + dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_h*np.cos(a_lat) - dx_m + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m + L1*np.sin(a_sag) - dy_h*np.cos(a_sag) - c*np.sin(a_sag)));
    return L_b
def getLength_C(a_lat, a_sag):
    d = 0.7;
    L1 = 4.994; # 5.0
    c = 0.75;
    dx_m = 5.55; 
    dy_m = 2.55;

    dx_h = 4.0;
    dy_h = 2.55;
    L_c = np.sqrt(np.square(L1 + d*np.cos(a_lat) + dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) + dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) + dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m + L1*np.sin(a_sag) - dy_h*np.cos(a_sag) - c*np.sin(a_sag)));
    return L_c
def getLength_D(a_lat, a_sag):
    d = 0.7;
    L1 = 4.994; # 5.0
    c = 0.75;
    dx_m = 5.55; 
    dy_m = 2.55;

    dx_h = 4.0;
    dy_h = 2.55;
    L_d = np.sqrt(np.square(L1 + d*np.cos(a_lat) + dx_h*np.sin(a_lat) + L1*np.cos(a_lat)*np.cos(a_sag) - c*np.cos(a_lat)*np.cos(a_sag) - dy_h*np.cos(a_lat)*np.sin(a_sag)) + np.square(dx_m - dx_h*np.cos(a_lat) + d*np.sin(a_lat) + L1*np.cos(a_sag)*np.sin(a_lat) - c*np.cos(a_sag)*np.sin(a_lat) - dy_h*np.sin(a_lat)*np.sin(a_sag)) + np.square(dy_m - L1*np.sin(a_sag) - dy_h*np.cos(a_sag) + c*np.sin(a_sag)));
    return L_d
    
def getAngDiffAndTime(Lf, Li):       
    r_pullSag = 6;
    r_pullLat = 3.1;
    mot_a = (((Lf[0]-Li[0]) / (2*np.pi*r_pullLat))*360) *2*2
    mot_b = (((Lf[1]-Li[1]) / (2*np.pi*r_pullSag))*360) *3*2
    mot_c = (((Lf[2]-Li[2]) / (2*np.pi*r_pullLat))*360) *2*2
    mot_d = (((Lf[3]-Li[3]) / (2*np.pi*r_pullSag))*360) *3*2

    
    angs = np.array([mot_a, mot_b, mot_c, mot_d])
    #print(angs)
    t = 0
    for i in range(0,4):
        #print(angs[i])
        val = np.abs((angs[i]/360)/(50/60)) *1000
        if val > t:
            t = val
            
    angs = angs /degPerPulse_XL
    return angs, np.ceil(t)

def readVoltage(ID):
    dxl_status, dxl_comm_result, dxl_error = packetHandler_XL.read2ByteTxRx(portHandler, ID, controlTable_XL430['presentVoltage_2byte'])
    print("[ID:%03d] voltage = %0d" % (ID, dxl_status))

def readLoad(ID):
    load_percentage, dxl_comm_result, dxl_error = packetHandler_XL.read2ByteTxRx(portHandler, ID, controlTable_XL430['presentLoad_2byte'])
    if load_percentage > 1100:
        load_percentage = np.invert(load_percentage,dtype=np.int16) + 1
        load_percentage = -load_percentage
        # load_percentage = ~load_percentage+1 
        # load_percentage = load_percentage & 32767
        # load_percentage = -load_percentage
        
    # print("[ID:%03d] Load = %.3f" % (ID, load_percentage/10))
    return load_percentage/10
    
def readPos(ID):
    pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID,controlTable_XL430['presentPos_4byte'])
    if pos > 2147483648:
        pos = np.invert(pos,dtype=np.int32) + 1
        pos = -pos
    # print("[ID:%03d] pos = %03d" % (ID,pos))
    return pos
    
def enableTorque(ID):
    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID, controlTable_XL430['torqueEnable_1byte'], 1)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % ID)
    return []

def disableTorque(ID):
    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID, controlTable_XL430['torqueEnable_1byte'], 0)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully disconnected" % ID)
    return []

def updatePos_XL(ID, pos):
    param_goal_position = [DXL_LOBYTE(DXL_LOWORD(pos)), \
                           DXL_HIBYTE(DXL_LOWORD(pos)), \
                           DXL_LOBYTE(DXL_HIWORD(pos)), \
                           DXL_HIBYTE(DXL_HIWORD(pos))]
    dxl_addparam_result = group_XL_pos.addParam(ID, param_goal_position)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % ID)


def goAtGoalVel_XL_step(ID, vel):
    dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, ID, controlTable_XL430['profileVel_4byte'], int(vel))
    if dxl_error != 0:
        pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID,controlTable_XL430['presentPos_4byte'])
        if pos > 2147483648:
            pos = np.invert(pos,dtype=np.int32) + 1
            pos = -pos
        print("[ID:%03d] pos = %03d" % (ID,pos))
        if pos < 0:
            val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
            print("[ID:%03d] updated offset = %03d" % (ID,val))
            legStepOffsets[ID] += val.astype(int)
        elif pos > 4096:
            val = -4096 * (np.floor( np.abs(pos) / 4096))
            print("[ID:%03d] updated offset = %03d" % (ID,val))
            legStepOffsets[ID] += val.astype(int)
        dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID)
        time.sleep(0.1)
        print("[ID:%03d] rebooted" % ID)
        enableTorque(ID)
        
def rebootMotor_step(ID):
    pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID,controlTable_XL430['presentPos_4byte'])
    if pos > 2147483648:
        pos = np.invert(pos,dtype=np.int32) + 1
        pos = -pos
    if pos < 0:
        val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
        print("[ID:%03d] updated offset = %03d" % (ID,val))
        legStepOffsets[ID] += val.astype(int)
    elif pos > 4096:
        val = -4096 * (np.floor( np.abs(pos) / 4096))
        print("[ID:%03d] updated offset = %03d" % (ID,val))
        legStepOffsets[ID] += val.astype(int)
    dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID)
    time.sleep(0.1)
    print("[ID:%03d] rebooted" % ID)
    enableTorque(ID)
    
def goAtGoalVel_XL_rot(ID, vel):
    dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, ID, controlTable_XL430['profileVel_4byte'], int(vel))
    if dxl_error != 0:
        pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID,controlTable_XL430['presentPos_4byte'])
        
        if pos > 2147483648:
            pos = np.invert(pos,dtype=np.int32) + 1
            pos = -pos
        
        if pos < 0:
            val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
            print("[ID:%03d] updated offset = %03d" % (ID,val))
            legRotOffsets[ID] += val.astype(int)
        elif pos > 4096:
            val = -4096 * (np.floor( np.abs(pos) / 4096))
            print("[ID:%03d] updated offset = %03d" % (ID,val))
            legRotOffsets[ID] += val.astype(int)
        dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID)
        time.sleep(0.1)
        print("[ID:%03d] rebooted" % ID)
        enableTorque(ID)
        
def rebootMotor_rot(ID):
    pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID,controlTable_XL430['presentPos_4byte'])
    if pos > 2147483648:
        pos = np.invert(pos,dtype=np.int32) + 1
        pos = -pos
    if pos < 0:
        val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
        print("[ID:%03d] updated offset = %03d" % (ID,val))
        legRotOffsets[ID] += val.astype(int)
    elif pos > 4096:
        val = -4096 * (np.floor( np.abs(pos) / 4096))
        print("[ID:%03d] updated offset = %03d" % (ID,val))
        legRotOffsets[ID] += val.astype(int)
    dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID)
    time.sleep(0.1)
    print("[ID:%03d] rebooted" % ID)
    enableTorque(ID)
        
def goAtGoalVel_2XL_main(ID_horz, ID_vert, vel):
    dxl_comm_result, dxl_error_horz = packetHandler_XL.write4ByteTxRx(portHandler, ID_horz, controlTable_XL430['profileVel_4byte'], int(vel))
    dxl_comm_result, dxl_error_vert = packetHandler_XL.write4ByteTxRx(portHandler, ID_vert, controlTable_XL430['profileVel_4byte'], int(vel))
    
     # previously in goAtGoalVel_2XL_main... removed until the position reset can be better verified
    if dxl_error_horz != 0 or dxl_error_vert != 0:
        
        print("[ID:%03d] failed" % ID_horz)
        print("[ID:%03d] failed" % ID_vert)
        pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID_horz,controlTable_XL430['presentPos_4byte'])
        print("[ID:%03d] pos = %03d" % (ID_horz,pos))
        if pos > 2147483648:
            pos = np.invert(pos,dtype=np.int32) + 1
            pos = -pos
        
        print("[ID:%03d] pos = %03d" % (ID_horz,pos))
        if pos < 0:
            val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
            print("[ID:%03d] updated offset = %03d" % (ID_horz,val))
            bodyOffsets[ID_horz] += val.astype(int)
        elif pos > 4096:
            val = -4096 * (np.floor( np.abs(pos) / 4096))
            print("[ID:%03d] updated offset = %03d" % (ID_horz,val))
            bodyOffsets[ID_horz] += val.astype(int)
            
        pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID_vert,controlTable_XL430['presentPos_4byte'])
        if pos > 2147483648:
            pos = np.invert(pos,dtype=np.int32) + 1
            pos = -pos
        
        print("[ID:%03d] pos = %03d" % (ID_vert,pos))
        if pos < 0:
            val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
            print("[ID:%03d] updated offset = %03d" % (ID_vert,val))
            bodyOffsets[ID_vert] += val.astype(int)
        elif pos > 4096:
            val = -4096 * (np.floor( np.abs(pos) / 4096))
            print("[ID:%03d] updated offset = %03d" % (ID_vert,val))
            bodyOffsets[ID_vert] += val.astype(int)
            
        dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID_horz)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
        #~ else:
        #~ print("[ID:%03d] successfully rebooted" % ID_horz)
        time.sleep(0.1)
        # dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID_vert)
        enableTorque(ID_horz)
        enableTorque(ID_vert)

def rebootMotor_2XL(ID_horz,ID_vert):
    pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID_horz,controlTable_XL430['presentPos_4byte'])
    
    if pos > 2147483648:
        pos = np.invert(pos,dtype=np.int32) + 1
        pos = -pos
    print("[ID:%03d] pos = %03d" % (ID_horz,pos))    
    if pos < 0:
        val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
        print("[ID:%03d] updated offset = %03d" % (ID_horz,val))
        bodyOffsets[ID_horz] = 0# val.astype(int)
    elif pos > 4096:
        val = -4096 * (np.floor( np.abs(pos) / 4096))
        print("[ID:%03d] updated offset = %03d" % (ID_horz,val))
        bodyOffsets[ID_horz] = 0#val.astype(int)
        
    pos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler,ID_vert,controlTable_XL430['presentPos_4byte'])
    
    if pos > 2147483648:
        pos = np.invert(pos,dtype=np.int32) + 1
        pos = -pos
    
    print("[ID:%03d] pos = %03d" % (ID_vert,pos))        
    if pos < 0:
        val = 4096 * (np.floor( np.abs(pos) / 4096)+1)
        print("[ID:%03d] updated offset = %03d" % (ID_vert,val))
        bodyOffsets[ID_vert] = 0 #val.astype(int)
    elif pos > 4096:
        val = -4096 * (np.floor( np.abs(pos) / 4096))
        print("[ID:%03d] updated offset = %03d" % (ID_vert,val))
        bodyOffsets[ID_vert] = 0# val.astype(int)
        
    dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID_horz)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
    enableTorque(ID_horz)
    enableTorque(ID_vert)
    dxl_comm_result, dxl_error = packetHandler_XL.reboot(portHandler, ID_vert)
    enableTorque(ID_horz)
    enableTorque(ID_vert)
    print("[ID:%03d] and [ID:%03d] rebooted" % (ID_horz,ID_vert))

def runMotors(tic, servoPos):
    posLegStep = servoPos['posLegStep']
    posLegRot = servoPos['posLegRot']
    posBody = servoPos['posBody']
    moveTime = servoPos['moveTime']
    prevStep = servoPos['prevStep']
    startFlag = servoPos['startFlag']
    torqueFlags = np.zeros(len(IDs_legStep))
    torqueFlags = torqueFlags.astype(bool)
    #posHead = servoPos['posHead']
    legTime = 400
    # presLoad = np.zeros(len(IDs_legStep))
    for i in range(0,len(IDs_legStep)):
        updatePos_XL(IDs_legStep[i],posLegStep[i])
        updatePos_XL(IDs_legRot[i],posLegRot[i])
        # if posLegStep[i] != prevStep[i] or startFlag:
            # # packetHandler_XL.write1ByteTxRx(portHandler, IDs_legStep[i], controlTable_XL430['torqueEnable_1byte'], 1)
            # updatePos_XL(IDs_legStep[i],posLegStep[i])
            # torqueFlags[i] = True
        # elif torqueFlags[i]:
            # packetHandler_XL.write1ByteTxRx(portHandler, IDs_legStep[i], controlTable_XL430['torqueEnable_1byte'], 0)
            # torqueFlags[i] = False
            # packetHandler_XL.write1ByteTxRx(portHandler, IDs_legStep[i], controlTable_XL430['torqueEnable_1byte'], 1)
        goAtGoalVel_XL_step(IDs_legStep[i],0) # telling it to move as fast as possible
        # presLoad[i] = readLoad(IDs_legStep[i]) # if this works, need to change this to groupRead
        if moveTime <= 1:
            goAtGoalVel_XL_rot(IDs_legRot[i],legTime)
        else:
            goAtGoalVel_XL_rot(IDs_legRot[i],moveTime)
        # oldLegStep[i] = posLegStep[i]  # consider using this to trigger the torque on the stepping
        
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            updatePos_XL(ID_body[i][j],posBody[i][j]+ posBody_zeros[i][j].astype(int) +bodyOffsets[ID_body[i][j]])
        goAtGoalVel_2XL_main(ID_body[i][0], ID_body[i][1], moveTime)
        goAtGoalVel_2XL_main(ID_body[i][2], ID_body[i][3], moveTime)
        
    dxl_comm_result = group_XL_pos.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
    # Clear syncwrite parameter storage
    group_XL_pos.clearParam()
    toc = time.time()
    if moveTime <= 1 and toc-tic < legTime/1000:
        time.sleep((legTime/1000-(toc-tic)))  
    elif toc-tic < 0.8*moveTime/1000:
        time.sleep((0.8*moveTime/1000-(toc-tic))) 
        
    # return presLoad
    # toc2 = time.time()
    # if toc2-toc < 0.5:
        # time.sleep((0.5-(toc2-toc)))   
    # the idea for below requires the motors to reach their final position (about 0.5 seconds).
    # this requires a global flag that starts a timer from when the step position changes per motor... 
    # for i in range(0,len(IDs_legStep)):
        # disableTorque(IDs_legStep[i])
        # enableTorque(IDs_legStep[i])
        
def activationFunc(phi, xis):
    act = np.ones(len(IDs_legRot))
    for i in range(0,len(IDs_legRot)):
#        t = np.fmod(t_real+(i)*legPhaseShift*2*math.pi,2*math.pi)
        c = (phi+(i)*xis*2*np.pi) % (2*np.pi)
        # c = (phi-(i)*xis*2*np.pi) % (2*np.pi)
#        print([t_real+(i)*legPhaseShift*2*np.pi, t])
        if c < (1-dutyFactor)*np.pi:
            act[i] = 0
        elif c < (1+dutyFactor)*np.pi:
            act[i] = 2
        else:
            act[i] = 0
    return act
    
def betaFunc(phi, xis):
    beta = np.ones(len(IDs_legRot))
    for i in range(0,len(IDs_legRot)):
#        t = np.fmod(t_real+(i)*legPhaseShift*2*math.pi,2*math.pi)
#        t = np.abs(t)
        c = (phi+(i)*xis*2*np.pi) % (2*np.pi)
        # c = (phi-(i)*xis*2*np.pi) % (2*np.pi)
        if c < (1-dutyFactor)*np.pi:
            lang = np.sin(c/(2*(1-dutyFactor)))
        elif c < (1+dutyFactor)*np.pi:
            lang = np.cos((c-(1-dutyFactor)*np.pi)/(2*dutyFactor))
        else:
            lang = -np.cos((c - 2*np.pi + (1-dutyFactor)*np.pi)/(2*(1-dutyFactor)))
        beta[i] = lang
    return beta

def generateTurningGaitForT(t_real, gaitParam,t_vec,ind):
    t_freq = gaitParam['timeFreq']
    S1_horz_forw = gaitParam['shapeBasis1_horz_forward']
    S2_horz_forw = gaitParam['shapeBasis2_horz_forward']
    bA_horz_forw = gaitParam['bodyAmp_horz_forward']
    
    t_freq_turn = gaitParam['timeFreq_turn']
    S1_horz_turn = gaitParam['shapeBasis1_horz_turning']
    S2_horz_turn = gaitParam['shapeBasis2_horz_turning']
    bA_horz_turn = gaitParam['bodyAmp_horz_turning']
    turn_phase = gaitParam['turningWave_phaseOffset']
    
    bA_vert = gaitParam['bodyAmp_vert']
    S1_vert = gaitParam['shapeBasis1_vert']
    S2_vert = gaitParam['shapeBasis2_vert']
    vert_phase = gaitParam['vertWave_phaseOffset']
    
    maxPhase = gaitParam['maxPhase']
    xisLeg = gaitParam['xisLeg']
    legAmp = gaitParam['legAmp']
    
    t_mod = t_real % (2*np.pi)
    
    w1 = bA_horz_turn + bA_horz_forw*np.cos(t_freq*t_mod) 
    w2 = bA_horz_forw*np.sin(t_freq*t_mod) 
    
    body_angle_horz = S1_horz_forw*w1 +  S2_horz_forw*w2
    body_angle_vert = bA_vert * (S1_vert*np.cos(t_freq*t_mod +vert_phase) +  S2_vert*np.sin(t_freq*t_mod+vert_phase))
    
    phi = np.arctan2(w2, w1) - maxPhase
    leg_act = -1*(activationFunc(phi,xisLeg/len(ID_body))-1) 
    
    
    if direction == 'backwards':
        leg_ang = 5*legAmp* betaFunc(phi, xisLeg/len(ID_body))
    else:
        leg_ang = -5*legAmp* betaFunc(phi, xisLeg/len(ID_body))
    
    # body_angle_horz = bA_horz_forw*(S1_horz_forw*np.cos(t_freq*t_mod) +  S2_horz_forw*np.sin(t_freq*t_mod)) + bA_horz_turn*(S1_horz_turn*np.cos(t_freq_turn*t_mod+turn_phase) + S2_horz_turn*np.sin(t_freq_turn*t_mod+turn_phase))
    
    
    # phi = np.arctan2(np.sin(t_freq*t_mod), np.cos(t_freq*t_mod)) - maxPhase
    
    leg_ang = (leg_ang / degPerPulse_XL) +2048
    leg_act = (stepAmp*leg_act) +2048
    legAng = leg_ang.astype(int)
    legAct = leg_act.astype(int)
    bodyAngle_horz = body_angle_horz.astype(int)
    bodyAngle_vert = body_angle_vert.astype(int)
    for i in range(0, len(IDs_legRot)):
        legAct[i] = leg_act[len(IDs_legRot)-1-i].astype(int)
        legAng[i] = leg_ang[len(IDs_legRot)-1-i].astype(int)
        
    for i in range(0,len(body_angle_horz)):
        bodyAngle_horz[i] = body_angle_horz[len(body_angle_horz)-1-i]
        bodyAngle_vert[i] = body_angle_vert[len(body_angle_vert)-1-i]
    
    lengths = np.zeros((len(ID_body),4))
    Lmax_sag = 11.2 # corresponds to 40 deg vert angle
    Lmax_lat = 14.77
    sF = 9 # slackFactor scaling variable
    G_lat = gaitParam['G_lat']
    G_sag = gaitParam['G_sag']
    A_lat = np.deg2rad(bA_horz)
    A_sag = np.deg2rad(bA_vert)
    for i in range(0,len(body_angle_horz)):
        body_angle_horz[i] = bodyAngle_horz[i]
        body_angle_vert[i] = bodyAngle_vert[i] 
        a_l = np.deg2rad(bodyAngle_horz[i])
        a_s = np.deg2rad(bodyAngle_vert[i])
        # apply compliance here bA_horz bA_vert
        if a_l < (2*G_lat-1)*A_lat and a_s < (2*G_sag-1)*A_sag:
            La = getLength_A(A_lat*min([1,2*G_lat-1]),-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_l < (2*G_lat-1)*bA_horz:
            La = getLength_A(A_lat*min([1,2*G_lat-1]),a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_s < (2*G_sag-1)*bA_vert:
            La = getLength_A(a_l,-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s)
            if La >= Lmax_sag:
                La = Lmax_sag
        else:
            La = getLength_A(a_l,a_s)
        
        if a_l > -(2*G_lat-1)*A_lat and a_s < (2*G_sag-1)*A_sag:
            Ld = getLength_D(-A_lat*min([1,2*G_lat-1]),-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s) + sF*((2*G_lat-1)*A_lat+a_l)
        elif a_l > -(2*G_lat-1)*bA_horz:
            Ld = getLength_D(-A_lat*min([1,2*G_lat-1]),a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_s < (2*G_sag-1)*bA_vert:
            Ld = getLength_D(a_l,-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s)
            if Ld >= Lmax_sag:
                Ld = Lmax_sag
        else:
            Ld = getLength_D(a_l,a_s)
        
        Lb = getLength_B(a_l,a_s)
        Lc = getLength_C(a_l,a_s)
        
        if La >= Lmax_lat:
            La = Lmax_lat
        
        if Ld >= Lmax_lat:
            Ld = Lmax_lat
            
        lengths[i,:] = [La, Lb, Lc, Ld]
        # lengths[i,:] = getLengths(np.deg2rad(body_angle_horz[i]),np.deg2rad(body_angle_vert[i]))
    
    return lengths, legAng, legAct, body_angle_horz, body_angle_vert
    
def generateTurningGait(t_stepNum, numCycles,gaitParam):
    bodyLengthsArr = []
    legAngArr = []
    legActArr = []
    bodyHorzArr = []
    bodyVertArr = []
    phiArr = []
    direction = gaitParam['direction']
    count = 0
    t_vec = np.linspace(0,2*np.pi,t_stepNum,False)
    for j in range(0,numCycles):
        if direction == 'backwards':
            for i in range(0,len(t_vec)):
                t = t_vec[len(t_vec)-1-i]
                bodyLengths, legAng,  legAct, bodyHorz, bodyVert = generateTurningGaitForT(t, gaitParam,t_vec,i)
                bodyLengthsArr.append(bodyLengths)
                legAngArr.append(legAng)
                legActArr.append(legAct)
                bodyHorzArr.append(bodyHorz) 
                bodyVertArr.append(bodyVert) 
        else:
            for i in range(0,len(t_vec)):
                t = t_vec[i]
                bodyLengths, legAng, legAct, bodyHorz, bodyVert = generateTurningGaitForT(t, gaitParam,t_vec,i)
                bodyLengthsArr.append(bodyLengths)
                legAngArr.append(legAng)
                legActArr.append(legAct)
                bodyHorzArr.append(bodyHorz) 
                bodyVertArr.append(bodyVert) 
                    
        
    moveTimes = []
    length0 = getLengths(0,0)
    bodyAngles = np.zeros((len(ID_body),4,np.size(bodyLengthsArr,0)+1))
    body1 = np.zeros((np.size(bodyLengthsArr,0),4))
    body1[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][0,:],length0)
    
    if len(ID_body) >= 2:
        body2 = np.zeros((np.size(bodyLengthsArr,0),4))
        body2[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][1,:],length0)
    
    if len(ID_body) >= 3:
        body3 = np.zeros((np.size(bodyLengthsArr,0),4))
        body3[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][2,:],length0)
    
    if len(ID_body) >= 4:
        body4 = np.zeros((np.size(bodyLengthsArr,0),4))
        body4[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][3,:],length0)
    
    
    for j in range(1,np.size(bodyLengthsArr,0)):
        T = 0
        for i in range(0,len(ID_body)):
            angs, t = getAngDiffAndTime(bodyLengthsArr[j][i,:],bodyLengthsArr[j-1][i,:])
            if i == 0:
                body1[j,:] = angs
            elif i == 1:
                body2[j,:] = angs
            elif i == 2:
                body3[j,:] = angs
            else:
                body4[j,:] = angs
            
            if t >T:
                T = t
        moveTimes.append(T)
        
    body1 = np.cumsum(body1,axis=0)
    if len(ID_body) >= 2:
        body2 = np.cumsum(body2,axis=0)
        
    if len(ID_body) >= 3:
        body3 = np.cumsum(body3,axis=0)
    
    if len(ID_body) >= 4:
        body4 = np.cumsum(body4,axis=0)
        
    vec = np.shape(body1)
    bodyAngles = []
    for j in range(0, vec[0]):
        temp = np.zeros((len(ID_body),4))
        temp[0,:] = body1[j,:].astype(int) # + posBody1_zeros
        if len(ID_body) >= 2:
            temp[1,:] = body2[j,:].astype(int) # + posBody2_zeros
        if len(ID_body) >= 3:
            temp[2,:] = body3[j,:].astype(int) # + posBody3_zeros
        if len(ID_body) >= 4:
            temp[3,:] = body4[j,:].astype(int) # + posBody4_zeros
        
        if j == 0:
            bodyAngles = [temp]
        else:
            bodyAngles = np.append(bodyAngles, [temp], axis = 0)
    bodyAngles = bodyAngles.astype(int)
    return bodyAngles, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr

def generateGaitForT(t_real, gaitParam,t_vec,ind):   
    ecc = gaitParam['eccentricity']
    t_freq = gaitParam['timeFreq']
    S1_horz = gaitParam['shapeBasis1']
    S2_horz = gaitParam['shapeBasis2']
    bA_horz = gaitParam['bodyAmp_horz']
    bA_vert = gaitParam['bodyAmp_vert']
    shapeTilt_vert = gaitParam['shapeTilt_vert']
    legAmp = gaitParam['legAmp']
    xisHorz = gaitParam['xisHorz']
    maxPhase = gaitParam['maxPhase']
    method = gaitParam['method']
    phaseOffset_vert = gaitParam['vertPhaseOffset']
    S1_vert = gaitParam['shapeBasis1_vert']
    S2_vert = gaitParam['shapeBasis2_vert']
    stepAmp = gaitParam['stepAmp']
    direction = gaitParam['direction']
    waveMult_vert = gaitParam['waveMult_vert']
    xisLeg = gaitParam['xisLeg']
    
    t_mod = t_real % (2*np.pi)
    # body_angle_horz = np.zeros(len(ID_body))
    # for i in range(0,len(ID_body)):
        # body_angle_horz[i] = bA_horz*np.cos(t_freq*t_mod-2*np.pi*xisHorz*i/len(ID_body))
    body_angle_horz = bA_horz*(((np.cos(t_freq*t_mod)- ecc)*S1_horz /(1+np.abs(ecc)) + np.sin(t_freq*t_mod) *S2_horz)) # alpha function
    
    phi = np.arctan2(np.sin(t_freq*t_mod), (np.cos(t_freq*t_mod) -ecc)/(1+np.abs(ecc))) - maxPhase
    
    phi = np.arctan2(np.sin(t_freq*t_mod), np.cos(t_freq*t_mod)) - maxPhase
    leg_act = -1*(activationFunc(phi,xisLeg/len(ID_body))-1) 
    if direction == 'backwards':
        leg_ang = 5*legAmp* betaFunc(phi, xisLeg/len(ID_body))
    else:
        leg_ang = -5*legAmp* betaFunc(phi, xisLeg/len(ID_body))
    
    if method == 'general':
        body_angle_vert = -bA_vert*((np.cos(t_freq*t_mod)*S1_vert + np.sin(t_freq*t_mod) *S2_vert)) 
        # body_angle_vert = -bA_vert*np.cos(waveMult_vert* (np.arange(phaseOffset_vert,(len(ID_body)+phaseOffset_vert),1) *xisHorz*2*np.pi/len(ID_body) + shapeTilt_vert + t_freq* t_mod))
    elif method == 'reverse':
        leg_ang = -leg_ang
        body_angle_vert = -bA_vert*np.cos(waveMult_vert* (np.arange(phaseOffset_vert,(len(ID_body)+phaseOffset_vert),1) *xisHorz*2*np.pi/len(ID_body) + shapeTilt_vert + t_freq* t_mod))
    elif method == 'turn':
        
        body_angle_horz = bA_horz*(((np.cos(t_freq*t_mod))*S1_horz + np.sin(t_freq*t_mod) *S2_horz)) + ecc# alpha function
        
        phi = np.arctan2(np.sin(t_freq*t_mod), (np.cos(t_freq*t_mod))) - maxPhase
        leg_act = -1*(activationFunc(phi,xisHorz/len(ID_body))-1) 
    
    elif method == 'backwardVert':
        if direction == 'backwards':
            t_temp = t_mod
        else:
            t_temp = t_vec[len(t_vec)-1-ind]
            t_temp = t_temp % (2*np.pi)
        body_angle_vert = -bA_vert*((np.cos(t_freq*t_temp)*S1_vert + np.sin(t_freq*t_temp) *S2_vert)) 
        # body_angle_vert = -bA_vert*np.cos(waveMult_vert* (np.arange(phaseOffset_vert,(len(ID_body)+phaseOffset_vert),1) *xisHorz*2*np.pi/len(ID_body) + shapeTilt_vert + t_freq* t_temp))
    elif method == 'spin':
        t_temp = (t_freq*t_mod) % (2*np.pi)
        body_angle_vert = np.ones(len(ID_body))*0
        direction = gaitParam['direction']
        if direction == 'left':
            indVec = [0, 3]
        else:
            indVec = [3, 0]
        if t_temp < np.pi: # adjusted for timeFreq
            body_angle_vert[indVec[0]] = -bA_vert
        else: # timeFreq*t_mod >= np.pi:
            body_angle_vert[indVec[1]] = -bA_vert
    elif method == 'sidewind':
        body_angle_horz = bA_horz*(((np.cos(t_freq*t_mod)- ecc)*S1_horz /(1+np.abs(ecc)) + np.sin(t_freq*t_mod) *S2_horz)) # alpha function
        body_angle_vert = -bA_vert*(np.cos(t_freq*t_mod)*S1_vert + np.sin(t_freq*t_mod) *S2_vert) 
    else:
        body_angle_vert = -bA_vert*((np.cos(t_freq*t_mod)*S1_vert + np.sin(t_freq*t_mod) *S2_vert)) 
        # body_angle_vert = -bA_vert*np.cos(waveMult_vert* (np.arange(phaseOffset_vert,(len(ID_body)+phaseOffset_vert),1) *xisHorz*2*np.pi/len(ID_body) + shapeTilt_vert + t_freq* t_mod))
        
        
    leg_ang = (leg_ang / degPerPulse_XL) +2048
    leg_act = (stepAmp*leg_act) +2048
    legAng = leg_ang.astype(int)
    legAct = leg_act.astype(int)
    bodyAngle_horz = body_angle_horz.astype(int)
    bodyAngle_vert = body_angle_vert.astype(int)
    for i in range(0, len(IDs_legRot)):
        legAct[i] = leg_act[len(IDs_legRot)-1-i].astype(int)
        legAng[i] = leg_ang[len(IDs_legRot)-1-i].astype(int)
        
    for i in range(0,len(body_angle_horz)):
        bodyAngle_horz[i] = body_angle_horz[len(body_angle_horz)-1-i]
        bodyAngle_vert[i] = body_angle_vert[len(body_angle_vert)-1-i]
    
    lengths = np.zeros((len(ID_body),4))
    Lmax_sag = 11.2 # corresponds to 40 deg vert angle
    Lmax_lat = 14.77
    sF = 9 # slackFactor scaling variable
    G_lat = gaitParam['G_lat']
    G_sag = gaitParam['G_sag']
    A_lat = np.deg2rad(bA_horz)
    A_sag = np.deg2rad(bA_vert)
    for i in range(0,len(body_angle_horz)):
        body_angle_horz[i] = bodyAngle_horz[i]
        body_angle_vert[i] = bodyAngle_vert[i] 
        a_l = np.deg2rad(bodyAngle_horz[i])
        a_s = np.deg2rad(bodyAngle_vert[i])
        # apply compliance here bA_horz bA_vert
        if a_l < (2*G_lat-1)*A_lat and a_s < (2*G_sag-1)*A_sag:
            La = getLength_A(A_lat*min([1,2*G_lat-1]),-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_l < (2*G_lat-1)*bA_horz:
            La = getLength_A(A_lat*min([1,2*G_lat-1]),a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_s < (2*G_sag-1)*bA_vert:
            La = getLength_A(a_l,-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s)
            if La >= Lmax_sag:
                La = Lmax_sag
        else:
            La = getLength_A(a_l,a_s)
        
        if a_l > -(2*G_lat-1)*A_lat and a_s < (2*G_sag-1)*A_sag:
            Ld = getLength_D(-A_lat*min([1,2*G_lat-1]),-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s) + sF*((2*G_lat-1)*A_lat+a_l)
        elif a_l > -(2*G_lat-1)*bA_horz:
            Ld = getLength_D(-A_lat*min([1,2*G_lat-1]),a_s) + sF*((2*G_lat-1)*A_lat-a_l)
        elif a_s < (2*G_sag-1)*bA_vert:
            Ld = getLength_D(a_l,-A_sag*min([1,2*G_sag-1])) + sF*((2*G_sag-1)*A_sag-a_s)
            if Ld >= Lmax_sag:
                Ld = Lmax_sag
        else:
            Ld = getLength_D(a_l,a_s)
        
        Lb = getLength_B(a_l,a_s)
        Lc = getLength_C(a_l,a_s)
        
        if La >= Lmax_lat:
            La = Lmax_lat
        
        if Ld >= Lmax_lat:
            Ld = Lmax_lat
            
        lengths[i,:] = [La, Lb, Lc, Ld]
        # lengths[i,:] = getLengths(np.deg2rad(body_angle_horz[i]),np.deg2rad(body_angle_vert[i]))
    
    return lengths, legAng, legAct, body_angle_horz, body_angle_vert
    
def generateGait(t_stepNum, numCycles,gaitParam):
    # sizeForArr = (2*np.pi / dt) * numCycles
    bodyLengthsArr = []
    legAngArr = []
    legActArr = []
    bodyHorzArr = []
    bodyVertArr = []
    phiArr = []
    direction = gaitParam['direction']
    count = 0
    t_vec = np.linspace(0,2*np.pi,t_stepNum,False)
    
    for j in range(0,numCycles):
        if direction == 'backwards':
            for i in range(0,len(t_vec)):
                t = t_vec[len(t_vec)-1-i]
                bodyLengths, legAng,  legAct, bodyHorz, bodyVert = generateGaitForT(t, gaitParam,t_vec,i)
                bodyLengthsArr.append(bodyLengths)
                legAngArr.append(legAng)
                legActArr.append(legAct)
                bodyHorzArr.append(bodyHorz) 
                bodyVertArr.append(bodyVert) 
        else:
            for i in range(0,len(t_vec)):
                t = t_vec[i]
                bodyLengths, legAng, legAct, bodyHorz, bodyVert = generateGaitForT(t, gaitParam,t_vec,i)
                bodyLengthsArr.append(bodyLengths)
                legAngArr.append(legAng)
                legActArr.append(legAct)
                bodyHorzArr.append(bodyHorz) 
                bodyVertArr.append(bodyVert) 
                    
        
    moveTimes = []
    length0 = getLengths(0,0)
    bodyAngles = np.zeros((len(ID_body),4,np.size(bodyLengthsArr,0)+1))
    body1 = np.zeros((np.size(bodyLengthsArr,0),4))
    body1[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][0,:],length0)
    
    if len(ID_body) >= 2:
        body2 = np.zeros((np.size(bodyLengthsArr,0),4))
        body2[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][1,:],length0)
    
    if len(ID_body) >= 3:
        body3 = np.zeros((np.size(bodyLengthsArr,0),4))
        body3[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][2,:],length0)
    
    if len(ID_body) >= 4:
        body4 = np.zeros((np.size(bodyLengthsArr,0),4))
        body4[0,:],t = getAngDiffAndTime(bodyLengthsArr[0][3,:],length0)
    
    
    for j in range(1,np.size(bodyLengthsArr,0)):
        T = 0
        for i in range(0,len(ID_body)):
            angs, t = getAngDiffAndTime(bodyLengthsArr[j][i,:],bodyLengthsArr[j-1][i,:])
            if i == 0:
                body1[j,:] = angs
            elif i == 1:
                body2[j,:] = angs
            elif i == 2:
                body3[j,:] = angs
            else:
                body4[j,:] = angs
            
            if t >T:
                T = t
        moveTimes.append(T)
        
    body1 = np.cumsum(body1,axis=0)
    if len(ID_body) >= 2:
        body2 = np.cumsum(body2,axis=0)
        
    if len(ID_body) >= 3:
        body3 = np.cumsum(body3,axis=0)
    
    if len(ID_body) >= 4:
        body4 = np.cumsum(body4,axis=0)
        
    vec = np.shape(body1)
    bodyAngles = []
    for j in range(0, vec[0]):
        temp = np.zeros((len(ID_body),4))
        temp[0,:] = body1[j,:].astype(int) # + posBody1_zeros
        if len(ID_body) >= 2:
            temp[1,:] = body2[j,:].astype(int) # + posBody2_zeros
        if len(ID_body) >= 3:
            temp[2,:] = body3[j,:].astype(int) # + posBody3_zeros
        if len(ID_body) >= 4:
            temp[3,:] = body4[j,:].astype(int) # + posBody4_zeros
        
        if j == 0:
            bodyAngles = [temp]
        else:
            bodyAngles = np.append(bodyAngles, [temp], axis = 0)
    bodyAngles = bodyAngles.astype(int)
    return bodyAngles, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr

def setupRobot():
    
    enableTorque(ID_jaw)  
    for i in range(0,len(IDs_legStep)):
        enableTorque(IDs_legStep[i])
        # print("Dynamixel#%d has been successfully connected" % IDs_legStep[i])
        enableTorque(IDs_legRot[i])
        # print("Dynamixel#%d has been successfully connected" % IDs_legRot[i])

    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            enableTorque(ID_body[i][j])      
            # print("Dynamixel#%d has been successfully connected" % ID_body[i][j])

def shutdownRobot():
    readVoltage(ID_jaw)  
    for i in range(0,len(IDs_legStep)):
        readVoltage(IDs_legStep[i])
        readVoltage(IDs_legRot[i])

    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            readVoltage(ID_body[i][j])  
            
    disableTorque(ID_jaw)  
    for i in range(0,len(IDs_legStep)):
        disableTorque(IDs_legStep[i])
        # print("Dynamixel#%d has been successfully disconnected" % IDs_legStep[i])
        disableTorque(IDs_legRot[i])
        # print("Dynamixel#%d has been successfully disconnected" % IDs_legRot[i])

    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            disableTorque(ID_body[i][j])  
            # print("Dynamixel#%d has been successfully disconnected" % ID_body[i][j])

def tensionCables():
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            disableTorque(ID_body[i][j])
    
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['operatingMode_1byte'], 1) # 4
            if dxl_comm_result != COMM_SUCCESS:
               print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
               print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
            else:
               print("Dynamixel#%d has been changed to velocity mode" % ID_body[i][j])
       
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            enableTorque(ID_body[i][j])
              
    for j in range(0,len(ID_body)):  
        singleSeg_IDs = ID_body[j]
        presLoad = np.zeros(len(singleSeg_IDs))
        pastLoad = np.zeros(len(singleSeg_IDs))
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[0], controlTable_XL430['goalSpeed_4byte'], -120)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[2], controlTable_XL430['goalSpeed_4byte'], -120)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[1], controlTable_XL430['goalSpeed_4byte'], -180)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[3], controlTable_XL430['goalSpeed_4byte'], -180)
        tic = time.time()
        flag = np.array([0,0,0,0])
        changeVal = 0.0
        try:
            while (time.time()-tic) < 10 and np.sum(flag) < 4:
                for i in  range(0,len(singleSeg_IDs)):
                    presLoad[i] = readLoad(singleSeg_IDs[i])
                # print(presLoad)
                presLoad = abs(presLoad)
                if presLoad[0] >= 45 or abs(presLoad[0]-pastLoad[0]) < changeVal:
                    print("ID%d load = %f" % (singleSeg_IDs[0], presLoad[0]))
                    # dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[0], controlTable_XL430['goalSpeed_4byte'], 0)
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[0], controlTable_XL430['torqueEnable_1byte'], 0) # disable torque
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[0], controlTable_XL430['torqueEnable_1byte'], 1) # enable torque
                    # disableTorque(singleSeg_IDs[0])  
                    # enableTorque(singleSeg_IDs[0])  
                    flag[0] = 1
                if presLoad[2] >= 30 or abs(presLoad[2]-pastLoad[2]) < changeVal:
                    print("ID%d load = %f" % (singleSeg_IDs[2], presLoad[2]))
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[2], controlTable_XL430['torqueEnable_1byte'], 0)
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[2], controlTable_XL430['torqueEnable_1byte'], 1) 
                    flag[2] = 1
                if presLoad[1] >= 45 or abs(presLoad[1]-pastLoad[1]) < changeVal:
                    print("ID%d load = %f" % (singleSeg_IDs[1], presLoad[1]))
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[1], controlTable_XL430['torqueEnable_1byte'], 0)
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[1], controlTable_XL430['torqueEnable_1byte'], 1) 
                    # dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[1], controlTable_XL430['goalSpeed_4byte'], 0)
                    flag[1] = 1
                if presLoad[3] >= 100 or abs(presLoad[3]-pastLoad[3]) < changeVal:
                    print("ID%d load = %f" % (singleSeg_IDs[3], presLoad[3]))
                    # dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[3], controlTable_XL430['goalSpeed_4byte'], 0)
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[3], controlTable_XL430['torqueEnable_1byte'], 0)
                    dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[3], controlTable_XL430['torqueEnable_1byte'], 1) 
                    flag[3] = 1
                pastLoad = presLoad
        except KeyboardInterrupt:
            pass
        print("Tensioned segment %d" % j)
        time.sleep(0.5)
        
    #return to extended position control
    for i in range(0,len(ID_body)):  
        for j in range(0,len(ID_body[i])):  
            disableTorque(ID_body[i][j])    
            
    for i in range(0,len(ID_body)):  
        for j in range(0,len(ID_body[i])):
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['operatingMode_1byte'], 4) # 4
            if dxl_comm_result != COMM_SUCCESS:
               print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
               print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
            else:
               print("Dynamixel#%d has been changed to time profile" % ID_body[i][j])  
    
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            enableTorque(ID_body[i][j])


def loosenCables():
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            disableTorque(ID_body[i][j])
    
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['operatingMode_1byte'], 1) # 4
            if dxl_comm_result != COMM_SUCCESS:
               print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
               print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
            else:
               print("Dynamixel#%d has been changed to velocity mode" % ID_body[i][j])
       
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            enableTorque(ID_body[i][j])
              
    for j in range(0,len(ID_body)):  
        singleSeg_IDs = ID_body[j]
        presLoad = np.zeros(len(singleSeg_IDs))
        pastLoad = np.zeros(len(singleSeg_IDs))
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[0], controlTable_XL430['goalSpeed_4byte'], 120)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[2], controlTable_XL430['goalSpeed_4byte'], 120)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[1], controlTable_XL430['goalSpeed_4byte'], 180)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, singleSeg_IDs[3], controlTable_XL430['goalSpeed_4byte'], 180)
        time.sleep(.25)
        for i in range(0,4):
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[i], controlTable_XL430['torqueEnable_1byte'], 0)
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, singleSeg_IDs[i], controlTable_XL430['torqueEnable_1byte'], 1)
        print("Loosened segment %d" % j)
        
    #return to extended position control
    for i in range(0,len(ID_body)):  
        for j in range(0,len(ID_body[i])):  
            disableTorque(ID_body[i][j])    
            
    for i in range(0,len(ID_body)):  
        for j in range(0,len(ID_body[i])):
            dxl_comm_result, dxl_error = packetHandler_XL.write1ByteTxRx(portHandler, ID_body[i][j], controlTable_XL430['operatingMode_1byte'], 4) # 4
            if dxl_comm_result != COMM_SUCCESS:
               print("%s" % packetHandler_XL.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
               print("%s" % packetHandler_XL.getRxPacketError(dxl_error))
            else:
               print("Dynamixel#%d has been changed to time profile" % ID_body[i][j])  
    
    for i in range(0,len(ID_body)):    
        for j in range(0,len(ID_body[i])):
            enableTorque(ID_body[i][j])

    # singleSeg_IDs = [27,28,29,30]
    # for i in range(0,len(singleSeg_IDs)):
        # readLoad(singleSeg_IDs[i])
    moveTimes = []


def testPots():
    # radVal = np.ones((len(jointSensors),len(CHANNELS)))
    radVal = np.ones(len(jointSensors)*len(CHANNELS))
    try:
        while True:
            for i in range(0,len(jointSensors)):
                for j in range(0,len(CHANNELS)):
                    #value = ads1015.get_compensated_voltage(channel=channel, reference_voltage=reference)
                    rawV = jointSensors[i].get_voltage(CHANNELS[j])
                    newDegVal = -100.4*rawV + 166.8
                    # radVal[i][j] = newDegVal*np.pi/180
                    # radVal[2*i+j] = newDegVal # rawV
                    radVal[2*i+j] = -newDegVal *np.pi/180
                    if i == 0 and j == 0:
                        radVal[2*i+j] = radVal[2*i+j] + np.deg2rad(7)
                    elif i == 0 and j == 1:
                        radVal[2*i+j] = radVal[2*i+j] + np.deg2rad(-7)
                    elif i == 1 and j == 0:
                        radVal[2*i+j] = radVal[2*i+j] + np.deg2rad(5)
            print(np.floor(np.rad2deg(radVal)))
            #segment 1: -7deg offset, +7deg offset
            #segment 2: -5deg offset, 0deg offset
    except KeyboardInterrupt:
            pass
    

def rezeroBodyPos():
    bigTic = time.time()
    for i in range(0,len(jointSensors)):
        radVal = np.ones(len(CHANNELS))
        count = 0
        while count <2: # (abs(radVal[0]) > 0.03) or (abs(radVal[1]) > 0.03):
            for j in range(0,len(CHANNELS)):
                #value = ads1015.get_compensated_voltage(channel=channel, reference_voltage=reference)
                rawV = jointSensors[i].get_voltage(CHANNELS[j])
                newDegVal = -100.4*rawV + 166.8
                radVal[j] = -newDegVal*np.pi/180
                if i == 0 and j == 0:
                    radVal[j] = radVal[j] + np.deg2rad(7)
                elif i == 0 and j == 1:
                    radVal[j] = radVal[j] + np.deg2rad(-7)
                elif i == 1 and j == 0:
                    radVal[j] = radVal[j] + np.deg2rad(5)
                # if i == 1 and j == 1:
                    # radVal[j] = radVal[j] -0.2
            currentLengths = getLengths(radVal[0],radVal[1])
            print(np.floor(np.rad2deg(radVal)))
            print(currentLengths)
            zeroLengths = getLengths(0,0)
            # if -radVal[1] <0 and count == 0:
                # zeroLengths = getLengths(0,np.deg2rad(10))
            # elif -radVal[1] >0 and count == 0:
                # zeroLengths = getLengths(0,np.deg2rad(-10))
            # else:
                # zeroLengths = getLengths(0,0)
            # if i == 1:
                # zeroLengths = getLengths(0,0)
            # elif i == 2:
                # zeroLengths = getLengths(0,np.deg2rad(5))
            # else:
                # zeroLengths = getLengths(0,np.deg2rad(10))
            
            print(zeroLengths)
            bodypos,moveTime = getAngDiffAndTime(zeroLengths,currentLengths)
            count = count +1
            
            motorPos = np.zeros((4))
            for j in range(0,len(ID_body[i])):
                pos = readPos(ID_body[i][j])
                motorPos[j] = pos

            posBody_updatedZeros = motorPos + bodypos
            posBody_updatedZeros[3] = posBody_updatedZeros[3] -300
            if i == 1:
                posBody_updatedZeros[1] = posBody_updatedZeros[1] -300
            print(posBody_updatedZeros)
            tic = time.time()
            for j in range(0,len(ID_body[i])):
                updatePos_XL(ID_body[i][j],posBody_updatedZeros[j].astype(int))
            goAtGoalVel_2XL_main(ID_body[i][0], ID_body[i][1], moveTime)
            goAtGoalVel_2XL_main(ID_body[i][2], ID_body[i][3], moveTime)
                
            dxl_comm_result = group_XL_pos.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler_2XL.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            group_XL_pos.clearParam()
            toc = time.time()
            if toc-tic < 2*moveTime/1000:
                time.sleep((2*moveTime/1000-(toc-tic))) 
        
        for j in range(0,len(ID_body[i])):
            rebootMotor_2XL(ID_body[i][0], ID_body[i][1])
            rebootMotor_2XL(ID_body[i][2], ID_body[i][3])
        motorPos = np.zeros((4))
        for j in range(0,len(ID_body[i])):
            pos = readPos(ID_body[i][j])
            bodyOffsets[ID_body[i][j]] = 0
            motorPos[j] = pos
        posBody_zeros[i] = motorPos
    bigToc = time.time()
    print(f"Time for full reset = {bigToc-bigTic} seconds")
    
def rezeroBodyPos_proportional():
    bigTic = time.time()
    K = 1.75
    # newDegVal = -100.4*rawV + 166.8
    for i in range(0,len(jointSensors)):
        radVal = np.ones(len(CHANNELS))
        count = 0
        while count < 5:
            for j in range(0,len(CHANNELS)):
                #value = ads1015.get_compensated_voltage(channel=channel, reference_voltage=reference)
                radVal[j]  = jointSensors[i].get_voltage(CHANNELS[j]) - 1.65
            if (abs(radVal[0]) <= 0.05) and (abs(radVal[1]) <= 0.05):
                print(radVal)
                print("breaking from control loop")
                break
            if (abs(radVal[0]) <= 0.05):
                radVal[0] = 0
            if (abs(radVal[1]) <= 0.05):
                radVal[1] = 0
            currentLengths = getLengths(0+K*radVal[0],0-K*radVal[1])
            print(radVal)
            print(currentLengths)
            zeroLengths = getLengths(0,0)
            print(zeroLengths)
            bodypos,moveTime = getAngDiffAndTime(zeroLengths,currentLengths)
            count = count +1
            
            
            motorPos = np.zeros((4))
            for j in range(0,len(ID_body[i])):
                pos = readPos(ID_body[i][j])
                motorPos[j] = pos

            posBody_updatedZeros = motorPos + bodypos
            print(posBody_updatedZeros)
            print("hit a key to move forward")
            keyPress = getch()
            tic = time.time()
            for j in range(0,len(ID_body[i])):
                updatePos_XL(ID_body[i][j],posBody_updatedZeros[j].astype(int) +bodyOffsets[ID_body[i][j]])
            goAtGoalVel_2XL_main(ID_body[i][0], ID_body[i][1], moveTime)
            goAtGoalVel_2XL_main(ID_body[i][2], ID_body[i][3], moveTime)
                
            dxl_comm_result = group_XL_pos.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler_2XL.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            group_XL_pos.clearParam()
            toc = time.time()
            if toc-tic < 1.2*moveTime/1000:
                time.sleep((1.2*moveTime/1000-(toc-tic))) 
        
        for j in range(0,len(ID_body[i])):
            rebootMotor_2XL(ID_body[i][0], ID_body[i][1])
            rebootMotor_2XL(ID_body[i][2], ID_body[i][3])
        motorPos = np.zeros((4))
        for j in range(0,len(ID_body[i])):
            pos = readPos(ID_body[i][j])
            motorPos[j] = pos
        posBody_zeros[i] = motorPos
    bigToc = time.time()
    print(f"Time for full reset = {bigToc-bigTic} seconds")
    
                     
   
def createGaits():

    numCycles = 3
    freq_t =1
    t_stepNum = 15*freq_t #10 # 15 # 20*freq_t # (2*np.pi*freq_t) / (1/np.pi)
    dt = 0.3
    
    step_amp = 1400 #1450 # pulses on the dynamixel
    amp_body_horz_forw = 30 #45
    amp_body_horz_turn = 30 #45
    amp_body_vert = 0*15
    amp_leg = 30# 35 is the max
    
    xis_horz = 0.5 # 1.5 # equivalent to wave_num
    S1_horz_forw = np.sin(np.arange(0,(len(ID_body)),1) *xis_horz*2*np.pi/(len(ID_body)))
    S2_horz_forw = np.cos(np.arange(0,(len(ID_body)),1) *xis_horz*2*np.pi/(len(ID_body)))
    
    
    shape_basis1_horz_forw = np.sin(np.arange(0,(len(ID_body)),1) *xis_horz*2*np.pi/(len(ID_body)))
    shape_basis2_horz_forw = np.cos(np.arange(0,(len(ID_body)),1) *xis_horz*2*np.pi/(len(ID_body)))
    
    
    freq_t_turn = 0*freq_t # serves as a way to have the offset turn included
    xis_turn = 1
    shape_basis1_horz_turn = np.sin(np.arange(0,(len(ID_body)),1) *xis_turn*2*np.pi/(len(ID_body)))
    shape_basis2_horz_turn = np.cos(np.arange(0,(len(ID_body)),1) *xis_turn*2*np.pi/(len(ID_body)))
    turningPhase = 0*np.pi
    
    xis_vert = 2.0 
    shape_basis1_vert = np.sin(np.arange(0,(len(ID_body)),1) *xis_vert*2*np.pi/(len(ID_body)))
    shape_basis2_vert = np.cos(np.arange(0,(len(ID_body)),1) *xis_vert*2*np.pi/(len(ID_body)))
    vertPhase = 0
    
    xisLeg = xis_horz
    phaseMax = np.pi #(xis_horz/len(ID_body) + 1/2)*np.pi # np.pi # len(ID_body)*xis_horz*np.pi # + np.pi /2
    G_lat = 0.0
    G_sag = 0.0
    

    t_freq_turn = gaitParam['timeFreq_turn']
    gait_param = dict([('shapeBasis1_horz_forward', shape_basis1_horz_forw), ('shapeBasis2_horz_forward', shape_basis2_horz_forw),('bodyAmp_horz_forward', amp_body_horz_forw) , \
    ('shapeBasis1_horz_turning', shape_basis1_horz_turn), ('shapeBasis2_horz_turning', shape_basis2_horz_turn),('bodyAmp_horz_turning', amp_body_horz_turn),('turningWave_phaseOffset',turningPhase)\
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert),('bodyAmp_vert', amp_body_vert),('vertWave_phaseOffset', vertPhase), \
    ('legAmp',amp_leg), ('maxPhase', phaseMax), ('xisLeg',xisLeg), ('stepAmp',step_amp), \
    ('timeFreq', freq_t), ('direction','forwards'), ('G_lat',G_lat), ('G_sag',G_sag), ('timeFreq_turn',freq_t_turn)])
    
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateTurningGait(t_stepNum, numCycles, gait_param)
    turningGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])



    numCycles = 3
    freq_t =1
    t_stepNum = 15*freq_t #10 # 15 # 20*freq_t # (2*np.pi*freq_t) / (1/np.pi)
    dt = 0.3
    
    xis_horz = 1.5 # 1.5 # equivalent to wave_num
    xis_vert = 2.0 
    xisLeg = xis_horz
    ecc_offset = 0.0
    waveMult_vert = 2 # normally 2
    step_amp = 1400 #1450 # pulses on the dynamixel
    amp_body_horz = 45 #45
    amp_body_vert = 0*15
    amp_leg = 30# 35 is the max
    shape_tilt_horz = 0*np.pi
    shape_tilt_vert = 0*np.pi 
    vertPhaseOffset =  0
    shape_offset = 0
    bodySubNum = 0 #1 or 0
    shape_basis1_horz = np.sin(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)-bodySubNum) + shape_tilt_horz)
    # print(shape_basis1_horz)
    shape_basis2_horz = np.cos(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)-bodySubNum) + shape_tilt_horz)
    shape_basis1_vert = np.sin(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)-bodySubNum) + shape_tilt_vert)
    shape_basis2_vert = np.cos(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)-bodySubNum) + shape_tilt_vert)
    phaseMax = np.pi #(xis_horz/len(ID_body) + 1/2)*np.pi # np.pi # len(ID_body)*xis_horz*np.pi # + np.pi /2
    
    G_lat = 0.0
    G_sag = 0.0
    
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','forwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','backwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    amp_body_vert = 20
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','forwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroHorzRetroVertGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['method'] = 'backwardVert' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroHorzDirectVertGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directHorzRetroVertGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['method'] = 'general' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directHorzDirectVertGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    amp_body_horz = 0*60 # 60
    amp_body_vert = 0*20 # 60 #80 # in degrees
    amp_leg = 30# 35 is the max
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','forwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    legGaitRetro = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    legGaitDirect = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['direction'] = 'forwards' 
    gait_param['method'] = 'reverse' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    legGaitReverse = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    t_stepNum = 10*freq_t 
    amp_body_vert = 60
    xis_vert = 2.0
    amp_leg = 0# 35 is the max
    step_amp = 0
    waveMult_vert = 2 # normally 2
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','backwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    crawlGaitDirect = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['direction'] = 'forwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    crawlGaitRetro = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    numCycles = 3
    xis_horz = 1.0 # equivalent to wave_num
    xis_vert = 1.0 
    amp_body_horz = 30 # 60
    amp_body_vert = 30# 60 #80 # in degrees
    amp_leg = 0*5# 10 is the max
    waveMult_vert = 1/2
    step_amp = 0
    phaseMax = len(ID_body)*xis_horz*np.pi + np.pi /2
    vertPhaseOffset =  1
    shape_offset = 1 
    shape_basis1_horz = np.sin(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)-1) + shape_tilt_horz)
    shape_basis2_horz = np.cos(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)-1) + shape_tilt_horz)
    shape_basis1_vert = np.sin(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)-1) + shape_tilt_vert)
    shape_basis2_vert = np.cos(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)-1) + shape_tilt_vert)
    G_lat = 0.0
    G_sag = 0.0
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','sidewind'), ('direction','forwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])

    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    strafeLeftGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    strafeRightGait = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    numCycles = 3
    xis_horz = 1.0 # equivalent to wave_num
    xis_vert = 1.0 
    ecc_offset = 2.5
    waveMult_vert = 2 # normally 2
    step_amp = 1300 #1450 # pulses on the dynamixel
    amp_body_horz = 45 #45
    amp_body_vert = 0*30
    amp_leg = 0*30# 35 is the max
    shape_tilt_horz = 0*np.pi
    shape_tilt_vert = 0*np.pi 
    vertPhaseOffset =  0
    shape_offset = 0 
    shape_basis1_horz = np.sin(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)) + shape_tilt_horz)
    shape_basis2_horz = np.cos(np.arange(shape_offset,(len(ID_body)+shape_offset),1) *xis_horz*2*np.pi/(len(ID_body)) + shape_tilt_horz)
    shape_basis1_vert = np.sin(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)) + shape_tilt_vert)
    shape_basis2_vert = np.cos(np.arange(vertPhaseOffset,(len(ID_body)+vertPhaseOffset),1) *xis_vert*2*np.pi/(len(ID_body)) + shape_tilt_vert)
    phaseMax = len(ID_body)*xis_horz*np.pi # + np.pi /2
    G_lat = 0.0
    G_sag = 0.0
    
    gait_param = dict([('shapeBasis1', shape_basis1_horz), ('shapeBasis2', shape_basis2_horz), ('shapeTilt_vert', shape_tilt_vert) , \
    ('bodyAmp_horz', amp_body_horz) ,('bodyAmp_vert', amp_body_vert), ('legAmp',amp_leg), \
    ('xisHorz', xis_horz) ,('maxPhase', phaseMax), ('eccentricity',ecc_offset), \
    ('timeFreq', freq_t) , ('method','general'), ('direction','forwards'), \
    ('waveMult_vert', waveMult_vert), ('vertPhaseOffset',vertPhaseOffset), \
    ('shapeBasis1_vert', shape_basis1_vert), ('shapeBasis2_vert', shape_basis2_vert), ('xisVert', xis_vert) , ('stepAmp',step_amp),\
    ('G_lat',G_lat), ('G_sag',G_sag), ('xisLeg',xisLeg)])
    
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccP025 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccN025 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccP025 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccN025 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    ecc_offset = 5.0
    gait_param['direction'] = 'forwards' 
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccP050 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccN050 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccP050 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccN050 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    ecc_offset = 7.5
    gait_param['direction'] = 'forwards' 
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccP075 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccN075 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccP075 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccN075 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    
    ecc_offset = 10.0
    gait_param['direction'] = 'forwards' 
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccP100 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    retroGait_eccN100 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = ecc_offset
    # gait_param['bodyAmp_horz'] = amp_body_horz
    gait_param['direction'] = 'backwards' 
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccP100 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])
    
    gait_param['eccentricity'] = -ecc_offset
    # gait_param['bodyAmp_horz'] = -amp_body_horz
    bodyAngArr, legAngArr, legActArr, moveTimes, bodyHorzArr, bodyVertArr = generateGait(t_stepNum, numCycles, gait_param)
    directGait_eccN100 = dict([('bodyAngArr', bodyAngArr), ('legAngArr', legAngArr), ('legActArr', legActArr) , \
    ('moveTimes',moveTimes), ('bodyHorzArr', bodyHorzArr) , ('bodyVertArr', bodyVertArr)])

    retroEccGaits = dict([('eccP0.25',retroGait_eccP025), ('eccN0.25',retroGait_eccN025) , \
    ('eccP0.50',retroGait_eccP050), ('eccN0.50',retroGait_eccN050) , \
    ('eccP0.75',retroGait_eccP075), ('eccN0.75',retroGait_eccN075) , \
    ('eccP1.00',retroGait_eccP100), ('eccN1.00',retroGait_eccN100) ])
     
    directEccGaits = dict([('eccP0.25',directGait_eccP025), ('eccN0.25',directGait_eccN025), \
    ('eccP0.50',directGait_eccP050), ('eccN0.50',directGait_eccN050), \
    ('eccP0.75',directGait_eccP075), ('eccN0.75',directGait_eccN075), \
    ('eccP1.00',directGait_eccP100), ('eccN1.00',directGait_eccN100)  ])
    
    
    gaits = dict([('retroGait',retroGait),('directGait',directGait),('retroHorzDirectVertGait',retroHorzDirectVertGait),('retroHorzRetroVertGait',retroHorzRetroVertGait), \
    ('directHorzDirectVertGait',directHorzDirectVertGait),('directHorzRetroVertGait',directHorzRetroVertGait), \
    ('legGaitRetro',legGaitRetro),('legGaitDirect',legGaitDirect),('crawlGaitDirect',crawlGaitDirect),('crawlGaitRetro',crawlGaitRetro),\
    ('strafeLeftGait',strafeLeftGait),('strafeRightGait',strafeRightGait),('reverseGait',legGaitReverse), \
    ('retroEccGaits',retroEccGaits), ('directEccGaits',directEccGaits)])
    return gaits
    
    
tic = time.time()
gaits = createGaits()
toc = time.time()
print("Time to calculate = %d" % (toc-tic))
retroGait = gaits['retroGait']
directGait = gaits['directGait']
retroHorzDirectVertGait = gaits['retroHorzDirectVertGait']
retroHorzRetroVertGait = gaits['retroHorzRetroVertGait']
directHorzDirectVertGait = gaits['directHorzDirectVertGait']
directHorzRetroVertGait = gaits['directHorzRetroVertGait']


legGaitReverse = gaits['reverseGait']
legGaitRetro = gaits['legGaitRetro']
legGaitDirect = gaits['legGaitDirect']
crawlGaitRetro = gaits['crawlGaitRetro']
crawlGaitDirect = gaits['crawlGaitDirect']
strafeLeftGait = gaits['strafeLeftGait']
strafeRightGait = gaits['strafeRightGait']


retroEccGaits = gaits['retroEccGaits']
directEccGaits = gaits['directEccGaits']

testPots()

directFlag = False
closedMouth = False

setupRobot()
cameraProcess = subprocess.Popen(['sudo python3 /home/pi/Desktop/headCameraV2.py'], stdin = subprocess.PIPE,stdout= subprocess.PIPE,stderr = subprocess.PIPE, shell = True, preexec_fn=os.setsid)

####################################start in extended position control mode
pauseFlag = False

while 1:
    pauseFlag = False
    if directFlag:
        print("Direct = on")
    else:
        print("Direct = off")
    print("Press 'g' to switch lateral direction. Press any key to perform lateral only, 'w' for vertical direct, 's' for vertical retro, 'q' for crawlGait, 'e' for legGait, 'r' to reset, 'R' to reset with reboot, 'j' and 'l' to strafe left and right, 'p' to reverse leg gait, 'm' to move jaws, 't' for torque on, 'x' to tension cables, 'z' to rezero, 'X' to loosen cables, 'P' to test potentiometers, (or press ESC to quit!)")
    keyPress = getch()
    
    print(keyPress)
    
    if keyPress == chr(0x1b):
        break
    elif keyPress == 'r':
        print('attempting reset')
        temp = np.zeros((len(ID_body),4))
        # temp[4,:] = posBody5_zeros.astype(int)
        bodyAngArr = [temp.astype(int)]
        # legAngArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        # legActArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        
        temp = np.zeros((len(IDs_legStep))) + 2048
        legAngArr = [temp.astype(int)]
        legActArr = [temp.astype(int)]
        temp = retroGait['moveTimes']
        moveTimes = [temp[0]]
    elif keyPress == 'R':
        print('attempting hard reset to zero positions')
        temp = np.zeros((len(ID_body),4))
        # temp[4,:] = posBody5_zeros.astype(int)
        bodyAngArr = [temp.astype(int)]
        # legAngArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        # legActArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        
        temp = np.zeros((len(IDs_legStep))) + 2048
        legAngArr = [temp.astype(int)]
        legActArr = [temp.astype(int)]
        moveTimes = [2]
            
        for i in range(0,len(ID_body)):    
            rebootMotor_2XL(ID_body[i][0], ID_body[i][1])
            rebootMotor_2XL(ID_body[i][2], ID_body[i][3])
        
        for i in range(0,len(IDs_legStep)):
            rebootMotor_step(IDs_legStep[i])
            rebootMotor_rot(IDs_legRot[i])
        
        setupRobot()
            
    elif keyPress == 't':   
        setupRobot()
        temp = np.zeros((len(ID_body),4))
        # temp[4,:] = posBody5_zeros.astype(int)
        bodyAngArr = [temp.astype(int)]
        # legAngArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        # legActArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        
        temp = np.zeros((len(IDs_legStep))) + 2048
        legAngArr = [temp.astype(int)]
        legActArr = [temp.astype(int)]
        temp = retroGait['moveTimes']
        moveTimes = [temp[0]]
    elif keyPress == 'g': # switch between lateral retro and direct
        directFlag = not directFlag
        moveTimes = []
    elif keyPress == 'w': # direct vertical
        if directFlag:
            gait = directHorzDirectVertGait
        else:
            gait = retroHorzDirectVertGait
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    elif keyPress == 's': # retro vertical
        if directFlag:
            gait = directHorzRetroVertGait
        else:
            gait = retroHorzRetroVertGait
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    elif keyPress == 'q': #crawl
        if directFlag:
            gait = crawlGaitDirect
        else:
            gait = crawlGaitRetro
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    elif keyPress == 'e': #legs
        if directFlag:
            gait = legGaitDirect
        else:
            gait = legGaitRetro
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    elif keyPress == 'j': # strafe left
        legActArr = strafeLeftGait['legActArr']
        legAngArr = strafeLeftGait['legAngArr']
        bodyAngArr = strafeLeftGait['bodyAngArr']
        moveTimes = strafeLeftGait['moveTimes']  
    elif keyPress == 'l': # strafe right
        legActArr = strafeRightGait['legActArr']
        legAngArr = strafeRightGait['legAngArr']
        bodyAngArr = strafeRightGait['bodyAngArr']
        moveTimes = strafeRightGait['moveTimes']  
    elif keyPress == 'p': # reverse
        legActArr = legGaitReverse['legActArr']
        legAngArr = legGaitReverse['legAngArr']
        bodyAngArr = legGaitReverse['bodyAngArr']
        moveTimes = legGaitReverse['moveTimes']  
    elif keyPress == 'm': # mouth
        # move from 512 to 200 and trigger a flag so that next call opens the mouth
        if closedMouth:
            jawPos = 1200
            closedMouth = False
        else: 
            jawPos = 2048
            closedMouth = True
            
        # read4ByteTxRx(portHandler,ID_horz,controlTable_XL430['presentPos_4byte'])
        goAtGoalVel_XL_step(ID_jaw,0)
        dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, ID_jaw, controlTable_XL430['goalPos_4byte'],jawPos)
        time.sleep(1)
        jaw_presentPos, dxl_comm_result, dxl_error = packetHandler_XL.read4ByteTxRx(portHandler, ID_jaw,  controlTable_XL430['presentPos_4byte'])
        if abs(jawPos - jaw_presentPos) > 15:
            print('grabbed something')
            jawPos = jaw_presentPos
            dxl_comm_result, dxl_error = packetHandler_XL.write4ByteTxRx(portHandler, ID_jaw, controlTable_XL430['goalPos_4byte'],jaw_presentPos+50)
        
        
        moveTimes = []
    elif keyPress == 'z': # reset body zeros (run after tensioning)
        rezeroBodyPos()
        # rezeroBodyPos_proportional()
        moveTimes = []
    elif keyPress == 'x': # tension cables
        tensionCables()
        moveTimes = []
    elif keyPress == 'X': # untension cables
        loosenCables()
        moveTimes = []
    elif keyPress == 'P': # test potentiometers
        testPots()
        moveTimes = []
    elif keyPress == 'h':
        if directFlag:
            gaitLib = directEccGaits
            print("Eccentric direct gait selected")
        else:
            gaitLib = retroEccGaits
            print("Eccentric retrograde gait selected")
        
        print("Press 'n' for negative eccentricity, any other key for positive")
        keyPress = getch()
        posFlag = True
        if keyPress == 'n':
            posFlag = False
        
        print("Press '1' for ecc0.25, '2' for ecc0.50, '3' for ecc0.75, '4' for ecc1.00")
        keyPress = getch()
        if keyPress == '1' and posFlag:
            gait = gaitLib['eccP0.25']
        elif keyPress == '1' and not posFlag:
            gait = gaitLib['eccN0.25']
        elif keyPress == '2' and posFlag:
            gait = gaitLib['eccP0.50']
        elif keyPress == '2' and not posFlag:
            gait = gaitLib['eccN0.50']
        elif keyPress == '3' and posFlag:
            gait = gaitLib['eccP0.75']
        elif keyPress == '3' and not posFlag:
            gait = gaitLib['eccN0.75']
        elif keyPress == '4' and not posFlag:
            gait = gaitLib['eccN1.00']
        else:
            gait = gaitLib['eccP1.00']
            
        # directEccGaits = dict([('eccP0.25',directGait_eccP025), ('eccN0.25',directGait_eccN025), \
        # ('eccP0.50',directGait_eccP050), ('eccN0.50',directGait_eccN050), \
        # ('eccP0.75',directGait_eccP075), ('eccN0.75',directGait_eccN075), \
        # ('eccP1.00',directGait_eccP100), ('eccN1.00',directGait_eccN100)  ])
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    elif keyPress == 'a':
        try: 
            print('Autonomous Section Starting ')
            cameraProcess = subprocess.Popen(['sudo python3 /home/pi/Desktop/headCameraV2.py'], stdin = subprocess.PIPE,stdout= subprocess.PIPE,stderr = subprocess.PIPE, shell = True, preexec_fn=os.setsid)
            while True: 
                time.sleep(5)
                message = cameraProcess.stdout.readline()
                print('-------------')
                print(message)
                print('Message Over')
                if message == 'True\n':
                    print("Turn left!!!")
                elif message == 'False\n':
                    print("Keep Going!")

        except KeyboardInterrupt:
            cameraProcess = subprocess.Popen(['sudo python3 /home/pi/Desktop/headCameraV2.py'], stdin = subprocess.PIPE,stdout= subprocess.PIPE,stderr = subprocess.PIPE, shell = True, preexec_fn=os.setsid)


        print('Autonomous Section Starting ')
        cameraProcess = subprocess.Popen(['sudo python3 /home/pi/Desktop/headCameraV2.py'], stdin = subprocess.PIPE,stdout= subprocess.PIPE,stderr = subprocess.PIPE, shell = True, preexec_fn=os.setsid)

    elif keyPress == 'v':
        if directFlag:
            gait = directGait
        else:
            gait = retroGait
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
        pauseFlag = True
    else:
        if directFlag:
            gait = directGait
        else:
            gait = retroGait
        
        legActArr = gait['legActArr']
        legAngArr = gait['legAngArr']
        bodyAngArr = gait['bodyAngArr']
        moveTimes = gait['moveTimes']  
    
    try:
        # loadsOverCycle = np.zeros((np.size(legActArr,0),len(IDs_legStep)))
        # stepsOverCycle = np.zeros((np.size(legActArr,0),len(IDs_legStep)))
        startFlag = True
        for j in range(0,len(moveTimes)):
            posLegStep = legActArr[j]
            posLegRot = legAngArr[j]
            posBody = bodyAngArr[j]
            moveTime = moveTimes[j]
            if j > 0:
                prevStep = legActArr[j-1]
            else:
                temp = np.zeros((len(IDs_legStep))) + 2048
                prevStep = temp.astype(int)
        
            servo_commands = dict([('posLegStep', posLegStep), ('posLegRot', posLegRot), \
            ('posBody', posBody) , ('moveTime', moveTime) , ('prevStep',prevStep), ('startFlag',startFlag)])
            if startFlag:
                startFlag = False
            t = time.time()
            runMotors(t, servo_commands)
            # loads = runMotors(t, servo_commands)
            # loadsOverCycle[j,:] = loads
            # stepsOverCycle[j,:] = posLegStep
            print([moveTime/1000, time.time()-t])
            if pauseFlag:
                tempSuper = getch()
                if tempSuper == 'v':
                    pauseFlag = False
                # pauseFlag = False
        # if keyPress != 'r' and keyPress != 'x' and keyPress != 'z':
            # # print(stepsOverCycle)
            # # print(loadsOverCycle)
            # # plt.figure(1)
            # # plt.subplot(2,2,1)
            # # plt.plot(stepsOverCycle[:,0])
            # # plt.title("Step 1 Encoder")
            # # plt.subplot(2,2,3)
            # # plt.plot(loadsOverCycle[:,0])
            # # plt.title("Step 1 Load")
            # # plt.subplot(2,2,2)
            # # plt.plot(stepsOverCycle[:,1])
            # # plt.title("Step 2 Encoder")
            # # plt.subplot(2,2,4)
            # # plt.plot(loadsOverCycle[:,1])
            # # plt.title("Step 2 Load")
            # plt.figure(1)
            # plt.subplot(len(IDs_legStep),1,1)
            # plt.plot(stepsOverCycle[:,0])
            # plt.title("Step 0 Encoder")
            # plt.subplot(len(IDs_legStep),1,2)
            # plt.plot(stepsOverCycle[:,1])
            # plt.title("Step 1 Encoder")
            # plt.subplot(len(IDs_legStep),1,3)
            # plt.plot(stepsOverCycle[:,2])
            # plt.title("Step 2 Encoder")
            # plt.subplot(len(IDs_legStep),1,4)
            # plt.plot(stepsOverCycle[:,3])
            # plt.title("Step 3 Encoder")
            # # plt.subplot(len(IDs_legStep),1,5)
            # # plt.plot(stepsOverCycle[:,4])
            # # plt.title("Step 4 Encoder")
            # plt.figure(2)
            # plt.plot(moveTimes)
            # plt.title("move times")
            # plt.show()
    except KeyboardInterrupt:
        
        group_XL_pos.clearParam()
        temp = np.zeros((len(ID_body),4))
        # temp[4,:] = posBody5_zeros.astype(int)
        bodyAngArr = [temp.astype(int)]
        # legAngArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        # legActArr = [[2048, 2048, 2048, 2048]] #, 2048]]
        
        temp = np.zeros((len(IDs_legStep))) + 2048
        legAngArr = [temp.astype(int)]
        legActArr = [temp.astype(int)]
        temp = retroGait['moveTimes']
        moveTimes = [temp[0]]
        j =0
        
        startFlag = True
        posLegStep = legActArr[j]
        posLegRot = legAngArr[j]
        posBody = bodyAngArr[j]
        moveTime = moveTimes[j]
        prevStep = posLegStep
    
        servo_commands = dict([('posLegStep', posLegStep), ('posLegRot', posLegRot), \
        ('posBody', posBody) , ('moveTime', moveTime) , ('prevStep',prevStep), ('startFlag',startFlag)])
        if startFlag:
            startFlag = False
        t = time.time()
        runMotors(t, servo_commands)
        print([moveTime, time.time()-t])
        pass
    
    # for j in range(0,len(moveTimes)):
        # posLegStep = legActArr[j]
        # posLegRot = legAngArr[j]
        # posBody = bodyAngArr[j]
        # moveTime = moveTimes[j]
    
        # servo_commands = dict([('posLegStep', posLegStep), ('posLegRot', posLegRot), \
        # ('posBody', posBody) , ('moveTime', moveTime)])
        # t = time.time()
        # runMotors(t, servo_commands)
        # print([moveTime, time.time()-t])
        

temp = np.zeros((len(ID_body),4))
# temp[4,:] = posBody5_zeros.astype(int)
bodyAngArr = [temp.astype(int)]
# legAngArr = [[2048, 2048, 2048, 2048]] #, 2048]]
# legActArr = [[2048, 2048, 2048, 2048]] #, 2048]]

temp = np.zeros((len(IDs_legStep))) + 2048
legAngArr = [temp.astype(int)]
legActArr = [temp.astype(int)]
moveTimes = [3]

# for i in range(0,len(ID_body)):    
    # rebootMotor(ID_body[i][0], ID_body[i][1])
    # rebootMotor(ID_body[i][2], ID_body[i][3])
    
startFlag = True
for j in range(0,len(moveTimes)):
    posLegStep = legActArr[j]
    posLegRot = legAngArr[j]
    posBody = bodyAngArr[j]
    moveTime = moveTimes[j]
    if j > 0:
        prevStep = legActArr[j-1]
    else:
        temp = np.zeros((len(IDs_legStep))) + 2048
        prevStep = temp.astype(int)

    servo_commands = dict([('posLegStep', posLegStep), ('posLegRot', posLegRot), \
    ('posBody', posBody) , ('moveTime', moveTime) , ('prevStep',prevStep), ('startFlag',startFlag)])
    if startFlag:
        startFlag = False
    t = time.time()
    runMotors(t, servo_commands)
    print([moveTime, time.time()-t])


for i in range(0,len(ID_body)):
    print("Body%d zeros are " % (i))
    print("[%d , %d , %d , %d ]" % (posBody_zeros[i][0].astype(int), posBody_zeros[i][1].astype(int), posBody_zeros[i][2].astype(int), posBody_zeros[i][3].astype(int) ))
shutdownRobot()

subprocess.Popen(['sudo killall python3'], stdout= subprocess.PIPE, shell = True)


 # #######chip value read
        # ads1015 = ADS1015()
        # chip_type = ads1015.detect_chip_type()
        # CHANNELS = ['in0/ref', 'in1/ref']

        # ads1015.set_mode('single')
        # ads1015.set_programmable_gain(2.048)

        # if chip_type == 'ADS1015':
            # ads1015.set_sample_rate(1600)
        # else:
            # ads1015.set_sample_rate(860)
        # reference = 3.3
        # radVal = np.ones(len(CHANNELS))
        # while (abs(radVal[0]) > 0.03) or (abs(radVal[1]) > 0.03):
            # tensionCables()
            # k = 0
            # for channel in CHANNELS:
                # #value = ads1015.get_compensated_voltage(channel=channel, reference_voltage=reference)
                # rawV = ads1015.get_voltage(channel)
                # #print("{}: {:6.3f}v".format(channel, value))
                # if k == 0:
                    # compensatedV = rawV - 0.643
                # else:
                    # compensatedV = rawV-0.656
                # newradVal = compensatedV*2*np.pi/reference
                # print(f"rawV: {channel,rawV}")
                # print(f"compV: {channel,compensatedV}")
                # degVal = newradVal*180/np.pi
                # print("{}: {:6.3f} radians".format(channel, newradVal))
                # radVal[k]= newradVal
                # k+=1
             
            # currentLengths = getLengths(radVal[1],-radVal[0])    
            # zeroLengths = getLengths(0,0)
            # print(f"current Length:{currentLengths}")
            # print(f"home Length:{zeroLengths}")
            # bodypos,t = getAngDiffAndTime(zeroLengths,currentLengths)
            # motorPos = np.zeros((len(ID_body),4))
            # for i in range(0,len(ID_body)):
                # for j in range(0,len(ID_body[i])):
                    # pos = readPos(ID_body[i][j])
                    # motorPos[i,j] = pos

            # temp = np.zeros((len(IDs_legStep))) + 2048
            # legAngArr = [temp.astype(int)]
            # legActArr = [temp.astype(int)]
            # moveTimes = [t]
            # posBody4_updatedZeros = motorPos + bodypos
            
            # temp = np.zeros((len(ID_body),4))
            # temp[0,:] = posBody1_zeros.astype(int)
            # temp[1,:] = posBody2_zeros.astype(int)
            # if len(ID_body) >= 3:
                # temp[2,:] = posBody3_zeros.astype(int)
            # if len(ID_body) >= 4:
                # temp[3,:] = posBody4_zeros.astype(int)
            # bodyAngArr = [temp.astype(int)]
            # print(f"radian val 0,1: {radVal}")
            # print(f"bodyAngArr {bodyAngArr}")
            
            # for j in range(0,len(moveTimes)):
                # posLegStep = legActArr[j]
                # posLegRot = legAngArr[j]
                # posBody = bodyAngArr[j]
                # moveTime = moveTimes[j]

                # servo_commands = dict([('posLegStep', posLegStep), ('posLegRot', posLegRot), \
                # ('posBody', posBody) , ('moveTime', moveTime)])
                # t = time.time()
                # runMotors(t, servo_commands)
                # print(time.time()-t)
