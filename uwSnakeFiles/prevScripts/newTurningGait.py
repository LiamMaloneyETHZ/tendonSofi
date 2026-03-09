import time, numpy as np
from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from tlsFuncs2 import *

###### INITIALIZATIONS #######
openPortObject()
config,_ = motorZeroConfig()

tls1 = XC330(id=11, zeroPos=int(config['XC330']['tls1']))
tls2 = XC330(id=12, zeroPos=int(config['XC330']['tls2']))
tls3 = XC330(id=13, zeroPos=int(config['XC330']['tls3']))
tls4 = XC330(id=14, zeroPos=int(config['XC330']['tls4']), shortBool=True)
syringeTuple = tls1,tls2,tls3,tls4
syringeArr = [tls1,tls2,tls3,tls4]
syrGroupReadPos, syrGroupReadLoad, syrGroupWrite = initializeSyncs(syringeArr[0])
syrCounter = 0

#initialize servos; initialize syncs with servo of the correct type
bodyServo1 = XL430(id=1, zeroPos=int(config['XL430']['bS1']))
bodyServo2 = XL430(id=2, zeroPos=int(config['XL430']['bS2']))
bodyServo3 = XL430(id=3, zeroPos=int(config['XL430']['bS3']))
bodyServo4 = XL430(id=4, zeroPos=int(config['XL430']['bS4']))
bodyServo5 = XL430(id=5, zeroPos=int(config['XL430']['bS5']))
bodyServo6 = XL430(id=6, zeroPos=int(config['XL430']['bS6']))
#bodyServos = bodyServo1,bodyServo2,bodyServo3,bodyServo4,bodyServo5,bodyServo6
bodyServos = bodyServo6,bodyServo5,bodyServo4,bodyServo3,bodyServo2,bodyServo1
#bodyServosVector = [bodyServo6.zeroPos,bodyServo5.zeroPos,bodyServo4.zeroPos,bodyServo3.zeroPos,bodyServo2.zeroPos,bodyServo1.zeroPos]

bodyGroupReadPos, bodyGroupReadLoad, bodyGroupWrite = initializeSyncs(bodyServos[0])
groupReadSetup(bodyGroupReadPos,*bodyServos)
groupReadSetup(bodyGroupReadLoad,*bodyServos)

### Gait and Trial Parameters
cycles_per_exp = 20
gait_amps = 30
gait_spFreq= .6
des_tmpFreq = 0.2
gait_tmFreq = des_tmpFreq*50
passiveness = np.array([0,0,0]) # passiveness = 0 #0 to 1.5 in intervals of 0.25
L_0 = 100
uwAmp = -18171
uwPhase = 0.5903
turnOffset = 20 #positive goes right

POS_0_DEG = np.array([bodyServo6.zeroPos,bodyServo5.zeroPos,bodyServo4.zeroPos,
                      bodyServo3.zeroPos,bodyServo2.zeroPos,bodyServo1.zeroPos])
POS_OFFSET = POS_0_DEG + -uwAmp*np.cos(uwPhase)
POS_MAX = np.zeros(len(bodyServos))
POS_MIN = np.zeros(len(bodyServos))
extra_to_give = 1000

for k in range(int(len(bodyServos)/2)):
    POS_MIN[2*k+1]= uwAmp*np.cos(-90/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1]-extra_to_give
    POS_MAX[2*k] = uwAmp*np.cos(90/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k]-extra_to_give

    POS_MIN[2*k] = uwAmp*np.cos(-90/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k]-extra_to_give
    POS_MAX[2*k+1] = uwAmp*np.cos(90/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1]-extra_to_give

A = gait_amps
N = int(len(bodyServos)/2)   #number of joints
omega_s = gait_spFreq
omega_t = gait_tmFreq
fraction = passiveness * 2 - 1
gamma = fraction * gait_amps
t = 0
dt = 0.001
full_cycle_steps = (1/omega_t)/dt
all_steps = int(full_cycle_steps*cycles_per_exp)
angle = np.zeros(N)
motor_pos_decimal = np.zeros(len(bodyServos))
motor_pos_decimal_original = np.zeros(len(bodyServos))

# ============== Setting motors to zero ====================
input("Press enter to zero body servos")
for bodyServo in bodyServos:
    bodyServo.goalPos = bodyServo.zeroPos
    print(bodyServo.goalPos)
groupMove(bodyGroupWrite,*bodyServos)

input("Press any key to extend syringes")
syrPullback(syringeArr,syrCounter)
groupMove(syrGroupWrite,*syringeTuple)

# Loop Gait

# ============== Initialize shape =====================
t = 0
input("Press enter to initialize Shape...")
for k in range(N):
    angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t)
    motor_pos_decimal_original[2*k] = uwAmp*np.cos(angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k]
    motor_pos_decimal_original[2*k+1] = uwAmp*np.cos(-angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1]
    motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
    motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]
print(angle)
for k in range(len(bodyServos)):
    if motor_pos_decimal[k] > POS_MAX[k]:
        motor_pos_decimal[k] = POS_MAX[k]
    elif motor_pos_decimal[k] < POS_MIN[k]:
        motor_pos_decimal[k] = POS_MIN[k]
    bodyServos[k].goalPos = motor_pos_decimal[k]
groupMove(bodyGroupWrite,*bodyServos)

# =============== initialize gait (cable loosened if G > 0) ======================
input("Press enter to initialize gait...")
t = 0
for k in range(N):
    angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t) + turnOffset
    motor_pos_decimal_original[2*k] = uwAmp*np.cos(angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k]
    motor_pos_decimal_original[2*k+1] = uwAmp*np.cos(-angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1]
    motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
    motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]
    if angle[k] >= -gamma[k]:
        motor_pos_decimal[2*k+1] = uwAmp*np.cos(-(-gamma[k])/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1] - L_0*abs(angle[k]-(-gamma[k]))
    if angle[k] <= gamma[k]:
        motor_pos_decimal[2*k] = uwAmp*np.cos((gamma[k])/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k] - L_0*abs(angle[k]-(gamma[k]))

for k in range(len(bodyServos)):
    if motor_pos_decimal[k] > POS_MAX[k]:
        motor_pos_decimal[k] = POS_MAX[k]
    elif motor_pos_decimal[k] < POS_MIN[k]:
        motor_pos_decimal[k] = POS_MIN[k]
    bodyServos[k].goalPos = motor_pos_decimal[k]
groupMove(bodyGroupWrite,*bodyServos)

input("Press enter to start gait...")
command_timeInterval = 0.05
try:
    torqueFlag = False
    syringeTimerStart = time.time()
    syrDisableClock = syringeTimerStart*100
    for index in range(all_steps):
        start_time = time.time()
        #readGroupPos(bodyGroupReadPos,*bodyServos)
        #readGroupLoad(bodyGroupReadLoad,*bodyServos)

        # ========================= writing to motors ==================================
        t = t + dt
        for k in range(N):
            angle[k] = A*np.sin(2*np.pi*omega_s*(k)/(N) + 2*np.pi*omega_t*t) + turnOffset
            motor_pos_decimal_original[2*k] = uwAmp*np.cos(angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k]
            motor_pos_decimal_original[2*k+1] = uwAmp*np.cos(-angle[k]/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1]
            motor_pos_decimal[2*k] = motor_pos_decimal_original[2*k]
            motor_pos_decimal[2*k+1] = motor_pos_decimal_original[2*k+1]
            if angle[k] >= -gamma[k]:
                motor_pos_decimal[2*k+1] = uwAmp*np.cos(-(-gamma[k])/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k+1] - L_0*abs(angle[k]-(-gamma[k]))
            if angle[k] <= gamma[k]:
                motor_pos_decimal[2*k] = uwAmp*np.cos((gamma[k])/180*np.pi/2 + uwPhase) + POS_OFFSET[2*k] - L_0*abs(angle[k]-(gamma[k]))

        for k in range(len(bodyServos)):
            if motor_pos_decimal[k] > POS_MAX[k]:
                motor_pos_decimal[k] = POS_MAX[k]
            elif motor_pos_decimal[k] < POS_MIN[k]:
                motor_pos_decimal[k] = POS_MIN[k]
            bodyServos[k].goalPos = motor_pos_decimal[k]
        groupMove(bodyGroupWrite,*bodyServos)
        # ======================= end writing ====================================
        
        presentTime = time.time()
        if (presentTime-syringeTimerStart) > 4:
            syrCounter +=1
            syrDisableClock = presentTime
            print("sending syringe command")
            syrPullback(syringeArr,syrCounter)
            #groupMove(syrGroupWrite,*syringeTuple)
            syringeTimerStart = presentTime
            torqueFlag = True

        turnFlag = turningSeq(syrCounter)
        if turnFlag:
            turnOffset = 15
        else:
            turnOffset = 0

        if torqueFlag:
            if (presentTime-syrDisableClock) > 3.9:
                print("disabling syringe torques")
                for servo in syringeArr: servo.torqueDisable()
                torqueFlag = False

        stop_time = time.time()
        if (stop_time - start_time) < command_timeInterval:
            time.sleep(command_timeInterval - (stop_time - start_time))

except KeyboardInterrupt:
    pass

for bodyServo in bodyServos:
    bodyServo.goalPos = bodyServo.zeroPos
    print(bodyServo.goalPos)
groupMove(bodyGroupWrite,*bodyServos)

print("extending syringes")
extendPos(syringeArr)
groupMove(syrGroupWrite,*syringeTuple)

closePortObject()