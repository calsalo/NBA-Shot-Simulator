import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

g = 9.81
rho = 1.225 # air density at sea level
Cd = 0.5 # basketball drag
r = 0.12 # basketball radius
A = np.pi * r**2 # basketball cross-sectional area
m = 0.6 # basketball mass
k = 0.5 * rho * Cd * A # the drag constant

def multi_equations(t, y): # t is time, y is the state vector. a state vector is all positions and velocities for all angles
    n_angles = len(y) // 4
    state = y.reshape((n_angles, 4)) # Reshapes the flat list y into a 2D array with n_angles rows and 4 columns.

    derivatives = np.zeros_like(state) # creates an empty array of the same shape as state

    for i in range(n_angles): # loops over each angle
        x, y_pos, vx, vy = state[i] # unpacks position and velocity for angle i
        v = np.sqrt(vx**2 + vy**2) # calculates total speed using pythagorean theorem

        derivatives[i, 0] = vx # calculates the derivative of x
        derivatives[i, 1] = vy # calculates the derivative of y

        derivatives[i, 2] = -(k / m) * v * vx # velocity derivative of x
        derivatives[i, 3] = -g - (k / m) * v * vy # velocity derivative of y

    return derivatives.flatten() # returns the flattened derivatives array

v0 = 8.50 # average speed of a 3 point shot
angles = np.linspace(25, 65, 9)  # 9 evenly spaced angles from 25° to 65°
angles_rad = np.radians(angles) # converts angles to radians

y0 = [] # empty list to store initial conditions for each angle
for angle in angles_rad:
	y0.extend([0, 0, v0 * np.cos(angle), v0 * np.sin(angle)]) # starting x position, y position, x velocity, y velocity

sol = solve_ivp(multi_equations, (0, 5), y0, t_eval=np.linspace(0, 5, 100)) # solves the ODE using solve_ivp

plt.figure()
n_angles = len(angles) # how many angles we have
for i in range(n_angles): # loops over each angle
    x_index = i * 4 # calculate where this angles x position is stored in sol.y
    y_index = i * 4 + 1 # calculate where this angles y position is stored in sol.y
    plt.plot(sol.y[x_index], sol.y[y_index], label=f'{angles[i]}°') # plots the angle's trajectory

plt.xlabel('Distance (m)')
plt.ylabel('Height (m)')
plt.title('Basketball Motion with Drag - Multiple Angles')
plt.legend()
plt.grid(True)
plt.xlim([0, 8])
plt.ylim([0, 6])
plt.show()
