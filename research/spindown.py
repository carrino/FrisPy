import math
from pprint import pprint

import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Discs

model = Discs.roc
v = 20
rot = -v / model.diameter
nose_up = 0
hyzer = 0
uphill = 10
dphi = 0

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": dphi})

result = disc.compute_trajectory(5, **{"max_step": .2, "atol": 1e-9})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

pprint(rot)

plt.plot(t, result.dgamma)

pprint(result.dgamma[-1])

plt.show()
