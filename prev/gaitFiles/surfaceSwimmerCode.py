from dynamixel_sdk import *
import time
import numpy as np
np.set_printoptions(suppress=True)
import math
# import matplotlib.pyplot as plt

trailNum = '1'
cycles_per_exp = 50
gait_amps = 55
gait_spFreq= 0.6

des_tmpFreq = 0.15
gait_tmFreq = des_tmpFreq*50

passiveness = np.array([1.0,1.0,1.0,1.0,1.0])
passiveData = passiveness
passiveOG = np.copy(passiveness)
# passiveness = 0 #0 to 1.5 in intervals of 0.25
LargeTorqueReactionQ = False
HeadSensorQ = False
BackTurnQ = False
ControllerQ = True

control_mode = 2
motorPos = np.zeros((10,1))
motorLoad = np.zeros((10,1))
motorLoadThresh = np.array([300,500,700])
passiveCount = np.array([0,0,0,0,0])


# Control constants

# Control table address
ADDR_PRO_TORQUE_ENABLE       = 64
ADDR_PRO_GOAL_POSITION       = 116
ADDR_PRO_PRESENT_POSITION    = 132
ADDR_PRO_PRESENT_LOAD        = 126

# Data byte length
LEN_PRO_GOAL_POSITION        = 4
LEN_PRO_PRESENT_POSITION     = 4
LEN_PRO_PRESENT_LOAD         = 2

# Protocol Version
PROTOCOL_VERSION            = 2.0

# Default Settings
BAUDRATE                    = 1000000
#DEVICENAME                  = '/dev/ttyUSB0'
DEVICENAME                  = 'COM14'
NUM_BODY_SERVOS             = 10
# NUM_BODY_SERVOS             = 2
ID                          = np.array(range(1,NUM_BODY_SERVOS+1))
COMM_SUCCESS                = 0
COMM_TX_FAIL                = -1001
# test
TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
DXL_MAXIMUM_MOVING_SPEED    = 0
DXL_MOVING_STATUS_THRESHOLD = 10

# Declare functions

def cvt2ByteArray(position:int):
    paramGoal = [DXL_LOBYTE(DXL_LOWORD(position)), DXL_HIBYTE(DXL_LOWORD(position)), DXL_LOBYTE(DXL_HIWORD(position)), DXL_HIBYTE(DXL_HIWORD(position))]
    return paramGoal




# Connect to motors
# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    quit()


POS_0_DEG = np.array([3800,1200,2000,1900,1700,400,1700,1000,2000,600])
# POS_0_DEG = POS_0_DEG - 3000
POS_OFFSET = POS_0_DEG + 8988.36*np.cos(0.7328)
POS_MAX = np.zeros(NUM_BODY_SERVOS)
POS_MIN = np.zeros(NUM_BODY_SERVOS)
extra_to_give = 500



for k in range(int(NUM_BODY_SERVOS/2)):
    POS_MIN[2*k+1]= -8988.36*np.cos(-90/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1]-extra_to_give
    POS_MAX[2*k] = -8988.36*np.cos(90/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k]-extra_to_give

    POS_MIN[2*k] = -8988.36*np.cos(-90/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k]-extra_to_give
    POS_MAX[2*k+1] = -8988.36*np.cos(-(-90)/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1]-extra_to_give


# Setup the Group read/write for getting position and load data from motors
group_num_read_position = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
group_num_read_load = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_LOAD, LEN_PRO_PRESENT_LOAD)
group_num_write = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
dxl_addparam_result = False
dxl_getdata_result = False



A = gait_amps
omega_s = gait_spFreq
N = int(NUM_BODY_SERVOS/2)
omega_t = gait_tmFreq

fraction = passiveness * 2 - 1
gamma = fraction * gait_amps


t = 0
dt = 0.001
full_cycle_steps = (1/omega_t)/dt
all_steps = int(full_cycle_steps*cycles_per_exp)

angle = np.zeros(N)
motor_pos_decimal = np.zeros(NUM_BODY_SERVOS)
motor_pos_decimal_original = np.zeros(NUM_BODY_SERVOS)


# ======================== Initializing motors ===========================
for k in ID:
    dxl_comm_result,dxl_error = packetHandler.write1ByteTxRx(portHandler, k, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)

    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Connection success")
    dxl_addparam_result = group_num_read_position.addParam(k)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % k)
        quit()
    dxl_addparam_result = group_num_read_load.addParam(k)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % k)
        quit()
   

# ============== Setting motors to zero ====================

for k in range(NUM_BODY_SERVOS):
    print(POS_0_DEG[k])

    param_goal_position = cvt2ByteArray(POS_0_DEG[k])
    dxl_addparam_result = group_num_write.addParam(ID[k], param_goal_position)
    # dxl_addparam_result = group_num_write.addParam(ID[k], int(POS_0_DEG[k]), LEN_PRO_GOAL_POSITION)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % ID[k])
        quit()
dxl_comm_result = group_num_write.txPacket()
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

group_num_write.clearParam()

# Loop Gait
commannd_freq = 0.05

# ============== Initialize shape =====================
input("Press enter to initialize shape...")
t = 0.05

for k in range(N):
    angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t)
    motor_pos_decimal_original[2*k] = -8988.36*np.cos(angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k]
    motor_pos_decimal_original[2*k+1] = -8988.36*np.cos(-angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1]
    motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
    motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]

for k in range(NUM_BODY_SERVOS):
    if motor_pos_decimal[k] > POS_MAX[k]:
        motor_pos_decimal[k] = POS_MAX[k]
    elif motor_pos_decimal[k] < POS_MIN[k]:
        motor_pos_decimal[k] = POS_MIN[k]
    # print(int(np.round(motor_pos_decimal[k])))
    param_goal_position = cvt2ByteArray(int(np.round(motor_pos_decimal[k])))
    dxl_addparam_result = group_num_write.addParam(ID[k], param_goal_position)
    
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % ID[k])
        quit()

dxl_comm_result = group_num_write.txPacket()
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

# Clear params storage to prepare for next param write
group_num_write.clearParam()

# =============== initialize gait (cable loosened if G > 0) ======================
input("Press enter to initialize gait...")
t = 0
for k in range(N):
    angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t)
    motor_pos_decimal_original[2*k] = -8988.36*np.cos(angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k]
    motor_pos_decimal_original[2*k+1] = -8988.36*np.cos(-angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1]
    motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
    motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]
    if angle[k] >= -gamma[k]:
        motor_pos_decimal[2*k+1] = -8988.36*np.cos(-(-gamma[k])/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1] - 100*abs(angle[k]-(-gamma[k]))
    if angle[k] <= gamma[k]:
        motor_pos_decimal[2*k] = -8988.36*np.cos((gamma[k])/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k] - 100*abs(angle[k]-(gamma[k]))

for k in range(NUM_BODY_SERVOS):
    if motor_pos_decimal[k] > POS_MAX[k]:
        motor_pos_decimal[k] = POS_MAX[k]
    elif motor_pos_decimal[k] < POS_MIN[k]:
        motor_pos_decimal[k] = POS_MIN[k]
    # print(int(np.round(motor_pos_decimal[k])))
    param_goal_position = cvt2ByteArray(int(np.round(motor_pos_decimal[k])))
    dxl_addparam_result = group_num_write.addParam(ID[k], param_goal_position)
    
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % ID[k])
        quit()

dxl_comm_result = group_num_write.txPacket()
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

# Clear params storage to prepare for next param write
group_num_write.clearParam()


try:
    for index in range(all_steps):
        start_time = time.time()

        # ========================= reading from motors ==============================
        presentPosition = np.zeros((NUM_BODY_SERVOS,1))
        presentLoad = np.zeros((NUM_BODY_SERVOS,1))


        dxl_comm_result = group_num_read_position.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("reading position")
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        
        dxl_comm_result = group_num_read_load.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("reading load")
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        
        for k in range(NUM_BODY_SERVOS):
            presentPosition[k] = group_num_read_position.getData(ID[k],ADDR_PRO_PRESENT_POSITION,LEN_PRO_PRESENT_POSITION)
            presentPosition[k] = int(presentPosition[k])
            presentLoad[k] = group_num_read_load.getData(ID[k],ADDR_PRO_PRESENT_LOAD,LEN_PRO_PRESENT_LOAD)
            if (presentLoad[k]>32768):
                presentLoad[k] = 65536 - presentLoad[k]

        # print(np.shape(presentPosition))
        motorPos = np.hstack((motorPos,presentPosition))
        motorLoad = np.hstack((motorLoad,presentLoad))

        # ========================= end reading ==============================

        # ========================= feedback controls ========================
        if ControllerQ :
            for i in range(N):
                if (passiveCount[i] == 0):
                    if (presentLoad[2*i] > motorLoadThresh[2]) or (presentLoad[2*i+1] > motorLoadThresh[2]):                
                        passiveness[i] = 1.6
                        passiveCount[i] = 10       
                    elif (presentLoad[2*i] > motorLoadThresh[1]) or (presentLoad[2*i+1] > motorLoadThresh[1]):                
                        passiveness[i] = 1.4
                        passiveCount[i] = 10 
                    elif (presentLoad[2*i] > motorLoadThresh[0]) or (presentLoad[2*i+1] > motorLoadThresh[0]):                
                        passiveness[i] = 1.2
                        passiveCount[i] = 10 
                    else:
                        passiveness[i] = 1
                else:
                   passiveCount[i] = passiveCount[i] - 1            

        print(passiveness)
        passiveData = np.vstack((passiveData,passiveness))


        fraction = passiveness * 2 - 1
        gamma = fraction * gait_amps






        
        # ========================= end feedback controls ====================

        # ========================= writing to motors ==================================
        t = t + dt
        for k in range(N):
            angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t)
            motor_pos_decimal_original[2*k] = -8988.36*np.cos(angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k]
            motor_pos_decimal_original[2*k+1] = -8988.36*np.cos(-angle[k]/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1]
            motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
            motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]
            if angle[k] >= -gamma[k]:
                motor_pos_decimal[2*k+1] = -8988.36*np.cos(-(-gamma[k])/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k+1] - 100*abs(angle[k]-(-gamma[k]))
            if angle[k] <= gamma[k]:
                motor_pos_decimal[2*k] = -8988.36*np.cos((gamma[k])/180*np.pi/2 + 0.7328) + POS_OFFSET[2*k] - 100*abs(angle[k]-(gamma[k]))

        for k in range(NUM_BODY_SERVOS):
            if motor_pos_decimal[k] > POS_MAX[k]:
                motor_pos_decimal[k] = POS_MAX[k]
            elif motor_pos_decimal[k] < POS_MIN[k]:
                motor_pos_decimal[k] = POS_MIN[k]

            param_goal_position = cvt2ByteArray(int(np.round(motor_pos_decimal[k])))
            dxl_addparam_result = group_num_write.addParam(ID[k], param_goal_position)
            
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncRead addparam failed" % ID[k])
                quit()

        dxl_comm_result = group_num_write.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        # Clear params storage to prepare for next param write
        group_num_write.clearParam()
        # ======================= end writing ====================================

        stop_time = time.time()
        if (stop_time - start_time) < commannd_freq:
            time.sleep(commannd_freq - (stop_time - start_time))


        # group_num_read_position.clearParam()
        # group_num_read_load.clearParam()
except KeyboardInterrupt:
    pass

np.savetxt((str(passiveOG) + 'T' + trailNum + 'motorPosition.csv'), motorPos, delimiter=',')
np.savetxt((str(passiveOG) + 'T' + trailNum + 'motorLoad.csv'), motorLoad, delimiter=',')
np.savetxt((str(passiveOG) + 'T' + trailNum + 'passiveData.csv'), passiveData, delimiter=',')

