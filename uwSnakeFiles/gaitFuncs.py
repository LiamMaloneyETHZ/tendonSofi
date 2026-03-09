import numpy as np
from dxlSetup.DxlServoBase import DxlServoBase
from dxlSetup.XL430 import XL430
from dxlSetup.groupSyncFuncs import groupMove
from datetime import datetime
import csv,os,platform

def getLengths(angle_deg,headFlag=False):
    angle = angle_deg*np.pi/180
    L_c = 45/2 #all units in mm
    handleTop = 5 #mm away from face
    if headFlag:
        L = 18.75-handleTop
        # print('USING HEAD LENGTH L = 18.75')
    else:
        L = 33.75-handleTop
    D = 14.55
    L_left = ((D + L*np.cos(angle) - L_c*np.sin(angle))**2 + (L*np.sin(angle) - L_c + L_c*np.cos(angle))**2)**(1/2)
    L_right = ((D + L*np.cos(angle) + L_c*np.sin(angle))**2 + (L_c + L*np.sin(angle) - L_c*np.cos(angle))**2)**(1/2)
    return L_left,L_right

pulley_diameter = 10 #mm
pulleyCircumference = np.pi*pulley_diameter
zeroLength,_ = getLengths(0)
zeroLengthHead,_ = getLengths(0,headFlag=True)
def getMotorPos(motorZero,length,headFlag=False):
    global zeroLength, zeroLengthHead
    zeroLengthInd = zeroLengthHead if headFlag else zeroLength
    neededLength = length-zeroLengthInd
    motorPos = motorZero-neededLength/pulleyCircumference*4096
    return motorPos

def zeroBodyServos(bodyGroupWrite,*bodyServos:XL430):
    for bodyServo in bodyServos:
        bodyServo.goalPos = bodyServo.zeroPos
        print(bodyServo.goalPos)
    groupMove(bodyGroupWrite,*bodyServos)

def moveTimeStep(bodyGroupWrite,params,*bodyServos:XL430,t=0):
    motor_pos_tick = params['motor_pos_tick']
    motor_pos_decimal = params['motor_pos_decimal']
    omega_s = params['omega_s']
    omega_t = params['omega_t']
    A = params['A']
    N = params['N']
    angle = params['angle']
    turnOffset = params['turnOffset']

    for k in range(N):
        headFlag = bodyServos[2*k+1].dxlID == 2    #this checks for joint one different length parameters
        angle[k] = A*np.sin(2*np.pi*omega_s*k/N + 2*np.pi*omega_t*t) + turnOffset# in paper it is minus 
        motor_pos_decimal[2*k],motor_pos_decimal[2*k+1] = getLengths(angle[k],headFlag)
        motor_pos_tick[2*k] = getMotorPos(bodyServos[2*k].zeroPos,motor_pos_decimal[2*k],headFlag)
        motor_pos_tick[2*k+1] = getMotorPos(bodyServos[2*k+1].zeroPos,motor_pos_decimal[2*k+1],headFlag)

    for k in range(len(bodyServos)):
        bodyServos[k].goalPos = motor_pos_tick[k]
    groupMove(bodyGroupWrite,*bodyServos)

def moveTimeStepG(bodyGroupWrite,params,*bodyServos:XL430,t=0):
    motor_pos_tick = params['motor_pos_tick']
    motor_pos_decimal = params['motor_pos_decimal']
    omega_s = params['omega_s']
    omega_t = params['omega_t']
    gamma = params['gamma']
    A = params['A']
    N = params['N']
    L_0_main = params['L_0']
    angle = params['angle']
    turnOffset = params['turnOffset']

    for k in range(N):
        headFlag = bodyServos[2*k+1].dxlID == 2    #this checks for joint one different length parameters
        angle[k] = A*np.sin(2*np.pi*omega_s*k/N + 2*np.pi*omega_t*t) + turnOffset # in paper it is minus 
        motor_pos_decimal[2*k],motor_pos_decimal[2*k+1] = getLengths(angle[k],headFlag)
        motor_pos_tick[2*k] = getMotorPos(bodyServos[2*k].zeroPos,motor_pos_decimal[2*k],headFlag)
        motor_pos_tick[2*k+1] = getMotorPos(bodyServos[2*k+1].zeroPos,motor_pos_decimal[2*k+1],headFlag)

        if headFlag:
            L_0 = L_0_main - 0
        else:
            L_0 = L_0_main
        if angle[k] <= gamma[k]:
            motor_pos_decimal[2*k],_ = getLengths(A*min(1,gamma[k]/A),headFlag)
            motor_pos_tick[2*k] = getMotorPos(bodyServos[2*k].zeroPos,motor_pos_decimal[2*k]+L_0*abs(angle[k]-gamma[k]),headFlag)
        if angle[k] >= -gamma[k]:
            _,motor_pos_decimal[2*k+1] = getLengths(-A*min(1,gamma[k]/A),headFlag)
            motor_pos_tick[2*k+1] = getMotorPos(bodyServos[2*k+1].zeroPos,motor_pos_decimal[2*k+1]+L_0*abs(angle[k]+gamma[k]),headFlag)
    for k in range(len(bodyServos)):
        bodyServos[k].goalPos = motor_pos_tick[k]
    groupMove(bodyGroupWrite,*bodyServos)

def moveTimeStepHead(bodyGroupWrite, params, *bodyServos: XL430, t=0):
    motor_pos_tick = params['motor_pos_tick']
    motor_pos_decimal = params['motor_pos_decimal']
    omega_s = params['omega_s']
    omega_t = params['omega_t']
    A = params['A']
    N = params['N']
    angle = params['angle']
    turnOffset = params['turnOffset']

    # Compute angles for joints 1 through N-1
    body_angles = np.zeros(N-1)
    for k in range(1, N):
        body_angles[k-1] = A * np.sin(2 * np.pi * omega_s * k / N + 2 * np.pi * omega_t * t)

    # Head compensation angle = negative of sum of all others
    angle[N-1] = -1*(np.sum(body_angles)+A*np.sin(2*np.pi*omega_t*t))
    angle[0:N-1] = body_angles
    for k in range(N):
        headFlag = bodyServos[2*k+1].dxlID == 2
        motor_pos_decimal[2*k], motor_pos_decimal[2*k+1] = getLengths(angle[k], headFlag)
        motor_pos_tick[2*k] = getMotorPos(bodyServos[2*k].zeroPos, motor_pos_decimal[2*k], headFlag)
        motor_pos_tick[2*k+1] = getMotorPos(bodyServos[2*k+1].zeroPos, motor_pos_decimal[2*k+1], headFlag)

    for k in range(len(bodyServos)):
        bodyServos[k].goalPos = motor_pos_tick[k]

    groupMove(bodyGroupWrite, *bodyServos)

def preCalculateAngles(angleMat,*bodyServos: XL430):
    angleMat = np.array(angleMat)
    N, num_timepoints = angleMat.shape
    assert N == 5, "Expected 5 joints"
    stringLengthMat = np.zeros((10, num_timepoints))  # 2 motors per joint
    motorPosMat = np.zeros((10, num_timepoints))  # 2 motors per joint

    for t in range(num_timepoints):
        for k in range(N):
            angle = angleMat[k, t]
            headFlag = (k == 4) 
            stringLengthMat[2*k,t], stringLengthMat[2*k+1,t] = getLengths(angle, headFlag)
            motorPosMat[2*k,t] = getMotorPos(bodyServos[2*k].zeroPos, stringLengthMat[2*k,t], headFlag)
            motorPosMat[2*k+1,t] = getMotorPos(bodyServos[2*k+1].zeroPos, stringLengthMat[2*k+1,t], headFlag)
    return motorPosMat


def movePredetermined(bodyGroupWrite, motorPosMat, *bodyServos: XL430, t=0):
    for k in range(len(bodyServos)):
        bodyServos[k].goalPos = motorPosMat[k,t]
        #print(f'k is {k} and t is {t}')
    groupMove(bodyGroupWrite, *bodyServos)

def torqueDisable(*allServos:DxlServoBase):
    for servo in allServos:
        servo.torqueDisable()
        print(f'Motor ID = {servo.dxlID} torque disabled')

def torqueEnable(*allServos:DxlServoBase):
    for servo in allServos:
        servo.torqueEnable()

def checkOverloads(*allServos:DxlServoBase):
    overloadFlag = False
    for servo in allServos:
        overload = servo.checkHardwareError()
        if overload:
            overloadFlag = True
            print(f'Overload in Servo {servo.dxlID}, rebooting')
            servo.reboot()
    if overloadFlag == False:
        print('No Overloads!')

def get_parameters():
    des_tmpFreq = float(input("Enter desired temp frequency (default: 0.2): ") or 0.2)
    omega_s = float(input("Enter omega_s (default: 1.0): ") or 1.0)
    A = float(input("Enter gait amplitude in degrees (default: 50): ") or 50)
    G = float(input("Enter G (default: 0): ") or 0)
    controllerBool = bool(int(input("Controller on? 0 or 1 (default: 0): ") or 0))
    syrMode = int(input("Syringe mode? 3 for Custom Seq! (default: 0): ") or 0)
    retractionPercentage = 100
    if syrMode == 2 or syrMode == 3:
        retractionPercentage = int(input("Retraction Percentage? (default: 100%): ") or 100)

    print(f"Temporal Frequency = {des_tmpFreq}")
    print(f"Spatial Frequency = {omega_s}")
    print(f"Amplitude = {A}")
    print(f"G = {G}")
    print(f"Controller? = {controllerBool}")
    print(f"Syringe Mode = {syrMode}")
    print(f"Retraction Percentage = {retractionPercentage}")

    return des_tmpFreq, omega_s, A, G, controllerBool, syrMode, retractionPercentage

def exportCSV(time_data, position_data, load_data, des_tmpFreq, omega_s, A, G, G_data):
# Determine the save directory based on the operating system
    if platform.system() == "Windows":
        home = os.path.expanduser("~")
        documents = os.path.join(home, "Documents")
        save_dir = os.path.join(documents, "CRAB_Lab", "AquaMILR_PRO_Test_Data")
    else:  # Assume Raspberry Pi (Linux)
        save_dir = "/home/uwpi/Desktop/Testing_Data/"
    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)

    valid_indices = []
    for i in range(len(time_data)):
        if time_data[i] < 0:
            break
        valid_indices.append(i)

    time_data = [time_data[i] for i in valid_indices]
    position_data = [[int(value) for value in row] for row in position_data]
    load_data = [[int(value) for value in row] for row in load_data]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    A_int = int(float(A)) if float(A).is_integer() else A
    filename = os.path.join(save_dir, f"{timestamp}_G{G}_A{A_int}_S{omega_s}_T{des_tmpFreq}.csv")

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        header = ['Time']
        for i in range(len(position_data[0])):
            header.append(f'Pos {i+1}')
        for i in range(len(load_data[0])):
            header.append(f'Load {i+1}')
        for i in range(len(G_data[0])):  # Add G_data headers
            header.append(f'G {i+1}')
        writer.writerow(header)
        
        for i in range(len(time_data)):
            time_value = round(time_data[i], 3) if isinstance(time_data[i], (int, float)) else round(time_data[i][0], 3)
            row = [time_value]  # Append time data directly
            for j in range(len(position_data[i])):
                row.append(position_data[i][j])
            for j in range(len(load_data[i])):
                row.append(load_data[i][j])
            for j in range(len(G_data[i])):
                row.append(G_data[i][j])
            writer.writerow(row)
    
    print(f"Data saved to {filename}")

def G_Controller(loadData, passiveness):
    loadData = np.array(loadData)  # Convert to NumPy array if it's not already
    loadAvg = abs(np.mean(loadData, axis=0))  # Compute the average per servo
    for i in range(len(passiveness)):  # Ensure i+1 is within bounds
        if (0 <= loadAvg[i] < 300) or (0 <= loadAvg[i+1] < 300):
            passiveness[i] = 0.75
        elif (300 <= loadAvg[i] < 500) or (300 <= loadAvg[i+1] < 500):
            passiveness[i] = 1.0
        elif loadAvg[i] >= 500 or loadAvg[i+1] >= 500:
            passiveness[i] = 1.25
        print(f'Joint {i} changed to G = {passiveness[i]} because of read average load {loadAvg[i]} [units of 0.1% total load]')

    return passiveness