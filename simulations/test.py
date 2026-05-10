
import numpy as np
import matplotlib.pyplot as plt

#initialize variables
#velocity, gravity
v = 30
g = 9.81
#increment theta 25 to 60 then find  t, x, y
#define x and y as arrays
theta = np.arange(25,65,5)[None,:]/180.0*np.pi #convert to radians, watch out for modulo division

plt.figure()

tmax = ((2 * v) * np.sin(theta)) / g
timemat = tmax*np.linspace(0,1,100)[:,None] #create time vectors for each angle

x = ((v * timemat) * np.cos(theta))
y = ((v * timemat) * np.sin(theta)) - ((0.5 * g) * (timemat ** 2))

plt.plot(x,y) #plot each dataset: columns of x and columns of y
plt.ylim([0,35])
plt.show()
