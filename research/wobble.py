import math
from pprint import pprint

import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Discs

model = Discs.stable_destroyer
v = 55 * 0.44704
rot = -v/model.diameter
nose_up = 0
hyzer = 0
uphill = 0
rotation_factor = 0
rotation_factor = 1 / 10

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
result = disc.compute_trajectory(1, **{"max_step": .001, "rtol": 1e-8, "atol": 1e-3})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(t, y)
#plt.plot(t, z)

#plt.plot(t, result.phi) # phi is anhyzer
plt.plot(t, result.theta) # theta is nose up
#plt.plot(t, result.gamma) # gamma is rotation around Z

#plt.plot(t, result.phi)
#plt.plot(t, [i * 180 / math.pi for i in result.phi])
#plt.plot(t, [i * 180 / math.pi for i in result.theta])
#plt.plot(t, [math.sin(i) for i in result.gamma])

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()
