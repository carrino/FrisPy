#  Copyright (c) 2021 John Carrino
import math
from pprint import pprint
import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

mph_to_mps = 0.44704

model = Discs.destroyer
v = 46 * mph_to_mps
rot = -v / model.diameter
nose_up = 0
hyzer = 0
uphill = 10

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15)
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(result.x, result.y)
plt.plot(result.x, result.z)
pprint(len(result.x))

pprint(result.x[-1] * 3.28084) # convert m to feet
plt.show()

