import math
from pprint import pprint
import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.roc
v = 20
rot = -v / model.diameter * 1.3 # add extra spin
nose_up = 0
hyzer = 11
uphill = 6

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(5, **{"max_step": .2, "atol": 1e-9})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

# advance rate
# goes from .5 to about 1.2
#plt.plot(t, [-i / np.linalg.norm(v) * model.diameter / 2 for i, v in zip(result.dgamma, result.v)])

# angle of attack
#plt.plot(t, [i / math.pi * 180 for i in result.aoa])


plt.plot(t, result.y)
plt.plot(t, result.z)


#plt.plot(t, result.x)
#plt.plot(t, result.y)
#plt.plot(t, result.z)

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

