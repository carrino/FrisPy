#  Copyright (c) 2021 John Carrino

import math
from pprint import pprint
import matplotlib.pyplot as plt
from frispy import Disc
from frispy import Discs

model = Discs.destroyer
mph_to_mps = 0.44704
v = 55 * mph_to_mps
rot = -v / model.diameter * 1.2

x0 = [10, -3, 7]
a, nose_up, hyzer = x0
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer, "gamma": -2})

result = disc.compute_trajectory(20.0, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, result.theta)
plt.plot(x, y)
plt.plot(x, z)

#plt.plot(t, x)
#plt.plot(t, y)
#plt.plot(t, z)

pprint(x[-1] * 3.28084) # feet

plt.show()
