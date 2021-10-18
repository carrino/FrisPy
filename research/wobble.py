import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.roc
v = 20
rot = -v / model.diameter
nose_up = 0
hyzer = 0
uphill = 11.89938406
dphi = 2
#dphi = 0
hyzer -= 1 / 4

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

x0 = [10, 0]
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": dphi})
                    #"nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(8, None, **{"max_step": .2, "atol": 1e-9})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, y)
#plt.plot(x, z)

#plt.plot(t, result.dphi)
#plt.plot(t, result.dtheta)

#plt.plot(t, y)
#plt.plot(t, x)

plt.plot(t, result.phi)
plt.plot(t, result.theta)

pprint(x[-1])

plt.show()
