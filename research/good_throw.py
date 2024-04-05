import math
from pprint import pprint
import numpy as np
import time
from frispy.environment import Environment


import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

#model = Discs.stable_destroyer
model = Discs.destroyer
v = 50 * 0.44704
rot = -133.7
nose_up = -0
hyzer = -10
uphill = 10
wx = -13.2
wx = 0
wy = -8.88
wy = 0
gamma = -1.135
gamma = 0

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
env: Environment = Environment()
env._ground_play_enabled = True
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": wx, "dtheta": wy, "gamma": gamma}, env)

hz = abs(rot) / math.pi / 2
# In order to get a smooth output for the rotation of the disc
# we need to have enough samples to spin in the correct direction
max_step = 0.45 / hz
#result = disc.compute_trajectory(30, **{"max_step": 1, "rtol": 1e-3, "atol": 1e-5})
result = disc.compute_trajectory(15.0,
                                 **{"max_step": max_step,
                                    "rtol": 1e-3,
                                    "atol": 1e-3,
                                    "method": "DOP853",
                                    })

duration = time.perf_counter() - start
pprint(duration)


times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

# advance rate
# goes from .5 to about 1.2
#plt.plot(t, [-i / np.linalg.norm(v) * model.diameter / 2 for i, v in zip(result.dgamma, result.v)])

# angle of attack
#plt.plot(t, [i / math.pi * 180 for i in result.aoa])


plt.plot(t, result.x)
plt.plot(t, result.y)
plt.plot(t, result.z)
#plt.plot(t, result.dgamma)


#plt.plot(t, result.phi)
#plt.plot(t, result.theta)

#plt.plot(t, result.dgamma)
#plt.plot(t, result.z)
#pprint(len(result.x))

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

