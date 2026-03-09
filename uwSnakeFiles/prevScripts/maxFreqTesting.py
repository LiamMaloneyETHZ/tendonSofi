import time, numpy as np
from dxlControlPath import relativeDir,motorZeroConfig
relativeDir('../')
from dxlSetup.portAndPackets import openPortObject,closePortObject
from dxlSetup.groupSyncFuncs import *
from dxlSetup.XL430 import XL430
from dxlSetup.XC330 import XC330
from gaitFuncs import *
from tlsFuncs2 import readKey

###### INITIALIZATIONS #######
openPortObject()
config,_ = motorZeroConfig('new_motor_zeros.ini')

flipped_bodyServos = tuple(XL430(id=i, zeroPos=int(config['XL430'][f'bS{i}'])) for i in range(1,11))

bodyServos = flipped_bodyServos[::-1]
bodyServosList = list(bodyServos)

bodyGroupReadPos, bodyGroupReadLoad, bodyGroupWrite = initializeSyncs(bodyServos[0])
groupReadSetup(bodyGroupReadPos,*bodyServos)
groupReadSetup(bodyGroupReadLoad,*bodyServos)

# ============== Initialize gait parameters ====================
des_tmpFreq, omega_s, A, G = get_parameters()
cycles_per_exp = 1000
dt = 0.001
command_timeInterval = 0.07

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

import time
import numpy as np
import pandas as pd
import os
from datetime import datetime

###### INITIALIZATIONS #######
position_data = np.zeros((all_steps+1))  # Only for motor 3
goal_pos = np.zeros((all_steps+1))       # Only for motor 3
time_data = np.zeros((all_steps+1))      # Time tracking

try:
    # ============== Setting motors to zero ====================
    input("Press enter to zero body servos")
    torqueEnable(*bodyServos)    
    zeroBodyServos(bodyGroupWrite, *bodyServos)

    # ============== Initialize Shape =====================
    input("Press enter to initialize Shape...")
    moveTimeStep(bodyGroupWrite, params, *bodyServos)

    # ============== Initialize Gait =====================
    if G != 0:
        input("Press enter to initialize Gait...")
        moveTimeStepG(bodyGroupWrite, params, *bodyServos)

    # ============== Start Gait =====================
    input("Press enter to start gait...")
    t = 0
    readGroupPos(bodyGroupReadPos, *bodyServos)

    # Collect initial readings
    position_data[0] = flipped_bodyServos[2].presPos  # Motor ID 3
    goal_pos[0] = flipped_bodyServos[2].goalPos
    initial_time = time.time()
    time_data[0] = 0  # First timestamp is relative to itself

    for index in range(all_steps):
        start_time = time.time()
        t += dt

        goal_pos[index+1] = moveTimeStepG(bodyGroupWrite, params, *bodyServos, t=t)[2]  # Only motor 3

        readGroupPos(bodyGroupReadPos, *bodyServos)
        position_data[index+1] = flipped_bodyServos[2].presPos  # Motor ID 3
        print(position_data[index+1])
        print(flipped_bodyServos[2])
        stop_time = time.time()
        time_data[index+1] = stop_time - initial_time  # Relative time

        print(f'Time = {time_data[index+1]}')
        print(f'Goal Pos = {goal_pos[index+1]}')
        print(f'Real Pos = {position_data[index+1]}\n')

        if (stop_time - start_time) < command_timeInterval:
            time.sleep(command_timeInterval - (stop_time - start_time))

except KeyboardInterrupt:
    pass

# ========== Save Data to Excel ==========
save_dir = r"C:\Users\boa92\OneDrive\Documents\CRAB Lab\maxFreqTestingData"

# Generate timestamp in YYYYMMDD_HHMM format
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# Create filename with timestamp and parameters
filename = f"{timestamp}_Motor3_freq{des_tmpFreq}_A{A}_G{G}.xlsx"
filepath = os.path.join(save_dir, filename)

df = pd.DataFrame({
    "Time (s)": time_data,
    "Position Servo 3": position_data,
    "Goal Pos Servo 3": goal_pos
})

df.to_excel(filepath, index=False)
print(f"Data saved to {filepath}")

time.sleep(1)
closePortObject()
