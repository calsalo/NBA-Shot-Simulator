import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Constants
g = 9.81
rho = 1.225
Cd = 0.47
r = 0.05
A = np.pi * r**2
m = 0.9
k = 0.5 * rho * Cd * A

def equations_multi(t, y):
    # y now has shape: [x1, y1, vx1, vy1, x2, y2, vx2, vy2, ...]
    # Reshape to (n_angles, 4)
    n_angles = len(y) // 4
    state = y.reshape(n_angles, 4)

    derivatives = np.zeros_like(state)

    for i in range(n_angles): # loops over each angle
        x, y_pos, vx, vy = state[i] # unpacks position and velocity for angle i
        v = np.sqrt(vx**2 + vy**2) # calculates total speed using pythagorean theorem

        # Position derivatives
        derivatives[i, 0] = vx
        derivatives[i, 1] = vy

        # Velocity derivatives (accelerations)
        derivatives[i, 2] = -(k / m) * v * vx
        derivatives[i, 3] = -g - (k / m) * v * vy

    return derivatives.flatten()

# Setup
v0 = 30
angles = np.arange(25, 65, 5)
angles_rad = np.radians(angles)

# Initial conditions for ALL angles at once
y0 = []
for angle in angles_rad:
    y0.extend([0, 0, v0 * np.cos(angle), v0 * np.sin(angle)])

# Solve once for all angles
sol = solve_ivp(equations_multi, (0, 5), y0, t_eval=np.linspace(0, 5, 500))

# Plot
plt.figure()
n_angles = len(angles)
for i in range(n_angles):
    x_index = i * 4
    y_index = i * 4 + 1
    plt.plot(sol.y[x_index], sol.y[y_index], label=f'{angles[i]}°')

plt.xlabel('Distance (m)')
plt.ylabel('Height (m)')
plt.title('Projectile Motion with Drag - Multiple Angles')
plt.legend()
plt.grid(True)
plt.ylim([0, 35])
plt.show()
