import math
from pprint import pprint

import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Discs

model = Discs.destroyer
v = 26
wz = -v/model.diameter
nose_up = 0
hyzer = 0
uphill = 10
degWobble = 5
phase = math.pi / 2

radWobble = degWobble * math.pi / 180

wx = math.sin(phase) * radWobble * wz * 2
wy = -math.cos(phase) * radWobble * wz * 2

hyzer += math.cos(phase) * degWobble
nose_up += math.sin(phase) * degWobble

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

x0 = [10, 0]
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": wz, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": wx, "dtheta": wy, "gamma": 0})
                    #"nose_up": nose_up, "hyzer": hyzer})

#result = disc.compute_trajectory(20)
result = disc.compute_trajectory(20, **{"max_step": .5, "rtol": 5e-4, "atol": 1e-6})
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

print(x[-1] * 3.28084, y[-1] * 3.28084)
plt.show()
