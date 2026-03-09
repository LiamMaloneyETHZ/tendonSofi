import matplotlib.pyplot as plt
from dxlControlPath import relativeDir
relativeDir('../')
from gaitFuncs import getLengths, getMotorPos
import numpy as np

N = 5
A = 50
des_tmpFreq = 0.2
omega_s = 1.0
cycles_per_exp = 2
dt = 0.001
command_timeInterval = 0.05
sampling_constant = command_timeInterval / dt
omega_t = des_tmpFreq * sampling_constant
full_cycle_steps = int((1 / omega_t) / dt)
all_steps = int(full_cycle_steps * cycles_per_exp)
 
t = 0
times = np.zeros(all_steps)
angles = np.zeros(all_steps)
stringLengths = np.zeros(all_steps)
motorPos = np.zeros(all_steps)

for i in range(all_steps):
    t += dt
    times[i] = i*command_timeInterval
    angles[i] = A * np.sin(2 * np.pi * omega_s * 1 / N + 2 * np.pi * omega_t * t)
    stringLengths[i], _ = getLengths(angles[i])
    motorPos[i] = getMotorPos(0, stringLengths[i])

posChange = (motorPos[1:] - motorPos[:-1])/4096
requiredVel = max(posChange) / command_timeInterval * 60
print(f'Highest Required Velocity is {requiredVel} RPM')
velMax = 63  # 10% loading case max motor speed in RPM
if requiredVel > velMax:
    print('Gait Max Amplitude Impossible!')
else:
    print('Gait Amplitude Possible!')

cyclePosChange = (max(motorPos)-min(motorPos))/4096
cycleVel = cyclePosChange/(0.5/des_tmpFreq) * 60
print(f'Highest Cycle Velocity is {cycleVel} RPM')
if cycleVel > velMax:
    print('Cycle Max Amplitude Impossible!')
else:
    print('Cycle Amplitude Possible!')

# Scatter plots
plt.figure(figsize=(10, 9))

plt.subplot(4, 1, 1)
plt.scatter(times, angles, label='Angle vs Time', s=10)
plt.xlabel('Time (s)')
plt.ylabel('Angle (degrees)')
plt.title('Angle Variation Over Time')
plt.legend()
plt.grid()

plt.subplot(4, 1, 2)
plt.scatter(times, stringLengths, label='Cord Length vs Time', s=10, color='r')
plt.xlabel('Time (s)')
plt.ylabel('Cord Length')
plt.title('Cord Length Variation Over Time')
plt.legend()
plt.grid()

plt.subplot(4, 1, 3)
plt.scatter(times, motorPos, label='Motor Pos vs Time', s=10, color='g')
plt.xlabel('Time (s)')
plt.ylabel('Motor Position')
plt.title('Motor Position Variation Over Time')
plt.legend()
plt.grid()

plt.subplot(4, 1, 4)
plt.scatter(times[:-1], posChange, label='Motor Position Change vs Time', s=10, color='b')
plt.xlabel('Time (s)')
plt.ylabel('Change in Motor Position (Radians)')
plt.title('Motor Position Change Over Time')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
