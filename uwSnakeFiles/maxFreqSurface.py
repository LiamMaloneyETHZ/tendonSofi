import matplotlib.pyplot as plt
from dxlControlPath import relativeDir
relativeDir('../')
from gaitFuncs import getLengths, getMotorPos
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm, colors

N = 5
dt = 0.001
command_timeInterval = 0.05
sampling_constant = command_timeInterval / dt
velMax = 63  # 10% loading case max motor speed in RPM
omega_s = 1.0; #spatial frequency
# Define amplitude and frequency ranges
A_values = np.linspace(0, 60, 100)  # Amplitude from 0 to 50 degrees
freq_values = np.linspace(0.01, 1, 100)  # Temporal frequency from 0.01 to 1 Hz

velocity_matrix = np.zeros((len(A_values), len(freq_values)))
cycle_velocity_matrix = np.zeros((len(A_values), len(freq_values)))  # Store cycleVel
colors_matrix = np.empty((len(A_values), len(freq_values)), dtype=object)

for i, A in enumerate(A_values):
    for j, des_tmpFreq in enumerate(freq_values):
        omega_t = des_tmpFreq * sampling_constant
        full_cycle_steps = max(1, int((1 / omega_t) / dt))        
        all_steps = int(full_cycle_steps * 2)  # Two cycles
        
        times = np.zeros(all_steps)
        angles = np.zeros(all_steps)
        stringLengths = np.zeros(all_steps)
        motorPos = np.zeros(all_steps)
        
        t = 0
        for k in range(all_steps):
            t += dt
            times[k] = t
            angles[k] = A * np.sin(2 * np.pi * omega_s * 1 / N + 2 * np.pi * omega_t * t)
            stringLengths[k], _ = getLengths(angles[k])
            motorPos[k] = getMotorPos(0, stringLengths[k])
        
        posChange = (motorPos[1:] - motorPos[:-1]) / 4096
        requiredVel = max(posChange) / command_timeInterval * 60
        cyclePosChange = (max(motorPos) - min(motorPos)) / 4096
        cycleVel = cyclePosChange / (0.5 / des_tmpFreq) * 60  # Compute cycle velocity

        velocity_matrix[i, j] = requiredVel
        cycle_velocity_matrix[i, j] = cycleVel  # Store cycle velocity

        if requiredVel <= velMax:
            colors_matrix[i, j] = 'g'  # Pass
        elif cycleVel <= velMax:
            colors_matrix[i, j] = 'orange'  # Maybe possible
        else:
            colors_matrix[i, j] = 'r'  # Fail

# Create 3D surface plot
X, Y = np.meshgrid(freq_values, A_values)
Z = velocity_matrix

fig1 = plt.figure(figsize=(10, 7))
ax1 = fig1.add_subplot(111, projection='3d')

# Define colors based on thresholds
cmap = np.array([[colors.to_rgba(c) for c in row] for row in colors_matrix])
ax1.plot_surface(X, Y, Z, facecolors=cmap, rstride=1, cstride=1, alpha=0.8, edgecolor='none')

ax1.set_xlabel('Temporal Frequency (Hz)')
ax1.set_ylabel('Amplitude (degrees)')
ax1.set_zlabel('Max Velocity (RPM)')
ax1.set_title('Max Velocity vs Temporal Frequency and Amplitude')

import matplotlib.lines as mlines  # Import for custom legend handles

# Create 2D colormap plot with improved visibility
fig2 = plt.figure(figsize=(10, 7))
ax2 = fig2.add_subplot(111)

# Use a high-contrast colormap (e.g., 'coolwarm')
c = ax2.pcolormesh(X, Y, Z, shading='auto', cmap='inferno')  # Removed edgecolors

fig2.colorbar(c, ax=ax2, label='Max Velocity (RPM)')

ax2.set_xlabel('Temporal Frequency (Hz)')
ax2.set_ylabel('Amplitude (degrees)')
ax2.set_title('Max Velocity Colormap')

# Add contour lines with increased thickness and distinct colors
contour_levels = [velMax]
req_contour = ax2.contour(X, Y, Z, levels=contour_levels, colors='yellow', linestyles='solid', linewidths=4)
cycle_contour = ax2.contour(X, Y, cycle_velocity_matrix, levels=contour_levels, colors='yellow', linestyles='dashed', linewidths=4)

# Create custom legend handles
legend_lines = [
    mlines.Line2D([0], [0], color='yellow', linestyle='solid', linewidth=4, label='Required Velocity'),
    mlines.Line2D([0], [0], color='yellow', linestyle='dotted', linewidth=4, label='Cycle Velocity')
]

# Add legend to the plot
#ax2.legend(handles=legend_lines, loc='lower left')

plt.show()
