import math
from pprint import pprint
import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

#model = Discs.stable_wraith
#v = 65 * 0.44704 # 65 mph
#rot = -20.4 * 2 * math.pi # 20.4 Hz in rad/s
#nose_up = 0.7
#hyzer = 18
#uphill = 6.4

model = Discs.wraith
v = 58 * 0.44704 # 58 mph
rot = -20.3 * 2 * math.pi # 20.4 Hz in rad/s
nose_up = 0.9
hyzer = -1.4
uphill = 10

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15, **{"max_step": .5, "atol": 1e-9})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

# advance rate
# goes from .5 to about 1.2
#plt.plot(t, [-i / np.linalg.norm(v) * model.diameter / 2 for i, v in zip(result.dgamma, result.v)])

# angle of attack
#plt.plot(t, [i / math.pi * 180 for i in result.aoa])


#plt.plot(t, result.y)
#plt.plot(t, result.z)


plt.plot(result.x, result.y)
plt.plot(result.x, result.z)
#plt.plot(t, result.z)

pprint(result.z)

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

