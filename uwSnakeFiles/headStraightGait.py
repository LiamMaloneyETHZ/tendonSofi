import time, numpy as np
from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from dxlSetup.XC330 import XC330
from gaitFuncs import *
from tlsFuncs2 import readKey
from tlsFuncs3 import *

## INPUTTED GAIT PARAMS 
G = 0
A = 30
omega_s = 1.0
des_tmpFreq = 0.1

controllerBool = 0
syrMode = 0
retractPer = 0

###### INITIALIZATIONS #######
openPortObject()
config,_ = motorZeroConfig('new_motor_zeros.ini')

# Body Servo Initialization
flipped_bodyServos = tuple(XL430(id=i, zeroPos=int(config['XL430'][f'bS{i}'])) for i in range(1,11))
bodyServos = flipped_bodyServos[::-1]
bodyServosList = list(bodyServos)
bodyGroupReadPos, bodyGroupReadLoad, bodyGroupWrite = initializeSyncs(bodyServos[0])
groupReadSetup(bodyGroupReadPos,*bodyServos)
groupReadSetup(bodyGroupReadLoad,*bodyServos)

#Syringe Motor Initialization
tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']), shortBool=True)
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']))
tls5 = XC330(id=15, zeroPos=int(config['XC330']['tls5']))
tls6 = XC330(id=16, zeroPos=int(config['XC330']['tls6']), shortBool=True)
syringeTuple = tls1, tls2, tls3, tls4, tls5, tls6
syringeArr = list(syringeTuple)
syrGroupReadPos, syrGroupReadLoad, syrGroupWrite = initializeSyncs(syringeArr[0])
syrCounter = 0

bodyServos[0].checkVoltage()

# ============== Initialize gait parameters ====================
# des_tmpFreq, omega_s, A, G, controllerBool, syrMode, retractPer = get_parameters()
cycles_per_exp = 10000
dt = 0.001
command_timeInterval = 0.05

sampling_constant = command_timeInterval/dt
omega_t = des_tmpFreq*sampling_constant
full_cycle_steps = (1/omega_t)/dt
all_steps = int(full_cycle_steps*cycles_per_exp)
N = int(len(bodyServos)/2)
passiveness = np.array([G] * N)

params = {
    'omega_t':           omega_t,                   # temporal frequency
    'omega_s':           omega_s,                       # spatial frequency
    'A':                 A,                        # gait amplitude
    'N':                 N,                         # number of joints
    'motor_pos_tick':    np.zeros(len(bodyServos)), # initialize motor positions
    'motor_pos_decimal': np.zeros(len(bodyServos)), # initialize motor positions in mm
    'angle':             np.zeros(N),               # initialize angle array for each joint
    'gamma':             A*(passiveness*2-1),       # angle to check for G values  
    'L_0'  :             0.6                        # G offset coefficient
}

position_data = np.zeros((all_steps+1, len(bodyServos)))
load_data = np.zeros((all_steps+1, len(bodyServos)))
time_data = np.zeros((all_steps+1,1))
G_data = np.zeros((all_steps+1, N))


try:
    # ============== Setting motors to zero ====================
    input("Press enter to zero body servos")
    torqueEnable(*bodyServos)    
    zeroBodyServos(bodyGroupWrite,*bodyServos)
    print(f'')
    if not syrMode == 0:
        input("Press any key to extend syringes")
        syringeController(syringeArr,syrCounter,syrMode,retractPer)
        groupMove(syrGroupWrite,*syringeTuple)
    # ============== Initialize Shape =====================
    input("Press enter to initialize Shape...")
    moveTimeStepHead(bodyGroupWrite, params,*bodyServos)
    # ============== Initialize Gait =====================
    if G != 0:
        input("Press enter to initialize Gait...")
        moveTimeStepHead(bodyGroupWrite, params,*bodyServos)

    # ============== Start Gait =====================
    input("Press enter to start gait...")
    #time.sleep(10)
    t = 0
    # readGroupPos(bodyGroupReadPos, *bodyServos)
    # readGroupLoad(bodyGroupReadLoad, *bodyServos)
    position_data[0, :] = [servo.presPos for servo in flipped_bodyServos]
    load_data[0, :] = [servo.presLoad for servo in flipped_bodyServos]
    initial_time = time.time()
    time_data[0] = initial_time
    G_data[0,:] = passiveness
    stepTime = 2 #seconds
    controllerStep = int(stepTime/command_timeInterval)

    startFlag = False
    torqueFlag = False
    syringeTimerStart = time.time()
    syrDisableClock = syringeTimerStart*100
    
    for index in range(all_steps):
        start_time = time.time()
        t += dt
        moveTimeStepHead(bodyGroupWrite,params,*bodyServos,t=t)

        readGroupPos(bodyGroupReadPos, *bodyServos)
        readGroupLoad(bodyGroupReadLoad, *bodyServos)
        position_data[index+1, :] = [servo.presPos for servo in flipped_bodyServos]
        load_data[index+1, :] = [servo.presLoad for servo in flipped_bodyServos]
        G_data[index+1,:] = passiveness

        if controllerBool and index > 0 and index % controllerStep == 0:
            passiveness = G_Controller(load_data[(index-controllerStep):index,:],passiveness)

        if not syrMode == 0:
            presentTime = time.time()
            if (presentTime-syringeTimerStart) > 2 and startFlag == False:
                startFlag = True
                syrCounter +=1
                syringeController(syringeArr,syrCounter,syrMode,retractPer)
            
            if (presentTime-syringeTimerStart) > 5:
                syrCounter +=1
                syrDisableClock = presentTime
                syringeController(syringeArr,syrCounter,syrMode,retractPer)
                groupMove(syrGroupWrite,*syringeTuple)
                syringeTimerStart = presentTime
                torqueFlag = True
            
            if torqueFlag:
                if (presentTime-syrDisableClock) > 5:
                    print("disabling syringe torques")
                    for servo in syringeArr: servo.torqueDisable()
                    torqueFlag = False

        stop_time = time.time()
        time_data[index+1] = stop_time
        if (stop_time - start_time) < command_timeInterval:
            time.sleep(command_timeInterval - (stop_time - start_time))

except KeyboardInterrupt:
    pass
clearReadParam(bodyGroupReadPos)
clearReadParam(bodyGroupReadLoad)

time_data -= initial_time

print("Press 'f' to end without zeroing")
key = readKey()
if key == 'f':
    pass
else:
    zeroBodyServos(bodyGroupWrite,*bodyServos)

#torque stays on...
time.sleep(3)
torqueDisable(*bodyServos)    
bodyServos[0].checkVoltage()

print("Press 'f' to not save data!")
key = readKey()
if key == 'f':
    pass
else:
    exportCSV(time_data, position_data, load_data, des_tmpFreq, omega_s, A, G, G_data)

time.sleep(1)
closePortObject()