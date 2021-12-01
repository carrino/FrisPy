import math
from pprint import pprint

import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Discs

model = Discs.destroyer
v = 25
rot = -v/model.diameter
nose_up = 0
hyzer = 10
uphill = 10
rotation_factor = 0
rotation_factor = 1 / 5

dphi = 0
dtheta = 0
#dtheta = -rot * rotation_factor
dtheta = rot * rotation_factor
#dphi = -rot * rotation_factor

hyzer += math.atan(rotation_factor) / 2 * 180 / math.pi

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

x0 = [10, 0]
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": dphi, "dtheta": dtheta, "gamma": math.pi})
                    #"nose_up": nose_up, "hyzer": hyzer})

#result = disc.compute_trajectory(20)
result = disc.compute_trajectory(1, **{"max_step": .5, "rtol": 5e-4, "atol": 1e-6})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, y)
#plt.plot(x, z)

#plt.plot(t, result.dphi)
#plt.plot(t, result.dtheta)

#plt.plot(t, result.phi)
plt.plot(t, [i * 180 / math.pi for i in result.phi])
plt.plot(t, [i * 180 / math.pi for i in result.theta])
#plt.plot(t, [math.sin(i) for i in result.gamma])

pprint(x[-1])
plt.show()
