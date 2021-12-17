import math
from pprint import pprint
import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

# model = Discs.destroyter
model = Discs.flick
v = 30 * 0.44704 # 30 mph
rot = -v / model.diameter
hyzer = -90
uphill = 0
z = 1000
# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "z": z, "hyzer": hyzer})

#result = disc.compute_trajectory(15)
#result = disc.compute_trajectory(15, **{"max_step": .5, "rtol": 1e-6, "atol": 1e-9})
result = disc.compute_trajectory(30, **{"max_step": .2, "rtol": 1e-5, "atol": 1e-8})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

# angle of attack
#plt.plot(t, [i / math.pi * 180 for i in result.aoa])


plt.plot(t, result.y)
#plt.plot(t, result.z)
#plt.plot(t, result.phi)
#plt.plot(t, result.theta)

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

