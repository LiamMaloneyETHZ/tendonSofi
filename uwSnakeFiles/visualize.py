import numpy as np
import matplotlib.pyplot as plt

def visualize_snake(angles, L=1.0):
    x, y = [0], [0]     # Starting point
    theta = 0           # Global orientation

    for a in angles:
        theta += a
        x.append(x[-1] + L * np.cos(theta))
        y.append(y[-1] + L * np.sin(theta))

    plt.figure()
    plt.plot(x, y, 'o-', linewidth=2)
    plt.axis('equal')
    plt.grid(True)
    plt.title("Snake Pose")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

# === Example test snake ===
N = 5
A = np.pi / 12
angles = [A * np.sin(2 * np.pi * k / N) for k in range(N)]

# Add head compensation
angles = [-np.sum(angles)] + angles

visualize_snake(angles)
