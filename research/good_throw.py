import math
from pprint import pprint
import numpy as np
import time


import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.destroyer
#v = 54.5 * 0.44704
v = 24.36
rot = -133.7
nose_up = 1.15
hyzer = 7.8
uphill = 2.79
wx = -13.2
wy = -8.88
gamma = -1.135

#wx = 0
#wy = 0
#hyzer = 5.8
#nose_up = -2.17


#degrees = math.atan2(wx/2, rot)
#degrees = math.atan2(rot, wx/2)
degrees = math.atan(wx/rot/2) * 180 / math.pi

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

start = time.perf_counter()
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": wx, "dtheta": wy, "gamma": gamma})

hz = abs(rot) / math.pi / 2
# In order to get a smooth output for the rotation of the disc
# we need to have enough samples to spin in the correct direction
max_step = 0.45 / hz
#result = disc.compute_trajectory(30, **{"max_step": 1, "rtol": 1e-3, "atol": 1e-5})
result = disc.compute_trajectory(15, **{"max_step": max_step, "rtol": 5e-4, "atol": 5e-6})

duration = time.perf_counter() - start
pprint(duration)


times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

# advance rate
# goes from .5 to about 1.2
#plt.plot(t, [-i / np.linalg.norm(v) * model.diameter / 2 for i, v in zip(result.dgamma, result.v)])

# angle of attack
#plt.plot(t, [i / math.pi * 180 for i in result.aoa])


plt.plot(t, result.y)
plt.plot(t, result.z)


#plt.plot(t, result.y)
#plt.plot(t, result.z)
#plt.plot(t, result.phi)
#plt.plot(t, result.theta)
#plt.plot(t, result.z)
#pprint(len(result.x))

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

